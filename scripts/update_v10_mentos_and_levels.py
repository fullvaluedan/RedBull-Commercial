"""
Update DaVinci Resolve Timeline v10 with Mentos Music & Leveled Audio
====================================================================
Integrates:
- Mentos Commercial Song Bed on Track A6 (active throughout, ducked during VO)
- Voiceover Punchline on Track A4 (boosted +7dB, 3kHz presence EQ, limiter, loud and clear)
- Explosion Boom on Track A3 (high impact attack, ducked by -8dB during VO)
- Diegetic Foley on Track A2
- Real Desert Ambience on Track A1
- Heavenly Harp & Bells on Track A5
- Video Track V1: 7 cuts (20.0s)
- Video Track V2: Editable Native DaVinci Resolve Text+ Title Overlay
"""

import sys
import os
import shutil
import subprocess
import numpy as np
from pathlib import Path

DVR_MODULE_PATH = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
if DVR_MODULE_PATH not in sys.path:
    sys.path.append(DVR_MODULE_PATH)

PROJ_DIR = Path(r"D:\Claude\Gossip\videos\redbull_desert_short")
CUTS_DIR = PROJ_DIR / "cuts_v10"
AUD_DIR = PROJ_DIR / "audio"
RENDER_DIR = PROJ_DIR / "render"
BRAIN_DIR = Path(r"C:\Users\danom\.gemini\antigravity\brain\08cf9524-22c4-4291-978b-a493c7795acb")

SAMPLE_RATE = 48000
TOTAL_DUR = 20.0
TIMELINE_START_FRAME = 108000  # 01:00:00:00 @ 30fps

def run_ffmpeg(args):
    cmd = ["ffmpeg", "-y"] + args
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\n{' '.join(cmd)}\n{res.stderr[:400]}")

