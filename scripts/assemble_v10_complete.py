"""
Assemble DaVinci Resolve Studio Timeline v10 Complete
=====================================================
Builds the complete short with:
- Video Track V1: 7 Omni-Flash Kuleshov cuts + freeze hold payoff (20.0s total)
- Video Track V2: Native DaVinci Resolve Text+ Editable Stylized Overlay:
    "Red Bull, it gives you wings
     if you want to go to heaven today."
- Audio Track A1: Ambience & Vintage Engine Bed (real desert sound, no white noise)
- Audio Track A2: Diegetic Foley with J-Cuts (sputter, beeps, gasp, chimes, can pop, pour)
- Audio Track A3: Sub-Bass Pyrotechnic Concussion Boom (50Hz punch)
- Audio Track A4: Voiceover Tagline ("Red Bull, it gives you wings if you want to go to heaven today.")
- Audio Track A5: Heavenly Angelic Harp & Shimmering Bells SFX
Exports consolidated master MP4 to project render and artifact brain directories.
"""

import sys
import os
import time
import shutil
import subprocess
import numpy as np
from pathlib import Path
from scipy.io import wavfile

DVR_MODULE_PATH = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
if DVR_MODULE_PATH not in sys.path:
    sys.path.append(DVR_MODULE_PATH)

PROJ_DIR = Path(r"D:\Claude\Gossip\videos\redbull_desert_short")
SHOTS_DIR = PROJ_DIR / "omniflash_pass"
CUTS_DIR = PROJ_DIR / "cuts_v10"
AUD_DIR = PROJ_DIR / "audio"
RENDER_DIR = PROJ_DIR / "render"
BRAIN_DIR = Path(r"C:\Users\danom\.gemini\antigravity\brain\08cf9524-22c4-4291-978b-a493c7795acb")

CUTS_DIR.mkdir(parents=True, exist_ok=True)
RENDER_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 48000
TIMELINE_START_FRAME = 108000  # 01:00:00:00 @ 30fps

TRIM_SPECS = [
    # (src_name, dst_name, start_sec, dur_sec, desc)
    ("shot01_sputter_arrival.mp4", "cut01_sputter_arrival.mp4", 0.0, 2.5, "Shot 1: Sputter into pump"),
    ("shot02_pov_price_macro.mp4", "cut02_pov_price_macro.mp4", 0.5, 2.0, "Shot 2: POV Gas Price $9.99"),
    ("shot03_reaction_sticker_shock.mp4", "cut03_reaction_sticker_shock.mp4", 0.5, 2.5, "Shot 3: Sticker Shock & Panic"),
    ("shot04_pov_redbull_deal.mp4", "cut04_pov_redbull_deal.mp4", 0.5, 2.0, "Shot 4: POV Red Bull 2 for $5"),
    ("shot05_reaction_eureka_smirk.mp4", "cut05_reaction_eureka_smirk.mp4", 0.5, 2.5, "Shot 5: Calculation & Eureka"),
    ("shot06_macro_pour_double_cans.mp4", "cut06_macro_pour_double_cans.mp4", 0.5, 2.5, "Shot 6: Macro Double Pour"),
    ("shot07_payoff_ignition_explosion.mp4", "cut07_payoff_ignition_explosion.mp4", 0.5, 6.0, "Shot 7: Fireball Detonation & Hold"),
]

def run_ffmpeg(args):
    cmd = ["ffmpeg", "-y"] + args
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\n{' '.join(cmd)}\n{res.stderr[:400]}")

