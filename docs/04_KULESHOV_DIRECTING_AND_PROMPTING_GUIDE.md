# 04. Kuleshov Directing & Prompting Guide

> **The definitive guide to prompting Google Flow diffusion models using classical film grammar: Kuleshov shot-reverse-shot coverage, negative token anchoring, and Hollywood stunt safety phrasing.**

---

## 1. The Kuleshov Effect in Generative AI

In classical cinema, Lev Kuleshov proved that viewers derive more meaning from the interaction of two sequential shots than from a single shot in isolation.

In Generative AI video, **the Kuleshov Effect is not just an aesthetic choice—it is a mathematical necessity**.

```
❌ FAILED PROMPT (Single Setup Overcrowding):
"A man at a gas pump looks at the price of $9.99, looks shocked, then glances at a sign for Red Bull 2 for $5 and smiles."
Result:
• Poster placed behind actor's back.
• Pump text illegible.
• Actor stares blankly into lens.
• Zero comedy timing.

✅ HARDENED KULESHOV COVERAGE (Two Sequential Shots):
Shot A (POV Insert): Macro ECU of pump LCD: "$9.99 / GAL" (Zero human in frame).
Shot B (Reaction):   Tight MCU of actor looking 30° screen-left at pump, jaw dropping in pure horror.
Result:
• Razor-sharp, perfectly legible text.
• Flawless, expressive comedic acting with authentic off-axis gaze.
• Editor controls the comedic cut timing down to the exact frame.
```

---

## 2. Negative Token Anchoring: Defeating Flow's Suburban Bias

Because Google Flow lacks a dedicated negative prompt parameter in its API, **negative constraints must be woven syntactically into the positive prompt**.

### The Training Bias
Google Flow's training dataset for `"gas station"` is dominated by modern suburban stations with:
* Green deciduous trees and manicured grass.
* Multi-lane paved highways with civilian commuter traffic.
* Modern illuminated vinyl canopies and convenience store chains.

### The Negative Anchor Formula
To keep a scene locked in a remote desert, you must explicitly forbid suburban features:

```text
"barren arid desert only, dry cracked sand, desolate Mojave wasteland, distant barren rocky hills, intense dry desert sunlight, zero trees, zero grass, zero city buildings, zero commuter traffic, zero modern storefronts."
```

---

## 3. Hollywood Stunt Phrasing: Bypassing Moderation Hangs

Google Flow incorporates an automated safety filter designed to prevent violent or destructive video generation. 

On the migrated `agent_only` composer, **moderation rejections do not return an immediate error**. Instead, the backend agent silently halts the render. The CLI client waits for the video tile to appear, resulting in a **600-second (10-minute) timeout hang** before exiting with code 9.

### The Banned vs. Safe Lexicon

| ❌ Moderation Trigger Phrases (Hang / Exit Code 9) | ✅ Safe Hollywood Stunt Replacements (Renders in ~85s) |
|---|---|
| `"violent explosion"` | `"Hollywood movie stunt pyrotechnics"` |
| `"obliterating the vehicle"` | `"enveloping the engine bay in a dramatic movie fireball"` |
| `"shredded metal and flying body fragments"` | `"billowing orange stunt flames and dark cinematic smoke"` |
| `"truck completely blows up and disintegrates"` | `"pyrotechnic blast erupts upward from hood, chassis remains anchored"` |
| `"carnage and catastrophe"` | `"classic action comedy movie special effects"` |

---

## 4. Master Prompt Templates for the Red Bull Short

### Shot 01: The Sputter & Arrival
```text
iPhone 17 video, horizontal 16:9, daylight desert highway. A dusty weathered blue vintage stepside pickup truck chugs and violently sputters onto the gravel of an isolated desert gas station, coughing a final puff of dark smoke from the exhaust as the engine dies beside a vintage rusted gas pump. Barren desert sand, distant arid mountains, zero trees, zero modern buildings. Handheld camera, realistic mechanical shake, zero dialogue.
```

### Shot 02: POV Insert — Gas Price Macro
```text
iPhone 17 video, horizontal 16:9, extreme close-up macro insert shot of a weathered vintage gas pump digital LED display. The black digital LCD screen clearly displays in bold glowing numbers 'PRICE PER GALLON $9.99'. Subtle heat distortion ripples across the sun-baked brushed metal pump casing. Razor-sharp focus, desert daylight, zero human in frame.
```

### Shot 03: Tight Reaction — Sticker Shock & Wallet Panic
```text
iPhone 17 video, horizontal 16:9, tight medium close-up of a 30-year-old scruffy man with stubble in a faded blue denim work shirt over a plain white t-shirt. Filmed 30 degrees off-axis looking screen-left toward the pump. His eyes widen in genuine horror and shock, jaw dropping open in disbelief. He frantically pulls an empty brown leather wallet from his pocket, panicking. Barren desert background, zero trees, zero grass, zero city buildings. Expressive facial acting, handheld camera, zero dialogue.
```

### Shot 04: POV Insert — The Red Bull Deal
```text
iPhone 17 video, horizontal 16:9, eye-level POV insert shot of the dusty gas station window pillar. A crisp promotional deal poster taped to the glass boldly reads 'RED BULL 2 FOR $5' beside two silver and blue cans. Desert sunlight reflects across the glass and weathered yellow wall. Sharp commercial sign, zero human in frame.
```

### Shot 05: Tight Reaction — Calculation & Eureka Smirk
```text
iPhone 17 video, horizontal 16:9, tight medium close-up of the 30-year-old scruffy man in the blue denim work shirt. Filmed 30 degrees off-axis. His eyes rapidly dart screen-left to screen-right between the pump and the sign. He rubs his stubbled chin in absurd deep calculation. Suddenly his eyes widen with a mischievous eureka spark, and a big sly grin spreads across his face with a decisive nod. Barren desert background, zero trees, zero grass, zero city buildings. Handheld camera, silent comedy acting, zero dialogue.
```

### Shot 06: Macro Action Bridge — The Double Pour
```text
iPhone 17 video, horizontal 16:9, extreme close-up macro action shot. Two masculine hands with blue denim sleeve cuffs vigorously tilt two opened 12oz silver and blue energy drink cans upside down over the vertical circular black fuel filler neck on the rear fender of the vintage truck. Fizzy golden carbonated liquid splashes and foams furiously into the gas tank opening in crisp high-speed detail. Zero face in frame.
```

### Shot 07: The Payoff — Starter Crank & Hollywood Fireball
```text
iPhone 17 video, horizontal 16:9, wide exterior three-quarter rear shot of the blue vintage pickup truck parked at the desert gas pump. The cab window is heavily tinted in dark desert glare silhouette. The truck shudders violently on its suspension as the starter motor cranks, and then a dramatic Hollywood movie stunt pyrotechnic fireball explosion engulfs the engine bay and truck hood in billowing bright orange flames and black smoke. Stunt pyrotechnics, movie special effects, truck chassis remains anchored to pavement, desert background.
```
