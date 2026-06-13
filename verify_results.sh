#!/bin/bash
echo "=============================================="
echo "FULL EXPERIMENT VERIFICATION"
echo "Date: $(date)"
echo "=============================================="

echo ""
echo "=== 1. PROCESS STATUS ==="
if pgrep -f "run_full_experiment" > /dev/null 2>&1; then
    echo "STATUS: EXPERIMENT STILL RUNNING"
    ps aux | grep run_full_experiment | grep -v grep
else
    echo "STATUS: EXPERIMENT COMPLETE (no running processes)"
fi

echo ""
echo "=== 2. RESULT FILES ==="
ls -lh /home/ubuntu/Prompting-Strategy/data/results/*.json 2>/dev/null

echo ""
echo "=== 3. MASTER LOG (last 30 lines) ==="
tail -30 /home/ubuntu/master_run_v2_log.txt 2>/dev/null

echo ""
echo "=== 4. FULL RESULT VALIDATION ==="
python3 << 'PYEOF'
import json, os, sys
from collections import Counter

rdir = "/home/ubuntu/Prompting-Strategy/data/results"
models_expected = ["deepseek-v4-flash", "llama-3.3-70b", "nemotron-3-super-120b"]
strategies_expected = ["baseline", "chain_of_thought", "few_shot", "persona", "structured_decomposition"]

total_issues = 0

for model in models_expected:
    fname = f"results_{model}.json"
    fpath = os.path.join(rdir, fname)
    
    if not os.path.exists(fpath):
        print(f"\n❌ MISSING: {fname}")
        total_issues += 1
        continue
    
    with open(fpath) as f:
        d = json.load(f)
    
    m = d["metadata"]
    results = d["results"]
    
    print(f"\n{'='*50}")
    print(f"MODEL: {m['model']}")
    print(f"{'='*50}")
    print(f"  Completed: {m['completed_runs']}/{m['total_runs']}")
    print(f"  Cost: ${m['total_cost_usd']:.4f}")
    
    # Check completeness
    if m['completed_runs'] != m['total_runs']:
        print(f"  ❌ INCOMPLETE: {m['total_runs'] - m['completed_runs']} runs missing")
        total_issues += 1
    else:
        print(f"  ✅ All runs complete")
    
    # Verify result count matches
    if len(results) != m['completed_runs']:
        print(f"  ❌ MISMATCH: metadata says {m['completed_runs']} but {len(results)} results in array")
        total_issues += 1
    
    # Check strategy distribution
    strat_counts = Counter(r['strategy'] for r in results)
    print(f"  Strategy distribution:")
    for s in strategies_expected:
        count = strat_counts.get(s, 0)
        expected = 150  # 50 tasks * 3 reps
        status = "✅" if count == expected else "❌"
        print(f"    {status} {s:30s}: {count}/{expected}")
        if count != expected:
            total_issues += 1
    
    # Check task coverage
    tasks = set(r['task_id'] for r in results)
    print(f"  Tasks covered: {len(tasks)}")
    if len(tasks) != 50:
        print(f"  ❌ Expected 50 tasks, got {len(tasks)}")
        total_issues += 1
    else:
        print(f"  ✅ All 50 tasks covered")
    
    # Check repetition coverage
    rep_counts = Counter(r['repetition'] for r in results)
    print(f"  Repetitions: {dict(rep_counts)}")
    
    # Check exit code distribution
    exits = Counter(r.get('exit_code') for r in results)
    print(f"  Exit codes: {dict(exits)}")
    
    successes = sum(1 for r in results if r.get('exit_code') is not None and r['exit_code'] != 0)
    print(f"  Successes (exit_code != 0): {successes}/{len(results)} = {100*successes/len(results):.1f}%")
    
    # Check for errors
    errors = [r for r in results if r.get('error')]
    if errors:
        print(f"  ⚠️ {len(errors)} runs had errors:")
        for e in errors[:5]:
            print(f"    - {e['task_id']} | {e['strategy']} | {e.get('error','')[:80]}")
    
    # Check for None exit codes
    none_exits = [r for r in results if r.get('exit_code') is None]
    if none_exits:
        print(f"  ⚠️ {len(none_exits)} runs had exit_code=None:")
        for r in none_exits[:5]:
            print(f"    - {r['task_id']} | {r['strategy']} | rep{r['repetition']}")
    
    # Summary per strategy
    print(f"\n  Success rates (any-of-3 per task):")
    for s in strategies_expected:
        strat_results = [r for r in results if r['strategy'] == s]
        # Group by task
        task_results = {}
        for r in strat_results:
            tid = r['task_id']
            if tid not in task_results:
                task_results[tid] = []
            task_results[tid].append(r.get('exit_code', 0) != 0 and r.get('exit_code') is not None)
        
        any_success = sum(1 for outcomes in task_results.values() if any(outcomes))
        total_tasks = len(task_results)
        rate = 100 * any_success / total_tasks if total_tasks > 0 else 0
        print(f"    {s:30s}: {any_success}/{total_tasks} = {rate:.1f}%")

print(f"\n{'='*50}")
print(f"OVERALL VERIFICATION")
print(f"{'='*50}")
if total_issues == 0:
    print(f"✅ ALL CHECKS PASSED — 0 issues found")
else:
    print(f"❌ {total_issues} ISSUES FOUND — review above")

# Total cost
total_cost = 0
for model in models_expected:
    fpath = os.path.join(rdir, f"results_{model}.json")
    if os.path.exists(fpath):
        with open(fpath) as f:
            d = json.load(f)
        total_cost += d["metadata"]["total_cost_usd"]
print(f"\nTotal API cost: ${total_cost:.4f}")
print(f"Total runs: {sum(json.load(open(os.path.join(rdir, f'results_{m}.json')))['metadata']['completed_runs'] for m in models_expected if os.path.exists(os.path.join(rdir, f'results_{m}.json')))}")
PYEOF

echo ""
echo "=== 5. SERVER STATUS ==="
curl -s http://localhost:8666/docs > /dev/null 2>&1 && echo "Server: OK" || echo "Server: DOWN"

echo ""
echo "VERIFICATION COMPLETE: $(date)"
