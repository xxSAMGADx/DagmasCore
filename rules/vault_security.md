# DAGMAS Brain Vault Global Agent Standards

## 1. Sovereign Vault Sandbox
- All memory ledgers (`DO.md`, `DONT.md`), squad rosters, and token stores MUST reside inside `~/.brain-vault` with strict `0700` (`drwx------`) filesystem permissions.

## 2. Mandatory Privacy Sanitization
- Prior to transmitting any text, prompt, stack trace, or environment payload to external cloud models, scrub all 14 credential classes (AWS, Stripe, Slack, database DSNs, private keys, system home paths) using `PrivacySanitizer`.

## 3. Local-First Small Model Inference (llama.cpp)
- Route routine planning, intent classification, and tool dispatching locally through `llama-server` on `http://127.0.0.1:8080/v1` (Qwen 2.5 1.5B, Llama 3.2 1B, IBM Granite 3B) with Apple Silicon Metal acceleration ($0.00 fees, <2 GB RAM).
- Reserve cloud models strictly for complex multi-repo synthesis or external APIs.

## 4. Architectural Verification Gate & ADHD Skill Skeptor
- Require deterministic, reproducible `prove-it-done` commands with `exit 0` verification for every software change.
- Enforce the **ADHD Skill Skeptor**: single-task hyperfocus lock preventing distraction drift, coupled with Spector.js 60 FPS WebGL/WebGPU graphics profiling (<= 150 draw calls, zero shader thrashing).

## 5. Quantum Vector DB & Automated Output Graphification
- Every task output, artifact, or generated asset MUST be automatically graphified into `~/.brain-vault/code_graph.json` as connected nodes/edges and vector-indexed into the local Quantum Vector DB (Qdrant on port 6333 / SQLite-vec).

## 6. Bilingual Token Optimization Protocol
- All inter-agent communications, swarm packets, subagent prompts, and task reports MUST be strictly formulated in **Simplified Chinese** to maximize information density and cut context token usage by ~70%.
- All direct user interactions, explanations, and artifacts MUST be formulated in **English**.

## 7. Asymmetric Nostr Ed25519 Cryptographic Mesh
- Inter-agent messaging between squads MUST use peer-to-peer asymmetric public/private key encryption with signed envelopes (Jack Dorsey / Nostr / Bitchat / Nostr style) to guarantee zero plaintext leakage on local buses or sockets.
