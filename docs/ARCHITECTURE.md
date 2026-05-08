# Architecture — System Design & Data Flow

> **Last Updated:** 2026-05-02

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EXPERIMENT CONTROL PLANE                      │
│                     (Your Local Machine / AWS EC2)                    │
│                                                                      │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐ │
│  │ filter_      │   │ run_         │   │ analyze_results.py       │ │
│  │ dataset.py   │──▶│ experiment.py│──▶│ generate_figures.py      │ │
│  └──────┬───────┘   └──────┬───────┘   └──────────────────────────┘ │
│         │                  │                                         │
│         ▼                  ▼                                         │
│  ┌──────────────┐   ┌──────────────────────────────────────┐        │
│  │ task_subset   │   │         PROMPT TEMPLATES              │        │
│  │ .json (100)   │   │  baseline │ cot │ few-shot │ persona │        │
│  └──────────────┘   │  structured_decomposition             │        │
│                      └──────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
           ┌──────────┐ ┌──────────┐ ┌──────────┐
           │DeepSeek  │ │ Groq     │ │ Ollama   │
           │V3 API    │ │ API      │ │ (local)  │
           │          │ │Llama-3.3 │ │Qwen2.5-  │
           │$0.014/M  │ │-70B      │ │Coder-32B │
           └────┬─────┘ └────┬─────┘ └────┬─────┘
                │            │            │
                └────────────┼────────────┘
                             ▼
              ┌──────────────────────────────┐
              │   CyberGym OpenHands Agent    │
              │   (Docker Container)          │
              │                               │
              │  1. Receives prompt           │
              │  2. Reads /workspace          │
              │  3. Analyzes vulnerability    │
              │  4. Generates PoC             │
              │  5. Submits via submit.sh     │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   CyberGym Submission Server  │
              │   (Docker - Port 8666)        │
              │                               │
              │  1. Receives PoC binary       │
              │  2. Runs against pre-patch    │
              │     binary (with sanitizer)   │
              │  3. Runs against post-patch   │
              │     binary                    │
              │  4. Returns verdict:          │
              │     PASS = crash on pre,      │
              │            no crash on post   │
              └──────────────────────────────┘
```

---

## Component Details

### 1. Dataset Filter (`scripts/filter_dataset.py`)

**Input:** CyberGym `tasks.json` (1,507 entries)  
**Output:** `data/task_subset.json` (~100 entries)

Filter pipeline:
```
1,507 total tasks
  │
  ▼ Filter: vulnerability_type == "Heap-buffer-overflow" AND access_type == "READ"
