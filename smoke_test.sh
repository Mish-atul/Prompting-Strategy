#!/bin/bash
set -e

export OPENROUTER_API_KEY="${OPENROUTER_API_KEY:?Set OPENROUTER_API_KEY}"
export GROQ_API_KEY="${GROQ_API_KEY:?Set GROQ_API_KEY}"
export PATH=$HOME/.local/bin:$PATH

echo "=========================================="
echo "END-TO-END SMOKE TEST"
echo "=========================================="

# Verify server is running (we already restarted it without mask_map)
echo "Checking server..."
if curl -s http://localhost:8666/docs > /dev/null 2>&1; then
    echo "Server is running OK"
else
    echo "Server not running! Starting..."
    cd /home/ubuntu/cybergym
    pkill -f "cybergym.server" 2>/dev/null || true
    sleep 2
    nohup python3 -m cybergym.server --port=8666 --host 0.0.0.0 > /home/ubuntu/server_log_v2.txt 2>&1 &
    sleep 5
    if curl -s http://localhost:8666/docs > /dev/null 2>&1; then
        echo "Server started OK"
    else
        echo "FATAL: Server won't start"
        exit 1
    fi
fi

# Run a quick 1-task, 1-strategy, 1-rep test with DeepSeek
echo ""
echo "=== Running smoke test: 1 task x 1 strategy x 1 rep ==="
cd /home/ubuntu/Prompting-Strategy

# Create a mini task subset with just 1 task
python3 << 'PYEOF'
import json
with open("data/task_subset.json") as f:
    d = json.load(f)
tasks = d.get("tasks", d) if isinstance(d, dict) else d
mini = [tasks[0]]
with open("/tmp/mini_subset.json", "w") as f:
    json.dump(mini, f, indent=2)
print(f"Created mini subset with task: {mini[0]['task_id']}")
print(f"Vulnerability: {mini[0].get('vulnerability_description', 'MISSING')[:100]}")
PYEOF

# Run the fixed experiment with just 1 task
python3 scripts/run_full_experiment.py \
    --model deepseek-v4-flash \
    --strategies baseline \
    --reps 1 \
    --tasks-file /tmp/mini_subset.json \
    --output-dir /tmp/smoke_test_results \
    --delay 1.0 \
    2>&1

echo ""
echo "=== SMOKE TEST RESULTS ==="
python3 << 'PYEOF'
import json
with open("/tmp/smoke_test_results/results_deepseek-v4-flash.json") as f:
    d = json.load(f)
print(f"Metadata: {json.dumps(d['metadata'], indent=2)}")
print(f"Summary: {json.dumps(d['summary'], indent=2)}")
r = d["results"][0]
print(f"\nFirst result:")
print(f"  task_id: {r['task_id']}")
print(f"  strategy: {r['strategy']}")
print(f"  success: {r['success']}")
print(f"  exit_code: {r['exit_code']}")
print(f"  poc_size: {r['poc_size']}")
print(f"  tokens: {r['tokens']}")
print(f"  tokens_input: {r['tokens_input']}")
print(f"  runtime: {r['runtime']}")
print(f"  server_response: {json.dumps(r['server_response'])[:200]}")
print(f"  llm_response_preview: {r['llm_response_preview'][:200]}")

# Key checks
if r['exit_code'] is not None:
    print(f"\n>>> exit_code is {r['exit_code']} — SERVER ACTUALLY RAN THE POC <<<")
    if r['exit_code'] != 0:
        print(f">>> THE POC CRASHED THE BINARY! SUCCESS! <<<")
    else:
        print(f">>> PoC didn't crash (expected for generic prompt + 1 attempt) <<<")
else:
    print(f"\n>>> exit_code is None — SOMETHING IS WRONG <<<")
    print(f">>> server_response: {r['server_response']} <<<")

if r['tokens_input'] > 300:
    print(f">>> tokens_input={r['tokens_input']} — LLM received vulnerability context! <<<")
else:
    print(f">>> WARNING: tokens_input={r['tokens_input']} — context may be too short <<<")
PYEOF

echo ""
echo "=========================================="
echo "SMOKE TEST COMPLETE"
echo "=========================================="
