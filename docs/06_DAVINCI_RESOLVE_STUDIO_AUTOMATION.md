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
while timeline.GetTrackCount("audio") < 5:
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

## 5. Non-Noise Multitrack Audio Engineering

To comply with professional standards and avoid psychoacoustic "static hiss" (`np.random.randn`), the audio timeline is split into 5 dedicated functional stems:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       5-STEM AUDIO ARCHITECTURE                             │
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
├─────────────────────────────────────────────────────────────────────────────┤
│ Track A4: VOICEOVER PUNCHLINE                                               │
│   • "Red Bull, it gives you wings if you want to go to heaven today."       │
│   • Starts cleanly at 14.2s and plays across the smoke cloud payoff.        │
├─────────────────────────────────────────────────────────────────────────────┤
│ Track A5: HEAVENLY ANGELIC HARP & SHIMMERING BELLS                          │
│   • Harmonic major 9th harp glissando (C4 to G6) + bell chime at 14.2s.     │
│   • Zero Gaussian noise. Pure musical harmonic comedy sting.                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Full Automation Script Reference

See [`scripts/assemble_v10_complete.py`](../scripts/assemble_v10_complete.py) for the complete, production-verified implementation.
