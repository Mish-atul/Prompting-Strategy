#!/bin/bash
# master_run_v3.sh - Run Llama-3.3-70B + Nemotron-3 Ultra via OpenRouter (paid)
# Budget: $7.98 remaining. Llama=$0.50, Ultra=$3.86 → Total=$4.36, Remaining=$3.62

set -e
export OPENROUTER_API_KEY="${OPENROUTER_API_KEY:?Set OPENROUTER_API_KEY}"

cd /home/ubuntu/Prompting-Strategy

echo "=============================================="
echo "MASTER RUN V3 - $(date)"
echo "Models: Llama-3.3-70B ($0.50), Nemotron-3 Ultra ($3.86)"
echo "Total estimated cost: $4.36"
echo "=============================================="

# Delete old broken Llama results
echo ""
echo "=== REMOVING OLD BROKEN LLAMA RESULTS ==="
rm -f data/results/results_llama-3.3-70b.json
echo "Deleted"

# Verify server
echo ""
echo "=== SERVER CHECK ==="
if curl -s http://localhost:8666/ > /dev/null 2>&1; then
    echo "CyberGym Server: UP"
else
    echo "CyberGym Server: DOWN - restarting..."
    bash /home/ubuntu/restart_server.sh
    sleep 5
fi

# 1. Llama-3.3-70B (cheapest, run first)
echo ""
echo "=== [1/2] LLAMA-3.3-70B via OpenRouter ==="
echo "Estimated cost: ~$0.50 | Estimated time: ~6-8 hours"
echo "Started: $(date)"
python3 scripts/run_full_experiment.py --model llama-3.3-70b --strategies all --reps 3 --delay 2.0
echo "Llama-3.3-70B COMPLETE: $(date)"

# 2. Nemotron-3 Ultra 550B (largest model, best chance of high results)
echo ""
echo "=== [2/2] NEMOTRON-3 ULTRA 550B via OpenRouter ==="
echo "Estimated cost: ~$3.86 | Estimated time: ~10-14 hours"
echo "Started: $(date)"
python3 scripts/run_full_experiment.py --model nemotron-3-ultra --strategies all --reps 3 --delay 2.0
echo "Nemotron Ultra COMPLETE: $(date)"

echo ""
echo "=============================================="
echo "ALL RUNS COMPLETE - $(date)"
echo "=============================================="

# Summary
echo ""
ls -lh data/results/*.json
python3 << 'PYEOF'
import json, os
rdir = "data/results"
for f in sorted(os.listdir(rdir)):
    if f.endswith('.json'):
        d = json.load(open(os.path.join(rdir, f)))
        m = d["metadata"]
        print(f"\n{m['model']} ({m['completed_runs']}/{m['total_runs']}, ${m['total_cost_usd']:.4f}):")
        for k, v in d["summary"].items():
            print(f"  {k:30s}: {v['successes']}/{v['total']} = {v['rate']:.1f}%")
PYEOF
