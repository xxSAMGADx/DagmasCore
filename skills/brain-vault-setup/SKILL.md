---
name: brain-vault-setup
description: >-
  System initialization and upgrade skill for DAGMAS Brain Vault.
  Invoked strictly at system initialization or system upgrade to configure,
  provision, test, and verify the sovereign local vault.
---

# DAGMAS Brain Vault Sovereign Master Skill

> [!NOTE]
> **Initialization & Upgrade Scope**:
> This Master Skill is designed to be used **strictly at system initialization or when performing a system upgrade to this system**. It does not run continuously on every turn.
> When invoked, the skill conducts a concise architectural interview to discover what you want to install and configure. You can execute the steps manually, or if your agent has computer use / terminal execution capabilities, the agent executes the entire pipeline automatically.
> Once the system is confirmed running and the full preflight passes smoothly with exit code 0, the agent executes an end-to-end live test, and finally asks you if you wish to set Brain Vault as your permanent default memory and universal backup system.

## Download & Triggering

### Step 1: Download the Master Skill File
If not already in your agent's skills catalog, download this file to your config directory:
```bash
mkdir -p ~/.agents/skills/brain-vault-setup
curl -sSL https://raw.githubusercontent.com/xxSAMGADx/DagmasCore/main/skills/brain-vault-setup/SKILL.md -o ~/.agents/skills/brain-vault-setup/SKILL.md
```

### Step 2: Trigger in Any Agent Session
Trigger it directly in your assistant prompt:
> *"Set up Brain Vault and grill me on my architecture choices."*

---

## 0. Strict Agent Execution Rules & Anti-Improvisation Directives

> [!CAUTION]
> **MANDATORY ANTI-DRIFT DIRECTIVE FOR ALL AGENTS**:
> Agents MUST NOT invent alternative procedures, guess configurations, install unrequested packages, or take unilateral actions they "think are good".
> The agent MUST follow the deterministic sequential setup pipeline in exact order:
> **External Tools Setup First (e.g. Qdrant) -> Brain Core Initialization -> Link Orchestrator Profile & Squads -> Preflight Verification (`exit 0`)**.
> Inverting, combining, or skipping steps is strictly forbidden.

### The 5 Strict Laws of Setup & Execution:

1. **Law 1: Zero Unauthorized Initiative ("Never Do What You Think Is Good")**:
   - The assistant MUST never run commands, create arbitrary files, or alter system state based on assumptions or personal judgment.
   - The assistant MUST strictly guide the user through the architectural questionnaire and execute ONLY the chosen tools and configurations.
2. **Law 2: Explicit Execution Mode Agreement Gate (Manual vs. Automatic)**:
   - The assistant MUST explicitly ask the user whether they choose **Mode A: Automated Execution** (assistant runs terminal commands) or **Mode B: Manual Step-by-Step** (assistant outputs exact terminal commands for the user to paste).
   - The assistant is STRICTLY FORBIDDEN from running any shell command until the user explicitly approves Mode A.
3. **Law 3: Mandatory External Tools Setup Gate (Dependency Gate)**:
   - **External tools MUST be installed and verified running BEFORE touching the Brain**.
   - If the user selected **Qdrant**: Qdrant MUST be verified active and listening on `http://localhost:6333/healthz` (via Docker `docker run -d -p 6333:6333 qdrant/qdrant` or native binary) with HTTP 200 before proceeding.
   - If the user selected **llama.cpp / Needle**: The inference runner or binary must be verified installed and responsive on `http://127.0.0.1:8080/v1` before proceeding.
   - If the user selected **Bitwarden CLI**: The `bw` CLI binary must be verified installed.
   - If the user selected **Bun**: The `bun` runtime must be verified installed (`which bun || curl -fsSL https://bun.sh/install | bash`).
   - If the user selected **Rust**: The `cargo` toolchain must be verified present.
   - If the user selected **Python**: `python3` (3.9+) must be verified present.
   - **HARD BLOCK**: The assistant is STRICTLY PROHIBITED from creating `~/.brain-vault`, writing configurations, or touching ledgers until ALL chosen external tools are verified healthy and active.