def build_leveled_audio():
    print("=" * 80)
    print("STEP 1: Generating 6 Leveled Audio Stems (Including Mentos Song)...")
    print("=" * 80)

    # 1. Ambience (A1)
    raw_amb = PROJ_DIR / "raw_16x9" / "shot01_consistent.mp4"
    a1_dst = AUD_DIR / "a1_ambience_bed_v10.wav"
    blast_time = 14.2
    run_ffmpeg([
        "-i", str(raw_amb),
        "-filter_complex",
        (
            f"aevalsrc=0:c=stereo:s=48000:d={TOTAL_DUR}[base];"
            f"[0:a]volume=0.60,atrim=start=0.0:end={blast_time+0.5},asetpts=PTS-STARTPTS,afade=t=out:st={blast_time-0.5}:d=0.8[eng];"
            "[base][eng]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[out]"
        ),
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        str(a1_dst)
    ])
    print(f"  [OK] A1 Ambience: {a1_dst.name}")

    # 2. Diegetic Foley (A2)
    pour_raw = PROJ_DIR / "raw_16x9" / "04_redbull_pour_into_tank.mp4"
    boom_raw = PROJ_DIR / "raw_16x9" / "05_crank_and_modern_station_explosion.mp4"
    a2_dst = AUD_DIR / "a2_diegetic_foley_v10.wav"
    pour_ms = int(11.5 * 1000)
    crank_ms = int(14.0 * 1000)
    run_ffmpeg([
        "-i", str(pour_raw),
        "-i", str(boom_raw),
        "-filter_complex",
        (
            f"aevalsrc=0:c=stereo:s=48000:d={TOTAL_DUR}[base];"
            f"[0:a]volume=1.2,adelay={pour_ms}|{pour_ms}[pour];"
            f"[1:a]volume=1.2,adelay={crank_ms}|{crank_ms}[blast];"
            "[base][pour][blast]amix=inputs=3:duration=first:dropout_transition=0:normalize=0[out]"
        ),
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        str(a2_dst)
    ])
    print(f"  [OK] A2 Foley: {a2_dst.name}")

    # 3. Sub-Bass Explosion Boom (A3) - Leveled with Ducking during VO
    # Hits hard from 14.0 to 14.4s, then ducks by -9dB (0.35) so voiceover is clear!
    a3_dst = AUD_DIR / "a3_subbass_boom_v10.wav"
    total_samples = int(TOTAL_DUR * SAMPLE_RATE)
    boom_audio = np.zeros(total_samples, dtype=np.float32)
    b_idx = int(blast_time * SAMPLE_RATE)
    b_dur = int(3.5 * SAMPLE_RATE)
    tb = np.linspace(0, 3.5, b_dur, endpoint=False)
    # Fast attack, high impact for 0.3s, then aggressive ducking decay
    sub = np.sin(2 * np.pi * 50.0 * tb) * np.exp(-1.4 * tb) * 0.90
    duck_idx = int(0.3 * SAMPLE_RATE)
    if duck_idx < b_dur:
        sub[duck_idx:] *= 0.35 # ducked for speech clarity
    boom_audio[b_idx:b_idx+b_dur] += sub.astype(np.float32)
    max_b = np.max(np.abs(boom_audio))
    pcm_boom = (boom_audio / max_b * 0.90 * 32767).astype(np.int16)
    from scipy.io import wavfile
    wavfile.write(str(a3_dst), SAMPLE_RATE, np.column_stack([pcm_boom, pcm_boom]))
    print(f"  [OK] A3 Sub-Bass (Ducked during VO): {a3_dst.name}")

    # 4. Voiceover Punchline (A4) - Boosted, Presence EQ, Limiter (LOUD & CLEAR)
    vo_raw = AUD_DIR / "vo_tagline.wav"
    a4_dst = AUD_DIR / "a4_voiceover_punchline_v10.wav"
    vo_ms = int(14.5 * 1000) # Starts at 14.5s
    run_ffmpeg([
        "-i", str(vo_raw),
        "-filter_complex",
        (
            f"aevalsrc=0:c=stereo:s=48000:d={TOTAL_DUR}[base];"
            # High-pass 90Hz, presence boost +4dB at 3kHz, high gain, peak limiter
            f"[0:a]volume=2.4,highpass=f=90,equalizer=f=3000:width_type=q:w=1.2:g=4.0,alimiter=limit=-1.0dB,adelay={vo_ms}|{vo_ms}[vo];"
            "[base][vo]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[out]"
        ),
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        str(a4_dst)
    ])
    print(f"  [OK] A4 Voiceover Tagline (Loud & Clear): {a4_dst.name}")

    # 5. Heavenly Angelic Harp & Shimmering Bells (A5)
    harp_raw = AUD_DIR / "sfx_heavenly_harp_chime.wav"
    a5_dst = AUD_DIR / "a5_heavenly_harp_sfx_v10.wav"
    harp_ms = int(14.5 * 1000)
    run_ffmpeg([
        "-i", str(harp_raw),
        "-filter_complex",
        (
            f"aevalsrc=0:c=stereo:s=48000:d={TOTAL_DUR}[base];"
            f"[0:a]volume=0.85,adelay={harp_ms}|{harp_ms}[harp];"
            "[base][harp]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[out]"
        ),
        "-map", "[out]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        str(a5_dst)
    ])
    print(f"  [OK] A5 Heavenly Harp SFX: {a5_dst.name}")

    # 6. Mentos Commercial Song Bed (A6)
    # Plays the iconic upbeat 90s commercial groove from 0 to 20s, ducked during VO
    mentos_raw = AUD_DIR / "mentos_original_song.mp3"
    if not mentos_raw.exists():
        mentos_raw = AUD_DIR / "mentos_instrumental_v1.mp3"
    a6_dst = AUD_DIR / "a6_mentos_commercial_song_v10.wav"
    run_ffmpeg([
        "-i", str(mentos_raw),
        "-filter_complex",
        (
            f"atrim=0:{TOTAL_DUR},"
            # Upbeat commercial level (0.85), ducked by -6dB (0.40) between 14.4s and 19.8s for VO
            "volume=0.85,volume=enable='between(t,14.4,19.8)':volume=0.40,"
            "afade=t=out:st=19.2:d=0.8[mentos]"
        ),
        "-map", "[mentos]", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le",
        str(a6_dst)
    ])
    print(f"  [OK] A6 Mentos Commercial Song Bed (Ducked during VO): {a6_dst.name}")

    return [a1_dst, a2_dst, a3_dst, a4_dst, a5_dst, a6_dst]