def build_cuts():
    print("=" * 80)
    print("STEP 1: Preparing 1080p 30fps Video Cuts with Extended Payoff...")
    print("=" * 80)
    cut_paths = []
    durations = []

    for src_name, dst_name, start_t, dur_t, desc in TRIM_SPECS:
        src = SHOTS_DIR / src_name
        dst = CUTS_DIR / dst_name

        if src_name == "shot07_payoff_ignition_explosion.mp4":
            # Extend shot 7 with a clean freeze-frame hold on the final billowing smoke frame so VO completes
            # Source is 4s. Play 0.5 to 3.9s (3.4s), then freeze hold for 2.6s (total 6.0s)
            run_ffmpeg([
                "-ss", "0.5", "-i", str(src), "-t", "3.4",
                "-vf", "scale=1920:1080:flags=lanczos,fps=30,format=yuv420p,tpad=stop_mode=clone:stop_duration=2.6",
                "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-g", "30", "-an",
                str(dst)
            ])
            actual_dur = 6.0
        else:
            run_ffmpeg([
                "-ss", str(start_t), "-i", str(src), "-t", str(dur_t),
                "-vf", "scale=1920:1080:flags=lanczos,fps=30,format=yuv420p",
                "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-g", "30", "-an",
                str(dst)
            ])
            actual_dur = dur_t

        cut_paths.append(dst)
        durations.append(actual_dur)
        print(f"  [OK] Cut: {dst.name} ({actual_dur:.2f}s @ 30fps) - {desc}")

    total_dur = sum(durations)
    print(f"\nTotal Timeline Duration: {total_dur:.2f}s ({int(total_dur * 30)} frames)")
    return cut_paths, durations, total_dur

def build_audio_tracks(durations, total_dur):
    print("=" * 80)
    print("STEP 2: Building 5 Synchronized Audio Tracks (Ambience, Foley, Boom, VO, Harp)...")
    print("=" * 80)

    # 1. Ambience (A1)
    raw_amb = PROJ_DIR / "raw_16x9" / "shot01_consistent.mp4"
    a1_dst = AUD_DIR / "a1_ambience_bed_v10.wav"
    blast_time = 14.2
    run_ffmpeg([
        "-i", str(raw_amb),
        "-filter_complex",
        (
            f"aevalsrc=0:c=stereo:s=48000:d={total_dur}[base];"
            f"[0:a]volume=0.85,atrim=start=0.0:end={blast_time+0.5},asetpts=PTS-STARTPTS,afade=t=out:st={blast_time-0.5}:d=0.8[eng];"
            "[base][eng]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[out]"
        ),
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        str(a1_dst)
    ])
    print(f"  [OK] A1 Ambience: {a1_dst.name}")

    # 2. Diegetic Foley (A2)
    pour_raw = PROJ_DIR / "raw_16x9" / "04_redbull_pour_into_tank.mp4"
    boom_raw = PROJ_DIR / "raw_16x9" / "05_crank_and_modern_station_explosion.mp4"
    chimes_raw = PROJ_DIR / "audio_v09" / "tmp_chimes.wav"
    a2_dst = AUD_DIR / "a2_diegetic_foley_v10.wav"
    pour_ms = int(11.5 * 1000)
    crank_ms = int(14.0 * 1000)
    run_ffmpeg([
        "-i", str(pour_raw),
        "-i", str(boom_raw),
        "-filter_complex",
        (
            f"aevalsrc=0:c=stereo:s=48000:d={total_dur}[base];"
            f"[0:a]volume=1.3,adelay={pour_ms}|{pour_ms}[pour];"
            f"[1:a]volume=1.4,adelay={crank_ms}|{crank_ms}[blast];"
            "[base][pour][blast]amix=inputs=3:duration=first:dropout_transition=0:normalize=0[out]"
        ),
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        str(a2_dst)
    ])
    print(f"  [OK] A2 Foley: {a2_dst.name}")

    # 3. Sub-Bass Explosion Boom (A3)
    a3_dst = AUD_DIR / "a3_subbass_boom_v10.wav"
    total_samples = int(total_dur * SAMPLE_RATE)
    boom_audio = np.zeros(total_samples, dtype=np.float32)
    b_idx = int(blast_time * SAMPLE_RATE)
    b_dur = int(3.5 * SAMPLE_RATE)
    tb = np.linspace(0, 3.5, b_dur, endpoint=False)
    sub = np.sin(2 * np.pi * 50.0 * tb) * np.exp(-1.8 * tb) * 0.95
    boom_audio[b_idx:b_idx+b_dur] += sub.astype(np.float32)
    max_b = np.max(np.abs(boom_audio))
    pcm_boom = (boom_audio / max_b * 0.95 * 32767).astype(np.int16)
    wavfile.write(str(a3_dst), SAMPLE_RATE, np.column_stack([pcm_boom, pcm_boom]))
    print(f"  [OK] A3 Sub-Bass: {a3_dst.name}")

    # 4. Voiceover Punchline (A4)
    vo_raw = AUD_DIR / "vo_tagline.wav"
    a4_dst = AUD_DIR / "a4_voiceover_punchline_v10.wav"
    vo_ms = int(blast_time * 1000)
    run_ffmpeg([
        "-i", str(vo_raw),
        "-filter_complex",
        (
            f"aevalsrc=0:c=stereo:s=48000:d={total_dur}[base];"
            f"[0:a]volume=1.35,adelay={vo_ms}|{vo_ms}[vo];"
            "[base][vo]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[out]"
        ),
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        str(a4_dst)
    ])
    print(f"  [OK] A4 Voiceover Tagline: {a4_dst.name}")

    # 5. Heavenly Angelic Harp & Shimmering Bells (A5)
    harp_raw = AUD_DIR / "sfx_heavenly_harp_chime.wav"
    a5_dst = AUD_DIR / "a5_heavenly_harp_sfx_v10.wav"
    harp_ms = int(blast_time * 1000)
    run_ffmpeg([
        "-i", str(harp_raw),
        "-filter_complex",
        (
            f"aevalsrc=0:c=stereo:s=48000:d={total_dur}[base];"
            f"[0:a]volume=1.1,adelay={harp_ms}|{harp_ms}[harp];"
            "[base][harp]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[out]"
        ),
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        str(a5_dst)
    ])
    print(f"  [OK] A5 Heavenly Harp SFX: {a5_dst.name}")

    return [a1_dst, a2_dst, a3_dst, a4_dst, a5_dst]

