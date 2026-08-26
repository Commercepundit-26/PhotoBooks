---
name: photobook-builder
description: End-to-end autonomous photobook pipeline and layout engine for Adobe Illustrator. Generates 22-page master photobooks across all 3 sizes (Square 10x10, Landscape 12x8, Portrait 8x12), places and masks photos, applies high-res backgrounds, enforces strict in-place typography with at least 18 text layouts per book, locks a consistent 3-font palette per template, enforces 1-inch safe margins, and exports 1500px Blank and Populated preview images. Trigger whenever creating, rebuilding, or automating photobook templates or layouts.
---

# Photobook Builder Skill & Operational Guidelines (All 3 Sizes)

This skill defines the complete rules, automation workflows, layout extraction logic, typography guidelines, and layer architectures for generating multi-page photobooks in Adobe Illustrator across all 3 master sizes: **Square 10x10**, **Landscape 12x8**, and **Portrait 8x12**.

---

## 1. Master Sizes & Technical Dimensions

| Size Name | Physical Dimensions | Illustrator Points | 1-Inch Safe Margin Boundaries | Preview Resolution (Blank & Populated) |
| :--- | :--- | :--- | :--- | :--- |
| **Square 10x10** | 10x10\text{ in} | 720x720\text{ pt} | X \in [72, 648]\text{ pt}, Y \in [-72, -648]\text{ pt} | **1500x1500\text{ px}** (1:1 Aspect Ratio) |
| **Landscape 12x8** | 12x8\text{ in} | 864x576\text{ pt} | X \in [72, 792]\text{ pt}, Y \in [-72, -504]\text{ pt} | **1500x1000\text{ px}** (3:2 Aspect Ratio) |
| **Portrait 8x12** | 8x12\text{ in} | 576x864\text{ pt} | X \in [72, 504]\text{ pt}, Y \in [-72, -792]\text{ pt} | **1000x1500\text{ px}** (2:3 Aspect Ratio) |

---

## 2. Layout Selection & Text Quota Rules

- **Master Vector Layout Repository**: `Layout/Final Layouts.ai`
  - Square 10x10: 44 artboards
  - Landscape 12x8: 40 artboards
  - Portrait 8x12: 36 artboards
- **At Least 18 Text-Based Layouts per 22-Page Book**:
  - For every 22-page master book, the system MUST select **at least 18 text-based layouts** (up to 20–22 text layouts).
  - Only 0 to 4 pages may be pure photo layouts without text frames.
  - **Cover (Page 01)** and **Back Cover (Page 22)** must ALWAYS use text-based layouts.
- **Dynamic Random Sampling Across Books**:
  - Never hardcode fixed layout index lists.
  - For each new book or template, dynamically shuffle and sample available text and photo layouts from `Layout/Final Layouts.ai` so that every photobook has a unique, fresh layout combination.
- **Strict In-Place Replacement (No Arbitrary Text Frames)**:
  - Text frames must ONLY be placed on layouts that originally contain text in `Final Layouts.ai`.
  - Retain the exact original (X, Y) coordinates, alignment, and rotation of the source text frames from `Final Layouts.ai`.

---

## 3. Typography & Strict 3-Font Hierarchy

### The 3-Font Lock Rule
Every photobook template MUST establish a strict, consistent typography hierarchy of at most **3 fonts** used consistently across all 22 pages and all 3 sizes:
1. **Primary Title / Accent Font** (Choose 1 only per book): For main headings, cover title, and major section accents.
2. **Secondary Heading / Subtitle Font** (Choose 1 only per book): For page subheadings, dates, and category tags.
3. **Body / Quote / Vows Font** (Choose 1 only per book): For narrative paragraphs, quotes, and multi-line vow blocks.

> **CRITICAL RULE**: Never mix multiple script fonts or multiple heading fonts in the same photobook template. Once a font palette is selected for a book, it is **100% locked across all 22 pages**. When generating a different book/template, choose a different font combination.

### Approved Font Inventory
- **Script / Calligraphy**: `GreatVibes-Regular`, `Fallinlove-Regular`, `BusinessSignatureDemo-Regular`, `NuraAsyifa-Regular`, `RaustilaRegular-Regular`
- **Serif / Editorial**: `Philosopher`, `Philosopher-Bold`, `BookAntiqua`, `BookAntiqua-Bold`
- **Sans-Serif / Modern**: `Poppins` (Light, Regular, Medium, SemiBold, Bold, Black), `Gotham` (Book, Bold, Black), `BebasNeue-Regular`, `Arial` (Regular, Bold)
- **Kids / Display**: `LobsterTwo-Regular`, `LobsterTwo-Bold`, `Rockwell-Regular`, `Rockwell-Bold`, `Abscissa-Regular`, `Abscissa-Bold`

---

## 4. Multi-Line Point Text (`\r`) & Safe Margin Constraints

- **Point Text Multi-Line Formatting (`\r`)**:
  - In Adobe Illustrator Point Text (`TextType.POINTTEXT`), text does NOT auto-wrap.
  - Any subtitle, vow, or quote longer than 40 characters MUST include explicit carriage returns (`\r`) to split into 2–4 balanced lines.
  - Never let point text run on a single unbroken line across page boundaries.
- **Pattern Matching Priority**:
  - Sort dictionary replacement keys by length descending (`b.length - a.length`) so longer patterns match before short prefixes.

---

## 5. Illustrator Layer Architecture & Export Workflow

### Layer Stacking (Bottom to Top)
1. `Backgrounds` — Placed 5.4K background images clipped to artboard bounds.
2. `Photos_Masked` — Placed photos scaled (proportional fill) and masked inside duplicate layout vector frames.
3. `Layout_Shapes` — Clean vector shapes for manual user editing.
4. `Typography` — In-place styled textframes.

### Execution Sequence & Safe Modification Rule
- Keep all layers `visible = true` while building and placing elements. Modifying items on hidden layers throws `Error 8705: Target layer cannot be modified`.
- **Export Previews**:
  - Blank Previews: Hide `Photos_Masked`, Show `Layout_Shapes`, `Typography`, `Backgrounds` -> Capture 22 PNGs @ 150 DPI.
  - Populated Previews: Show `Photos_Masked`, Hide `Layout_Shapes`, Show `Typography`, `Backgrounds` -> Capture 22 PNGs @ 150 DPI.
  - Master Save: Restore visibility on all 4 layers before saving `.ai`.
- **Resize Previews**:
  - Square: 1500x1500\text{ px}
  - Landscape: 1500x1000\text{ px}
  - Portrait: 1000x1500\text{ px}