4. **Law 4: Sovereign Brain Core Initialization**:
   - Only AFTER all external tools pass verification:
     1. Create the `0700` sandbox at `~/.brain-vault` with subdirectories `teams/`, `skills/`, `memory/`, `ledgers/`.
     2. Write canonical configurations: `vault_config.json`, `limits.json`, `registry.json`, `code_graph.json`.
     3. Write living ledgers: `DO.md`, `DONT.md`, `LESSONS.md`.
5. **Law 5: Link Orchestrator Profile, Squads & Skills**:
   - Only AFTER the Brain Core is initialized:
     1. Provision tailored `SOUL.md` and `*.json` squad profiles into `~/.brain-vault/teams/`.
     2. Link and register specialist skills into `~/.brain-vault/skills/`.
     3. If approved in Phase 12: link/install `dagmas_brain_vault.md` into global agent rules (`~/.agents/rules/dagmas_brain_vault.md`).
6. **Law 6: Deterministic Preflight Diagnostics & Verification Gate**:
   - Setup is NOT complete until `python3 -m src.preflight` executes, evaluates all 8 diagnostic checks, auto-heals any degraded state, and outputs a 100% green `[PASS]` report with exit code 0 (`prove-it-done`).

---

## 1. The Autonomous Cognitive Pipeline (The 10 Infographic Stages)

