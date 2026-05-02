# Progress Tracker

> **Project:** Prompting Strategy Impact on LLM Vulnerability Reproduction  
> **Start Date:** 2026-05-02  
> **Target Completion:** 2026-07-27

---

## Overall Status: 🟡 Phase 1 — Foundation & Setup

| Phase | Status | Progress | Dates |
|-------|--------|----------|-------|
| Phase 1: Foundation | 🟢 In Progress | ████░░░░░░ 40% | May 5–18 |
| Phase 2: Dataset & Prompts | ⚪ Not Started | ░░░░░░░░░░ 0% | May 19–Jun 1 |
| Phase 3: Experimentation | ⚪ Not Started | ░░░░░░░░░░ 0% | Jun 2–29 |
| Phase 4: Analysis | ⚪ Not Started | ░░░░░░░░░░ 0% | Jun 30–Jul 13 |
| Phase 5: Paper Writing | ⚪ Not Started | ░░░░░░░░░░ 0% | Jul 14–27 |

---

## Sprint Log

### Sprint 1 — Week 1 (May 5–11, 2026)

| Task | Status | Notes |
|------|--------|-------|
| Initialize GitHub repository | ✅ Done | github.com/Mish-atul/Prompting-Strategy |
| Create project directory structure | ✅ Done | All dirs created |
| Write README.md | ✅ Done | Full project overview |
| Create IMPLEMENTATION_PLAN.md | ✅ Done | 12-week phased plan |
| Create ARCHITECTURE.md | ✅ Done | System design & data flow |
| Create PRD.md | ✅ Done | Requirements & success criteria |
| Create DESIGN.md | ✅ Done | Statistical analysis plan |
| Create PROGRESS.md | ✅ Done | This file |
| Create LITERATURE_REVIEW.md | ✅ Done | Related work analysis |
| Design 5 prompt templates | ✅ Done | All in prompts/ directory |
| Write filter_dataset.py | ✅ Done | HBO-READ + PoC size filter |
| Write run_experiment.py | ✅ Done | Batch orchestrator |
| Write analyze_results.py | ✅ Done | Statistical analysis pipeline |
| Write generate_figures.py | ✅ Done | Visualization scripts |
| Write utils.py | ✅ Done | Model backends & helpers |
| Create .gitignore | ✅ Done | |
| Create requirements.txt | ✅ Done | |
| Set up API keys | ⬜ TODO | DeepSeek, Groq |
| Initial git commit & push | ⬜ TODO | |

### Sprint 2 — Week 2 (May 12–18, 2026)

| Task | Status | Notes |
|------|--------|-------|
| Provision AWS EC2 | ⬜ TODO | c5.2xlarge spot instance |
| Install CyberGym on EC2 | ⬜ TODO | |
| Download CyberGym dataset | ⬜ TODO | Binary-only mode, ~130GB |
| Install Ollama on EC2 | ⬜ TODO | For Qwen2.5-Coder-32B |
| Verify DeepSeek API | ⬜ TODO | |
| Verify Groq API | ⬜ TODO | |
| Run hello-world task | ⬜ TODO | 1 task, 1 model, end-to-end |

---

## Key Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Tasks completed | 0 / ~35 | All Phase 1 tasks |
| Budget spent | $0 | < $300 |
| Experiment runs completed | 0 | 4,500 |
| Paper sections drafted | 0 / 8 | All sections |
| Days elapsed | 0 | 84 (12 weeks) |

---

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-02 | Pivoted from frontier models to open-weight models | Cost reduction ($200 vs $5,000+); higher novelty |
| 2026-05-02 | Selected HBO-READ with PoC < 100 bytes | Maximize signal per paper's Figure 7 analysis |
| 2026-05-02 | 5 prompt strategies (not 8) | Focused set; each technique has clear theoretical justification |
| 2026-05-02 | 3 repetitions per condition | Balance between statistical rigor and budget |
| 2026-05-02 | McNemar's test as primary statistic | Appropriate for paired binary outcomes on same instances |

---

## Blockers & Risks

| ID | Blocker | Status | Mitigation |
|----|---------|--------|-----------|
| — | None currently | — | — |
