# Photobooks Master Automation Repository

End-to-end autonomous photobook production system for Adobe Illustrator. Contains master vector layouts, approved typography scales, image library pipelines, automated build scripts, and production export workflows.

---

## 📁 Repository Structure

```
Photobooks/
├── Layout/
│   └── Final Layouts.ai         # Master Clean Layouts (44 Square, 39 Landscape, 35 Portrait)
├── Fonts/                       # Approved Typography font files
│   ├── Great Vibes (Regular)
│   ├── Philosopher (Bold / Regular)
│   ├── Fall in love (Regular)
│   ├── Poppins (Light / Regular / Medium / SemiBold / Bold)
│   ├── Book Antiqua
│   └── Gotham
├── Image_Library/               # Curated master photo libraries by theme (Wedding, Couple, Baby, Friends)
├── New/                         # Photobook Theme Projects
│   └── Wedding-V2/
│       ├── Backgorunds/         # 22 High-Res (5.4K) background textures (wed_p01.jpg - wed_p22.jpg)
│       ├── Previews/
│       │   ├── Blank/           # 22 High-res 1500x1500px blank layout JPEGs
│       │   └── Populated/       # 22 High-res 1500x1500px photo-populated JPEGs
│       └── Wedding_Square_10x10.ai # Master 22-page Illustrator Photobook
├── Scripts/                     # Centralized automation scripts & knowledge bases
│   ├── RULES.md                 # Permanent design, typography & margin rules
│   ├── MASTER_PROMPT.md         # Universal master prompt for any AI engine
│   ├── Layout/                  # Layout de-duplication and inspection scripts
│   ├── Wedding/                 # Master photobook generation & export scripts
│   ├── Image_Harvesting/        # Image asset scrapers & organizers
│   └── General/                 # Shared utilities
├── Stickers/                    # Badge, sticker, and decorative vector assets
├── SVG/                         # Frame and divider vector graphics
└── README.md                    # This master guide
```

---

## 🎨 Design & Layout Rules (Summary)

1. **Strict In-Place Text Replacement**: Only add typography to pages whose source layout in `Final Layouts.ai` originally contained text frames. Never synthesize arbitrary text on pure photo spreads.
2. **Multi-line Point Text Formatting (`\r`)**: In Adobe Illustrator Point Text, long subtitles, vows, or quotes (>40 characters) must include explicit carriage returns (`\r`) to split into 2–4 balanced lines.
3. **1-Inch Safe Margin**: All text and artwork frames must stay within the 1-inch ($72\text{ pt}$) margin boundaries:
   - **Square (10x10 in / 720x720 pt)**: $X \in [72, 648]\text{ pt}$, $Y \in [-72, -648]\text{ pt}$.
   - **Landscape (12x8 in / 864x576 pt)**: $X \in [72, 792]\text{ pt}$, $Y \in [-72, -504]\text{ pt}$.
   - **Portrait (8x12 in / 576x864 pt)**: $X \in [72, 504]\text{ pt}$, $Y \in [-72, -792]\text{ pt}$.
4. **Pattern Matching Priority**: Match replacement template patterns by longest string length first to avoid prefix collisions.
5. **Layer Stacking Order**:
   - `Typography` (Top layer)
   - `Layout_Shapes` (Editable vector boxes)
   - `Photos_Masked` (Scaled and clipped photos)
   - `Backgrounds` (Bottom layer)

---

## 📥 What the User Needs to Provide for a New Book

When commissioning a new photobook theme or variation, the user only needs to provide:
1. **Theme Name & Book Size**: e.g., `Wedding-V3`, `Baby-Square-10x10`, `Travel-Landscape-12x8`.
2. **22 Background Images**: Placed in `New/<ThemeName>/Backgorunds/` (named `p01.jpg` to `p22.jpg` or `wed_p01.jpg` to `wed_p22.jpg`).
3. **Photo Collection (Optional)**: If custom photos are provided, placed in `Image_Library/<ThemeName>/`. Otherwise, existing categorized image library photos will be utilized automatically.
4. **Custom Copy/Titles (Optional)**: Specific couple names, wedding dates, or quote preferences. (If not provided, the pipeline generates poetic theme-appropriate copy).

---

## ❓ Standard Intake Questions to Ask Before Starting

Before starting every new photobook task, the AI will confirm:
1. **Book Dimensions**: Square ($10\times10\text{ in}$), Landscape ($12\times8\text{ in}$), or Portrait ($8\times12\text{ in}$)?
2. **Target Theme & Background Folder**: Which folder inside `New/` contains the 22 backgrounds?
3. **Typography / Event Details**:
   - Names / Cover Title (e.g. *"Alexander & Charlotte"* or *"Our Wedding Story"*?)
   - Event Date & Subtitle (e.g. *"October 24, 2026"*?)
   - Any specific quotes, vows, or font preferences?
4. **Photo Source**: Use master `Image_Library/<Theme>/` photos or user-uploaded photos?
