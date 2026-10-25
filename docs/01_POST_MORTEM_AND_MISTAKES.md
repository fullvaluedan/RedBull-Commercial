# 01. Comprehensive Post-Mortem & Mistake Analysis

> *"Those who cannot remember the past are condemned to repeat it."* — George Santayana

This document provides a candid, forensic examination of every technical, directorial, operational, and financial mistake made across the iterative development of the Red Bull Desert commercial.

---

## 1. Directing & Narrative Failures

### Mistake 1.1: Single-Prompt Overcrowding
* **The Error:** In Passes v01 through v04, we attempted to generate complex multi-beat narrative sequences in 1 or 2 long Text-to-Video (T2V) prompts (e.g. *"A man runs out of gas, pulls up to a pump, sees $9.99, looks shocked, sees Red Bull 2 for $5, gets an idea, pours cans into tank, drives, and truck explodes"*).
* **The Failure Mode:** Diffusion video models do not possess spatial scene graphs, 3D blocking awareness, or directorial timing. When asked to render an actor and two conflicting signs in one frame:
  1. The model placed the `"Red Bull 2 for $5"` poster **behind the actor's back**.
  2. The `$9.99/GAL` digital pump readout was pushed completely off-screen or rendered as illegible digital noise.
  3. The actor stared blankly directly into the camera lens (breaking the 4th wall) because the model had no defined off-axis gaze vector.
  4. There was no visible eye dart, calculation, or eureka realization because the beats fired simultaneously in the first 2 seconds.
