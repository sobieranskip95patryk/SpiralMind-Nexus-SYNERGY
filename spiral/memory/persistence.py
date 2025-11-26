"""
Memory Persistence Layer for SpiralMind Nexus
Implements episodic and semantic memory for AGI evolution
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import threading

from ..utils.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class MemoryRecord:
    """Single memory record with metadata"""
    id: str
    content: str
    memory_type: str  # 'episodic' | 'semantic' | 'procedural'
    confidence: float
    success: float
    decision: str
    pipeline_mode: str
    context: Dict[str, Any]
    timestamp: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    importance: float = 0.0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        if isinstance(self.last_accessed, str) and self.last_accessed:
            self.last_accessed = datetime.fromisoformat(self.last_accessed)

@dataclass
class MemoryPattern:
    """Discovered pattern in memory data"""
    pattern_type: str
    pattern_data: Dict[str, Any]
    confidence: float
    frequency: int
    last_seen: datetime
    contexts: List[str]

class MemoryPersistence:
    """
    Advanced memory persistence system with episodic and semantic layers
    
    Features:
    - SQLite storage with efficient indexing
    - Episodic memory (specific experiences)
    - Semantic memory (generalized knowledge)
    - Pattern recognition and extraction
    - Importance scoring and retention policies
    - Thread-safe operations
    """
    
    def __init__(self, db_path: str = "spiral_memory.db"):
        self.db_path = Path(db_path)
        self.lock = threading.RLock()
        self._initialize_database()
        logger.info(f"Memory persistence initialized: {self.db_path}")
    
    def _initialize_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_records (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    success REAL NOT NULL,
                    decision TEXT NOT NULL,
                    pipeline_mode TEXT NOT NULL,
                    context TEXT,  -- JSON
                    timestamp TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    importance REAL DEFAULT 0.0,
                    tags TEXT  -- JSON array
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,  -- JSON
                    confidence REAL NOT NULL,
                    frequency INTEGER NOT NULL,
                    last_seen TEXT NOT NULL,
                    contexts TEXT  -- JSON array
                )
            """)
            
            # Create indexes for efficient queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_records(memory_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_records(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memory_records(importance)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_decision ON memory_records(decision)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pattern_type ON memory_patterns(pattern_type)")
            
            conn.commit()
    
    def _generate_memory_id(self, content: str, context: Dict[str, Any]) -> str:
        """Generate unique memory ID based on content and context"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        context_str = json.dumps(context, sort_keys=True)
        context_hash = hashlib.sha256(context_str.encode()).hexdigest()[:8]
        return f"{content_hash}_{context_hash}"
    
    def store_memory(self, 
                    content: str,
                    decision: str,
                    confidence: float,
                    success: float,
                    pipeline_mode: str,
                    context: Dict[str, Any] = None,
                    memory_type: str = "episodic",
                    tags: List[str] = None) -> str:
        """
        Store new memory record
        
        Args:
            content: The text content that was processed
            decision: Pipeline decision result
            confidence: Confidence score
            success: Success probability
            pipeline_mode: Mode used for processing
            context: Additional context information
            memory_type: Type of memory ('episodic', 'semantic', 'procedural')
            tags: Optional tags for categorization
            
        Returns:
            Memory record ID
        """
        if context is None:
            context = {}
        if tags is None:
            tags = []
        
        memory_id = self._generate_memory_id(content, context)
        timestamp = datetime.now()
        
        # Calculate importance based on confidence, success, and uniqueness
        importance = self._calculate_importance(confidence, success, decision, content)
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                # Check if memory already exists (update access count)
                existing = conn.execute(
                    "SELECT access_count FROM memory_records WHERE id = ?",
                    (memory_id,)
                ).fetchone()
                
                if existing:
                    # Update existing record
                    conn.execute("""
                        UPDATE memory_records 
                        SET access_count = access_count + 1,
                            last_accessed = ?,
                            importance = MAX(importance, ?)
                        WHERE id = ?
                    """, (timestamp.isoformat(), importance, memory_id))
                    logger.debug(f"Updated existing memory: {memory_id}")
                else:
                    # Insert new record
                    conn.execute("""
                        INSERT INTO memory_records 
                        (id, content, memory_type, confidence, success, decision, 
                         pipeline_mode, context, timestamp, importance, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        memory_id, content, memory_type, confidence, success,
                        decision, pipeline_mode, json.dumps(context),
                        timestamp.isoformat(), importance, json.dumps(tags)
                    ))
                    logger.debug(f"Stored new memory: {memory_id}")
                
                conn.commit()
        
        # Trigger pattern analysis for semantic memories
        if memory_type == "semantic":
            self._analyze_patterns()
        
        return memory_id
    
    def _calculate_importance(self, confidence: float, success: float, 
                            decision: str, content: str) -> float:
        """Calculate importance score for memory retention"""
        base_score = (confidence + success) / 2.0
        
        # Boost importance for certain decisions
        decision_weights = {
            "ACCEPT": 1.0,
            "REVISE": 0.8,
            "REJECT": 0.6,
            "FORCE_ACCEPT": 1.2
        }
        decision_weight = decision_weights.get(decision, 1.0)
        
        # Boost for longer, more complex content
        content_factor = min(1.2, 1.0 + len(content) / 1000.0)
        
        return min(1.0, base_score * decision_weight * content_factor)
    
    def retrieve_memories(self,
                         memory_type: Optional[str] = None,
                         decision: Optional[str] = None,
                         min_importance: float = 0.0,
                         limit: int = 100,
                         recent_days: Optional[int] = None) -> List[MemoryRecord]:
        """
        Retrieve memories based on criteria
        
        Args:
            memory_type: Filter by memory type
            decision: Filter by decision type
            min_importance: Minimum importance threshold
            limit: Maximum number of records to return
            recent_days: Only return memories from last N days
            
        Returns:
            List of matching memory records
        """
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                query = "SELECT * FROM memory_records WHERE importance >= ?"
                params = [min_importance]
                
                if memory_type:
                    query += " AND memory_type = ?"
                    params.append(memory_type)
                
                if decision:
                    query += " AND decision = ?"
                    params.append(decision)
                
                if recent_days:
                    cutoff_date = datetime.now() - timedelta(days=recent_days)
                    query += " AND timestamp >= ?"
                    params.append(cutoff_date.isoformat())
                
                query += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
                params.append(limit)
                
                rows = conn.execute(query, params).fetchall()
                
                memories = []
                for row in rows:
                    context = json.loads(row['context']) if row['context'] else {}
                    tags = json.loads(row['tags']) if row['tags'] else []
                    
                    memory = MemoryRecord(
                        id=row['id'],
                        content=row['content'],
                        memory_type=row['memory_type'],
                        confidence=row['confidence'],
                        success=row['success'],
                        decision=row['decision'],
                        pipeline_mode=row['pipeline_mode'],
                        context=context,
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        access_count=row['access_count'],
                        last_accessed=datetime.fromisoformat(row['last_accessed']) if row['last_accessed'] else None,
                        importance=row['importance'],
                        tags=tags
                    )
                    memories.append(memory)
                
                # Update access counts
                memory_ids = [m.id for m in memories]
                if memory_ids:
                    placeholders = ','.join(['?'] * len(memory_ids))
                    conn.execute(f"""
                        UPDATE memory_records 
                        SET access_count = access_count + 1,
                            last_accessed = ?
                        WHERE id IN ({placeholders})
                    """, [datetime.now().isoformat()] + memory_ids)
                    conn.commit()
                
                logger.debug(f"Retrieved {len(memories)} memories")
                return memories
    
    def _analyze_patterns(self):
        """Analyze stored memories for patterns and trends"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Decision pattern analysis
                decision_patterns = conn.execute("""
                    SELECT decision, pipeline_mode, 
                           AVG(confidence) as avg_confidence,
                           AVG(success) as avg_success,
                           COUNT(*) as frequency
                    FROM memory_records
                    WHERE timestamp >= datetime('now', '-7 days')
                    GROUP BY decision, pipeline_mode
                    HAVING frequency >= 3
                """).fetchall()
                
                for pattern in decision_patterns:
                    pattern_data = {
                        "decision": pattern['decision'],
                        "pipeline_mode": pattern['pipeline_mode'],
                        "avg_confidence": pattern['avg_confidence'],
                        "avg_success": pattern['avg_success']
                    }
                    
                    self._store_pattern(
                        pattern_type="decision_trend",
                        pattern_data=pattern_data,
                        confidence=pattern['avg_confidence'],
                        frequency=pattern['frequency']
                    )
                
                # Content complexity patterns
                complexity_patterns = conn.execute("""
                    SELECT 
                        CASE 
                            WHEN LENGTH(content) < 50 THEN 'short'
                            WHEN LENGTH(content) < 200 THEN 'medium'
                            ELSE 'long'
                        END as content_length,
                        AVG(confidence) as avg_confidence,
                        AVG(success) as avg_success,
                        COUNT(*) as frequency
                    FROM memory_records
                    WHERE timestamp >= datetime('now', '-7 days')
                    GROUP BY content_length
                    HAVING frequency >= 5
                """).fetchall()
                
                for pattern in complexity_patterns:
                    pattern_data = {
                        "content_length": pattern['content_length'],
                        "avg_confidence": pattern['avg_confidence'],
                        "avg_success": pattern['avg_success']
                    }
                    
                    self._store_pattern(
                        pattern_type="complexity_pattern",
                        pattern_data=pattern_data,
                        confidence=pattern['avg_confidence'],
                        frequency=pattern['frequency']
                    )
    
    def _store_pattern(self, pattern_type: str, pattern_data: Dict[str, Any],
                      confidence: float, frequency: int):
        """Store discovered pattern"""
        timestamp = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            # Update existing or insert new pattern
            conn.execute("""
                INSERT OR REPLACE INTO memory_patterns
                (pattern_type, pattern_data, confidence, frequency, last_seen, contexts)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                pattern_type,
                json.dumps(pattern_data),
                confidence,
                frequency,
                timestamp.isoformat(),
                json.dumps([])  # contexts placeholder
            ))
            conn.commit()
        
        logger.debug(f"Stored pattern: {pattern_type}")
    
    def get_patterns(self, pattern_type: Optional[str] = None) -> List[MemoryPattern]:
        """Retrieve discovered patterns"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if pattern_type:
                    rows = conn.execute(
                        "SELECT * FROM memory_patterns WHERE pattern_type = ? ORDER BY confidence DESC",
                        (pattern_type,)
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM memory_patterns ORDER BY confidence DESC"
                    ).fetchall()
                
                patterns = []
                for row in rows:
                    pattern = MemoryPattern(
                        pattern_type=row['pattern_type'],
                        pattern_data=json.loads(row['pattern_data']),
                        confidence=row['confidence'],
                        frequency=row['frequency'],
                        last_seen=datetime.fromisoformat(row['last_seen']),
                        contexts=json.loads(row['contexts'])
                    )
                    patterns.append(pattern)
                
                return patterns
    
    def cleanup_old_memories(self, retention_days: int = 30, min_importance: float = 0.3):
        """Clean up old, low-importance memories"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute("""
                    DELETE FROM memory_records 
                    WHERE timestamp < ? AND importance < ?
                """, (cutoff_date.isoformat(), min_importance))
                
                deleted_count = result.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old memories")
                return deleted_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}
                
                # Total memories by type
                memory_counts = conn.execute("""
                    SELECT memory_type, COUNT(*) as count
                    FROM memory_records
                    GROUP BY memory_type
                """).fetchall()
                stats['memory_counts'] = {row[0]: row[1] for row in memory_counts}
                
                # Average scores
                avg_scores = conn.execute("""
                    SELECT AVG(confidence) as avg_confidence,
                           AVG(success) as avg_success,
                           AVG(importance) as avg_importance
                    FROM memory_records
                """).fetchone()
                
                stats['average_scores'] = {
                    'confidence': avg_scores[0] or 0.0,
                    'success': avg_scores[1] or 0.0,
                    'importance': avg_scores[2] or 0.0
                }
                
                # Decision distribution
                decisions = conn.execute("""
                    SELECT decision, COUNT(*) as count
                    FROM memory_records
                    GROUP BY decision
                    ORDER BY count DESC
                """).fetchall()
                stats['decision_distribution'] = {row[0]: row[1] for row in decisions}
                
                # Pattern counts
                pattern_counts = conn.execute("""
                    SELECT pattern_type, COUNT(*) as count
                    FROM memory_patterns
                    GROUP BY pattern_type
                """).fetchall()
                stats['pattern_counts'] = {row[0]: row[1] for row in pattern_counts}
                
                # Recent activity (last 7 days)
                recent_activity = conn.execute("""
                    SELECT DATE(timestamp) as date, COUNT(*) as count
                    FROM memory_records
                    WHERE timestamp >= datetime('now', '-7 days')
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """).fetchall()
                stats['recent_activity'] = {row[0]: row[1] for row in recent_activity}
                
                return stats

# Global memory instance
_memory_instance = None
_memory_lock = threading.Lock()

def get_memory_system(db_path: str = "spiral_memory.db") -> MemoryPersistence:
    """Get singleton memory system instance"""
    global _memory_instance
    
    with _memory_lock:
        if _memory_instance is None:
            _memory_instance = MemoryPersistence(db_path)
        return _memory_instance