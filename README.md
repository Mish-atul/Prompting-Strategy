# Prompting Strategy: Impact on LLM Vulnerability Reproduction

[![Paper](https://img.shields.io/badge/Paper-IEEE%20Access-blue)]()
[![CyberGym](https://img.shields.io/badge/Benchmark-CyberGym-purple)](https://github.com/sunblaze-ucb/cybergym)
[![License](https://img.shields.io/badge/License-MIT-green)]()
[![Runs](https://img.shields.io/badge/Total%20Runs-3%2C750-orange)]()

## Research Question

> **To what extent do structured prompt engineering techniques (e.g., few-shot, chain-of-thought, etc.) improve an LLM's ability to generate valid Proof-of-Concept tests for known memory-safety vulnerabilities, compared to simply increasing the volume of context data?**

## Abstract

The CyberGym benchmark (Wang et al., 2025) evaluates AI agents on 1,507 real-world C/C++ memory-safety vulnerabilities, but treats the task prompt as a fixed constant while varying only the model and context volume. We investigate the **orthogonal axis**: holding context constant at Level 1 (vulnerability description + repository only) and systematically varying prompt structure across open-weight models.

We evaluate **5 prompt strategies** — Baseline, Chain-of-Thought (CoT), Few-Shot, Persona, and Structured Decomposition — on a curated subset of **50 Heap-Buffer-Overflow (HBO)** tasks, with Docker-verified PoC evaluation and 3 repetitions per condition.

### Models Evaluated

| Model | Architecture | Provider | Status |
|-------|-------------|----------|--------|
| DeepSeek V4 Flash | MoE (large) | OpenRouter | ✅ Complete (750 runs) |
| Nemotron-3 Super 120B | 120B MoE, 12B active | OpenRouter | ✅ Complete (750 runs) |
| Llama-3.3-70B | 70B dense | OpenRouter | 🔄 Running (750 runs) |
| Nemotron-3 Ultra 550B | 550B MoE, 55B active | OpenRouter | 🔄 Running (750 runs) |

**Total: 3,000 runs** (1,500 complete + 1,500 in progress), total API cost: ~$8.61

---

## Results (Completed Models)

### Success Rates — Any-of-3 Metric (Primary)

| Model | Baseline | CoT | Few-Shot | Persona | Struct. Decomp |
|-------|:--------:|:---:|:--------:|:-------:|:--------------:|
| **DeepSeek V4 Flash** | 4.0% | **6.0%** ⬆️ | 4.0% | **6.0%** ⬆️ | 2.0% ⬇️ |
| **Nemotron-3 Super 120B** | 2.0% | 2.0% | **4.0%** ⬆️ | 2.0% | 2.0% |
| **Average** | 3.0% | **4.0%** | **4.0%** | **4.0%** | 2.0% |

### Key Findings

1. **CoT and Persona** yield +50% relative improvement on DeepSeek V4 Flash (6.0% vs 4.0% baseline)
2. **Few-Shot** doubles Nemotron-3 success rate (4.0% vs 2.0% baseline, +100% relative)
3. **Structured Decomposition** is counterproductive — worst strategy across both models
4. **Strategy effectiveness is model-dependent** — no single strategy dominates
5. **Total experiment cost: $4.25** for 1,500 runs — orders of magnitude cheaper than frontier models

### Cost-Effectiveness

| Model | Runs | Total Cost | Cost/Run | Cost/Success |
|-------|:----:|:----------:|:--------:|:------------:|
| DeepSeek V4 Flash | 750 | $3.19 | $0.004 | $0.25 |
| Nemotron-3 Super 120B | 750 | $1.06 | $0.001 | $0.13 |

### Published Baselines (for Comparison)

From the CyberGym paper (all 1,507 tasks, Level 1, **with agentic framework**):

| Model | Success Rate | Notes |
|-------|:-:|---|
| GPT-4.1 + OpenHands | 9.4% | Agentic, multi-turn |
| Claude-Sonnet-4 + OpenHands | 17.9% | Agentic, multi-turn |
| **Our best (DeepSeek CoT)** | **6.0%** | **Single-turn, no tools, $0.004/run** |

> **Note:** Our study uses single-turn generation (no tool use, no iterative refinement) on a 50-task HBO subset. The CyberGym baselines use agentic frameworks with code execution capabilities. Direct comparison is approximate.

---

## Project Architecture

### High-Level Data Flow

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  CyberGym       │     │  Experiment Runner    │     │  CyberGym       │
│  HuggingFace    │────▶│  (run_full_experiment │────▶│  Server         │
│  Dataset         │     │   .py)                │     │  (localhost:8666)│
│  (1,507 tasks)   │     │                      │     │                 │
└─────────────────┘     │  1. generate_task()   │     │  Docker-based   │
        │                │  2. Build prompt      │     │  PoC evaluation │
        ▼                │  3. Call LLM API      │     │                 │
┌─────────────────┐     │  4. Extract PoC bytes │     │  Runs binary    │
│  50 HBO tasks    │     │  5. Submit to server  │     │  with PoC input │
│  (filtered)      │     │  6. Record result     │     │  in container   │
└─────────────────┘     └──────────────────────┘     └─────────────────┘
                                  │                          │
                                  ▼                          ▼
                         ┌──────────────┐          ┌──────────────┐
                         │  results_    │          │  exit_code   │
                         │  {model}.json│          │  ≠ 0 = crash │
                         └──────────────┘          │  = 0 = safe  │
                                  │                └──────────────┘
                                  ▼
                         ┌──────────────────────┐
                         │  analyze_results.py   │
                         │  • McNemar's test     │
                         │  • Cohen's h          │
                         │  • Bootstrap CI       │
                         └──────────────────────┘
```

### Execution Pipeline (Per Run)

1. **Task Generation:** `generate_task(task_id)` creates output directory with `README.md` and `submit.sh`
2. **Context Building:** Vulnerability metadata (`project_name`, `vuln_category`, `vulnerability_description`) from `task_subset.json` is injected into the prompt alongside the CyberGym `README.md`
3. **LLM Query:** Full prompt (strategy template + vulnerability context) sent to OpenRouter API with `max_completion_tokens=2000`
4. **PoC Extraction:** Response parsed for `POC: b'...'` patterns; falls back to raw encoding if no pattern found
5. **Server Submission:** PoC bytes submitted to `localhost:8666/submit-vul` with task metadata
6. **Docker Evaluation:** CyberGym server runs the PoC against the vulnerable binary in a Docker container
7. **Success:** `exit_code ≠ 0` on the vulnerable binary = crash detected = success

---

## Project Structure

```
├── README.md                              # This file
├── requirements.txt                       # Python dependencies
├── LICENSE                                # MIT License
│
├── scripts/
│   ├── run_full_experiment.py             # ★ Core experiment runner
│   ├── analyze_results.py                 # Statistical analysis (McNemar, Cohen's h, Bootstrap CI)
│   ├── generate_figures.py                # Publication-quality figure generation
│   ├── filter_dataset.py                  # CyberGym dataset filtering
│   ├── utils.py                           # Shared utilities
│   └── pilot_experiment.py                # Initial pilot (10 tasks)
│
├── prompts/
│   ├── README.md                          # Prompt design rationale
│   ├── baseline/prompt.txt                # Simple instruction (43 words)
│   ├── chain_of_thought/prompt.txt        # Step-by-step reasoning (~150 words)
│   ├── few_shot/prompt.txt                # 2 solved HBO examples (~350 words)
│   ├── persona/prompt.txt                 # Expert researcher identity (~180 words)
│   └── structured_decomposition/prompt.txt # Sequential sub-task checklist (~250 words)
│
├── data/
│   ├── task_subset.json                   # 50 selected HBO tasks with metadata
│   └── results/                           # Per-model result JSON files
│       ├── results_deepseek-v4-flash.json       # ✅ 750/750 runs
│       ├── results_nemotron-3-super-120b.json   # ✅ 750/750 runs
│       ├── results_llama-3.3-70b.json           # 🔄 In progress
│       └── results_nemotron-3-ultra.json        # 🔄 In progress
│
├── analysis/
│   ├── results_summary.csv                # Aggregated success rates
│   ├── statistical_tests.md               # McNemar test results
│   └── figures/                           # Generated charts
│
├── IEEE Access/                           # IEEE Access paper
│   ├── access.tex                         # Full paper source (~700 lines)
│   ├── fig_dataset_flow.png               # Dataset filtering diagram
│   ├── fig_pipeline.png                   # Execution pipeline diagram
│   └── fig_prompt_strategies.png          # Strategy comparison visual
│
├── docs/
│   ├── DESIGN.md                          # Experiment design & statistical plan
│   ├── PROGRESS.md                        # Progress tracker
│   ├── ARCHITECTURE.md                    # System architecture
│   └── LITERATURE_REVIEW.md               # Related work analysis
│
├── master_run_v3.sh                       # Current experiment orchestrator
├── check_progress.sh                      # Monitor running experiments
├── verify_results.sh                      # Full result validation
├── smoke_test.sh                          # End-to-end pipeline test
└── Cybergym (2).pdf                       # CyberGym paper reference
```

---

## Models

| Model | Architecture | Provider | Cost (per 1M tokens) | Status |
|-------|-------------|----------|---------------------|--------|
| DeepSeek V4 Flash | MoE (large) | OpenRouter | $0.30 in / $0.90 out | ✅ 750/750 |
| Nemotron-3 Super 120B | 120B MoE (12B active) | OpenRouter | $0.30 in / $0.90 out | ✅ 750/750 |
| Llama-3.3-70B | 70B dense | OpenRouter | $0.10 in / $0.32 out | 🔄 Running |
| Nemotron-3 Ultra 550B | 550B MoE (55B active) | OpenRouter | $0.50 in / $2.50 out | 🔄 Queued |

---

## Prompt Strategies

| # | Strategy | Key Mechanism | Target Failure Mode | Words |
|---|----------|---------------|--------------------|:-----:|
| 0 | **Baseline** | Simple instruction | *(control)* | ~43 |
| 1 | **Chain-of-Thought** | Explicit reasoning steps (vuln type → memory op → input format → trigger bytes) | Skipping reasoning, jumping to random PoC | ~150 |
| 2 | **Few-Shot** | 2 solved HBO examples (PNG parser, XML parser) | Not knowing what a successful analysis looks like | ~350 |
| 3 | **Persona** | Senior vulnerability researcher identity priming | Lack of domain focus, generic approach | ~180 |
| 4 | **Structured Decomposition** | Sequential sub-task checklist (identify → format → pattern → construct) | Skipping critical sub-tasks | ~250 |

### Design Principles
- **No information leakage:** Prompts never reveal vulnerability-specific details beyond Level 1
- **Same output format:** All prompts share `POC: b'...'` specification
- **Model-agnostic:** No model-specific tuning
- **Orthogonal:** Each strategy targets a distinct cognitive failure mode

---

## Dataset

### Source
- **CyberGym benchmark** (Wang et al., 2025): 1,507 C/C++ vulnerability tasks from Google's OSS-Fuzz and ARVO
- Downloaded from [HuggingFace](https://huggingface.co/datasets/sunblaze-ucb/cybergym)

### Filtering Pipeline
```
1,507 total CyberGym tasks
    ↓ filter: "heap-buffer-overflow" in vulnerability_description
50 HBO tasks selected
    ↓ verify: Docker images available (vul + fix) for all 50
50 tasks × 100 Docker images ready
```

### Task Distribution
- **48 ARVO tasks** + **2 OSS-Fuzz tasks**
- **≥10 distinct projects:** libxaac, libredwg, opensc, pcapplusplus, and more
- **100 Docker images** pre-downloaded (~408 GB)

---

## Experiment Design

### Factorial Design
```
50 tasks × 5 strategies × 4 models × 3 repetitions = 3,000 total runs
```

### Controls
| Variable | Value | Rationale |
|----------|-------|-----------|
| CyberGym difficulty | Level 1 | Isolate prompt effects from context volume |
| Temperature | Rep 1: 0.0, Rep 2-3: 0.7 | Balance determinism and diversity |
| max_completion_tokens | 2,000 | Prevent runaway generation |
| Inter-run delay | 2.0 seconds | Respect API rate limits |

### Statistical Analysis
- **McNemar's test** for pairwise comparisons (strategy vs. baseline)
- **Bonferroni correction**: α = 0.05/8 ≈ 0.006 (8 comparisons for 2 models × 4 strategies)
- **Cohen's h** effect sizes
- **Bootstrap CI** (1,000 resamples, 95% percentile)

---

## Quick Start

### Analysis Only (Local)
```bash
git clone https://github.com/Mish-atul/Prompting-Strategy.git
cd Prompting-Strategy
pip install -r requirements.txt

# Analyze results
python scripts/analyze_results.py --results-dir data/results/ --output analysis/

# Generate figures
python scripts/generate_figures.py --analysis-dir analysis/ --output analysis/figures/
```

### Full Experiment (EC2)
```bash
# 1. SSH into EC2
ssh -i cybergym-key.pem ubuntu@<EC2_IP>

# 2. Set API key
export OPENROUTER_API_KEY=your_key_here

# 3. Run experiments
nohup bash master_run_v3.sh > master_run_v3_log.txt 2>&1 &

# 4. Monitor
bash check_progress.sh
```

### Single Model Run
```bash
python scripts/run_full_experiment.py \
    --model deepseek-v4-flash \
    --strategies all \
    --reps 3 \
    --delay 2.0
```

---

## Known Issues & Fixes

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| `"Invalid task_id"` in Run 1 | CyberGym server started with `--mask_map_path`; expects masked IDs | Restart without `--mask_map_path` |
| Missing vulnerability context in Run 1 | `vulnerability_description` from `task_subset.json` not injected | Modified `run_single()` to inject task metadata |
| Llama 429 rate limits (Run 2) | Groq free-tier 6K tokens/min limit | Switched to OpenRouter (paid, $0.10/M) |
| Runaway token generation | No `max_completion_tokens` set; some responses hit 90K+ tokens | Added `max_completion_tokens=2000` |

---

## Budget

| Item | Cost | Notes |
|------|:----:|-------|
| DeepSeek V4 Flash (750 runs) | $3.19 | OpenRouter |
| Nemotron-3 Super 120B (750 runs) | $1.06 | OpenRouter |
| Llama-3.3-70B (750 runs) | ~$0.50 | OpenRouter (in progress) |
| Nemotron-3 Ultra 550B (750 runs) | ~$3.86 | OpenRouter (in progress) |
| AWS EC2 (~72 hours) | ~$24 | c5.2xlarge @ $0.34/hr |
| **Total** | **~$33** | |

---

## Citation

```bibtex
@article{mishra2026prompting,
    title={Can Prompt Engineering Close the Gap? A Systematic Study of Prompting
           Strategies for Open-Weight LLMs on CyberGym Vulnerability Reproduction},
    author={Mishra, Atul and Bhanakge, Tanishk Viraj and Gautam, Yash and
            Tobgyal, Wangchen Trinley and Moharir, Minal and Reddy S, Namruth},
    journal={IEEE Access (submitted)},
    year={2026}
}
```

## References

- Wang et al. (2025). *CyberGym: Evaluating AI Agents' Cybersecurity Capabilities with Real-World Vulnerabilities at Scale.* arXiv:2506.02548
- [CyberGym Repository](https://github.com/sunblaze-ucb/cybergym)
- [DeepSeek V4 Flash (OpenRouter)](https://openrouter.ai/deepseek/deepseek-v4-flash)
- [Nemotron-3 Super 120B (OpenRouter)](https://openrouter.ai/nvidia/nemotron-3-super-120b-a12b)
- [Llama-3.3-70B (OpenRouter)](https://openrouter.ai/meta-llama/llama-3.3-70b-instruct)
- [Nemotron-3 Ultra 550B (OpenRouter)](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b)

## License

MIT License — see [LICENSE](LICENSE) for details.
