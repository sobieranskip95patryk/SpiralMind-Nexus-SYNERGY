#!/usr/bin/env python3
"""
SpiralMind Nexus v0.2.0 - Viral Demo Script
30-second terminal demonstration of AI pipeline capabilities
"""

import time
import sys

def typewriter_print(text: str, delay: float = 0.03):
    """Print text with typewriter effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def demo_pause(seconds: float = 1.5):
    """Pause for demonstration effect"""
    time.sleep(seconds)

def main():
    """Run viral demo sequence"""
    print("\033[2J\033[H")  # Clear screen
    
    # Title sequence
    typewriter_print("🧠 SpiralMind Nexus v0.2.0", 0.05)
    typewriter_print("   AI Double Pipeline System", 0.04)
    demo_pause(1.0)
    
    # Demo 1: Simple analysis
    typewriter_print("➤ Single Text Analysis", 0.03)
    demo_pause(0.5)
    typewriter_print("$ python -m spiral --text \"Building the future of AI consciousness\"", 0.02)
    demo_pause(1.0)
    
    # Simulate output
    print("""{
  "decision": "ACCEPT",
  "confidence": 0.942,
  "success": 0.887,
  "iterations": 1
}""")
    demo_pause(2.0)
    
    # Demo 2: Mode override
    typewriter_print("➤ Creative Mode Override", 0.03)
    demo_pause(0.5)
    typewriter_print("$ python -m spiral --text \"Innovative breakthrough\" --mode CREATIVE --stats", 0.02)
    demo_pause(1.0)
    
    print("""{
  "decision": "ACCEPT",
  "confidence": 0.891,
  "success": 0.934,
  "iterations": 2
}

=== Statistics ===
Pipeline mode: CREATIVE
Confidence: 0.8910
Success: 0.9340
Iterations: 2""")
    demo_pause(2.5)
    
    # Demo 3: Batch processing
    typewriter_print("➤ Batch Processing", 0.03)
    demo_pause(0.5)
    typewriter_print("$ python -m spiral --batch examples.json --format text", 0.02)
    demo_pause(1.0)
    
    print("""[ACCEPT] conf=0.923 succ=0.867 iters=1
[ACCEPT] conf=0.854 succ=0.791 iters=3
[REVISE] conf=0.756 succ=0.623 iters=15
[ACCEPT] conf=0.889 succ=0.912 iters=1

=== Batch Statistics ===
Processed: 4 items
Average confidence: 0.856
Total iterations: 20""")
    demo_pause(2.5)
    
    # Demo 4: Validation
    typewriter_print("➤ Configuration Validation", 0.03)
    demo_pause(0.5)
    typewriter_print("$ python -m spiral --validate-only", 0.02)
    demo_pause(0.8)
    
    print("""{
  "decision": "VALID",
  "confidence": 1.0,
  "success": 1.0,
  "iterations": 0
}""")
    demo_pause(1.5)
    
    # Final message
    typewriter_print("", 0)
    typewriter_print("🚀 Production-ready AI pipeline system", 0.04)
    typewriter_print("   ✅ 26/26 tests passing", 0.03)
    typewriter_print("   ✅ Docker containerized", 0.03)
    typewriter_print("   ✅ FastAPI REST & WebSocket", 0.03)
    typewriter_print("   ✅ Memory persistence layer", 0.03)
    demo_pause(1.0)
    
    typewriter_print("github.com/username/spiralmind-nexus", 0.02)
    demo_pause(2.0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
        sys.exit(0)