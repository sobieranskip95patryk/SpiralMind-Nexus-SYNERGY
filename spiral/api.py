"""
FastAPI Web API for SpiralMind Nexus v0.2
Provides REST endpoints and WebSocket support for AI pipeline
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
from datetime import datetime

from .config.loader import load_config
from .pipeline.double_pipeline import execute, create_event
from .utils.logging_config import setup_logging, get_logger

# Initialize FastAPI app
app = FastAPI(
    title="SpiralMind Nexus API",
    description="AI Double Pipeline System - REST & WebSocket API",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Load configuration
try:
    config = load_config("config/config.yaml")
    logger.info("Configuration loaded successfully")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    config = None

# Pydantic Models
class AnalysisRequest(BaseModel):
    text: str = Field(..., description="Text to analyze", min_length=1)
    mode: Optional[str] = Field("BALANCED", description="Pipeline mode: VERIFICATION, CREATIVE, BALANCED")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

class BatchAnalysisRequest(BaseModel):
    items: List[AnalysisRequest] = Field(..., description="List of texts to analyze")
    
class AnalysisResponse(BaseModel):
    decision: str = Field(..., description="Pipeline decision")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    success: float = Field(..., description="Success probability (0.0-1.0)")
    iterations: int = Field(..., description="Number of pipeline iterations")
    pipeline_mode: str = Field(..., description="Used pipeline mode")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    timestamp: str = Field(..., description="Analysis timestamp")

class BatchAnalysisResponse(BaseModel):
    results: List[AnalysisResponse] = Field(..., description="Individual analysis results")
    summary: Dict[str, Any] = Field(..., description="Batch processing summary")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    config_loaded: bool = Field(..., description="Configuration status")
    uptime_seconds: int = Field(..., description="Service uptime")

class StreamMessage(BaseModel):
    type: str = Field(..., description="Message type: analysis, status, error")
    data: Dict[str, Any] = Field(..., description="Message payload")
    timestamp: str = Field(..., description="Message timestamp")

# Global state
start_time = datetime.now()
active_connections: List[WebSocket] = []

# Helper functions
def get_current_timestamp() -> str:
    return datetime.now().isoformat()

async def process_single_analysis(request: AnalysisRequest) -> AnalysisResponse:
    """Process single text analysis"""
    import time
    start_time = time.time()
    
    if not config:
        raise HTTPException(status_code=503, detail="Configuration not loaded")
    
    # Override mode if specified
    analysis_config = config
    if request.mode and request.mode in ["VERIFICATION", "CREATIVE", "BALANCED"]:
        analysis_config.pipeline.mode = request.mode
    
    # Create event and execute pipeline
    event = create_event(request.text, request.context)
    result, iterations = execute(event, analysis_config)
    
    processing_time = (time.time() - start_time) * 1000
    
    return AnalysisResponse(
        decision=result.decision,
        confidence=result.score.confidence,
        success=result.score.success,
        iterations=iterations,
        pipeline_mode=result.pipeline_mode,
        processing_time_ms=round(processing_time, 2),
        timestamp=get_current_timestamp()
    )

async def broadcast_to_websockets(message: StreamMessage):
    """Broadcast message to all connected WebSocket clients"""
    if not active_connections:
        return
    
    message_json = message.json()
    disconnected = []
    
    for connection in active_connections:
        try:
            await connection.send_text(message_json)
        except WebSocketDisconnect:
            disconnected.append(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        active_connections.remove(conn)

# REST Endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information"""
    return """
    <html>
        <head>
            <title>SpiralMind Nexus API v0.2.0</title>
        </head>
        <body>
            <h1>🧠 SpiralMind Nexus API v0.2.0</h1>
            <p>AI Double Pipeline System - REST & WebSocket API</p>
            <ul>
                <li><a href="/docs">📚 API Documentation (Swagger)</a></li>
                <li><a href="/redoc">📖 ReDoc Documentation</a></li>
                <li><a href="/health">💚 Health Check</a></li>
            </ul>
            <h2>Quick Start</h2>
            <pre>
# Single analysis
curl -X POST "http://localhost:8000/analyze" \\
     -H "Content-Type: application/json" \\
     -d '{"text": "Hello SpiralMind", "mode": "BALANCED"}'

# WebSocket connection
ws://localhost:8000/ws/stream
            </pre>
        </body>
    </html>
    """

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now() - start_time).total_seconds()
    
    return HealthResponse(
        status="healthy",
        version="0.2.0",
        config_loaded=config is not None,
        uptime_seconds=int(uptime)
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(request: AnalysisRequest):
    """
    Analyze single text using SpiralMind pipeline
    
    - **text**: Text to analyze (required)
    - **mode**: Pipeline mode - VERIFICATION, CREATIVE, or BALANCED (optional)
    - **context**: Additional context dictionary (optional)
    """
    try:
        logger.info(f"Processing analysis request: mode={request.mode}, text_length={len(request.text)}")
        result = await process_single_analysis(request)
        logger.info(f"Analysis completed: decision={result.decision}, confidence={result.confidence:.3f}")
        
        # Broadcast to WebSocket clients
        stream_message = StreamMessage(
            type="analysis",
            data=result.dict(),
            timestamp=get_current_timestamp()
        )
        await broadcast_to_websockets(stream_message)
        
        return result
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_batch(request: BatchAnalysisRequest):
    """
    Analyze multiple texts in batch
    
    - **items**: List of analysis requests
    
    Returns individual results plus batch summary statistics
    """
    try:
        logger.info(f"Processing batch analysis: {len(request.items)} items")
        
        results = []
        total_processing_time = 0.0
        
        for item in request.items:
            result = await process_single_analysis(item)
            results.append(result)
            total_processing_time += result.processing_time_ms
        
        # Calculate summary statistics
        if results:
            avg_confidence = sum(r.confidence for r in results) / len(results)
            avg_success = sum(r.success for r in results) / len(results)
            total_iterations = sum(r.iterations for r in results)
        else:
            avg_confidence = avg_success = total_iterations = 0
        
        summary = {
            "total_items": len(results),
            "average_confidence": round(avg_confidence, 4),
            "average_success": round(avg_success, 4),
            "total_iterations": total_iterations,
            "total_processing_time_ms": round(total_processing_time, 2)
        }
        
        batch_response = BatchAnalysisResponse(
            results=results,
            summary=summary
        )
        
        logger.info(f"Batch analysis completed: {len(results)} items processed")
        
        # Broadcast batch completion
        stream_message = StreamMessage(
            type="batch_complete",
            data={"summary": summary, "items_count": len(results)},
            timestamp=get_current_timestamp()
        )
        await broadcast_to_websockets(stream_message)
        
        return batch_response
    
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

# WebSocket Endpoints
@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time analysis streaming
    
    Send JSON messages with analysis requests:
    {"text": "your text", "mode": "BALANCED"}
    
    Receive real-time analysis results and status updates
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    logger.info("WebSocket client connected")
    
    # Send welcome message
    welcome = StreamMessage(
        type="status",
        data={"message": "Connected to SpiralMind Nexus stream", "version": "0.2.0"},
        timestamp=get_current_timestamp()
    )
    await websocket.send_text(welcome.json())
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                # Parse request
                request_data = json.loads(data)
                request = AnalysisRequest(**request_data)
                
                # Process analysis
                result = await process_single_analysis(request)
                
                # Send result back
                response = StreamMessage(
                    type="analysis",
                    data=result.dict(),
                    timestamp=get_current_timestamp()
                )
                await websocket.send_text(response.json())
                
            except json.JSONDecodeError:
                error_msg = StreamMessage(
                    type="error",
                    data={"error": "Invalid JSON format"},
                    timestamp=get_current_timestamp()
                )
                await websocket.send_text(error_msg.json())
                
            except Exception as e:
                error_msg = StreamMessage(
                    type="error",
                    data={"error": str(e)},
                    timestamp=get_current_timestamp()
                )
                await websocket.send_text(error_msg.json())
    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
        if websocket in active_connections:
            active_connections.remove(websocket)

# Optional: Static file serving for simple web client
@app.get("/client", response_class=HTMLResponse)
async def simple_client():
    """Simple HTML client for testing WebSocket functionality"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SpiralMind Nexus Client</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; }
            textarea { width: 100%; height: 100px; }
            button { padding: 10px 20px; margin: 10px 0; }
            #output { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll; }
            .message { margin: 5px 0; padding: 5px; border-radius: 3px; }
            .analysis { background-color: #e8f5e8; }
            .error { background-color: #ffe8e8; }
            .status { background-color: #e8f0ff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 SpiralMind Nexus Client</h1>
            <textarea id="textInput" placeholder="Enter text to analyze..."></textarea><br>
            <select id="modeSelect">
                <option value="BALANCED">BALANCED</option>
                <option value="VERIFICATION">VERIFICATION</option>
                <option value="CREATIVE">CREATIVE</option>
            </select>
            <button onclick="sendAnalysis()">Analyze</button>
            <button onclick="clearOutput()">Clear</button>
            <div id="output"></div>
        </div>
        
        <script>
            const ws = new WebSocket('ws://localhost:8000/ws/stream');
            const output = document.getElementById('output');
            
            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                const div = document.createElement('div');
                div.className = 'message ' + message.type;
                
                if (message.type === 'analysis') {
                    div.innerHTML = `<strong>Analysis:</strong> ${message.data.decision} 
                                   (conf: ${message.data.confidence.toFixed(3)}, 
                                    succ: ${message.data.success.toFixed(3)}, 
                                    iters: ${message.data.iterations})`;
                } else {
                    div.innerHTML = `<strong>${message.type}:</strong> ${JSON.stringify(message.data)}`;
                }
                
                output.appendChild(div);
                output.scrollTop = output.scrollHeight;
            };
            
            function sendAnalysis() {
                const text = document.getElementById('textInput').value;
                const mode = document.getElementById('modeSelect').value;
                
                if (text.trim()) {
                    ws.send(JSON.stringify({text: text, mode: mode}));
                }
            }
            
            function clearOutput() {
                output.innerHTML = '';
            }
            
            document.getElementById('textInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && e.ctrlKey) {
                    sendAnalysis();
                }
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")