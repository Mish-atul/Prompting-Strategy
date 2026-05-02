# Prompt Design Rationale

> **Last Updated:** 2026-05-02

## Design Philosophy

Each prompt strategy targets a specific cognitive failure mode observed in LLM vulnerability reproduction. The strategies are **orthogonal** — each addresses a different aspect of the task.

## Strategy Comparison

| Strategy | Target Failure Mode | Word Count | Key Mechanism |
|----------|-------------------|------------|---------------|
| Baseline | (control) | 43 | Simple instruction |
| Chain-of-Thought | Skipping reasoning, jumping to random PoC | ~150 | Explicit reasoning steps |
| Few-Shot | Not knowing what a successful analysis looks like | ~350 | 2 solved examples |
| Persona | Lack of domain focus, generic approach | ~180 | Expert identity priming |
| Structured Decomposition | Skipping critical sub-tasks | ~250 | Sequential sub-task checklist |

## Design Constraints

1. **No information leakage:** Prompts never reveal vulnerability-specific details beyond what Level 1 provides
2. **Same task instructions:** All prompts include the submit command and stop condition
3. **Model-agnostic:** Prompts don't reference specific model capabilities
4. **Concise:** Prompts are kept as short as possible while implementing the technique

## Theoretical Justification

### Why Chain-of-Thought Should Help
Vulnerability reproduction requires multi-step reasoning:
1. Parse vulnerability description → 2. Locate vulnerable code → 3. Understand memory layout → 4. Craft trigger input

The baseline prompt collapses all of this into "generate the exploit." CoT forces the model to externalize each step, reducing the chance of skipping critical analysis.

### Why Few-Shot Should Help
LLMs perform better when shown the expected output format and reasoning process. By providing 2 solved HBO-READ examples, we teach:
- What a good analysis looks like
- What format the PoC should take
- How to reason about memory layouts

### Why Persona Should Help
Role prompting activates domain-specific knowledge. A "vulnerability researcher" persona should:
- Increase precision (every byte deliberate vs. random input)
- Reduce generic responses
- Encourage systematic methodology

### Why Structured Decomposition Should Help
Forces explicit completion of each sub-task before moving on:
- Prevents the model from skipping code analysis
- Ensures input format is identified before PoC construction
- Creates natural checkpoints for the agent to verify progress
