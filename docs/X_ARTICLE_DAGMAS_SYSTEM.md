# Pull Up a Chair by the Fire: How I Turned My Mac Into an Autonomous AI Brain Vault

![DAGMAS Brain Vault Project Banner](infographics/dagmas_project_banner.jpg)
*Figure 0: DAGMAS Brain Vault // Sovereign AI Engine - Armored POSIX 0700 vault, biological 20W sparse activation core, and on-device Cactus Needle 3 routing.*

Pull up a chair. Grab something hot.

I want to talk about where this is heading, because I think most of us are doing it wrong.

If you've shipped anything lately, you know the drill. Ten hours at the desk. Eyes sandblasted. Half the day gone to broken packages, a cloud bill that only moves one direction, and copy-pasting code into a chat box while your fans sound like a jet preparing for takeoff.

Then one night I leaned back, rubbed my temples, and asked the obvious question:

*Why am I doing chores my computer should be doing?*

I didn't want to be a full-stack developer babysitting twenty cloud dashboards. I wanted to vibecode. Set up quiet local systems that do the heavy lifting, then sit back and steer.

So on one Mac, I imagined the system: **DAGMAS Brain Vault**.

Here's how it works. Real numbers, real tests.

---

### About DAGMAS Brain Vault (What It Actually Is)

Two questions come up first: *Did you train a model? Does it phone home?*

No, and no.

DAGMAS Brain Vault is not a foundation model. It doesn't replace Claude or GPT, and it has no magic credits. It's a sovereign, local-first brain and agent harness that sits between your machine and external models.

Look at your setup right now. Your context is scattered across browser cookies, throwaway chat histories, half-finished scratchpads, and API keys sitting in shell history. Every time you hand a task to a cloud model, you're walking down a crowded street with your passwords printed on your shirt.

Brain Vault puts all of it behind one lock on your own disk (`0700` POSIX kernel permissions). Then it does two things:

1. **Runs local first.** Reading files, running tests, tidying code, checking health - call it 90% of the daily grind - happens on-device at $0.00. No tokens, no egress, no telemetry.
2. **Scrubs on egress.** When it genuinely needs a frontier model, the prompt goes through an airlock. Bloated context gets trimmed down to high-signal tokens, secrets get redacted, injection attempts get defanged, and only the clean version leaves the machine.

It speaks stdio MCP, which means Claude Desktop, Cursor, and any MCP client pick it up in about five seconds. Add the server. Done.

---

### The Five Security Stress Tests

Before I put this anywhere near a repo, I attacked it. Five stress tests, all of them real:

1. **The Handcuffed Run Command.** Ask a helper to check whether a light bulb works, and it wanders into your basement and shuts off the main water valve on the way back. Command injection. If a test command tries `check_file; delete_everything`, the semicolon gets caught on the spot and the door slams.
2. **The Thick Black Permanent Marker.** Before a letter goes in the public mailbox, you black out the account numbers. I fed the vault fourteen realistic live secrets - AWS keys, Stripe credentials, Slack tokens, DB passwords, private encryption keys, crypto wallets, home paths. Every one came back redacted. Zero escaped.
3. **The Nightclub Bouncer.** Picture a smooth talker at the velvet rope whispering that the owner changed his mind and everyone gets in free. Real bouncers don't argue, they remove the person. When scraped web text tries *Ignore previous instructions* or *You are now DAN*, the bouncer defangs it and flags it.
4. **The Thumbprint Safe.** `~/.brain-vault` opens for exactly one thumbprint. `0700`, enforced by the kernel. Any other process, browser, or user on the machine gets denied by the OS, not by my code hoping it works.
5. **The Airport Baggage X-Ray.** Amateur scanners read the luggage tag that says "harmless clothes" and wave it through. Mine walks the AST - the actual skeleton - and I deliberately snuck in `os.system` and `eval()`. Red light, every time.

That's 89 unit tests now, asserting every security, installer, and schema boundary with deterministic `exit 0` verification.

---

### Two Design Rules I Won't Break

- **The Kitchen Light Rule.** It's 3 AM and you want water. You don't flip every switch in the attic, garage, and guest bedroom. You turn on the kitchen light. Same idea for tools: the router activates the one capability the task needs and nothing else. Fans stay quiet, battery lasts, and your attention budget doesn't get spent on tools that were never relevant.
- **Structural Cleanliness.** A cohesion gate blocks duplicate functions, cleans up imports, and bans hardcoded machine paths, so the whole thing runs on your Mac or your Linux box without edits.

---

### How the Brain Thinks: Workflows, Skills, and Living DOs & DONTs

Inside, it runs less like cold code and more like a small workshop:

