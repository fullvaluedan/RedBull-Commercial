# 03. Platform Constraints: Google Flow Agent-Only Composer

> **A technical breakdown of Google Flow Issue #799, the migrated account cohort (`ComposerKind = "agent_only"`), and how to achieve character/object consistency when reference tools are blocked via CLI.**

---

## 1. The Architecture of Google Flow Migration (Issue #799)

In late 2026, Google migrated user accounts from the classic `labs.google` backend to the new unified web frontend at `flow.google.com`. 

In `gflow-cli` (v0.86), accounts served from this new infrastructure are identified by:
```python
ComposerKind = "agent_only"  # (agent_only_composer.py)
```

### The Technical Divide: Classic vs. Agent-Only

| Capability / API Feature | Classic Labs Composer (`labs.google`) | Migrated Agent-Only Composer (`flow.google.com`) |
|---|---|---|
| **Text-to-Video (`t2v`)** | ✅ Fully Supported | ✅ Supported (Routes to Agent Driver) |
| **Image-to-Video (`i2v` / First Frame)** | ✅ Supported (`--initial-frame`) | ❌ **REFUSED (Exit Code 36: `FlowHostMigratedError`)** |
| **Reference-to-Video (`r2v` / Image Ref)** | ✅ Supported (Up to 7 images) | ❌ **REFUSED (Exit Code 36: `FlowHostMigratedError`)** |
| **Reference Character Entities** | ✅ Supported (`--reference-entity`) | ❌ **REFUSED (Exit Code 36: `FlowHostMigratedError`)** |
| **Multi-Clip Batching** | ✅ Supported (`--count 1-4`) | ❌ **REFUSED for count > 1** |
| **Balance API Query** | ✅ Reads JSON balance | ⚠️ Unreadable (Issue #795: `aisandbox-auth`) |

---

## 2. Source Code Proof from `gflow-cli`

From `agent_only_composer.py` (lines 759–780):

```python
def unported_video(action: str) -> None:
    """Raise FlowHostMigratedError for video CLI features not yet ported to the agent-only composer."""
    raise FlowHostMigratedError(
        f"gflow video {action} is not yet supported for accounts on Flow's new frontend.\n"
        "Works here: text to video (count 1, no explicit resolution), text to image.\n"
        "Do in the Flow web UI instead: image to video, character references, ingredients.\n"
        "Download the result and keep editing locally."
    )
```

When an automated script attempts:
```bash
gflow video i2v start_frame.png "Prompt..."
# or
gflow video t2v "Prompt..." --reference-entity char_12345
```
The CLI halts immediately with **Return Code 36** (`FlowHostMigratedError`) and spends zero credits.

---

## 3. How to Direct Consistency Without Reference Tools

Because CLI scripts cannot inject reference images or character embeddings on migrated accounts, **every generation is an independent probabilistic roll of the diffusion latent space**.

To achieve character and object consistency across multiple shots, you must use **Cinematographic Directing Solutions** rather than algorithmic reference tools:

### Strategy 1: The Macro Cut Bridge ("The Hand Technique")
* **Principle:** When an actor must perform a physical action (e.g. pouring cans, opening a wallet, turning an ignition key), **frame the shot as an extreme close-up showing only hands and wardrobe cuffs**.
* **Why it Works:** The model does not need to generate a face. This eliminates 100% of face-swap glitches, sunglasses hallucinations, or haircut changes. As long as the wardrobe sleeves (e.g. blue denim cuffs) match, the human brain seamlessly assumes the continuity.

---

### Strategy 2: Single-Actor Off-Axis Framing
* **Principle:** Never put the actor and the text-heavy prop in the same frame.
* **Why it Works:** Asking a diffusion model to render both an actor's face and a readable sign causes the model to split its attention, producing distorted text and awkward blocking. By filming the actor in a tight medium close-up looking 30° off-axis, the model devotes 100% of its parameters to believable facial micro-acting.

---

### Strategy 3: Silhouetted / Three-Quarter Rear Angles
* **Principle:** For master action payoff shots (such as vehicle explosions or crashes), film the vehicle from the three-quarter rear or with heavy window tint / desert sun glare.
* **Why it Works:** Obscuring the driver through the window prevents the diffusion model from hallucinating an alternate actor in the cab at the moment of impact.

---

### Strategy 4: Redundant Visual Anchoring
* **Principle:** In every single prompt, repeat the exact same 5 visual anchors in the exact same order:
  1. **Aesthetic/Camera:** `"iPhone 17 video, horizontal 16:9, handheld natural daylight"`
  2. **Actor Base:** `"30-year-old man, short brown hair, stubble"`
  3. **Wardrobe Base:** `"faded blue denim work shirt over plain white crewneck t-shirt"`
  4. **Vehicle Base:** `"weathered blue vintage stepside pickup truck, rounded fenders"`
  5. **Environment Base:** `"arid desert, barren sand, distant mountains, zero trees, zero buildings"`
* **Why it Works:** Repeating the full token sequence maximizes latent convergence across independent prompts.
