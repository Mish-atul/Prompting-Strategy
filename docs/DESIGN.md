# Experiment Design & Statistical Plan

## Research Design

**Repeated-measures factorial design** with two independent variables:

| Variable | Type | Levels |
|----------|------|--------|
| **Prompt Strategy** | Categorical (5) | Baseline, CoT, Few-Shot, Persona, Structured Decomposition |
| **Model** | Categorical (4) | DeepSeek V4 Flash, Nemotron-3 Super 120B, Llama-3.3-70B, Nemotron-3 Ultra 550B |

**Run matrix:** 50 tasks × 5 strategies × 4 models × 3 reps = **3,000 total runs**

## Models Under Evaluation

| Model | Architecture | Active Params | Provider | Cost/1M tok |
|-------|-------------|:------------:|----------|:-----------:|
| DeepSeek V4 Flash | MoE | Large | OpenRouter | $0.30/$0.90 |
| Nemotron-3 Super 120B | MoE (120B total) | 12B | OpenRouter | $0.30/$0.90 |
| Llama-3.3-70B | Dense | 70B | OpenRouter | $0.10/$0.32 |
| Nemotron-3 Ultra 550B | MoE (550B total) | 55B | OpenRouter | $0.50/$2.50 |

## Dataset

- **Source:** CyberGym benchmark (1,507 tasks)
- **Filter:** `heap-buffer-overflow` in `vulnerability_description`
- **Final subset:** 50 HBO tasks, 100 Docker images
- **Projects:** ≥10 distinct (libxaac, libredwg, opensc, pcapplusplus, etc.)

## Evaluation Metrics

### Primary: PoC Success
- `exit_code ≠ 0` on vulnerable binary = crash = success

### Aggregation: Any-of-3
- Task succeeds if **any** of 3 repetitions succeeds (matches CyberGym protocol)

### Statistical Tests
1. **McNemar's test** — pairwise comparisons (strategy vs baseline per model)
2. **Bonferroni correction** — α = 0.05/n_comparisons
3. **Cohen's h** — effect size for proportions
4. **Bootstrap CI** — 1,000 resamples, 95% percentile

## Controlled Variables

| Variable | Value | Rationale |
|----------|-------|-----------|
| CyberGym Level | 1 | Isolate prompt effects |
| Temperature | Rep1=0.0, Rep2-3=0.7 | Balance determinism/diversity |
| max_completion_tokens | 2,000 | Prevent runaway generation |
| Inter-run delay | 2.0s | Respect rate limits |
| Output format | `POC: b'...'` | Consistent across all prompts |

## Results Summary (Completed Models)

### Any-of-3 Success Rates

| Model | BL | CoT | FS | Per | SD |
|-------|:--:|:---:|:--:|:---:|:--:|
| DeepSeek V4 Flash | 4.0% | **6.0%** | 4.0% | **6.0%** | 2.0% |
| Nemotron-3 Super 120B | 2.0% | 2.0% | **4.0%** | 2.0% | 2.0% |

### Effect Sizes (Cohen's h vs Baseline)

| Model | CoT | FS | Per | SD |
|-------|:---:|:--:|:---:|:--:|
| DeepSeek | 0.09 | 0.00 | 0.09 | -0.11 |
| Nemotron-3 Super | 0.00 | 0.10 | 0.00 | 0.00 |

All effects are in the negligible range (|h| < 0.2) — directionally consistent but small absolute magnitude due to the extreme difficulty of single-turn PoC generation.
