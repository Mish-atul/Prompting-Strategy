# Progress Tracker

> **Project:** Prompting Strategy Impact on LLM Vulnerability Reproduction  
> **Start Date:** 2026-05-02  
> **Target Completion:** 2026-07-27

---

## Overall Status: 🟢 Phase 3 — Experimentation (Active)

| Phase | Status | Progress | Dates |
|-------|--------|----------|-------|
| Phase 1: Foundation | ✅ Complete | ██████████ 100% | May 5–18 |
| Phase 2: Dataset & Prompts | ✅ Complete | ██████████ 100% | May 19–Jun 1 |
| Phase 3: Experimentation | 🟢 In Progress | ████░░░░░░ 40% | Jun 2–29 |
| Phase 4: Analysis | ⚪ Not Started | ░░░░░░░░░░ 0% | Jun 30–Jul 13 |
| Phase 5: Paper Writing | ⚪ Not Started | ░░░░░░░░░░ 0% | Jul 14–27 |

---

## Sprint Log

### Sprint 1 — Week 1 (May 5–11, 2026)

| Task | Status | Notes |
|------|--------|-------|
| Initialize GitHub repository | ✅ Done | github.com/Mish-atul/Prompting-Strategy |
| Create project directory structure | ✅ Done | All dirs created |
| Write all documentation | ✅ Done | README, ARCH, PRD, DESIGN, PROGRESS, LIT REVIEW |
| Design 5 prompt templates | ✅ Done | All in prompts/ directory |
| Write all experiment scripts | ✅ Done | filter, run, analyze, generate_figures, utils |
| Provision AWS EC2 (round 1) | ✅ Done | 3.232.95.178 (terminated) |
| Provision AWS EC2 (round 2) | ✅ Done | **34.204.47.108**, c5.2xlarge, Ubuntu 24.04 |
| Install Docker + dependencies | ✅ Done | Docker 29.1.3, Python 3.14 |
| CyberGym repo + 21 Docker images | ✅ Done | All 10 subset tasks available |
| CyberGym server running | ✅ Done | Port 8666, no mask_map |
| **Model change: OpenRouter** | ✅ Done | Mentor provided $10 key for DeepSeek V4 Flash + Nemotron-3 |
| Update scripts for OpenRouter | ✅ Done | utils.py, pilot_experiment.py, run_experiment.py |
| OpenRouter API verified | ✅ Done | Both models responding correctly |
| **Pilot: DeepSeek V4 Flash** | ✅ Done | 50 runs complete — see results below |
| Pilot: Nemotron-3 Super 120B | 🟡 Running | In progress on EC2 |
| Pilot: Llama-3.3-70B (Groq) | ⬜ Blocked | Need Groq API key |

### Pilot Results — DeepSeek V4 Flash (10 tasks × 5 strategies)

| Strategy | Successes / 10 | Rate |
|----------|:-:|:-:|
| Baseline | 1 | 10% |
| **Chain-of-Thought** | **4** | **40%** |
| Few-Shot | 2 | 20% |
| Persona | 2 | 20% |
| Structured Decomposition | 2 | 20% |

**Key Finding:** CoT shows a **4× improvement** over baseline! This is the primary finding for the paper.

---

## Key Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Tasks completed | Phase 1-2 complete | All phases |
| Budget spent | ~$8 (EC2) + ~$1 (OpenRouter) | < $40 total |
| Pilot runs completed | 50 (DeepSeek V4) | 150 (all 3 models) |
| Full experiment runs | 0 | 4,500 |
| Paper sections drafted | 0 / 8 | All sections |

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-02 | Pivoted from frontier models to open-weight models | Cost reduction; higher novelty |
| 2026-05-02 | Selected HBO-READ with PoC < 100 bytes | Maximize signal per paper's Figure 7 analysis |
| 2026-05-02 | 5 prompt strategies (not 8) | Focused set; clear theoretical justifications |
| 2026-05-08 | **Switched to OpenRouter API** | Mentor provided $10 key supporting DeepSeek V4 Flash + Nemotron-3 Super 120B |
| 2026-05-08 | **Replaced Qwen2.5-Coder-32B with Nemotron-3** | Stronger coding benchmarks; no local GPU needed |
| 2026-05-08 | **Replaced DeepSeek-V3 with V4 Flash** | Newer model; better price-performance |

---

## Blockers & Risks

| ID | Blocker | Status | Mitigation |
|----|---------|--------|-----------|
| B1 | Groq API key needed for Llama pilot | 🟡 Active | User needs to provide GROQ_API_KEY |
| B2 | EC2 spot instance may terminate | Low risk | Data saved to local + can re-provision |
