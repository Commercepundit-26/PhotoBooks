# Photobooks Master Automation Repository

End-to-end autonomous photobook production system for Adobe Illustrator. Contains master vector layouts, approved typography scales, image library pipelines, automated build scripts, and production export workflows.

---

## 📁 Clean Repository Structure

```
Photobooks/
├── Layout/                      # Master Vector Layouts
├── Fonts/                       # Approved Typography font files (Script, Serif, Sans, Kids)
├── Image_Library/               # Curated master photo libraries by theme (Wedding, Baby, Couple, Friends)
├── backgrounds/                 # Theme Background Libraries (e.g., backgrounds/wedding/)
├── extra/                       # Reference Deliverables & Completed Themes
│   └── Wedding-V2/
│       ├── Backgorunds/         # 22 High-Res (5.4K) background textures (wed_p01.jpg - wed_p22.jpg)
│       ├── Previews/
│       │   ├── Blank/           # 22 High-res 1500x1500px blank layout JPEGs
│       │   └── Populated/       # 22 High-res 1500x1500px photo-populated JPEGs
│       └── Wedding_Square_10x10.ai # Master 22-page Illustrator Photobook
├── Scripts/                     # Centralized automation scripts & knowledge bases
│   ├── RULES.md                 # Permanent design, typography & margin rules
│   ├── MASTER_PROMPT.md         # Universal master prompt for any AI engine
│   ├── Layout/                  # Layout inspection & analysis tools
│   ├── Wedding/                 # Production pipeline scripts
│   ├── Image_Harvesting/        # Image asset scrapers & organizers
│   └── General/                 # Shared utilities
└── README.md                    # This master guide
```

---

## 🎨 Key Automation Rules (Summary)

1. **At Least 18 Text-Based Layouts**: Every 22-page master photobook must contain **at least 18 text-based layouts** (up to 20–22), with 0 to 4 pure photo layouts. Cover (P01) and Back Cover (P22) are always text-based.
2. **Dynamic Random Layout Sampling**: Layouts are randomly sampled from `Layout/Final Layouts.ai` so each generated book has a unique combination of layouts and photo frames.
3. **Strict 3-Font Consistency per Book**: Each photobook template locks **at most 3 fonts** (1 Title/Accent + 1 Subheading + 1 Body) used consistently across all 22 pages. No font mixing or multiple scripts within the same book.
4. **Multi-line Point Text Formatting (`\r`)**: In Adobe Illustrator Point Text, long subtitles, vows, or quotes (>40 characters) must include explicit carriage returns (`\r`) to split into 2–4 balanced lines.
5. **1-Inch Safe Margin**: All text frames must stay within the 1-inch ($72\text{ pt}$) margin boundaries ($X \in [72, W-72]$, $Y \in [-72, -(H-72)]$).
6. **Layer Stacking Order**:
   - `Typography` (Top layer)
   - `Layout_Shapes` (Editable vector boxes)
   - `Photos_Masked` (Scaled and clipped photos)
   - `Backgrounds` (Bottom layer)
