#!/bin/bash
echo "=== LATEST LOG ==="
tail -25 /home/ubuntu/exp_deepseek_v2.log 2>/dev/null

echo ""
echo "=== RESULT FILES ==="
ls -lh /home/ubuntu/Prompting-Strategy/data/results/

echo ""
echo "=== RESULT SUMMARY ==="
python3 << 'PYEOF'
import json, os

rdir = "/home/ubuntu/Prompting-Strategy/data/results"
for fname in sorted(os.listdir(rdir)):
    if fname.endswith(".json") and fname.startswith("results_"):
        fpath = os.path.join(rdir, fname)
        with open(fpath) as f:
            d = json.load(f)
        m = d["metadata"]
        print(f"\n{m['model']} ({m['completed_runs']}/{m['total_runs']} runs, ${m['total_cost_usd']:.4f}):")
        for k, v in d["summary"].items():
            print(f"  {k:30s}: {v['successes']}/{v['total']} = {v['rate']:.1f}%")
        
        # Show last few results
        results = d["results"]
        if results:
            last = results[-1]
            print(f"  Last run: {last['task_id']} | {last['strategy']} | exit={last['exit_code']} | {last['poc_size']}B")
            print(f"  Last timestamp: {last['timestamp']}")
            # Count exit_code types
            exits = {}
            for r in results:
                ec = r.get("exit_code")
                exits[ec] = exits.get(ec, 0) + 1
            print(f"  Exit code distribution: {exits}")
PYEOF

echo ""
echo "=== PROCESS STATUS ==="
ps aux | grep -E 'master_run|run_full_experiment' | grep -v grep

echo ""
echo "=== SERVER STATUS ==="
curl -s http://localhost:8666/docs > /dev/null 2>&1 && echo "Server OK" || echo "Server DOWN"

echo ""
echo "=== DISK SPACE ==="
df -h / | tail -1
