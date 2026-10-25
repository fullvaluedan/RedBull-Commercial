# 02. Google Flow Model Comparison & Economics

> **A granular benchmark of Veo 3.1 Fast, Veo 3.1 Quality, and Omni-Flash across cost, quality, resolution, native audio, latency, and credit-per-minute economics.**

---

## 1. Google Flow Video Model Catalog Benchmark

| Benchmark Metric | Veo 3.1 Fast (`veo-fast`) | Veo 3.1 Quality (`veo-quality`) | Omni-Flash (`omni-flash`) |
|---|---|---|---|
| **Advertised Credit Cost** | 20 credits | 40 credits (Catalog) / **100 credits (Actual billed)** | 20 credits (Catalog) / **~7 credits (Actual billed)** |
| **Max Clip Duration** | 8.0 seconds | 8.0 seconds | **10.0 seconds** (also 4s, 6s, 8s) |
| **Raw Output Resolution** | 1280x720 (720p) @ 24fps | 1280x720 (720p) @ 24fps | 1280x720 (720p) @ 24fps |
| **Texture & Grain Fidelity** | Low / Smudged motion | **Ultra-High Photorealism** | Medium / Smoothed AI Sheen |
| **Facial & Anatomical Stability** | Poor (Drifts after 2s) | High (Holds structure for 4s) | Medium-High (Fast micro-acting) |
| **Native Synchronized Audio** | ❌ Silent (Video only) | ❌ Silent (Video only) | **✅ Native Audio (Stereo AAC 48kHz)** |
| **Average Generation Latency** | ~45–60 seconds | ~110–180 seconds | **~45–85 seconds** |
| **Moderation Sensitivity** | Standard | High (Filters destruction keywords) | Moderate |
| **Supported Aspects** | 16:9, 9:16 | 16:9, 9:16 | 16:9, 9:16 |

---

## 2. In-Depth Architectural Analysis

### 2.1 Veo 3.1 Quality (`veo-quality`)
* **Strengths:** Unrivaled volumetric lighting, realistic dust kick-up, accurate metallic reflections on vehicles, and convincing cinematic depth of field. Film grain and micro-textures look authentic rather than synthesized.
* **Weaknesses:**
  * **Prohibitive Cost:** In actual production on migrated accounts, `veo-quality` bills **100 credits per generation**. Four shots consume 400 credits—over half of an entire monthly subscription quota.
  * **High Latency:** Generation runs take 2 to 3 minutes per shot, slowing iteration cycles.
  * **Silent Output:** Video tracks contain no audio streams, requiring 100% external foley synthesis.
  * **Duration Degradation:** Despite the high credit cost, 8-second clips still suffer from temporal diffusion morphing (e.g., cans refilling themselves at 5.0 seconds).
* **Best Used For:** Hero close-ups, critical texture shots, or master establishing shots where single-frame photographic realism is paramount.

---

### 2.2 Omni-Flash (`omni-flash`)
* **Strengths:**
  * **Economics:** Advertised at 20 credits, but on migrated agent-only cohorts, billed as low as **~7 credits per clip** (49 credits total for 7 shots).
  * **Native Audio:** Generates synchronized stereo AAC audio (engine rumble, exhaust chug, wind, foley).
  * **Rapid Turnaround:** Averages 60–85 seconds per generation.
  * **Expression Agility:** Highly responsive to comedic physical acting (shock, eye darts, smirks).
* **Weaknesses:**
  * **Surface Smoothing:** Textures exhibit a subtle plastic or waxy AI sheen compared to Veo Quality.
  * **720p Raw Output:** Requires high-quality lanczos upscaling via FFmpeg or DaVinci Resolve Super Scale to reach broadcast 1080p.
  * **Diffusion Hallucinations:** Prone to background defaulting (suburban gas stations with green trees) if negative prompts are omitted.
* **Best Used For:** Rapid coverage iterations, comedic short-form content, multitrack audio scaffolding, and budget-constrained productions.

---

### 2.3 Veo 3.1 Fast (`veo-fast`)
* **Strengths:** Fast generation turnaround (~45s), low cost (20 credits).
* **Weaknesses:** Excessive motion blur, muddy textures, frequent anatomical distortions, and silent audio.
* **Verdict:** Obsolete. Omni-Flash completely supersedes Veo Fast by offering faster speeds, comparable or lower cost, better anatomical holding, and native audio.

---

## 3. Financial & Credit Planning Matrix

### Scenario: 30-Second Commercial (8 Shots Required)

| Strategy | Engine Used | Credits Consumed | Remaining from 600 Baseline | Iteration Buffer |
|---|---|---|---|---|
| **Brute-Force Quality** | Veo Quality (All Shots) | **800 credits** | **-200 (INSUFFICIENT)** | 0 Retakes |
| **Blind Batch Omni** | Omni-Flash (All Shots) | **160 credits** | **+440 credits** | ~20 Retakes |
| **Hybrid Hero Workflow (Recommended)** | 6 Omni-Flash + 2 Hero Veo Quality | **320 credits** | **+280 credits** | ~10 Retakes |

> [!IMPORTANT]
> **The Golden Rule of AI Video Production:**  
> Never generate in flagship models (`veo-quality`) until the prompt geometry, camera vectors, and blocking have been **calibrated and verified** in `omni-flash` for 1/10th the cost.
