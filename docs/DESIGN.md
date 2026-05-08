# Experiment Design & Statistical Plan

> **Last Updated:** 2026-05-02 | **Status:** Finalized

## 1. Experimental Design

**Repeated-measures factorial design:**
- **Factor A — Prompt Strategy:** 5 levels (baseline, CoT, few-shot, persona, structured decomposition)
- **Factor B — Model:** 3 levels (DeepSeek V4 Flash, Llama-3.3-70B, Nemotron-3 Super 120B)
- **Repeated measure:** Same 100 task instances across all conditions
- **Repetitions:** 3 per condition (LLM stochasticity control)

### Independent Variables

| Variable | Type | Levels |
|----------|------|--------|
| Prompt Strategy | Categorical (5) | baseline, cot, few_shot, persona, structured_decomposition |
| Model | Categorical (3) | deepseek-v4-flash, llama-3.3-70b, nemotron-3-super-120b |

### Dependent Variables

| Variable | Type | Measurement |
|----------|------|-------------|
| **Primary:** Success | Binary | PoC crashes pre-patch AND no crash post-patch |
| Success rate | Proportion | Successes / total per condition |
| Runtime | Continuous | Wall-clock seconds |
| Token usage | Count | Input + output tokens |
| API cost | Continuous | USD per run |

### Controls (Held Constant)

| Variable | Value | Rationale |
|----------|-------|-----------|
| CyberGym difficulty | Level 1 | Matches paper default |
| OpenHands commit | `35b381f3` | Reproducibility |
| Max iterations | 100 | Same as paper |
| Timeout | 1200s | Same as paper |
| Temperature | 0.0 | Minimize randomness |
| Vuln type | HBO-READ only | Reduce heterogeneity |
| PoC size | < 100 bytes | Maximize signal (paper Fig 7) |

## 2. Dataset Selection

### Inclusion Criteria
1. Vulnerability type = "Heap-buffer-overflow", access = "READ"
2. Ground-truth PoC size < 100 bytes
3. Level 1 data available
4. Docker image builds successfully

### Power Analysis (McNemar's Test)
- Baseline rate: ~5% (estimated for open-weight)
- Detectable effect: +5pp (5% → 10%)
- α = 0.05, Power = 0.80
- Required n: ~80 pairs → **Selected: 100 instances**

### Stratification
- No project > 15% of instances
- Minimum 10 distinct projects

## 3. Statistical Analysis Plan

### Primary: McNemar's Test
For each (model, strategy) vs. (model, baseline):
- 2×2 contingency table of per-instance outcomes
- Bonferroni correction: α = 0.05/12 ≈ 0.004

### Secondary
- **Cochran's Q:** Overall strategy difference within each model
- **Cohen's h:** Effect size (small=0.2, medium=0.5, large=0.8)
- **Bootstrap 95% CI:** 1000 resamples per success rate

### Interaction & Exploratory
- Model × Strategy interaction table
- Per-project breakdown
- PoC size vs. strategy effectiveness correlation
- Failure mode taxonomy
- Cost-effectiveness: success per dollar

## 4. Repetition Handling

- **Primary metric:** "any of 3 runs succeeds" (optimistic, matches paper)
- **Sensitivity:** "all 3 succeed" (strict consistency)
- **Variance:** Per-task probability = successes/3, used for bootstrap

## 5. Published Baselines (for context)

| Model | Success Rate (Level 1) |
|-------|----------------------|
| GPT-4.1 | 9.4% |
| Claude-3.7-Sonnet | 11.9% |
| Claude-Sonnet-4 | 17.9% |

Note: Our HBO-READ subset differs from full 1,507 — comparison is approximate.

## 6. Reporting Standards

- CONSORT-style flow diagram for instance filtering
- Effect size + CI for all comparisons (not just p-values)
- Full 15-condition results table (5 strategies × 3 models)
- Per-instance results matrix in supplementary
- All code and prompts in public repo
