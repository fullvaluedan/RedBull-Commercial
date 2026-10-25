# 06. DaVinci Resolve Studio Automation Guide

> **A comprehensive technical guide to programmatically assembling, titling, and rendering commercials in DaVinci Resolve Studio 21.1 via Python.**

---

## 1. Environment & Scripting Prerequisites

To drive DaVinci Resolve Studio from external Python scripts on Windows:
1. Enable external scripting in Resolve:
   * **Preferences > System > General > External scripting using: Local**
2. Ensure the scripting module is on Python's module search path:
   ```python
   DVR_MODULE_PATH = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
   if DVR_MODULE_PATH not in sys.path:
       sys.path.append(DVR_MODULE_PATH)
   import DaVinciResolveScript as dvr
   resolve = dvr.scriptapp("Resolve")
   ```

---

## 2. Critical Gotcha: Timeline Start Timecode (`01:00:00:00`)

In DaVinci Resolve, newly created timelines default to a start timecode of **`01:00:00:00`** (1 hour).

At 30.0 frames per second:
$$\text{Start Frame} = 1 \text{ hour} \times 3600 \text{ seconds/hour} \times 30 \text{ fps} = 108,000 \text{ frames}$$

### The Trap:
If you append clips using `recordFrame = 0`:
```python
# ❌ INCORRECT: Places clips 1 hour before the timeline start timecode!
mp.AppendToTimeline([{"mediaPoolItem": clip, "recordFrame": 0}])
```
The clips will be placed at `00:00:00:00`. When the user opens Resolve, the playhead sits at `01:00:00:00`—and the timeline appears completely blank!

### The Correct Fix:
```python
# ✅ CORRECT: Read the timeline start frame dynamically
start_frame = timeline.GetStartFrame()  # Returns 108000
mp.AppendToTimeline([{
    "mediaPoolItem": clip,
    "startFrame": 0,
    "endFrame": dur_frames - 1,
    "recordFrame": start_frame + offset_frames,
    "trackIndex": 1,
    "mediaType": 1
}])
```

---

## 3. Multi-Track Architecture: Pre-Creating Tracks

By default, `mp.CreateEmptyTimeline()` creates a timeline with only **1 Video Track (V1)** and **1 Audio Track (A1)**.

If you attempt to append clips to `trackIndex = 2` without creating the track first, **Resolve silently fails or drops the clip**.

### The Track Verification Pattern:
```python
# Ensure required video tracks exist
while timeline.GetTrackCount("video") < 2:
    timeline.AddTrack("video")

# Ensure required audio tracks exist
while timeline.GetTrackCount("audio") < 6:
    timeline.AddTrack("audio")
```

---

## 4. Native Editable Text+ Title Integration

Users want stylized text overlays that remain **fully editable in DaVinci Resolve's Inspector and Fusion pages**, rather than baked raster images.

### How to Create an Editable Text+ Overlay on Track V2:
1. Place an overlay asset (or title) on Track V2 starting at the desired timestamp (e.g. at the explosion detonation at `01:00:14:06`).
2. Access the timeline item's Fusion composition:
   ```python
   v2_item = timeline.GetItemListInTrack("video", 2)[0]
   comp = v2_item.GetFusionCompByIndex(1) or v2_item.AddFusionComp()
   ```
3. Add a native `TextPlus` tool into the Fusion composition:
   ```python
   tplus = comp.AddTool("TextPlus")
   tplus.SetInput("StyledText", "Red Bull, it gives you wings\nif you want to go to heaven today.")
   tplus.SetInput("Font", "Impact")
   tplus.SetInput("Size", 0.065)
   tplus.SetInput("Center", [0.5, 0.18])  # Lower-third position
   ```
4. When opened in Resolve:
   * The text renders cleanly over Track V1.
   * Clicking the clip on the Edit page exposes the full text, font, tracking, and styling controls directly in the **Inspector**.
   * Clicking the **Fusion** page opens the complete node graph.

---

## 5. Non-Noise 6-Stem Multitrack Audio Engineering & Leveling

To comply with professional standards and avoid psychoacoustic "static hiss" (`np.random.randn`), the audio timeline is split into 6 dedicated functional stems:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       6-STEM AUDIO ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ Track A1: AMBIENCE & ENGINE BED                                             │
│   • Authentic recorded desert wind and vintage 1950s engine idle.           │
│   • Fades out at explosion detonation (14.2s).                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ Track A2: DIEGETIC FOLEY (J-CUTS)                                           │
│   • Sputter chug (0.0s) ──► Pump LCD beeps (2.5s) ──► Wallet rustle (4.5s) │
│   ──► Store chime (7.0s) ──► Can pop & pour (11.5s) ──► Starter crank (14s) │
├─────────────────────────────────────────────────────────────────────────────┤
│ Track A3: SUB-BASS PYROTECHNIC BOOM                                         │
│   • 50Hz pure acoustic sine blast with exponential decay at 14.2s.          │
│   • Leveled & ducked by -9 dB at 14.4s so it never drowns out dialogue.     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Track A4: VOICEOVER PUNCHLINE (LOUD & CRISP)                                │
│   • "Red Bull, it gives you wings if you want to go to heaven today."       │
│   • Boosted +7.5 dB, 3kHz presence EQ (+4 dB), HPF 90Hz, true peak -1.0 dB. │
│   • Cuts right through the explosion and music bed.                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ Track A5: HEAVENLY ANGELIC HARP & SHIMMERING BELLS                          │
│   • Harmonic major 9th harp glissando (C4 to G6) + bell chime at 14.2s.     │
│   • Zero Gaussian noise. Pure musical harmonic comedy sting.                │
├─────────────────────────────────────────────────────────────────────────────┤
│ Track A6: MENTOS COMMERCIAL MUSIC BED                                       │
│   • Iconic Mentos commercial song playing from 0.0s to 20.0s.                │
│   • Normal level: 0.85 (-14 dB LUFS); ducked to 0.40 (-20 dB) during the    │
│     voiceover punchline (14.4s to 19.8s).                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Acoustic Masking Problem & The Ducking Solution:
1. **The Masking Defect**: The sub-bass explosion boom peaked at `-0.4 dB`, while the dry voiceover sat at `-20.5 dB`. Playing them simultaneously caused the voiceover to be completely drowned out.
2. **The Forensic Fix**:
   * **Voiceover Processing**: Applied a high-pass filter at 90Hz (eliminating low-end mud), a +4 dB parametric boost at 3,000Hz (enhancing consonant intelligibility), a +7.5 dB overall gain boost, and a peak limiter at -1.0 dB.
   * **Explosion Ducking**: The explosion boom retains its violent 0.2s initial transient attack (`volume=1.0`), then immediately ducks down by -9 dB (`volume=0.35`) at 14.4s when speech begins.
   * **Music Bed Ducking**: The Mentos song plays energetically at `volume=0.85` throughout cuts 1-6, smoothly ducks to `volume=0.40` during the punchline, and gently fades out with the logo resolve at 19.8s.

---

## 6. Automation Scripts Reference

* [`scripts/update_v10_mentos_and_levels.py`](../scripts/update_v10_mentos_and_levels.py): Complete 6-track audio balancing, Mentos music ducking, and DaVinci Resolve Studio automation.
* [`scripts/assemble_v10_complete.py`](../scripts/assemble_v10_complete.py): Complete timeline build script.