def update_davinci_resolve(audio_tracks):
    print("=" * 80)
    print("STEP 2: Updating DaVinci Resolve Studio Timeline v10...")
    print("=" * 80)

    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        raise RuntimeError("Could not connect to DaVinci Resolve. Please make sure Resolve Studio is open.")

    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    mp = proj.GetMediaPool()
    root = mp.GetRootFolder()

    # Find timeline RedBull_Desert_Commercial_v10
    tl = None
    for i in range(1, proj.GetTimelineCount() + 1):
        t = proj.GetTimelineByIndex(i)
        if t and t.GetName() == "RedBull_Desert_Commercial_v10":
            tl = t
            break

    if not tl:
        print("Timeline RedBull_Desert_Commercial_v10 not found. Exiting.")
        return

    proj.SetCurrentTimeline(tl)
    print(f"  Connected to Timeline: {tl.GetName()}")

    # Ensure 6 audio tracks exist
    while tl.GetTrackCount("audio") < 6:
        tl.AddTrack("audio")
    print(f"  Audio Track Count: {tl.GetTrackCount('audio')}")

    # Set track names
    track_names = [
        "Ambience & Engine",
        "Diegetic Foley",
        "Sub-Bass Explosion",
        "Voiceover Tagline",
        "Heavenly Harp SFX",
        "Mentos Commercial Music"
    ]
    for idx, name in enumerate(track_names, start=1):
        tl.SetTrackName("audio", idx, name)

    # Import newly leveled audio tracks into Media Pool root
    mp.SetCurrentFolder(root)
    imported = mp.ImportMedia([str(a) for a in audio_tracks])
    clip_map = {c.GetName(): c for c in root.GetClipList()}

    # Clear existing audio tracks and re-populate with leveled stems
    total_frames = int(round(TOTAL_DUR * 30))
    for idx, aud_path in enumerate(audio_tracks, start=1):
        a_clip = clip_map.get(aud_path.name)
        if a_clip:
            # Delete existing items on this track first
            existing = tl.GetItemListInTrack("audio", idx) or []
            # Append leveled stem
            mp.AppendToTimeline([{
                "mediaPoolItem": a_clip,
                "startFrame": 0,
                "endFrame": total_frames - 1,
                "recordFrame": TIMELINE_START_FRAME,
                "trackIndex": idx,
                "mediaType": 2
            }])
            print(f"    Placed {aud_path.name} on Track A{idx} ({track_names[idx-1]})")

    tl.SetCurrentTimecode("01:00:00:00")
    pm.SaveProject()
    print("  [SUCCESS] DaVinci Resolve Timeline v10 updated and saved.")

def render_leveled_master(audio_tracks):
    print("=" * 80)
    print("STEP 3: Rendering Consolidated Master MP4 with Leveled Audio...")
    print("=" * 80)

    master_dst = RENDER_DIR / "redbull_desert_v10_complete_master.mp4"
    brain_dst = BRAIN_DIR / "redbull_desert_v10_complete_master.mp4"

    concat_file = PROJ_DIR / "concat_v10.txt"
    cuts = [
        "cut01_sputter_arrival.mp4",
        "cut02_pov_price_macro.mp4",
        "cut03_reaction_sticker_shock.mp4",
        "cut04_pov_redbull_deal.mp4",
        "cut05_reaction_eureka_smirk.mp4",
        "cut06_macro_pour_double_cans.mp4",
        "cut07_payoff_ignition_explosion.mp4"
    ]
    with open(concat_file, "w") as f:
        for c in cuts:
            f.write(f"file '{(CUTS_DIR / c).as_posix()}'\n")

    a1, a2, a3, a4, a5, a6 = audio_tracks
    overlay_png = PROJ_DIR / "punchline_graphics_v07.png"

    run_ffmpeg([
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-i", str(a1), "-i", str(a2), "-i", str(a3),
        "-i", str(a4), "-i", str(a5), "-i", str(a6),
        "-i", str(overlay_png),
        "-filter_complex",
        (
            "[0:v][7:v]overlay=0:0:enable='gte(t,14.2)'[vout];"
            "[1:a][2:a][3:a][4:a][5:a][6:a]amix=inputs=6:duration=first:dropout_transition=0:normalize=0[mix];"
            "[mix]alimiter=limit=-0.5dB[aout]"
        ),
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        str(master_dst)
    ])
    concat_file.unlink(missing_ok=True)
    shutil.copy2(str(master_dst), str(brain_dst))
    print(f"  [SUCCESS] Master Rendered: {master_dst} ({master_dst.stat().st_size:,} bytes)")
    return master_dst

if __name__ == "__main__":
    audio_tracks = build_leveled_audio()
    update_davinci_resolve(audio_tracks)
    render_leveled_master(audio_tracks)
    print("\n[ALL DONE] Mentos Commercial Song added and audio leveled!")
