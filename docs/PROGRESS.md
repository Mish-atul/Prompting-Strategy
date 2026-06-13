# Progress Tracker

## Experiment Status

### Phase 1: Setup ✅
- [x] CyberGym dataset downloaded from HuggingFace
- [x] 50 HBO tasks filtered and validated
- [x] 100 Docker images downloaded (vul + fix for each task)
- [x] EC2 instance provisioned (c5.2xlarge, 1.2TB)
- [x] CyberGym server running on localhost:8666
- [x] All 5 prompt templates designed and validated

### Phase 2: Model Runs

| Model | Runs | Status | Date | Cost |
|-------|:----:|--------|------|:----:|
| DeepSeek V4 Flash | 750/750 | ✅ Complete | Jun 2-3, 2026 | $3.19 |
| Nemotron-3 Super 120B | 750/750 | ✅ Complete | Jun 3, 2026 | $1.06 |
| Llama-3.3-70B (Groq) | 152/750 | ❌ Failed (79.7% rate-limited) | Jun 3, 2026 | $0.00 |
| Llama-3.3-70B (OpenRouter) | 0/750 | 🔄 Running | Jun 13, 2026 | ~$0.50 |
| Nemotron-3 Ultra 550B | 0/750 | ⏳ Queued | Jun 13, 2026 | ~$3.86 |

### Phase 3: Analysis
- [x] Verified DeepSeek results (750/750 valid)
- [x] Verified Nemotron-3 Super results (750/750 valid)
- [x] Pilot analysis completed (10 tasks, DeepSeek only)
- [ ] Full statistical analysis (after all 4 models complete)
- [ ] Figure generation for paper

### Phase 4: Paper
- [x] IEEE Access template initialized
- [x] Abstract, Introduction, Related Work written
- [x] Methodology section complete
- [x] Experimental Setup section complete
- [x] Results section written (2-model data)
- [x] Discussion and Conclusion drafted
- [x] All 6 authors added
- [ ] Update results with Llama + Nemotron Ultra data
- [ ] Final figures generated and embedded
- [ ] Submission

## Timeline

| Date | Event |
|------|-------|
| Jun 1 | Project kickoff, setup |
| Jun 2-3 | DeepSeek + Nemotron Super runs complete |
| Jun 3 | Llama run failed (Groq rate limits) |
| Jun 3 | Paper draft (methodology + 2-model results) |
| Jun 13 | Llama re-run (OpenRouter) + Nemotron Ultra started |
| Jun 14 (est.) | All runs complete |
| Jun 15 (est.) | Final analysis + paper update |

## Budget

| Item | Spent | Remaining |
|------|:-----:|:---------:|
| OpenRouter credits | $4.25 | $3.62 |
| AWS EC2 | ~$24 | Varies |
