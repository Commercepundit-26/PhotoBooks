# Photobook Design & Typography Knowledge Rules

This document outlines the strict guidelines, typography standards, layout mappings, and margin constraints learned and validated across all Photobook projects.

---

## 1. Text Placement & Replacement Principles

- **Strict In-Place Replacement**:
  - Text frames must only be added to layouts that originally possess text frames in `Final Layouts.ai`.
  - Never synthesize arbitrary text frames on pure photo layouts.
  - Retain the exact original (X, Y) coordinates, alignment, and rotation of the source text frames.
- **Point Text Multi-Line Formatting (`\r`)**:
  - In Adobe Illustrator Point Text (`TextType.POINTTEXT`), text does NOT auto-wrap.
  - Any subtitle or quote longer than 40 characters must include explicit carriage returns (`\r`) to break into 2–4 balanced lines.
  - Never allow point text to run on a single unbroken line across page boundaries.
- **Pattern Matching Priority**:
  - When matching text frame templates by content pattern, always sort keys in descending order of string length (`b.length - a.length`) to prevent shorter prefix patterns (e.g. `"Heading "`) from unintentionally matching longer distinct patterns (e.g. `"Heading Goes here too"`).

---

## 2. Margin & Safe Area Specifications

- **1-Inch Safe Margin**:
  - Square (10x10 in / 720x720 pt): All text frames must strictly reside within $X \in [72, 648]$ pt and $Y \in [-72, -648]$ pt.
  - Landscape (12x8 in / 864x576 pt): Margin safe area $X \in [72, 792]$ pt, $Y \in [-72, -504]$ pt.
  - Portrait (8x12 in / 576x864 pt): Margin safe area $X \in [72, 504]$ pt, $Y \in [-72, -792]$ pt.
- **Zero Neighbor Artboard Bleed**:
  - Verify bounding boxes using ExtendScript geometric audit (`relBounds = [left, top, right, bottom]`) before exporting.

---

## 3. Approved Typography & Font Sizing Scale

Only use approved fonts from `/Users/cp/Ronak/CC/Photobooks/Fonts/`:

| Role | Font Family | Size Range | Typical Use Cases |
| :--- | :--- | :---: | :--- |
| **Cover Title** | `GreatVibes-Regular` | 42–46 pt | Cover title, back cover sign-offs |
| **Section Headings** | `Philosopher` / `GreatVibes-Regular` | 32–38 pt | Page titles, romantic headlines |
| **Vertical Script Titles** | `Fallinlove-Regular` | 50–56 pt | Vertical layout accents |
| **Vertical Sans Subtitles**| `Poppins-Regular` / `Poppins-Medium` | 16–20 pt | Vertical layout side text |
| **Multi-line Body & Quotes**| `Poppins-Regular` / `Poppins-Light` | 12.5–14 pt | Vows, love quotes, multi-line notes |
| **Date & Metadata Subtitles**| `Poppins-Medium` | 11.5–12 pt | Cover dates, author subtitles |

---

## 4. Script Organization Architecture

All operation scripts must strictly reside inside `/Users/cp/Ronak/CC/Photobooks/Scripts/`:
- `Scripts/Layout/` — Layout merging, de-duplication, and inspection scripts.
- `Scripts/Wedding/` — Wedding photobook generation, photo placement, and export automation.
- `Scripts/Image_Harvesting/` — Image library fetching and categorization.
- `Scripts/General/` — Shared utilities and format helpers.

*Root project directories and template folders must never contain loose scripts.*

---

## 5. Layer Architecture & Export Workflow

In Adobe Illustrator photobook automation:
- **Layer Stacking (Bottom to Top)**:
  1. `Backgrounds` (Placed 5.4K background images, clipped to artboards)
  2. `Photos_Masked` (Placed photos masked inside duplicate layout vectors)
  3. `Layout_Shapes` (Clean vector shapes for manual user editing)
  4. `Typography` (In-place styled textframes)
- **Layer Modification Rule**:
  - Always keep all layers `visible = true` while creating or modifying elements. Modifying items on hidden layers throws `Error 8705: Target layer cannot be modified`.
- **Export Previews**:
  - **Blank Previews**: `photoLayer.visible = false`, `layoutLayer.visible = true` -> capture 22 images.
  - **Populated Previews**: `photoLayer.visible = true`, `layoutLayer.visible = false` -> capture 22 images.
  - **Master Save**: Ensure all layers are visible before saving `.ai` document.