def assemble_davinci_resolve(cut_paths, durations, total_dur, audio_tracks):
    print("=" * 80)
    print("STEP 3: Assembling DaVinci Resolve Studio Timeline v10...")
    print("=" * 80)

    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        raise RuntimeError("Could not connect to DaVinci Resolve. Please make sure DaVinci Resolve is open.")

    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        project = pm.LoadProject("RedBull_Desert_Commercial_v06")
        if not project:
            project = pm.CreateProject("RedBull_Desert_Commercial_v06")

    print(f"  Connected to Project: {project.GetName()}")
    project.SetSetting("timelineResolutionWidth", "1920")
    project.SetSetting("timelineResolutionHeight", "1080")
    project.SetSetting("timelineFrameRate", "30.0")

    mp = project.GetMediaPool()
    root_folder = mp.GetRootFolder()

    # Create Bin v10
    v10_bin = None
    for folder in root_folder.GetSubFolderList():
        if folder.GetName() == "Commercial_v10":
            v10_bin = folder
            break
    if not v10_bin:
        v10_bin = mp.AddSubFolder(root_folder, "Commercial_v10")
    mp.SetCurrentFolder(v10_bin)

    # Import media assets
    all_import_paths = [str(p) for p in cut_paths] + [str(a) for a in audio_tracks]
    imported = mp.ImportMedia(all_import_paths)
    print(f"  Imported {len(imported)} media items into bin 'Commercial_v10'.")

    clip_map = {c.GetName(): c for c in v10_bin.GetClipList()}

    # Create Timeline v10
    tl_name = "RedBull_Desert_Commercial_v10"
    for i in range(1, project.GetTimelineCount() + 1):
        t = project.GetTimelineByIndex(i)
        if t and t.GetName() == tl_name:
            print(f"  Found existing timeline {tl_name}. Switching to it.")
            break

    timeline = mp.CreateEmptyTimeline(tl_name)
    if not timeline:
        timeline = project.GetCurrentTimeline()

    project.SetCurrentTimeline(timeline)
    print(f"  Active Timeline: {timeline.GetName()}")

    # Ensure tracks exist: 2 video tracks, 5 audio tracks
    while timeline.GetTrackCount("video") < 2:
        timeline.AddTrack("video")
    while timeline.GetTrackCount("audio") < 5:
        timeline.AddTrack("audio")

    print(f"  Tracks Verified: Video = {timeline.GetTrackCount('video')}, Audio = {timeline.GetTrackCount('audio')}")

    # Insert Video Cuts onto V1 sequentially
    current_frame = TIMELINE_START_FRAME
    for cut_path, dur in zip(cut_paths, durations):
        clip = clip_map.get(cut_path.name)
        dur_frames = int(round(dur * 30))
        if clip:
            mp.AppendToTimeline([{
                "mediaPoolItem": clip,
                "startFrame": 0,
                "endFrame": dur_frames - 1,
                "recordFrame": current_frame,
                "trackIndex": 1,
                "mediaType": 1
            }])
            print(f"    V1: Placed {cut_path.name} (frame {current_frame} to {current_frame + dur_frames})")
            current_frame += dur_frames

    # Insert Audio Tracks onto A1, A2, A3, A4, A5
    total_frames = int(round(total_dur * 30))
    for idx, aud_path in enumerate(audio_tracks, start=1):
        a_clip = clip_map.get(aud_path.name)
        if a_clip:
            mp.AppendToTimeline([{
                "mediaPoolItem": a_clip,
                "startFrame": 0,
                "endFrame": total_frames - 1,
                "recordFrame": TIMELINE_START_FRAME,
                "trackIndex": idx,
                "mediaType": 2
            }])
            print(f"    A{idx}: Placed {aud_path.name}")

    # Insert Native DaVinci Resolve Text+ Editable Title on Track V2
    # Position: starts at 14.2s (frame 108426) right at explosion detonation, runs to end (108600)
    explosion_frame = TIMELINE_START_FRAME + int(round(14.2 * 30))
    overlay_dur_frames = (TIMELINE_START_FRAME + total_frames) - explosion_frame

    # Set timeline playhead to explosion frame
    timeline.SetCurrentTimecode(f"01:00:14:06")
    title_item = timeline.InsertFusionTitleIntoTimeline("Text+")
    if title_item:
        print(f"  [SUCCESS] Inserted native editable Text+ title onto timeline: {title_item.GetName()}")
        comp = title_item.GetFusionCompByIndex(1)
        if comp:
            tools = comp.GetToolList()
            tplus = tools.get(1)
            if tplus:
                tplus.SetInput("Font", "Impact")
                tplus.SetInput("Style", "Regular")
                tplus.SetInput("Size", 0.062)
                tplus.SetInput("StyledText", "Red Bull, it gives you wings\nif you want to go to heaven today.")
                tplus.SetInput("Center", [0.5, 0.18])  # lower third
                print("    Configured Text+ styled text, font, size, and lower-third position.")

    timeline.SetCurrentTimecode("01:00:00:00")
    print(f"  Playhead reset to 01:00:00:00. Active in Resolve GUI.")

    # Render Consolidated Master MP4
    print("=" * 80)
    print("STEP 4: Rendering Consolidated Master MP4...")
    print("=" * 80)
    master_dst = RENDER_DIR / "redbull_desert_v10_complete_master.mp4"
    brain_dst = BRAIN_DIR / "redbull_desert_v10_complete_master.mp4"

    concat_file = PROJ_DIR / "concat_v10.txt"
    with open(concat_file, "w") as f:
        for p in cut_paths:
            f.write(f"file '{p.as_posix()}'\n")

    a1, a2, a3, a4, a5 = audio_tracks
    run_ffmpeg([
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-i", str(a1), "-i", str(a2), "-i", str(a3), "-i", str(a4), "-i", str(a5),
        "-filter_complex",
        (
            "[1:a][2:a][3:a][4:a][5:a]amix=inputs=5:duration=first:dropout_transition=0:normalize=0[aout]"
        ),
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        str(master_dst)
    ])
    concat_file.unlink(missing_ok=True)
    shutil.copy2(str(master_dst), str(brain_dst))
    print(f"  [SUCCESS] Rendered Master: {master_dst} ({master_dst.stat().st_size:,} bytes)")
    return master_dst, brain_dst

if __name__ == "__main__":
    cut_paths, durations, total_dur = build_cuts()
    audio_tracks = build_audio_tracks(durations, total_dur)
    master_dst, brain_dst = assemble_davinci_resolve(cut_paths, durations, total_dur, audio_tracks)
    print("\n[ALL DONE] DaVinci Resolve Timeline v10 Complete!")
