# Research Paper Figure Prompts — IEEE Access Publication

> **Paper:** _Can Prompt Engineering Close the Gap? A Systematic Study of Prompting Strategies for Open-Weight LLMs on CyberGym Vulnerability Reproduction_
>
> **Target:** IEEE Access journal — all figures must be publication-grade, high-resolution (300+ DPI), clean white/light backgrounds, professional color palette, clear labels with proper font sizing.
>
> **Style Guide:** Use a consistent, muted academic color palette (e.g., blues: #2C3E50, #3498DB; greens: #27AE60; oranges: #E67E22; reds: #C0392B; grays: #7F8C8D). Avoid garish colors. All text should be legible at print size (minimum 8pt equivalent). Use sans-serif fonts (Helvetica, Arial, or similar).

---

## Figure 1 — Dataset Curation Flow Diagram
**File name:** `fig_dataset_flow.png` *(already exists, regenerate for higher quality)*
**Paper location:** Section III-B (Dataset Curation)
**LaTeX caption:** _CONSORT-style flow diagram of the dataset curation pipeline._

### Prompt:
```
Create a professional academic CONSORT-style flow diagram for a research paper (IEEE Access journal). 
The diagram shows a dataset filtering pipeline with the following exact stages, connected by 
downward-pointing arrows:

Stage 1 (top, large rounded rectangle, dark blue #2C3E50 background, white text):
"CyberGym Benchmark (Full Dataset)"
"1,507 vulnerability tasks"
"Sources: ARVO (1,368) + OSS-Fuzz (139)"

Arrow down labeled: "Filter: 'heap-buffer-overflow' in vulnerability_description"

Stage 2 (medium rounded rectangle, medium blue #3498DB background, white text):
"Heap-Buffer-Overflow (HBO) Subset"
"50 tasks identified"

Arrow down labeled: "Verify: Docker images available (vul + fix)"

Stage 3 (medium rounded rectangle, green #27AE60 background, white text):
"Final Experimental Dataset"
"50 HBO tasks × 100 Docker images"

To the right of Stage 3, show a summary box (light gray background, dark text) with:
"• 48 ARVO + 2 OSS-Fuzz tasks"
"• ≥10 distinct open-source projects"  
"• Languages: C, C++"
"• libxaac, libredwg, OpenSC, PcapPlusPlus, ..."

On the left side, show a rejected box (light red background) connected to Stage 2:
"Excluded: 1,457 non-HBO tasks"
"(use-after-free, stack overflow, integer overflow, etc.)"

Clean white background. Professional academic style with subtle drop shadows on boxes.
No decorative elements. Crisp vector-quality rendering. Landscape orientation, 
aspect ratio approximately 16:9.
```

---

## Figure 2 — Prompt Strategy Comparison
**File name:** `fig_prompt_strategies.png` *(already exists, regenerate for higher quality)*
**Paper location:** Section III-C (Prompt Strategy Design)
**LaTeX caption:** _Visual comparison of the five prompt engineering strategies._

### Prompt:
```
Create a professional academic figure for an IEEE Access journal paper comparing five prompt 
engineering strategies for LLM-based vulnerability reproduction. The figure should be a 
horizontal layout showing 5 strategy cards side by side, arranged from simplest (left) to 
most complex (right).

Each card should be a tall rounded rectangle with:
- A colored header strip at the top (each strategy gets a distinct color from this palette:
  Baseline=#7F8C8D gray, CoT=#3498DB blue, Few-Shot=#27AE60 green, 
  Persona=#9B59B6 purple, Struct. Decomp=#E67E22 orange)
- Strategy name in bold white text on the header
- Below the header, on white background:
  * "Target Failure Mode:" in small bold, then the target in regular text
  * "Mechanism:" in small bold, then a 1-2 line description
  * "Word Count:" followed by the number
  * A small icon or visual representing the strategy concept

Strategy details (left to right):
1. BASELINE (gray): Target="Control", Mechanism="Minimal instruction: generate PoC using 
   vulnerability info", Words="~43", Icon: simple document
2. CHAIN-OF-THOUGHT (blue): Target="Reasoning omission", Mechanism="4-step explicit reasoning: 
   vuln type → memory op → input format → trigger bytes", Words="~150", Icon: chain of connected steps
3. FEW-SHOT (green): Target="Format unfamiliarity", Mechanism="2 solved HBO examples prepended 
   (PNG parser, XML parser)", Words="~350", Icon: example documents
4. PERSONA (purple): Target="Domain disengagement", Mechanism="'Senior vulnerability researcher 
   with 15 years experience' identity priming", Words="~180", Icon: expert badge
5. STRUCTURED DECOMPOSITION (orange): Target="Sub-task skipping", Mechanism="Sequential 5-step 
   checklist: identify → analyze → format → construct → validate", Words="~250", Icon: checklist

At the bottom, show a shared element across all 5 cards:
"Common output format: POC: b'\x00\x01...'"

Clean white background. Landscape orientation ~16:9. Publication quality, 300 DPI equivalent.
All text must be clearly readable at journal column width. No decorative elements beyond 
the colored headers.
```

---

## Figure 3 — Execution Pipeline Architecture
**File name:** `fig_pipeline.png` *(already exists, regenerate for higher quality)*
**Paper location:** Section IV-B (Execution Pipeline)
**LaTeX caption:** _End-to-end execution pipeline for a single experimental run._

### Prompt:
```
Create a professional academic system architecture diagram for an IEEE Access journal paper 
showing the end-to-end execution pipeline for an LLM-based vulnerability reproduction experiment.
The diagram should flow left-to-right with 6 numbered stages connected by arrows.

Stage 1 - "Task Initialization" (light blue box):
- Icon: database/folder
- "CyberGym generate_task(task_id)"
- "→ workspace/README.md + submit.sh"
- Small label below: "CyberGym API"

Stage 2 - "Context Assembly" (light green box):
- Icon: document merge
- "Inject vulnerability metadata"
- "project_name + vuln_category + vuln_description"
- "Apply prompt strategy template"
- Small label below: "task_subset.json"

Stage 3 - "LLM Inference" (light purple box):
- Icon: brain/neural network
- "Send assembled prompt to model"
- "max_tokens=2000"
- "temp=0.0 (rep 1) / 0.7 (rep 2-3)"
- Below, show 3 API endpoints branching:
  * "OpenRouter → DeepSeek V4 Flash"
  * "OpenRouter → Nemotron-3 Super 120B"  
  * "OpenRouter → Llama-3.3-70B"

Stage 4 - "PoC Extraction" (light yellow box):
- Icon: regex/parse
- "Regex cascade: POC: b'...'"
- "Fallback: raw text → bytes"
- "Extract byte literal"

Stage 5 - "Server Submission" (light orange box):
- Icon: Docker container
- "POST /submit-vul"
- "CyberGym Docker Server (localhost:8666)"
- "Run PoC against vulnerable binary in container"

Stage 6 - "Result Recording" (light red box):
- Icon: JSON file
- "Record: exit_code, poc_size, tokens, cost"
- "Incremental JSON save"
- "exit_code ≠ 0 → SUCCESS"
- "exit_code = 0 → FAILURE"

Below the pipeline, show a feedback annotation:
"× 50 tasks × 5 strategies × 3 reps × N models = 750N total runs"

Clean white background. Horizontal flow. Each stage numbered 1-6 with circled numbers.
Professional academic style. Subtle connecting arrows with arrowheads. 
Landscape ~16:9. No decorative elements.
```

---

## Figure 4 — Success Rate Bar Chart ⭐ NEW
**File name:** `fig_success_rates.png`
**Paper location:** Section V-A (Overall Success Rates)
**LaTeX caption:** _Any-of-3 success rates by model and prompt strategy on the 50-task HBO subset._

### Prompt:
```
Create a professional grouped bar chart for an IEEE Access journal paper showing vulnerability 
reproduction success rates across prompt strategies and LLM models.

Chart specifications:
- X-axis: 5 prompt strategy groups, each with 2 bars (one per model)
  Labels: "Baseline", "Chain-of-Thought", "Few-Shot", "Persona", "Struct. Decomp"
- Y-axis: "Any-of-3 Success Rate (%)" ranging from 0% to 8%
- Two bar colors with legend:
  * DeepSeek V4 Flash: #3498DB (medium blue)
  * Nemotron-3 Super 120B: #E67E22 (orange)

Data (exact values, show value labels on top of each bar):
  Baseline:     DeepSeek=4.0%, Nemotron=2.0%
  CoT:          DeepSeek=6.0%, Nemotron=2.0%
  Few-Shot:     DeepSeek=4.0%, Nemotron=4.0%
  Persona:      DeepSeek=6.0%, Nemotron=2.0%
  Struct.Decomp: DeepSeek=2.0%, Nemotron=2.0%

Add a horizontal dashed line at 4.0% labeled "Baseline Average" in gray.

Draw subtle upward arrows above CoT and Persona bars for DeepSeek, annotated "+50%" in green.
Draw subtle upward arrow above Few-Shot bar for Nemotron, annotated "+100%" in green.
Draw subtle downward arrow above Struct.Decomp bar for DeepSeek, annotated "-50%" in red.

Clean white background with light gray gridlines on Y-axis only. Legend in upper-right corner.
Professional academic style matching IEEE publication standards. 
Aspect ratio ~4:3. All text clearly readable at print size.
```

---

## Figure 5 — Model × Strategy Heatmap ⭐ NEW
**File name:** `fig_heatmap.png`
**Paper location:** Section V-A (Overall Success Rates)
**LaTeX caption:** _Heatmap of any-of-3 success rates across all model-strategy conditions._

### Prompt:
```
Create a professional heatmap figure for an IEEE Access journal paper showing success rates 
across model-strategy combinations for LLM-based vulnerability reproduction.

Heatmap specifications:
- Rows (Y-axis, 2 rows): "DeepSeek V4 Flash", "Nemotron-3 Super 120B"
- Columns (X-axis, 5 columns): "Baseline", "CoT", "Few-Shot", "Persona", "Struct. Decomp"
- Each cell contains the percentage value displayed in bold

Data matrix:
  DeepSeek:   4.0%  |  6.0%  |  4.0%  |  6.0%  |  2.0%
  Nemotron:   2.0%  |  2.0%  |  4.0%  |  2.0%  |  2.0%

Color scale: Sequential blue colormap (white=0% → dark blue=#2C3E50=8%)
- 2.0% cells: very light blue
- 4.0% cells: medium blue  
- 6.0% cells: dark blue

Text color: white on dark cells (6.0%), black on light cells (2.0%, 4.0%).

Add a colorbar on the right labeled "Success Rate (%)".
Add a title: "Any-of-3 Success Rate by Model × Strategy"

Below the heatmap, add a small annotation row showing "Δ vs Baseline": 
"+0pp", "+2pp", "+0pp", "+2pp", "-2pp" for DeepSeek
"+0pp", "+0pp", "+2pp", "+0pp", "+0pp" for Nemotron

Clean white background. Aspect ratio ~3:2 (wider than tall). 
Cells should be square-ish. All text clearly readable.
Professional academic style. No decorative elements.
```

---

## Figure 6 — Cohen's h Effect Size Forest Plot ⭐ NEW
**File name:** `fig_effect_sizes.png`
**Paper location:** Section V-C (Effect Sizes)
**LaTeX caption:** _Forest plot of Cohen's h effect sizes for each strategy vs. baseline comparison._

### Prompt:
```
Create a professional forest plot (also known as a blobbogram) for an IEEE Access journal paper 
showing effect sizes of prompt engineering strategies compared to baseline.

Plot specifications:
- Y-axis (labels on left): List each comparison:
  "DeepSeek × CoT"
  "DeepSeek × Few-Shot"
  "DeepSeek × Persona"  
  "DeepSeek × Struct. Decomp"
  --- horizontal separator ---
  "Nemotron × CoT"
  "Nemotron × Few-Shot"
  "Nemotron × Persona"
  "Nemotron × Struct. Decomp"

- X-axis: "Cohen's h (Effect Size)" ranging from -0.20 to +0.20

- For each row, show a point (filled circle) at the effect size value:
  DeepSeek × CoT:         h = +0.09  (blue circle)
  DeepSeek × Few-Shot:    h =  0.00  (gray circle)
  DeepSeek × Persona:     h = +0.09  (blue circle)
  DeepSeek × Struct.Decomp: h = -0.11 (red circle)
  Nemotron × CoT:         h =  0.00  (gray circle)
  Nemotron × Few-Shot:    h = +0.10  (blue circle)
  Nemotron × Persona:     h =  0.00  (gray circle)
  Nemotron × Struct.Decomp: h =  0.00 (gray circle)

- Draw a vertical dashed line at h=0 (no effect)
- Draw vertical dotted lines at h=±0.20 labeled "Small effect threshold"
- Shade the region between -0.20 and +0.20 in very light gray, labeled "Negligible effect zone"

- Color coding: blue for positive (improvement), red for negative (decline), gray for zero

Clean white background. Landscape orientation. Professional academic style.
All text clearly readable at journal column width. Aspect ratio ~4:3.
```

---

## Figure 7 — Cost-Effectiveness Comparison ⭐ NEW
**File name:** `fig_cost_comparison.png`
**Paper location:** Section V-E / Section VI-E (Cost-Effectiveness)
**LaTeX caption:** _Cost comparison between open-weight models (this study) and frontier model baselines._

### Prompt:
```
Create a professional dual-axis comparison chart for an IEEE Access journal paper comparing 
the cost-effectiveness of open-weight vs. frontier models for vulnerability reproduction.

The chart should have two panels side by side:

LEFT PANEL — "Cost per Run ($)"
Horizontal bar chart (bars going right):
  "DeepSeek V4 Flash":      $0.004  (blue bar, very short)
  "Nemotron-3 Super 120B":  $0.001  (orange bar, tiny)
  "Our Average":            $0.003  (green bar, very short)
  --- separator ---
  "GPT-4.1 + OpenHands":    $5-10   (dark gray bar, very long)
  "Claude-Sonnet-4 + OpenHands": $10-50 (dark gray bar, longest)

Use a logarithmic X-axis ($0.001 to $100) so the small and large bars are visible.
Label each bar with the dollar amount.

RIGHT PANEL — "Success Rate vs. Cost Bubble Chart"
Scatter/bubble plot:
  X-axis: "Total Experiment Cost ($)" — log scale, from $1 to $10,000
  Y-axis: "Success Rate (%)" — linear, 0% to 20%
  
  Bubbles (size proportional to number of runs):
  - DeepSeek CoT (best): x=$3.19, y=6.0%, color=blue, label="DeepSeek CoT"
  - Nemotron FS (best):  x=$1.06, y=4.0%, color=orange, label="Nemotron FS"
  - GPT-4.1:            x=~$5000, y=9.4%, color=dark gray, label="GPT-4.1*"
  - Claude-Sonnet-4:    x=~$8000, y=17.9%, color=dark gray, label="Claude-Sonnet-4*"
  
  Add asterisk note: "* Estimated cost. Uses agentic framework (OpenHands) with multi-turn tool use."

Draw a diagonal dashed line showing "iso-efficiency" (same success/dollar ratio).
Annotate: "100-1000× cheaper per run"

Clean white background. Two-panel layout. Professional academic style.
Landscape orientation ~16:9. All text clearly readable.
```

---

## Figure 8 — Per-Run Exit Code Distribution ⭐ NEW
**File name:** `fig_exit_codes.png`
**Paper location:** Section V-D (Error Analysis)
**LaTeX caption:** _Distribution of exit codes across all 1,500 experimental runs._

### Prompt:
```
Create a professional stacked bar chart for an IEEE Access journal paper showing the 
distribution of exit codes across LLM-generated vulnerability PoC submissions.

Chart specifications:
- X-axis: Two bars, one for each model: "DeepSeek V4 Flash", "Nemotron-3 Super 120B"
- Y-axis: "Number of Runs" from 0 to 750
- Each bar is stacked with three segments:

  DeepSeek V4 Flash (total=750):
    exit_code=0 (no crash): 733 runs — light gray #BDC3C7
    exit_code≠0 (crash/success): 13 runs — green #27AE60  
    API error (None): 4 runs — red #E74C3C

  Nemotron-3 Super 120B (total=750):
    exit_code=0 (no crash): 736 runs — light gray #BDC3C7
    exit_code≠0 (crash/success): 8 runs — green #27AE60
    API error (None): 6 runs — red #E74C3C

- Show exact count labels inside or next to each segment
- The success segments (green) should have an annotation arrow pointing to them:
  "13 successful crashes (1.7%)" for DeepSeek
  "8 successful crashes (1.1%)" for Nemotron

Legend (horizontal, below chart):
  Gray = "No crash (exit_code=0)"
  Green = "Crash detected (exit_code≠0) — SUCCESS"  
  Red = "API error (exit_code=None)"

Add a text annotation at the bottom:
"Overall: 21/1,500 runs (1.4%) produced successful crashes"

Clean white background. Portrait-ish aspect ratio ~3:4. Professional academic style.
Clearly readable at single-column width.
```

---

## Figure 9 — Strategy Interaction Radar/Spider Chart ⭐ NEW
**File name:** `fig_radar_strategies.png`
**Paper location:** Section VI-A (Prompt Strategy Effectiveness)
**LaTeX caption:** _Radar chart comparing prompt strategy effectiveness profiles across models._

### Prompt:
```
Create a professional radar chart (spider chart) for an IEEE Access journal paper comparing 
how different prompt strategies perform across two LLM models.

Radar chart specifications:
- 5 axes radiating from center, one per strategy:
  Top: "Baseline"
  Upper-right: "Chain-of-Thought"
  Lower-right: "Few-Shot"
  Lower-left: "Persona"
  Upper-left: "Struct. Decomp"

- Radial scale: 0% at center → 8% at outer edge, with gridlines at 2%, 4%, 6%, 8%
- Label each gridline with the percentage

- Two overlaid polygons:
  1. DeepSeek V4 Flash (blue #3498DB, semi-transparent fill, solid border):
     Baseline=4%, CoT=6%, Few-Shot=4%, Persona=6%, Struct.Decomp=2%
  2. Nemotron-3 Super 120B (orange #E67E22, semi-transparent fill, dashed border):
     Baseline=2%, CoT=2%, Few-Shot=4%, Persona=2%, Struct.Decomp=2%

- Mark each vertex with a dot (filled circle) in the respective color
- Show value labels at each vertex

- Legend in upper-right corner outside the radar:
  Blue solid line = "DeepSeek V4 Flash"
  Orange dashed line = "Nemotron-3 Super 120B"

Key observation annotation (small text box at bottom):
"DeepSeek benefits from CoT and Persona; Nemotron benefits only from Few-Shot"

Clean white background. Square aspect ratio ~1:1. Professional academic style.
All axis labels clearly readable. Subtle gray gridlines.
```

---

## Figure 10 — Comparison with CyberGym Published Results ⭐ NEW
**File name:** `fig_comparison_cybergym.png`
**Paper location:** Section VI-B (Comparison with Frontier Models)
**LaTeX caption:** _Performance comparison between our single-turn open-weight approach and CyberGym's published agentic baselines._

### Prompt:
```
Create a professional comparison figure for an IEEE Access journal paper contrasting our 
single-turn open-weight LLM results with published CyberGym agentic baselines.

The figure should be a horizontal bar chart with clear visual separation between the two 
groups of results:

GROUP 1 — "This Study (Single-Turn, Non-Agentic)" — bars in blue/color tones:
  "DeepSeek V4 Flash × CoT":      6.0%  (blue bar #3498DB)
  "DeepSeek V4 Flash × Persona":  6.0%  (blue bar, slightly lighter)
  "Nemotron-3 × Few-Shot":        4.0%  (orange bar #E67E22)
  "DeepSeek V4 Flash × Baseline": 4.0%  (gray bar #95A5A6)

--- Visual separator with label "Agentic Framework Baselines (CyberGym Paper)" ---

GROUP 2 — "CyberGym (Multi-Turn, Agentic + OpenHands)" — bars in dark gray:
  "GPT-4.1 + OpenHands":          9.4%  (dark gray #34495E)
  "Claude-3.7-Sonnet + OpenHands": 11.9% (dark gray, slightly lighter)
  "Claude-Sonnet-4 + OpenHands":  17.9% (dark gray #2C3E50)

X-axis: "Success Rate (%)" from 0% to 20%
Show exact percentage labels at the end of each bar.

Add annotation boxes:
- Near our results: "Cost: $4.25 total (1,500 runs)" in green text
- Near CyberGym results: "Cost: Est. $5,000-10,000+" in red text
- Bridge annotation between groups: "Gap: 3.4-11.9 pp"
- Footer note: "⚠ Not directly comparable: different task subsets (50 HBO vs. 1,507 all types), 
  different evaluation modes (single-turn vs. multi-turn agentic with tool use)"

Clean white background. Landscape orientation ~16:9. Professional academic style.
Clear visual hierarchy separating the two groups. All text readable at print size.
```

---

## Figure 11 — Research Framework Overview ⭐ NEW (Optional — for Introduction)
**File name:** `fig_framework_overview.png`
**Paper location:** Section I (Introduction) — overview figure
**LaTeX caption:** _Research framework: evaluating prompt engineering as an orthogonal improvement axis to context volume for LLM vulnerability reproduction._

### Prompt:
```
Create a professional conceptual research framework diagram for an IEEE Access journal paper.
The diagram illustrates two orthogonal axes of improvement for LLM-based vulnerability 
reproduction.

Layout: A 2D conceptual space with two axes:

HORIZONTAL AXIS (bottom): "Context Volume (CyberGym Levels)"
  Left: "Level 1: Vuln description only"
  Middle: "Level 2: + Stack traces"
  Right: "Level 3: + Patch diffs"
  Arrow pointing right, labeled "Prior work (CyberGym paper)"

VERTICAL AXIS (left): "Prompt Engineering (This Study)"
  Bottom: "Baseline (43 words)"
  Middle: "CoT / Persona (~150-180 words)"
  Top: "Few-Shot (~350 words)"
  Arrow pointing up, labeled "Our contribution"

In the 2D space, show:
- A horizontal arrow from Level 1 to Level 3 at Baseline prompt level, labeled:
  "CyberGym approach: Fix prompt, vary context"
  "GPT-4.1: 9.4% → ~15% → ~22%"

- A vertical arrow from Baseline to CoT at Level 1, labeled:
  "Our approach: Fix context, vary prompt"  
  "DeepSeek: 4.0% → 6.0% (+50%)"

- A question mark in the upper-right quadrant (high context + high prompt engineering),
  labeled "Unexplored: Combined optimization"

- Color the "Our contribution" axis/zone in blue (#3498DB)
- Color the "Prior work" axis/zone in gray (#7F8C8D)
- Color the "Unexplored" zone in light yellow with a dashed border

Title at top: "Two Orthogonal Axes of Improvement for LLM Vulnerability Reproduction"

Clean white background. Square-ish aspect ratio. Professional academic style.
This is a conceptual diagram, not a data plot — use clean geometric shapes and arrows.
Clearly readable at full-page width in a journal.
```

---

## Usage Notes

1. **Generate these figures using** an AI image generation tool (e.g., ChatGPT DALL-E, Midjourney, or a specialized diagram tool like Mermaid/draw.io for architecture diagrams).
2. **For data plots** (Figures 4-10): Consider generating via Python matplotlib/seaborn for pixel-perfect accuracy — the prompts above can guide the visual design.
3. **Resolution:** All figures should be saved at **300 DPI minimum** for print quality.
4. **Format:** PNG for raster, PDF preferred for vector (bar charts, line plots).
5. **Color consistency:** Use the same palette across all figures for visual coherence.
6. **Accessibility:** Ensure sufficient contrast ratios. Use patterns (hatching) in addition to color for bar charts to support grayscale printing.

### Recommended Figure Placement in Paper

| Figure | Section | Type | Priority |
|--------|---------|------|:--------:|
| Fig. 1 — Dataset Flow | III-B Methodology | Architecture | ★★★ Must have |
| Fig. 2 — Prompt Strategies | III-C Methodology | Comparison | ★★★ Must have |
| Fig. 3 — Execution Pipeline | IV-B Experimental Setup | Architecture | ★★★ Must have |
| Fig. 4 — Success Rate Bars | V-A Results | Data plot | ★★★ Must have |
| Fig. 5 — Heatmap | V-A Results | Data plot | ★★☆ Recommended |
| Fig. 6 — Effect Size Forest | V-C Results | Data plot | ★★☆ Recommended |
| Fig. 7 — Cost Comparison | VI-E Discussion | Data plot | ★★★ Must have |
| Fig. 8 — Exit Code Dist. | V-D Results | Data plot | ★☆☆ Optional |
| Fig. 9 — Radar Chart | VI-A Discussion | Data plot | ★★☆ Recommended |
| Fig. 10 — CyberGym Comparison | VI-B Discussion | Comparison | ★★★ Must have |
| Fig. 11 — Framework Overview | I Introduction | Conceptual | ★★★ Must have |
