# Photobook Design, Typography & Engineering Rules (All 3 Sizes)

Permanent operational guidelines and engineering constraints for autonomous photobook generation across all 3 standard sizes in Adobe Illustrator.

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
1. **Primary Title / Accent Font** (Choose 1 only per book):
   - Used for main headings, cover title, and major section accents.
2. **Secondary Heading / Subtitle Font** (Choose 1 only per book):
   - Used for page subheadings, dates, and category tags.
3. **Body / Quote / Vows Font** (Choose 1 only per book):
   - Used for narrative paragraphs, quotes, and multi-line vow blocks.

> **CRITICAL RULE**: Never mix multiple script fonts or multiple heading fonts in the same photobook template. Once a font palette is selected for a book, it is **100% locked across all 22 pages**. When generating a different book/template, choose a different font combination.

---

## 4. Approved Font Catalog by Category

All approved font files reside in `Fonts/`. Reference fonts by their exact PostScript name:

### Category 1: Script & Calligraphy (Romantic, Wedding, Anniversary)
- **Great Vibes**: `GreatVibes-Regular`
- **Fall in love**: `Fallinlove-Regular`
- **Business Signature Demo**: `BusinessSignatureDemo-Regular`
- **Nura Asyifa**: `NuraAsyifa-Regular`
- **Raustila Regular**: `RaustilaRegular-Regular`

### Category 2: Serif & Editorial (Classic, Timeless, High-End)
- **Philosopher**: `Philosopher`, `Philosopher-Bold`
- **Book Antiqua**: `BookAntiqua`, `BookAntiqua-Bold`, `BookAntiqua-Italic`

### Category 3: Sans-Serif & Modern (Clean, Contemporary, Minimalist)
- **Poppins**: `Poppins-Light`, `Poppins-Regular`, `Poppins-Medium`, `Poppins-SemiBold`, `Poppins-Bold`, `Poppins-Black`
- **Gotham**: `Gotham-Book`, `Gotham-Bold`, `Gotham-Black`, `Gotham-BookItalic`
- **Bebas Neue**: `BebasNeue-Regular`
- **Arial**: `Arial-Regular`, `Arial-Bold`, `Arial-Italic`

### Category 4: Kids & Display (Baby, Family, Playful, Holiday)
- **Lobster Two**: `LobsterTwo-Regular`, `LobsterTwo-Bold`, `LobsterTwo-Italic`
- **Rockwell**: `Rockwell-Regular`, `Rockwell-Bold`, `Rockwell-Italic`
- **Abscissa**: `Abscissa-Regular`, `Abscissa-Bold`, `Abscissa-Italic`

---

## 5. Multi-Line Point Text (`\r`) & Safe Margin Constraints

- **Point Text Multi-Line Formatting (`\r`)**:
  - In Adobe Illustrator Point Text (`TextType.POINTTEXT`), text does NOT auto-wrap.
  - Any subtitle, vow, or quote longer than 40 characters MUST include explicit carriage returns (`\r`) to split into 2–4 balanced lines.
  - Never let point text run on a single unbroken line across page boundaries.
- **Pattern Matching Priority**:
  - Sort dictionary replacement keys by length descending (`b.length - a.length`) so longer patterns match before short prefixes.

---

## 6. Illustrator Layer Architecture & Export Workflow

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
