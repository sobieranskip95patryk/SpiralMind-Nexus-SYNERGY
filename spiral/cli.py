"""
Command Line Interface for SpiralMind Nexus v0.2
"""

import argparse
import json
import sys
import pathlib
from .config.loader import load_config
from .pipeline.double_pipeline import execute, create_event
from .utils.logging_config import setup_logging


def _print(payload, fmt):
    """Print result in specified format"""
    if fmt == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"[{payload['decision']}] conf={payload['confidence']:.3f} succ={payload['success']:.3f} iters={payload['iterations']}")


def main():
    """Main CLI entry point"""
    ap = argparse.ArgumentParser(
        prog="spiral",
        description="SpiralMind Nexus v0.2.0 - AI Double Pipeline System"
    )
    
    # Configuration
    ap.add_argument("--config", default="config/config.yaml", 
                   help="Configuration file path (default: config/config.yaml)")
    
    # Input options
    ap.add_argument("--text", help="Input text to process")
    ap.add_argument("--batch", help="JSON file with batch inputs")
    
    # Pipeline options
    ap.add_argument("--mode", choices=["VERIFICATION", "CREATIVE", "BALANCED"], 
                   help="Override pipeline mode")
    
    # Operation modes
    ap.add_argument("--validate-only", action="store_true", 
                   help="Only validate configuration, don't process")
    
    # Output options
    ap.add_argument("--format", choices=["text", "json"], default="json", 
                   help="Output format (default: json)")
    ap.add_argument("--stats", action="store_true", 
                   help="Show processing statistics")
    ap.add_argument("--quiet", action="store_true", 
                   help="Suppress non-essential output")
    
    args = ap.parse_args()
    
    # Setup logging
    log_level = "ERROR" if args.quiet else "INFO"
    setup_logging(log_level)
    
    try:
        # Load configuration
        cfg = load_config(args.config)
        
        # Override mode if specified
        if args.mode:
            cfg.pipeline.mode = args.mode
        
        # Validation-only mode
        if args.validate_only:
            _print({
                "decision": "VALID",
                "confidence": 1.0,
                "success": 1.0,
                "iterations": 0
            }, args.format)
            return 0
        
        # Batch processing
        if args.batch:
            batch_path = pathlib.Path(args.batch)
            if not batch_path.exists():
                print(f"❌ Batch file not found: {args.batch}", file=sys.stderr)
                return 1
            
            try:
                items = json.loads(batch_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in batch file: {e}", file=sys.stderr)
                return 1
            
            results = []
            for i, item in enumerate(items):
                # Handle different input formats
                if isinstance(item, str):
                    event = create_event(item)
                elif isinstance(item, dict):
                    text = item.get("text", "")
                    context = item.get("context", {})
                    event = create_event(text, context)
                else:
                    print(f"⚠️ Skipping invalid item {i}: {item}", file=sys.stderr)
                    continue
                
                result, iters = execute(event, cfg)
                results.append({
                    "decision": result.decision,
                    "confidence": result.score.confidence,
                    "success": result.score.success,
                    "iterations": iters
                })
            
            # Summary for batch
            if not args.quiet:
                batch_summary = {
                    "decision": "BATCH",
                    "confidence": sum(r["confidence"] for r in results) / len(results) if results else 0.0,
                    "success": sum(r["success"] for r in results) / len(results) if results else 0.0,
                    "iterations": len(results)
                }
                _print(batch_summary, args.format)
            
            # Output results
            if args.format == "json":
                print(json.dumps(results, ensure_ascii=False, indent=2))
            else:
                for i, result in enumerate(results):
                    print(f"Item {i+1}: [{result['decision']}] conf={result['confidence']:.3f} succ={result['success']:.3f} iters={result['iterations']}")
            
            # Stats if requested
            if args.stats and results:
                print("\n=== Batch Statistics ===", file=sys.stderr)
                print(f"Processed: {len(results)} items", file=sys.stderr)
                print(f"Average confidence: {sum(r['confidence'] for r in results) / len(results):.3f}", file=sys.stderr)
                print(f"Average success: {sum(r['success'] for r in results) / len(results):.3f}", file=sys.stderr)
                print(f"Total iterations: {sum(r['iterations'] for r in results)}", file=sys.stderr)
            
            return 0
        
        # Single text processing
        text = args.text or "Hello SpiralMind"
        event = create_event(text)
        result, iters = execute(event, cfg)
        
        payload = {
            "decision": result.decision,
            "confidence": result.score.confidence,
            "success": result.score.success,
            "iterations": iters
        }
        
        _print(payload, args.format)
        
        # Stats if requested
        if args.stats:
            print("\n=== Statistics ===", file=sys.stderr)
            print(f"Pipeline mode: {result.pipeline_mode}", file=sys.stderr)
            print(f"Confidence: {result.score.confidence:.4f}", file=sys.stderr)
            print(f"Success: {result.score.success:.4f}", file=sys.stderr)
            print(f"Iterations: {iters}", file=sys.stderr)
        
        return 0
    
    except Exception as e:
        if not args.quiet:
            print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())