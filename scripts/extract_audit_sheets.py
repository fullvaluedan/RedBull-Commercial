"""
Extract 1-Second Interval Audit Sheets for Omni-Flash 7-Shot Sequence
=====================================================================
Extracts frames at 0s, 1s, 2s, 3s for each shot, builds composite contact
sheets (4 frames horizontal per shot), saves them locally and to the artifact directory.
"""

import sys
import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJ_DIR = Path(r"D:\Claude\Gossip\videos\redbull_desert_short")
OUT_DIR = PROJ_DIR / "omniflash_pass"
AUDIT_DIR = PROJ_DIR / "audit_omniflash"
BRAIN_DIR = Path(r"C:\Users\danom\.gemini\antigravity\brain\08cf9524-22c4-4291-978b-a493c7795acb")

AUDIT_DIR.mkdir(parents=True, exist_ok=True)

SHOTS = [
    "shot01_sputter_arrival.mp4",
    "shot02_pov_price_macro.mp4",
    "shot03_reaction_sticker_shock.mp4",
    "shot04_pov_redbull_deal.mp4",
    "shot05_reaction_eureka_smirk.mp4",
    "shot06_macro_pour_double_cans.mp4",
    "shot07_payoff_ignition_explosion.mp4"
]

def extract_and_build():
    print("=" * 80)
    print("EXTRACTING 1-SECOND AUDIT SHEETS FOR OMNI-FLASH SHOTS")
    print("=" * 80)

    for shot_idx, shot_name in enumerate(SHOTS, start=1):
        shot_path = OUT_DIR / shot_name
        if not shot_path.exists():
            print(f"[SKIP] {shot_name} does not exist yet.")
            continue

        base_id = shot_name.split(".")[0]
        shot_audit_dir = AUDIT_DIR / base_id
        shot_audit_dir.mkdir(parents=True, exist_ok=True)

        frames = []
        # 4 frames: 0.5s, 1.5s, 2.5s, 3.5s
        timestamps = [0.5, 1.5, 2.5, 3.5]
        for sec in timestamps:
            frame_path = shot_audit_dir / f"{base_id}_sec{int(sec):02d}.jpg"
            cmd = [
                "ffmpeg", "-y", "-ss", str(sec), "-i", str(shot_path),
                "-vframes", "1", "-q:v", "2", str(frame_path)
            ]
            subprocess.run(cmd, capture_output=True)
            if frame_path.exists():
                frames.append(frame_path)

        if not frames:
            print(f"[WARN] No frames extracted for {shot_name}")
            continue

        # Build composite 4-up horizontal sheet
        thumb_w, thumb_h = 480, 270
        sheet_w = thumb_w * len(frames)
        sheet_h = thumb_h + 40
        sheet = Image.new("RGB", (sheet_w, sheet_h), color=(18, 18, 18))
        draw = ImageDraw.Draw(sheet)

        for i, fpath in enumerate(frames):
            img = Image.open(fpath).resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            sheet.paste(img, (i * thumb_w, 40))
            draw.text((i * thumb_w + 15, 12), f"T+{timestamps[i]:.1f}s", fill=(255, 215, 0))

        draw.text((sheet_w - 380, 12), f"{shot_name} (Omni-Flash)", fill=(180, 180, 180))

        sheet_out = AUDIT_DIR / f"audit_sheet_{base_id}.jpg"
        sheet.save(str(sheet_out), quality=92)
        print(f"[OK] Saved audit sheet: {sheet_out.name}")

        # Copy to brain dir
        brain_out = BRAIN_DIR / f"audit_sheet_{base_id}.jpg"
        sheet.save(str(brain_out), quality=92)

if __name__ == "__main__":
    extract_and_build()
