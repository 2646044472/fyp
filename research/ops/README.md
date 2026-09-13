# Research Operations

This directory separates creative candidate generation from adversarial validation so a main Codex agent can launch two subagents concurrently without overwriting one another or converging on the same convenient story.

## Launch protocol

Open one Codex CLI session at the project root and paste [MASTER-GOAL-PROMPT.md](MASTER-GOAL-PROMPT.md). The main agent launches the divergence and validation roles in parallel, then returns their evidence, conflicts, and the next gate directly in chat.

Interrupt the main agent whenever you need to change scope, provide constraints, or ask a question. It must cancel or redirect unfinished subagent work and continue from the newest instruction.

## Research loop

1. The coordinator sets one concrete current goal.
2. It launches the divergence and validation subagents in parallel.
3. It checks both handoffs, reports candidate states and evidence conflicts, and asks only a blocking high-value question.
4. You may interrupt, narrow, redirect, or start another round.
5. Only after you choose a direction does the coordinator update canonical files and prepare the novelty/feasibility gates.

## File naming

Use YYYY-MM-DD-short-topic.md, for example 2026-08-28-no-wake-audit.md. One run writes one new file. Do not append to a shared progress file.
