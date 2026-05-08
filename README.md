# Prompting Strategy: Impact on LLM Vulnerability Reproduction

[![Paper](https://img.shields.io/badge/Paper-In%20Progress-orange)]()
[![CyberGym](https://img.shields.io/badge/Benchmark-CyberGym-blue)](https://github.com/sunblaze-ucb/cybergym)
[![License](https://img.shields.io/badge/License-MIT-green)]()

## Research Question

> **Can structured prompt engineering close the performance gap between small open-weight models (~7B–32B) and frontier models on real-world vulnerability reproduction — without providing additional context data?**

## Abstract

The CyberGym benchmark (Wang et al., 2025) evaluates AI agents on 1,507 real-world C/C++ memory-safety vulnerabilities, but treats the task prompt as a fixed constant while varying only the model and context volume. We investigate the **orthogonal axis**: holding context constant at Level 1 and systematically varying prompt structure across open-weight models. Using DeepSeek V4 Flash, NVIDIA Nemotron-3 Super 120B, and Llama-3.3-70B (via OpenRouter and Groq APIs), we test 5 prompt strategies (Chain-of-Thought, Few-Shot, Persona, Structured Decomposition, and a baseline control) on a curated subset of ~100 Heap-buffer-overflow READ vulnerabilities with short ground-truth PoCs.

## Key Contributions

1. **First systematic prompt engineering study on CyberGym** — the original paper never varies prompt structure
2. **Open-weight model analysis** — DeepSeek V4 Flash, Nemotron-3 Super 120B, and Llama-3.3-70B received minimal coverage in the original paper
3. **Cost-effectiveness analysis** — can $10-20 in API costs match $2,000+ in frontier model calls?
4. **Practical guidance** — which prompting techniques help (and which don't) for vulnerability reproduction

## Project Structure

```
├── README.md                           # This file
├── docs/
│   ├── IMPLEMENTATION_PLAN.md          # Phased implementation roadmap
│   ├── ARCHITECTURE.md                 # System architecture & data flow
│   ├── PRD.md                          # Product Requirements Document
│   ├── DESIGN.md                       # Experiment design & statistical plan
│   ├── PROGRESS.md                     # Sprint progress tracker
│   ├── LITERATURE_REVIEW.md            # Related work analysis
│   └── research_paper/
│       ├── paper.tex                   # LaTeX research paper
│       ├── references.bib             # Bibliography
│       └── figures/                   # Paper figures
├── prompts/
│   ├── baseline/prompt.txt            # CyberGym default (control)
│   ├── chain_of_thought/prompt.txt    # CoT reasoning steps
│   ├── few_shot/prompt.txt            # 2-3 solved examples
│   ├── persona/prompt.txt             # Expert researcher persona
│   └── structured_decomposition/prompt.txt  # Sub-task breakdown
├── scripts/
│   ├── filter_dataset.py              # Select HBO-READ subset
│   ├── run_experiment.py              # Batch experiment orchestrator
│   ├── analyze_results.py             # Statistical analysis
│   ├── generate_figures.py            # Visualization pipeline
│   └── utils.py                       # Shared utilities
├── data/
│   ├── task_subset.json               # Selected ~100 instances
│   └── results/                       # Per-strategy outputs
└── analysis/
    ├── results_summary.csv            # Aggregated metrics
    └── figures/                       # Generated charts
```

## Models

| Model | Access Method | Cost | Parameters |
|-------|-------------|------|------------|
| DeepSeek V4 Flash | OpenRouter API | ~$0.30/M input tokens | MoE |
| NVIDIA Nemotron-3 Super 120B | OpenRouter API | ~$0.30/M input tokens | 120B MoE (12B active) |
| Llama-3.3-70B | Groq API (free tier) | Free | 70B |

## Prompt Strategies

| # | Strategy | Description |
|---|----------|-------------|
| 0 | **Baseline** | CyberGym's exact default prompt (1 sentence) |
| 1 | **Chain-of-Thought** | Step-by-step reasoning about vuln type, memory layout, trigger bytes |
| 2 | **Few-Shot** | 2 solved HBO-READ examples prepended to prompt |
| 3 | **Persona** | Senior vulnerability researcher identity with methodology |
| 4 | **Structured Decomposition** | Explicit sub-tasks: identify vuln path → find parser → craft input |

## Quick Start

### Prerequisites
- Python 3.11+
- Docker (for CyberGym server)
- API keys: OpenRouter ($10 budget), Groq (free tier)

### Setup
```bash
# Clone
git clone https://github.com/Mish-atul/Prompting-Strategy.git
cd Prompting-Strategy

# Install dependencies
pip install -r requirements.txt

# Set API keys
export OPENROUTER_API_KEY=your_key_here   # For DeepSeek V4 Flash + Nemotron-3
export GROQ_API_KEY=your_key_here          # For Llama-3.3-70B (free tier)
```

### Running Experiments
```bash
# 1. Filter dataset to HBO-READ subset
python scripts/filter_dataset.py --tasks-file ./cybergym_data/tasks.json --output data/task_subset.json

# 2. Run a single experiment
python scripts/run_experiment.py \
    --strategy baseline \
    --model deepseek-v3 \
    --task-subset data/task_subset.json \
    --reps 3

# 3. Analyze results
python scripts/analyze_results.py --results-dir data/results/ --output analysis/
```

## Experiment Matrix

- **100 instances** × **5 strategies** × **3 models** × **3 repetitions** = **4,500 runs**
- Estimated cost: **$15–30** (DeepSeek API) + **~$170** (AWS compute) = **~$200 total**

## Citation

If you use this work, please cite:
```bibtex
@misc{prompting-strategy-2026,
    title={Can Prompt Engineering Close the Gap? A Systematic Study of Prompting 
           Strategies for Open-Weight LLMs on CyberGym Vulnerability Reproduction},
    author={[Your Name]},
    year={2026},
    note={In preparation}
}
```

## References

- Wang et al. (2025). *CyberGym: Evaluating AI Agents' Cybersecurity Capabilities with Real-World Vulnerabilities at Scale.* arXiv:2506.02548
- [CyberGym Repository](https://github.com/sunblaze-ucb/cybergym)
- [CyberGym Agent Examples](https://github.com/sunblaze-ucb/cybergym-agent-examples)

## License

MIT License — see [LICENSE](LICENSE) for details.
