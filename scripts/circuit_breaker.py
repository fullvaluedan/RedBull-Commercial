"""
Single-Shot Generation & 2-Strike Circuit Breaker Harness
=========================================================
Enforces the strict production protocol:
1. Single-piece generation (batch = 1).
2. Automated 1.0s audit frame extraction.
3. 2-Strike Circuit Breaker: Max 2 attempts per shot. If Attempt 2 fails,
   hard-stops execution and triggers manual review.
4. Interfaces with the 3 verification subagents:
   - continuity-qc
   - physics-acting-qc
   - technical-resolve-qc
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

PROJ_DIR = Path(r"D:\Claude\Gossip\videos\redbull_desert_short")
OUT_DIR = PROJ_DIR / "omniflash_pass"
AUDIT_DIR = PROJ_DIR / "audit_omniflash"
BRAIN_DIR = Path(r"C:\Users\danom\.gemini\antigravity\brain\08cf9524-22c4-4291-978b-a493c7795acb")

OUT_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


class CircuitBreaker:
    def __init__(self, shot_id: str, description: str):
        self.shot_id = shot_id
        self.description = description
        self.attempts = 0
        self.max_attempts = 2
        self.attempt_history: List[Dict[str, Any]] = []

    def can_attempt(self) -> bool:
        """Returns True if the circuit breaker has not tripped."""
        return self.attempts < self.max_attempts

    def record_attempt(self, prompt: str, video_path: Optional[str], verdicts: Dict[str, Any]) -> Dict[str, Any]:
        """Record the outcome of an attempt."""
        self.attempts += 1
        passed = all(v.get("status") == "PASS" for v in verdicts.values())
        record = {
            "attempt": self.attempts,
            "prompt": prompt,
            "video_path": str(video_path) if video_path else None,
            "verdicts": verdicts,
            "passed": passed
        }
        self.attempt_history.append(record)

        if not passed and self.attempts >= self.max_attempts:
            print(f"\n🚨 [CIRCUIT BREAKER TRIPPED] {self.shot_id} failed {self.max_attempts} consecutive attempts!")
            print("Execution halted. Manual review required.")
        return record

    def is_tripped(self) -> bool:
        return self.attempts >= self.max_attempts and not self.attempt_history[-1].get("passed", False)


def extract_audit_frames(video_path: Path, shot_id: str) -> List[Path]:
    """Extract frames at 0.5s, 1.5s, 2.5s, 3.5s for multi-agent inspection."""
    shot_audit_dir = AUDIT_DIR / shot_id
    shot_audit_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    timestamps = [0.5, 1.5, 2.5, 3.5]
    for sec in timestamps:
        frame_file = shot_audit_dir / f"{shot_id}_sec{int(sec):02d}.jpg"
        cmd = [
            "ffmpeg", "-y", "-ss", str(sec), "-i", str(video_path),
            "-vframes", "1", "-q:v", "2", str(frame_file)
        ]
        subprocess.run(cmd, capture_output=True)
        if frame_file.exists():
            frames.append(frame_file)
    return frames