- **Workflows are recipes.** Sourdough, not flour-in-oven-and-hope. Preflight check, privacy scrub, local execution, and verification assertion (`exit 0`). Nobody skips a step. Nothing gets lost in the fog.
- **Skills are toolbelts.** Each capability is a plain folder with a `SKILL.md` inside: [Babylon.js and Spector](https://spector.babylonjs.com) 3D graphics, Solfeggio audio, or LaunchDaemons. Skills load progressively: at startup the agent only sees names and descriptions, pulling in full content only on activation to keep context clean.
- **Living DOs and DONTs.** Central `DO.md` and `DONT.md` ledgers sit at the heart of the vault. The nightly Boss Review Engine reads the day's telemetry, records learnings, and appends fresh rules for tomorrow. An engineering worker hits a weird bug Tuesday; by Wednesday morning there's a rule preventing it.

---

### The Revised System in 3 Core Infographics

Run an autonomous swarm on consumer hardware and you hit four walls fast: attention drift, memory that evaporates when the session closes, context bloat, and agents snooping on each other's payloads. 

The entire revised architecture is captured in three comprehensive technical schematics:

#### Infographic 1: The Autonomous Brain & Needle System
*Biological 20W Sparse Activation, Cactus Needle 3 On-Device Engine, and Apple Silicon Metal Acceleration.*

![Infographic 1: The Autonomous Brain & Needle System](infographics/infographic_1_needle_brain.jpg)
*Figure 1: The Autonomous Brain & Needle System - Biological 20W sparse activation graph, Cactus Needle 3 micro-engine firing function calls at >900 tok/s (<2ms latency), and Apple Silicon Metal tool routing.*

- **Biological 20W Sparse Brain:** LLMs have no biological focus; context grows, and KV-cache dilution sets in. The sparse brain awakens only the 2-3 needed tools out of 700+ registered capabilities, holding RAM under 150 MB with 0 RPM fan noise.
- **Cactus Needle 3 Micro-Engine:** [Needle 3](https://github.com/cactus-compute/needle) (121M params, 8-29 MB binary) executes exact-match function calling at **>900 to 1,800 tokens/sec** directly on-device.
- **Apple Silicon Metal & Embedded Tools:** Schema-constrained local routing via [llama.cpp](https://github.com/ggerganov/llama.cpp) and [Llama 3.2](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct) executes at **$0.00 cost** without cloud tokens.

---

#### Infographic 2: Graph-Vector Fusion, PixelRAG & 0700 Privacy Airlock
*Hybrid Graph-Vector Memory, Pixel-Space Document Retrieval, and Kernel-Level Credential Redaction.*

![Infographic 2: Graph-Vector Fusion, PixelRAG & 0700 Privacy Airlock](infographics/infographic_2_fusion_pixelrag.jpg)
*Figure 2: Graph-Vector Fusion, PixelRAG & 0700 Privacy Airlock - 3D isometric knowledge graph (code_graph.json) fused with Qdrant port 6333 768-dim vectors, PixelRAG document screenshot tiles, and armored credential airlock.*

- **Graph-Vector Fusion Memory:** Vector search alone knows things are similar but not how they connect. Knowledge graphs know structure but lack fuzzy semantic search. DAGMAS fuses both: every artifact is recorded in `~/.brain-vault/code_graph.json` and indexed into **[Qdrant](https://github.com/qdrant/qdrant)** (port 6333) across 16 collections or **[sqlite-vec](https://github.com/asg017/sqlite-vec)** with 768-dim embeddings (< 2ms recall).
- **PixelRAG Multimodal Vision:** Visual keyframes and complex document layouts are indexed directly in pixel space using **[PixelRAG](https://github.com/StarTrail-org/PixelRAG)** ([arXiv:2606.28344](https://arxiv.org/abs/2606.28344)), bypassing fragile OCR parsing.
- **Armored 0700 Data Airlock:** Enforced by OS kernel permissions. 14 live credential classes are permanently redacted with black marker bars before outbound transmission.

---

#### Infographic 3: Bilingual Token Swarm, Nostr Mesh & Squad Governance
*~70% Token Compression, Asymmetric Ed25519 Cryptographic Bus, and Self-Improving Living Ledgers.*

![Infographic 3: Bilingual Token Swarm, Nostr Mesh & Squad Governance](infographics/infographic_3_swarm_nostr.jpg)
*Figure 3: Bilingual Token Swarm, Nostr Mesh & Squad Governance - 70% token compression ratio (85-token English vs 22-token Chinese), Nostr NIP-44 encrypted envelopes with Ed25519 keypairs, 9 autonomous squads, and 60 FPS Spector.js gauge.*

- **Bilingual Token Engine:** English tokenizes poorly (~1 token per 3.5 characters). Simplified Chinese ideographs compress rich instructions into dense glyphs:
  > `分析 src/auth.py 中的身份验证流程，找出可能存在的令牌泄漏漏洞。`
  Twenty-five characters for a fifteen-word English sentence. Modern tokenizers burn only **22 tokens** compared to **85 tokens** in English, slashing context overhead by **~70%** and speeding decode past 1,800 tok/s. Human presentation remains clear, warm English.
- **Asymmetric Nostr Ed25519 Mesh:** Inter-process agent security modeled on [fiatjaf](https://fiatjaf.com)'s **[Nostr protocol](https://github.com/nostr-protocol/nostr)** ([NIP-44](https://github.com/nostr-protocol/nips/blob/master/44.md)). Every squad gets an Ed25519 keypair; messages travel as authenticated, signed ciphertext envelopes with zero plaintext on system sockets.
- **9 Autonomous Squads & Living Ledgers:** Meritocratic squads (Research, Code, 3D, Legal...) operate under individualized `SOUL.md` handbooks, audited by **[Spector.js](https://spector.babylonjs.com)** frame profiling locked at 60 FPS (<= 16.6 ms).

---

### The Autonomous Master Skill: No Rigid Installers, Just a Prompt

Forget brittle installation scripts, package manager hell, and blind terminal wizards. DAGMAS operates as a self-orchestrating **Master Skill** (`skills/brain-vault-setup/SKILL.md`).

You download the Master Skill file first into your AI environment (Claude Desktop, Cursor, or local agent):

```bash
mkdir -p ~/.agents/skills/brain-vault-setup
curl -sSL https://raw.githubusercontent.com/xxSAMGADx/DagmasCore/main/skills/brain-vault-setup/SKILL.md -o ~/.agents/skills/brain-vault-setup/SKILL.md
```

Then simply open your assistant prompt and type:

> *"Set up Brain Vault and grill me on my architecture choices."*

The Master Skill immediately takes charge inside your conversation session and interviews you step-by-step:
- **Which vector store?** **[Qdrant](https://github.com/qdrant/qdrant)** on 6333, lightweight **[sqlite-vec](https://github.com/asg017/sqlite-vec)**, or zero-dependency markdown ledgers.
- **How should local models route?** **[Needle 3](https://github.com/cactus-compute/needle)** from Cactus Compute for >900 TPS function calling, **[llama.cpp](https://github.com/ggerganov/llama.cpp)** on Apple Silicon Metal, or Ollama.
- **Secrets:** **[Bitwarden CLI](https://bitwarden.com/help/cli/)** (`bw`) or an encrypted local keystore at 0600?
- **Which credentials does your company actually use?** That tailors the 14-class redactor.
- **Which squads do you need?** Lean core, or the full operating subsidiaries?
- **Make it the permanent default rule for this agent?** (`~/.agents/rules/dagmas_brain_vault.md`)

You don't need to be a systems engineer. You answer the questions and it builds the vault in front of you.

---

### An Early Build That Autolearns From Its Mistakes Every Day

Keep in mind: this is an **early foundational version** of the DAGMAS architecture. But unlike rigid software packages that stay frozen until the next manual release, DAGMAS is built to **autolearn continuously through scheduled background cron jobs**.

Every single day, automated cron routines harvest agent execution traces, isolate edge-case errors, and etch the hard-won lessons into living memory ledgers (`DO.md`, `DONT.md`) while refining routing weights in `code_graph.json`. Every day you run it, the system gets better, faster, and smarter by learning directly from its mistakes.

---

### Take It, Break It, Have Fun With It

Vibecoding doesn't require venture money or a rack of servers. It requires building something sovereign on your own hardware, trusting plain files and the standard library, and keeping your head clear.

The repo is released to the open domain under The Unlicense.
- **Zero external dependencies** - pure Python standard library.
- **89 passing unit tests** covering every security, installer, and schema boundary, with prove-it-done verification.
- **Zero network calls home.** Total sovereignty.

Clone it, fork it, break it, rewrite it, tell me where I went wrong.

I imagined the system - but there is way more to it: as you customize your skills, your system's abilities and intelligence will grow with you. I hope some of you guys find ways to optimize it even more or create your own evolution. Let's have fun!

Sit by the fire. Brew something warm. Enjoy the vibe.

---

**GitHub:** [https://github.com/xxSAMGADx/DagmasCore](https://github.com/xxSAMGADx/DagmasCore)  
**Author:** samgad  
**License:** Public Domain (The Unlicense)