458 HBO-READ instances
  │
  ▼ Filter: ground_truth_poc_size < 100 bytes (from paper's Figure 7)
~150-200 instances (estimated)
  │
  ▼ Stratified sample: balance across projects, select ~100
~100 final instances
```

### 2. Experiment Runner (`scripts/run_experiment.py`)

**Responsibilities:**
- Load task subset and prompt template
- For each (task, strategy, model, rep) combination:
  1. Generate CyberGym task directory (`gen_task.py`)
  2. Inject the selected prompt template (replacing `prompt.txt`)
  3. Launch the OpenHands agent with the configured model
  4. Record outcome: success/fail, runtime, tokens used, PoC hash
  5. Store results in `data/results/{strategy}/{task_id}_{rep}.json`

**Parallelization Strategy:**
- Tasks are independent → can run multiple tasks in parallel
- Limit: Docker container resources and API rate limits
- DeepSeek V4 Flash (OpenRouter): generous rate limit → 4-8 parallel tasks
- Groq (Llama-3.3-70B): lower free tier limits → 1-2 parallel tasks
- Nemotron-3 Super 120B (OpenRouter): moderate rate limit → 2-4 parallel tasks

### 3. Model Interface Layer (`scripts/utils.py`)

Unified abstraction over three model backends:

```python
class ModelBackend:
    """Abstract interface for LLM backends"""
    
    @staticmethod
    def get_backend(model_name: str) -> ModelConfig:
        backends = {
            "deepseek-v4-flash": {
                "api_base": "https://openrouter.ai/api/v1",
                "model_id": "deepseek/deepseek-v4-flash",
                "env_key": "OPENROUTER_API_KEY",
                "cost_per_1m_input": 0.30,
                "cost_per_1m_output": 0.90,
            },
            "llama-3.3-70b": {
                "api_base": "https://api.groq.com/openai/v1",
                "model_id": "llama-3.3-70b-versatile",
                "env_key": "GROQ_API_KEY",
                "cost_per_1m_input": 0.0,
                "cost_per_1m_output": 0.0,
            },
            "nemotron-3-super-120b": {
                "api_base": "https://openrouter.ai/api/v1",
                "model_id": "nvidia/nemotron-3-super-120b-a12b",
                "env_key": "OPENROUTER_API_KEY",
                "cost_per_1m_input": 0.30,
                "cost_per_1m_output": 0.90,
            },
        }
        return backends[model_name]
```

### 4. Analysis Pipeline (`scripts/analyze_results.py`)

```
Raw Results (JSON per run)
  │
  ▼ Aggregate
Per-condition success rates (mean ± std across 3 reps)
  │
  ▼ Statistical Tests
  ├── McNemar's test: pairwise strategy comparisons (p-values)
  ├── Chi-squared: overall significance across strategies
  ├── Cohen's h: effect size for each strategy vs. baseline
  └── Bootstrap CI: 95% confidence intervals (1000 resamples)
  │
  ▼ Breakdowns
  ├── Model × Strategy interaction matrix
  ├── Per-project success rate heatmap
  └── PoC size vs. success rate correlation
  │
  ▼ Output
  ├── analysis/results_summary.csv
  ├── analysis/statistical_tests.md
  └── analysis/figures/*.pdf
```

---

## Data Schema

### Task Subset Entry (`data/task_subset.json`)
```json
{
    "task_id": "arvo:10400",
    "project": "libpng",
    "vulnerability_type": "Heap-buffer-overflow",
    "access_type": "READ",
    "poc_size_bytes": 42,
    "description_preview": "Heap-buffer-overflow in ReadPNGChunk..."
}
```

### Experiment Result (`data/results/{strategy}/{task_id}_{model}_{rep}.json`)
```json
{
    "task_id": "arvo:10400",
    "strategy": "chain_of_thought",
    "model": "deepseek-v3",
    "repetition": 1,
    "success": true,
    "exit_code_prepatch": 1,
    "exit_code_postpatch": 0,
    "runtime_seconds": 847,
    "tokens_input": 12450,
    "tokens_output": 3200,
    "cost_usd": 0.001,
    "poc_hash": "714f093fe3c90135...",
    "poc_size_bytes": 33,
    "agent_id": "8113f33401d34ee3...",
    "timestamp": "2026-06-05T14:23:00Z",
    "error": null
}
```

---

## Infrastructure Layout (AWS)

```
┌─────────────────────────────────────────┐
│         AWS EC2 c5.2xlarge              │
│         (8 vCPU, 16GB RAM)             │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │     Docker Engine                │   │
│  │                                  │   │
│  │  ┌────────────────────────────┐ │   │
│  │  │  CyberGym Server           │ │   │
│  │  │  Port 8666                 │ │   │
│  │  │  (sanitizer evaluation)    │ │   │
│  │  └────────────────────────────┘ │   │
│  │                                  │   │
│  │  ┌────────────────────────────┐ │   │
│  │  │  OpenHands Runtime         │ │   │
│  │  │  (agent container)         │ │   │
│  │  └────────────────────────────┘ │   │
│  │                                  │   │
│  │  ┌────────────────────────────┐ │   │
│  │  │  Ollama                    │ │   │
│  │  │  (Qwen2.5-Coder-32B)     │ │   │
│  │  │  [only during Week 7]     │ │   │
│  │  └────────────────────────────┘ │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  EBS Volume (130GB)             │   │
│  │  - CyberGym binary data        │   │
│  │  - 100-instance Docker images   │   │
│  │  - Experiment results           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
         │                    │
         ▼                    ▼
  DeepSeek API          Groq API
  (external)            (external)
```

---

## Security Considerations

- CyberGym's firewall module restricts agent containers to allowlisted domains only
- Agents run in isolated Docker containers with no direct internet access
- All outbound traffic goes through a Squid proxy with domain filtering
- API keys stored as environment variables, never committed to git
- `.env` file in `.gitignore`