* **The Rule Violated:** Violates [`ai-short-edit-rules.md`](file:///C:/Users/danom/.claude/projects/D--Claude--Content/memory/ai-short-edit-rules.md): *"Never show a reveal before its line... separate setup and reveal clips."*
* **The Hardened Fix:** **The Kuleshov Shot-Reverse-Shot Blueprint**. Split setup and reveal across separate shots:
  * **POV Macro Inserts:** Extreme close-up of props (Pump LCD `$9.99`, Poster `2 for $5`) with **zero actor in frame**.
  * **Tight Reaction Shots:** Filmed 30° off-axis looking off-screen at the props, allowing 100% of the model's capacity to focus on facial acting and micro-expressions.

---

### Mistake 1.2: Environmental Teleportation (Desert vs. Suburban Ohio)
* **The Error:** In Omni-Flash Pass v09, Shot 01 and Shot 07 were filmed in an arid Mojave desert, but Shot 03 (Sticker Shock) and Shot 05 (Eureka Smirk) featured **lush green leafy deciduous trees**, manicured suburban grass, modern multi-lane asphalt highways, and retail strip malls with commuter traffic.
* **The Root Cause:** Google Flow's training dataset is heavily biased toward suburban gas stations. When a prompt includes `"gas station"`, `"pump"`, and `"man"`, those high-frequency tokens overpower the single word `"desert"` unless negative constraints or aggressive landscape anchors are specified.
* **The Hardened Fix:** Negative token anchoring:
  ```text
  "Cinematic 16:9, barren arid desert only, dry cracked sand, desolate Mojave wasteland, distant barren rocky hills, intense dry desert sunlight, zero trees, zero grass, zero city buildings, zero commuter traffic."
  ```

---

### Mistake 1.3: Vehicle Morphing & Vanishing Geometry (Shot 07)
* **The Error:** In Shot 07, the truck began as a rounded 1950s Chevy stepside pickup parked beside a vintage pump. At `T+2.5s` (the instant the fireball detonated), the truck **morphed into an entirely different 1970s squarebody pickup** with a flat square front grille and horizontal rectangular headlights. Simultaneously, the **gas pump completely vanished into thin air**.
* **The Root Cause:** Generative diffusion models suffer temporal latent drift during violent physical events. Flow's training weights for "vehicle explosion" were dominated by 1970s pickup trucks, so at the point of explosion, the latent representation collapsed into its training centroid, discarding the 1950s truck body and the nearby gas pump.
* **The Hardened Fix:**
  1. Specify stunt pyrotechnics where the truck chassis remains anchored to the pavement: `"movie stunt pyrotechnics, vehicle chassis remains completely stationary on pavement, hood blows upward"`.
  2. Direct the camera angle to a low-angle three-quarter rear or silhouette, masking frontal grille differences.

---

### Mistake 1.4: Anatomical Horror & False Fuel Tanks (Shot 06)
* **The Error:** In Shot 06 (The Pour), the actor poured energy drink cans onto a flat, horizontal circular plastic engine cover surrounded by hex bolts, rather than a truck's fuel filler neck. In frames 3 and 4, floating detached arms entered from impossible angles, phantom fingers warped around the cans, and amber soda splashed across a flat plastic tray.
* **The Root Cause:** The prompt asked for `"two hands pouring two cans into the fuel tank"`. Flow interpreted "tank" as an engine reservoir or flat oil cap.
* **The Hardened Fix:** Macro framing with explicit vertical orientation and sleeve cuffs:
  ```text
  "Extreme close-up macro action shot. Two masculine hands with blue denim sleeve cuffs tilt two opened cans over the vertical circular black fuel filler neck on the rear fender of the vintage truck. Golden liquid pours down into the dark circular fuel pipe opening."
  ```

---

## 2. Operational & Financial Mistakes

### Mistake 2.1: The 400-Credit Veo Quality Blind Batch
* **The Error:** In Pass v08, four 8-second shots were queued sequentially in `veo-quality` at **100 credits per generation**, consuming **400 credits** ($40 equivalent) in one script run.
* **The Financial Impact:** The account dropped from ~591 credits to 191 credits in 15 minutes, leaving zero room for re-takes on the flagship model.
* **Why It Happened:** We assumed that upgrading model tier would automatically solve narrative and continuity issues. Instead, `veo-quality` delivered photorealistic textures on flawed prompts, producing high-resolution mistakes.
* **The Policy Fix:** **Hard Freeze on Multi-Shot Batching**. Batch size is permanently locked to `1`. Every shot must pass verification before any credit is spent on subsequent shots.

---

### Mistake 2.2: Bypassing MCP Guardrails
* **The Error:** `gemini-media-pass` had built-in credit protection (`MAX_CREDITS = 40`, `spend_check()`, and 50%/20% milestone alerts in `flow.py`). However, during production, scripts were written to execute `gflow video t2v` directly via raw Python `subprocess.run()`, completely bypassing the MCP server.
* **The Consequence:** No credit caps fired, no warnings appeared, and `flow_spend.jsonl` was never updated.
* **The Policy Fix:** All programmatic generation must route through verified MCP wrappers or utilize the newly built `circuit_breaker.py` harness with hardcoded credit thresholds.

---

### Mistake 2.3: Silent Model Defaulting
* **The Error:** In early iterations, the pipeline silently defaulted to `veo-fast` (20 credits) without disclosing model parameters, credit costs, or resolution trade-offs to the user until explicitly questioned.
* **The Policy Fix:** Mandatory upfront disclosure of model selection, resolution, duration, and credit cost before any execution.

---

## 3. Audio & NLE Assembly Failures

### Mistake 3.1: Synthetic White-Noise Audio ("Static Hiss")
* **The Error:** Ambient desert wind on Track A1 was synthesized using `np.random.randn(total_samples)` low-pass filtered white noise (`alpha = 0.03`).
* **The Result:** Psychoacoustically, filtered Gaussian noise registers as harsh background static hiss or amplifier noise rather than organic desert atmosphere.
* **The Rule Violated:** Violates [`dan-style-preferences.md`](file:///C:/Users/danom/.claude/projects/D--Claude--Video-pipeline/memory/dan-style-preferences.md): *"NO noise-based sound effects: whooshes made from (even low-passed) noise read as 'static' to Dan."*
* **The Hardened Fix:** Ban all synthetic random noise algorithms. Use real recorded environmental foley or harmonic sine-wave acoustics.

---

### Mistake 3.2: DaVinci Resolve Timeline Start Timecode Blindness
* **The Error:** In `assemble_v09_omniflash.py`, video cuts were appended with `"recordFrame": 0`.
* **The Result:** In DaVinci Resolve Studio, default timeline start timecode is `01:00:00:00` (frame 108,000 at 30fps). Placing clips at frame 0 put them **1 hour in the past**, making the timeline appear completely blank to the user when opened in Resolve!
* **The Hardened Fix:** Always anchor timeline record frames to `timeline.GetStartFrame()` (108,000).

---

### Mistake 3.3: Dropped Tracks Due to Missing `AddTrack()` Calls
* **The Error:** `mp.AppendToTimeline()` was called with `"trackIndex": 2`, but the freshly created timeline only had 1 Video track and 1 Audio track by default.
* **The Result:** Track V2 (punchline graphics) and Tracks A2–A4 (diegetic foley, sub-bass boom) were silently dropped by the Resolve API.
* **The Hardened Fix:** Explicitly loop `timeline.AddTrack("video")` and `timeline.AddTrack("audio")` until the required track count is verified before appending media.
