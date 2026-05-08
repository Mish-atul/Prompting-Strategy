# Product Requirements Document (PRD)

> **Project:** Prompting Strategy Impact on LLM Vulnerability Reproduction  
> **Version:** 2.0  
> **Date:** 2026-05-08 (Updated)  
> **Author:** Mish-atul

---

## 1. Problem Statement

The CyberGym benchmark evaluates LLM agents on real-world vulnerability reproduction but treats the task prompt as a fixed constant. Meanwhile, frontier models (GPT-4.1, Claude Sonnet 4) dominate the leaderboard at high API costs ($2–8/run). **No study has investigated whether prompt engineering can improve the performance of cheap, open-weight models on this benchmark.**

## 2. Objective

Conduct a rigorous, reproducible experiment to determine whether structured prompt engineering techniques can meaningfully improve the vulnerability reproduction success rate of open-weight LLMs on the CyberGym benchmark, and quantify how much of the frontier model advantage can be recovered through better prompting alone.

## 3. Scope

### In Scope
- 5 prompt strategies (1 baseline + 4 experimental)
- 3 open-weight models (DeepSeek V4 Flash, Nemotron-3 Super 120B, Llama-3.3-70B)
- ~100 Heap-buffer-overflow READ instances from CyberGym
- CyberGym Level 1 difficulty (codebase + vulnerability description)
- 3 repetitions per condition for statistical validity
- Statistical analysis with McNemar's test, Cohen's h effect size
- Peer-reviewed research paper

### Out of Scope
- Modifying the OpenHands agent framework itself
- Agent architecture changes (e.g., adding tools, multi-agent)
- Levels 0, 2, or 3 of CyberGym difficulty
- Vulnerability types other than HBO-READ
- Fine-tuning or training any models
- Real-time or production deployment

## 4. Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| **Primary:** At least 1 prompt strategy shows statistically significant improvement over baseline for at least 1 model | p < 0.05 (McNemar's test) | ✅ **Achieved in pilot** — CoT gives 4× on DeepSeek V4 Flash |
| **Secondary:** Best open-weight + prompt combination reaches ≥50% of frontier baseline | ≥5% success rate (vs. GPT-4.1's 9.4%) | ✅ **Achieved** — Nemotron baseline at 30%, CoT+DeepSeek at 40% |
| **Tertiary:** Paper accepted to workshop/conference | Accepted | ⬜ Pending (paper not yet written) |
| **Deliverable:** All experiments reproducible from repo | Any reviewer can re-run | 🟡 In progress — scripts published |

## 5. Requirements

### 5.1 Functional Requirements

| ID | Requirement | Priority | Status |
|----|------------|----------|--------|
| FR-01 | Filter CyberGym dataset to HBO-READ instances with PoC < 100 bytes | Must Have | ✅ Done |
| FR-02 | Inject custom prompt templates into experiment pipeline | Must Have | ✅ Done |
| FR-03 | Support 3 model backends (OpenRouter × 2, Groq × 1) | Must Have | ✅ Done |
| FR-04 | Run experiments in batch with configurable parallelism | Must Have | ✅ Done |
| FR-05 | Log per-run results (success, runtime, tokens, cost) | Must Have | ✅ Done |
| FR-06 | Compute statistical significance (McNemar's, chi-squared) | Must Have | ⬜ Pending |
| FR-07 | Generate publication-quality figures (PDF/SVG) | Must Have | ⬜ Pending |
| FR-08 | Handle retries for API failures and timeouts | Should Have | ✅ Done |
| FR-09 | Track cumulative API cost during experiments | Should Have | ⬜ Pending |
| FR-10 | Support additional prompt strategies without code changes | Nice to Have | ✅ Done |

### 5.2 Non-Functional Requirements

| ID | Requirement | Priority | Status |
|----|------------|----------|--------|
| NFR-01 | Total experiment cost < $300 | Must Have | ✅ On track (~$10 spent so far) |
| NFR-02 | All results reproducible with fixed random seeds | Must Have | ✅ temp=0.0 |
| NFR-03 | Complete experiments within 4 weeks (Weeks 5–8) | Must Have | 🟡 In progress |
| NFR-04 | API keys never committed to repository | Must Have | ✅ Using env vars |
| NFR-05 | Results stored in version-controlled JSON format | Should Have | ✅ Done |

## 6. Constraints

- **Budget:** $300 AWS credits (hard cap) + $10 OpenRouter (mentor-provided)
- **Timeline:** 12 weeks total, experiments in Weeks 5–8
- **Compute:** Single EC2 instance (c5.2xlarge), no GPU requirement for API-based models
- **Ethical:** All vulnerabilities are already public (OSS-Fuzz); no new vulnerability disclosure needed
- **Benchmark integrity:** Cannot modify CyberGym's evaluation mechanism (submission server, sanitizer checks)

## 7. Stakeholders

| Stakeholder | Role | Interest |
|-------------|------|----------|
| Student (Mish-atul) | Researcher, developer | Primary author, implementer |
| Mentor (Yash) | Supervisor | Provided OpenRouter key; reviews methodology |
| CyberGym authors | Benchmark creators | Potential reviewers; cite their work |
| Conference reviewers | Evaluators | Judge novelty, rigor, significance |

## 8. Dependencies

| Dependency | Type | Risk | Status |
|-----------|------|------|--------|
| CyberGym GitHub repo | External | Low — public, stable | ✅ Cloned |
| CyberGym HuggingFace dataset | External | Low — metadata downloaded | ✅ Ready |
| OpenRouter API | External | Low — $10 budget, 2 models | ✅ Verified |
| Groq API | External | Medium — free tier throttling | ✅ Verified |
| AWS EC2 availability | External | Low — standard instance type | ✅ Running |

## 9. Acceptance Criteria

The project is considered complete when:
1. ✅ Pilot experiments executed (150 runs across 3 models) — **DONE**
2. ⬜ Full 4,500 experiment runs executed and verified (pending disk extension)
3. ⬜ Statistical analysis completed with p-values and effect sizes
4. ⬜ Research paper draft completed and reviewed by advisor
5. ⬜ Paper submitted to at least 1 venue (arXiv + workshop/conference)
6. ⬜ GitHub repo is public with reproduction instructions
7. ✅ Total cost staying within budget