Every Brain Vault implements the complete 10-stage cognitive architecture:
1. **Stage 1: Preflight Check & ADHD Skill Skeptor** - `qdrant_guard` & health checks on `localhost:6333`, embedder cache verification, environment sanity, combined with **ADHD Skill Skeptor (Spector)** for hyper-focus single-task locking and 60 FPS WebGL/WebGPU GPU draw call profiling.
2. **Stage 2: Sparse Activation Brain** - Biological 20W model; out of 718 tracked nodes, only awakens the 2-3 pathways needed for the task (<= 5.5 GB RAM ceiling).
3. **Stage 3: Sub-1B Reasoning Models + Embedded Tools & Needle 3** - Sub-1B edge reasoning models (Needle 3 at 121M, Qwen 2.5 0.5B at 490M, SmolLM2 360M) taking < 400 MB RAM, coupled with open-weights Llama 3.2 / Gemma 2 for typed function calling and vector embeddings on Apple Silicon Metal (< 1.5 GB VRAM).
4. **Stage 4: Privacy Sanitizers & Secret Scrubbers** - Intercepts 14 credential classes (AWS, Stripe, Slack, DSNs, keys) + custom tokens, and defangs prompt injections before cloud transmission.
5. **Stage 5: Competitive Subsidiary Squads** - 33 autonomous business entities competing under meritocracy with individualized `SOUL.md` DOs and DONTs.
6. **Stage 6: Automations & Autolearning Layer** - Background LaunchDaemons (`launchd`), scheduled cron jobs, and health monitors that audit daily agent execution logs to harvest mistakes, refine heuristics, and ensure the system improves every single day.
7. **Stage 7: Cloud Models + DAGMAS Runtime** - Frontier Cloud subloops (Claude / OpenAI) for heavy multi-repo synthesis with zero secret leakage.
8. **Stage 8: Multi-Agent Swarm, Nostr Cryptographic Mesh & Bilingual Protocol**:
   - **Nostr-Style Asymmetric Encryption Mesh**: Peer-to-peer inter-agent messaging encrypted with Ed25519 public/private keys and signed envelopes (inspired by fiatjaf's Nostr NIP-44 protocol), ensuring zero plaintext leakage on local buses or sockets.
   - **Bilingual Token Engine**: Inter-agent communications are strictly formatted in **Simplified Chinese** for ~70% token/context compression, while all direct user interactions remain strictly in **English**.
9. **Stage 9: Security & Architecture Gates** - Automated Tri-Gate (Security AST, UI/UX zero-emoji, Architecture) requiring `exit 0` and deterministic `prove-it-done`.
10. **Stage 10: Graphified Quantum Vector DB & Living Ledgers**:
    - **Every output is automatically graphified** as nodes and edges in `~/.brain-vault/code_graph.json` and vector-indexed into the Quantum Vector DB (Qdrant on port 6333 / SQLite-vec).
    - Nightly memory consolidation in living ledgers (`DO.md`, `DONT.md`), distilling lessons learned from mistakes so the system continuously autolearns, alongside CAPI scorecards and meritocratic squad evolution.


---

## 2. The Interview Protocol ("The Grill")

When a user initiates setup (e.g. "set up brain vault", "configure my vault", or `/brain-vault-setup`), DO NOT blindly run a script. **Grill them step-by-step** through these essential architecture decisions:

### Phase 1: Core Runtime Engine (Python vs Rust)
Ask the user which language runtime they want to power their sovereign brain system:
- **Option A (Python - Universal Sovereign Standard Library - Default & Recommended)**:
  - *Zero Setup / Instant Boot*: Runs natively out of the box on macOS, Linux, and Windows using standard `python3`. Zero build steps, zero compiler dependencies, and zero package manager friction.
  - *Dynamic Extensibility & Hot-Patching*: AI agents and users can inspect, modify, and hot-patch cognitive routing rules, tools, and living ledgers in plaintext on the fly without recompiling binaries.
  - *Footprint*: Pure standard library with zero external dependencies, ~20-50 MB RAM overhead, leaving 7+ GB free on an 8 GB machine.
  - *Best for*: Rapid customization, transparent prompt/tool hacking, interactive pair programming, and zero-friction onboarding.
- **Option B (Rust - High-Performance Compiled Native Binary)**:
  - *Sub-Millisecond Execution & Zero GC*: Compiled native machine code with zero garbage collection overhead. Tool dispatch, AST syntax tree parsing, and token streaming execute in sub-millisecond latency (< 1 ms).
  - *Ultra-Low Footprint*: Produces a tiny, self-contained static binary (5-15 MB executable) consuming `< 10 MB` resident RAM.
  - *Maximum Swarm Concurrency*: High-throughput multi-threaded parallelism for heavy concurrent Nostr Ed25519 cryptographic signing and dense vector math.
  - *Trade-off*: Requires `cargo` / Rust compiler toolchain; dynamic agent modifications require code re-compilation.
  - *Best for*: Production servers, edge IoT hardware, embedded micro-daemons, and latency-critical agent swarms.

### Phase 2: Bun Web & Toolchain Engine Option (Bun vs Python-Only)
Ask the user if they want to install/enable the **Bun runtime and toolchain** (`bun.sh`):
- **Option A (Bun Toolchain - Recommended)**: Installs/verifies `bun` (`curl -fsSL https://bun.sh/install | bash`). Powers lightning-fast package management (`bun install`, `bun add`), instant TypeScript execution without compile steps, local API microservices (Elysia/Hono), and Babylon.js WebGPU graphics tools.
- **Option B (Python Standard Library Only)**: Keeps the system purely Python standard-library-based with zero JS/TS runtime tooling.

### Phase 3: Vector Database Selection (Qdrant / SQLite / Markdown)
Ask the user where they want to store and retrieve dense vector embeddings and semantic memories:
- **Option A (Qdrant on localhost:6333 - Recommended Local)**: Standalone Docker or native loopback on port 6333 across 16 specialized memory collections. High throughput, dense HNSW indexing, and hardware-accelerated cosine similarity search.
- **Option B (Chroma / SQLite-vec - Zero Setup)**: Pure local embedded file database with zero network ports or Docker requirements.
- **Option C (Plain Markdown Ledgers)**: Pure file-based storage in `~/.brain-vault/memory/` with zero embeddings. Simplest, human-readable, and 100% git-friendly.

### Phase 4: Knowledge Graph & Output Graphification (Graphify Engine vs Flat File)
Ask the user how they want agent outputs, code artifacts, and task memories indexed structurally:
- **Option A (Automated Graphify Engine - Recommended)**:
  Automatically converts every agent output, tool execution, code module, and task into connected nodes and bidirectional dependency edges in `~/.brain-vault/code_graph.json` (`VaultSandbox.graphify_and_index_quantum_db()`). Fuses visual structural topology (which code imports what, which task generated an artifact) directly with semantic vector retrieval.
- **Option B (Flat File Storage)**:
  Pure flat markdown files in `~/.brain-vault/memory/` without building cross-file node/edge graph connections. Simple and human-readable, but lacks structural dependency awareness.

### Phase 5: Local Reasoning Core & Embedded Tools (Sub-1B & Open-Weights)
On an 8 GB Mac, memory headroom is strictly preserved by keeping reasoning models **Sub-1B** and delegating tool calling and embeddings to **Embedded Open-Weights Models**:
- **Option A (Sub-1B Reasoning Models - Recommended for 8 GB RAM)**:
  - **Needle 3 by Cactus Compute**: Single 8-29 MB binary ([cactus-compute/needle](https://github.com/cactus-compute/needle) / `pip install cactus-needle`), 121M parameters, ~50 MB RAM, >900 TPS decode, built-in Whistle 16.9 MB STT.
  - **Qwen 2.5 0.5B Instruct GGUF** (`Qwen/Qwen2.5-0.5B-Instruct-GGUF`): 490M parameters, ~350 MB RAM, 1,800+ TPS on Metal GPU offload.
  - **SmolLM2 360M Instruct GGUF**: 360M parameters, ~250 MB RAM, instant intent router.
- **Option B (Embedded Open-Weights for Tools & Embeddings)**:
  - Open-Weights Llama 3.2 / Gemma 2 (`bartowski/Llama-3.2-1B-Instruct-GGUF` / `gemma-2-2b-it`):
  - Specialized for schema-constrained tool execution, structured argument extraction, and local vector embeddings.
  - Takes ~1.4 GB VRAM on Apple Silicon Metal, leaving 3.5+ GB of RAM free for the host OS and applications.
  - Launch one-liner: `llama-server -hf bartowski/Llama-3.2-1B-Instruct-GGUF --port 8080 -ngl 99`.
- **Option C (Ollama / LM Studio Loopback)**: Hook up to an existing local server on `http://localhost:11434`.
- **Option D (Deterministic Rule-Based Router)**: Zero model download. Uses keyword and intent regex decomposition to route tasks to local Python scripts (0 MB VRAM, 0 tokens burned).


### Phase 6: Privacy Sanitizer & Secret Redaction
Configure which credential classes the user's workflow needs to protect:
- Confirm standard 14 credential classes:
  1. AWS Access Keys (`AKIA...`)
  2. AWS Secret Access Keys (`wJalrX...`)
  3. Stripe Live & Restricted Keys (`sk_live_...`)
  4. Slack Bot & User Tokens (`xoxb-...`)
  5. Database Connection DSNs (`postgres://user:pass@...`)
  6. Cloud Provider API Keys (`AIzaSy...`)
  7. OpenAI API Keys (`sk-proj-...`)
  8. Anthropic API Keys (`sk-ant-...`)
  9. GitHub Personal & Fine-Grained Tokens (`ghp_...`)
  10. Private Keys & Certificates (`-----BEGIN RSA PRIVATE KEY-----`)
  11. Ethereum / EVM Wallet Addresses (`0x...`)
  12. Bearer Authentication Tokens
  13. Generic Password Assignments (`password = '...'`)
  14. Local System Home Paths (`/Users/...`, `/home/...`)
- Ask if they have **custom proprietary tokens, internal company domain names, or project-specific keys** that need custom regex redaction.

### Phase 7: Specialist Skills & Extensions Setup ("Lean Core vs Custom Extensions")
The assistant **MUST ask the user if they want a minimal lean core or wish to attach custom project skills**:
- **Option A (Lean Core - Default & Recommended)**: Zero external skill bloat. Installs only the sovereign DAGMAS Brain Vault core cognitive pipeline (Local Vector DB, Local GGUF Inference with `llama.cpp`, 14-class Privacy Sanitizer, AST Security Tri-Gate, Prompt Injection Guard, and Needle cognitive routing).
- **Option B (Custom Domain Extensions)**: The user can provide Git repository URLs or local filesystem paths to any specific community skills or internal tools they wish to register into their vault workspace.

### Phase 8: ADHD Skill Skeptor & Graphics Performance Budgeting
Configure the hyper-focus guardrail and rendering engine standards:
- **ADHD Hyper-Focus Lock**: Restricts agent attention to a single milestone at a time; rejects rabbit-holing and unauthorized context switching until the active milestone passes verification.
- **Spector GPU Profiler**: Monitors WebGL / WebGPU / Babylon.js graphics frame budgets, enforcing a hard 60 FPS standard with <= 150 draw calls and zero shader state thrashing.

### Phase 9: Multi-Agent Mesh Cryptography & Bilingual Token Standard
Configure swarm transport and token optimization:
- **Asymmetric Nostr Key Mesh (Nostr NIP-44 Protocol)**: Each agent squad generates an Ed25519-style asymmetric keypair. Swarm messages are encapsulated in encrypted envelopes with recipient public keys and signed by sender private keys.
- **High-Density Bilingual Protocol**:
  - Inter-agent messages, subagent prompts, and task reports are strictly formulated in **Simplified Chinese** to maximize information density and cut token overhead by ~70%.
  - User-facing responses, explanations, and artifacts are strictly formulated in **English**.

### Phase 10: Business Operations & Squad Hierarchy
Tailor the user's digital company org chart:
- Review the 9 default squads (Research, Engineering, Gaming, Legal, Sound, Marketing, Crypto, Automations, Publishing) or full 33-company enterprise structure.
- Ask which squads they actively need right now.
- Generate or customize individual `SOUL.md` profiles with explicit **DOs** and **DONTs**, authority levels, and daily performance metrics.

### Phase 11: Key Storage & Vault Keystore Backend
Ask how API keys and credentials should be securely retained inside the vault:
- **Option A (Bitwarden CLI Sync)**: Connects to the user's Bitwarden vault via official `bw` CLI. Zero plaintext keys on disk; retrieved on-demand via authenticated vault sessions.
- **Option B (Local Encrypted Keystore - 0600 POSIX File)**: Pure local encrypted keystore file stored inside `~/.brain-vault/keystore.json` with strict owner-only permissions (`0600` / `0700`). Zero cloud accounts, zero third-party software needed.

### Phase 12: Default Memory & Universal Backup System Selection
The assistant asks the user whether, once setup, preflight verification, and live testing succeed, they wish to register Brain Vault as their default memory and universal backup system:

> *"Once verified and tested, do you want to set Brain Vault as your default memory and universal backup system from now on?"*

- **Option A (Yes - Global Default Memory & Universal Backup System)**: Upon passing preflight and live test, installs `dagmas_brain_vault.md` into global agent rules (`~/.agents/rules/dagmas_brain_vault.md`). Every future agent session across all workspaces automatically boots with Brain Vault living ledgers, local-first routing via `llama.cpp`, and privacy sanitization active by default.
- **Option B (No - Workspace Only)**: Keeps Brain Vault scoped strictly to the current workspace repository without modifying system-wide agent rules.


---

## 3. Strict Sequential Execution Pipeline: Tools -> Brain -> Orchestrator -> Preflight

Before executing any terminal commands or modifying system files, the assistant **MUST ask the user how they want to proceed**:

> *"I can execute this setup automatically for you right now, or I can give you the exact step-by-step commands so you can run them manually in your own terminal. Which do you prefer?"*

---

### Mode A: Automated Execution (When tool execution is permitted)

If the user selects automated execution, the agent MUST follow this exact 4-step sequence without reordering or skipping:

#### Step 1: External Prerequisites Setup & Verification (Hard Dependency Gate)
Before touching or creating the brain sandbox, the agent MUST verify and start all selected external services:

1. **Vector DB (Qdrant)**:
   If the user selected Qdrant (Phase 2 Option A):
   - Check if Qdrant is already running:
     ```bash
     curl -s http://localhost:6333/healthz
     ```
   - If not running, start Qdrant container:
     ```bash
     docker ps -a | grep qdrant && docker start qdrant || docker run -d -p 6333:6333 --name qdrant qdrant/qdrant
     ```
   - Wait until `curl -s http://localhost:6333/healthz` returns `HTTP 200 OK`.
2. **Bun Runtime Toolchain (`bun`)**:
   If the user selected Bun (Phase 2 Option A):
   - Verify `bun` is installed: `which bun || curl -fsSL https://bun.sh/install | bash`
   - Verify `bun --version` returns successfully.
3. **Local Reasoning Inference (llama.cpp / Needle)**:
   If the user selected llama.cpp or Needle (Phase 5):
   - Verify runner binary is present and local endpoint is reachable (`http://127.0.0.1:8080/v1`).
4. **Keystore Backend (Bitwarden CLI)**:
   If the user selected Bitwarden CLI (Phase 11 Option A):
   - Verify `bw` executable is installed (`which bw`).

> [!CAUTION]
> **HARD GATE**: The agent is STRICTLY PROHIBITED from executing Step 2 until all selected external tools are confirmed operational and responsive.

#### Step 2: Initialize Sovereign Brain Core
Only once all external prerequisites are green, initialize the POSIX `0700` sandbox, directory structure, living ledgers, and canonical schemas:
```python
from src.vault import VaultSandbox
vault = VaultSandbox("~/.brain-vault")
vault.initialize(
    local_model_id="Qwen/Qwen2.5-0.5B-Instruct-GGUF",
    embedder_id="gemma2-embedded",
    runner="llama.cpp",
    local_endpoint="http://127.0.0.1:8080/v1",
    runtime_engine="python"
)
```
This automatically provisions:
- `~/.brain-vault/` and subdirectories (`teams/`, `skills/`, `memory/`, `ledgers/`) locked to `0700`.
- Living ledgers: `DO.md`, `DONT.md`, `LESSONS.md`.
- Canonical schemas: `vault_config.json`, `limits.json`, `registry.json`, `code_graph.json`.

#### Step 3: Link Orchestrator Profile, Digital Squads & Specialist Skills
Provision the active digital organization and link agent profiles:
1. Write customized `SOUL.md` profiles into `~/.brain-vault/teams/` for each squad chosen in Phase 10.
2. Link or register specialist skills into `~/.brain-vault/skills/` as selected in Phase 7.
3. If the user approved Phase 12 (Global Default Memory & Universal Backup System):
   ```python
   vault.install_global_agent_default()
   ```
   Installs `dagmas_brain_vault.md` into `~/.agents/rules/dagmas_brain_vault.md`.

#### Step 4: Autonomous Preflight Diagnostics & Self-Healing Verification
Launch the comprehensive preflight diagnostic engine:
```bash
python3 -m src.preflight
```
* **Agent Self-Healing Obligation**: The agent MUST inspect the preflight report. If any check reports `FAIL` or `WARN`, the agent must immediately diagnose and apply the fix, re-running `python3 -m src.preflight` until all 8 checks return `[PASS]` with `exit 0` (`prove-it-done`).

#### Step 5: Live Functional Test (End-to-End Verification)
Once preflight diagnostics confirm the system is running smoothly with `exit 0`, execute a live functional test directly inside the vault:
```python
from src.vault import VaultSandbox
vault = VaultSandbox("~/.brain-vault")

# 1. Test secret encryption and retrieval
sec_res = vault.store_secret("TEST_VERIFY_KEY", "sk-proj-test123456", backend="local_encrypted")
assert sec_res["success"], "Live secret test failed"

# 2. Test graphification and memory indexing
graph_res = vault.graphify_and_index_quantum_db(
    node_id="init_live_verification",
    label="Live System Test",
    content="End-to-end memory indexing and graph topology confirmed operational.",
    node_type="test"
)
assert graph_res["success"], "Live memory graph test failed"
```

#### Step 6: Final User Confirmation ("Set as Default Memory and Universal Backup System?")
With the system confirmed running smoothly and the test passed, the assistant **MUST ask the user**:

> *"Brain Vault is confirmed running smoothly with all preflight checks green and live test passed. Do you want to set Brain Vault as your default memory and universal backup system from now on?"*

If the user selects Yes:
```python
vault.install_global_agent_default()
```
Installs `dagmas_brain_vault.md` into `~/.agents/rules/dagmas_brain_vault.md`, making Brain Vault the permanent default memory, secret scrubber, and universal backup standard for all future sessions.

---

### Mode B: Manual Step-by-Step Execution (For restricted computer environments)

If the user chooses manual installation, provide this exact copy-paste guide in the identical sequential order:

#### Step 1: Set Up & Verify External Prerequisites First
```bash
# 1. Start Qdrant vector database (Docker):
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant

# Verify Qdrant is listening on port 6333:
curl -s http://localhost:6333/healthz

# 2. (Optional) Install & launch llama.cpp for local inference:
brew install llama.cpp
llama-server -hf Qwen/Qwen2.5-0.5B-Instruct-GGUF --port 8080 -ngl 99

# Verify endpoint:
curl -s http://127.0.0.1:8080/v1/models

# 3. (Optional) If Bitwarden was selected:
brew install bitwarden-cli
bw login

# 4. (Optional) If Bun was selected:
curl -fsSL https://bun.sh/install | bash
bun --version
```

#### Step 2: Initialize the 0700 Locked Sandbox Directory & Ledgers
```bash
# Create main vault and secure subdirectories
mkdir -p ~/.brain-vault/{teams,skills,memory,ledgers}

# Lock to strict owner-only permissions (0700: drwx------)
chmod 700 ~/.brain-vault ~/.brain-vault/*

# Initialize living ledgers
cat << 'EOF' > ~/.brain-vault/ledgers/DO.md
# Living Ledger: DO
- [System] Always verify preflight before execution.
- [Security] Enforce 0700 permissions on all vault files.
- [Inference] Route routine tasks to Sub-1B models.
- [Tools] Delegate structured function calls to Gemma 2 Embedded.
EOF

cat << 'EOF' > ~/.brain-vault/ledgers/DONT.md
# Living Ledger: DONT
- [Security] Never leak unredacted tokens to external APIs.
- [System] Never bypass the verify-against-source check.
- [Memory] Never exceed the 5.5 GB system RAM ceiling.
EOF

cat << 'EOF' > ~/.brain-vault/ledgers/LESSONS.md
# Living Ledger: LESSONS
- [Architecture] The Brain registry tracks nodes with SHA256 hashes to prevent redundant embeddings.
EOF

chmod 600 ~/.brain-vault/ledgers/*.md
```

#### Step 3: Write Canonical Configurations & Schemas
```bash
cat << 'EOF' > ~/.brain-vault/vault_config.json
{
  "vault_path": "~/.brain-vault",
  "initialized": true,
  "version": "1.0.0",
  "permissions": "0700",
  "runtime_engine": "python",
  "bun_enabled": true,
  "graphify_enabled": true,
  "key_storage": {
    "backend": "local_encrypted",
    "bitwarden_status": false
  },
  "local_model": {
    "runner": "llama.cpp",
    "model_id": "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
    "parameter_tier": "sub-1b",
    "tool_engine": "gemma2-embedded",
    "endpoint": "http://127.0.0.1:8080/v1",
    "llama_cpp_installed": true
  },
  "tool_engine": "gemma2-embedded",
  "embedder_model": "gemma2-embedded",
  "qdrant_url": "http://localhost:6333",
  "qdrant_collections": 16,
  "max_ram_gb": 5.5,
  "min_headroom_mb": 500
}
EOF

cat << 'EOF' > ~/.brain-vault/limits.json
{
  "local_llm": "http://127.0.0.1:8080/v1/chat/completions",
  "local_model": "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
  "frontier_models": ["claude-3-7-sonnet", "deepseek-r1", "gpt-4o"],
  "decay_days": 60,
  "decay_max_per_tick": 10,
  "rule_max_chars": 1800,
  "plugin_dir": "~/.brain-vault/skills",
  "qdrant_url": "http://localhost:6333",
  "embedder_model": "gemma2-embedded",
  "embed_cache": "~/.brain-vault/memory/embed_cache",
  "max_ram_gb": 5.5,
  "min_headroom_mb": 500
}
EOF

cat << 'EOF' > ~/.brain-vault/registry.json
{
  "version": "1.0.0",
  "total_nodes": 6,
  "last_scan_utc": "2026-10-10T00:00:00Z",
  "nodes": [
    {"id": "node-core-vault", "kind": "tool", "name": "VaultSandbox", "desc": "0700 sandbox file store", "path": "src/vault.py", "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
    {"id": "node-sanitizer", "kind": "tool", "name": "PrivacySanitizer", "desc": "14 credential classes scrubber", "path": "src/sanitizer.py", "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
    {"id": "node-prompt-guard", "kind": "tool", "name": "PromptGuard", "desc": "Prompt injection defanger", "path": "src/prompt_guard.py", "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
    {"id": "node-needle-engine", "kind": "pipeline", "name": "NeedleEngine", "desc": "Cactus Needle 3 sub-1b router", "path": "src/needle.py", "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
    {"id": "node-preflight-engine", "kind": "tool", "name": "PreflightEngine", "desc": "Autonomous self-healing engine", "path": "src/preflight.py", "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
    {"id": "node-schemas", "kind": "schema", "name": "BrainSchemas", "desc": "Brain & System canonical schemas", "path": "src/schemas.py", "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
  ]
}
EOF

cat << 'EOF' > ~/.brain-vault/code_graph.json
{
  "version": "1.0.0",
  "nodes": [
    {"id": "vault", "type": "module", "label": "Vault Sandbox"},
    {"id": "sanitizer", "type": "module", "label": "Privacy Sanitizer"},
    {"id": "needle", "type": "engine", "label": "Cactus Needle 3"},
    {"id": "preflight", "type": "engine", "label": "Preflight Engine"}
  ],
  "edges": [
    {"source": "preflight", "target": "vault", "relation": "verifies"},
    {"source": "needle", "target": "sanitizer", "relation": "scrubs"}
  ]
}
EOF

chmod 600 ~/.brain-vault/*.json
```

#### Step 4: Link Orchestrator Profile, Squads & Global Agent Rule
```bash
# If you chose to make Brain Vault the default for your agent (Phase 12):
mkdir -p ~/.agents/rules
cp rules/vault_security.md ~/.agents/rules/dagmas_brain_vault.md
```

#### Step 5: Launch Preflight Diagnostics & Verification
Run the comprehensive preflight diagnostic engine to inspect sandbox integrity, permissions, canonical schemas, inference readiness, and all unit tests:
```bash
python3 -m src.preflight
```
> **Verification Requirement**: Preflight audits all 8 subsystems and self-heals any degraded state. All checks must show `[PASS]` with `exit 0`.

#### Step 6: Run Functional Live Test
Verify that local secret encryption and knowledge graph memory indexing are functioning smoothly:
```bash
python3 -c "
from src.vault import VaultSandbox
v = VaultSandbox('~/.brain-vault')
res = v.graphify_and_index_quantum_db('test_node', 'Manual Test', 'Verifying memory indexing.', 'test')
assert res['success'], 'Test failed'
print('[PASS] Live functional memory test passed successfully.')
"
```

#### Step 7: (Optional) Set as Default Memory & Universal Backup System
If you wish to make Brain Vault your agent's permanent default memory and universal backup standard across all sessions:
```bash
mkdir -p ~/.agents/rules
cp rules/vault_security.md ~/.agents/rules/dagmas_brain_vault.md
```


---

## 4. Guiding Principles for the Assistant

- **Autonomous Preflight & Fix Loop**: Always conclude setup by running `python3 -m src.preflight`. If any failure is detected (e.g. loose permissions, missing ledgers, failing tests, or unreachable configs), proactively repair the issue and re-verify until 100% green before presenting completion.
- **Strict Schema Compliance**: Ensure that all canonical Brain & System schemas (`vault_config.json`, `limits.json`, `registry.json`, `code_graph.json`, and living ledgers) are strictly provisioned and valid.
- **Keep It Relatable**: Use everyday analogies (the leather wallet, the kitchen light, the airport baggage X-ray, the artisan sourdough recipe).
- **Be Candid**: Remind the user that Brain Vault does not magical create cloud tokens; it enforces local-first habits and trims context so they don't overspend on cloud models.
- **Never Compromise Sandbox Security**: Ensure `~/.brain-vault` permissions are always verified at `0700` (`drwx------`).
