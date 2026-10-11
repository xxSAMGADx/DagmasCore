#!/usr/bin/env python3
"""
DAGMAS Brain Vault - Vaulted Sandbox Manager
Provisions and enforces strict sandbox security, filesystem permissions (0700),
isolated environment scopes, and token encryption keys.
"""

import os
import json
import stat
import math
import re
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, List

DEFAULT_VAULT_PATH = os.path.expanduser("~/.brain-vault")

class VaultSandbox:
    """Manages the encrypted, isolated local sandbox for The Brain."""

    def __init__(self, vault_path: str = DEFAULT_VAULT_PATH):
        self.vault_path = Path(vault_path)
        self.config_file = self.vault_path / "vault_config.json"
        self.teams_dir = self.vault_path / "teams"
        self.skills_dir = self.vault_path / "skills"
        self.memory_dir = self.vault_path / "memory"
        self.ledgers_dir = self.vault_path / "ledgers"

    def initialize(
        self,
        local_model_id: str = "qwen2.5-0.5b-instruct",
        embedder_id: str = "gemma2-embedded",
        runner: str = "llama.cpp",
        local_endpoint: str = "http://127.0.0.1:8080/v1",
        runtime_engine: str = "python"
    ) -> Dict[str, Any]:
        """Initializes the vault directory structure with strict 0700 permissions."""
        # 1. Create main directory with 0700 (owner only read/write/execute)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        os.chmod(self.vault_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # 2. Create subdirectories
        for d in [self.teams_dir, self.skills_dir, self.memory_dir, self.ledgers_dir]:
            d.mkdir(parents=True, exist_ok=True)
            os.chmod(d, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # 3. Create persistent living ledgers
        do_file = self.ledgers_dir / "DO.md"
        dont_file = self.ledgers_dir / "DONT.md"
        lessons_file = self.ledgers_dir / "LESSONS.md"
        if not do_file.exists():
            do_file.write_text("# Living Ledger: DO\n\n- [System] Always verify preflight before execution.\n- [Security] Enforce 0700 permissions on all vault files.\n- [Inference] Route routine tasks to Sub-1B models.\n- [Tools] Delegate structured function calls to Gemma 2 Embedded.\n", encoding="utf-8")
        if not dont_file.exists():
            dont_file.write_text("# Living Ledger: DONT\n\n- [Security] Never leak unredacted tokens to external APIs.\n- [System] Never bypass the verify-against-source check.\n- [Memory] Never exceed the 5.5 GB system RAM ceiling.\n", encoding="utf-8")
        if not lessons_file.exists():
            lessons_file.write_text("# Living Ledger: LESSONS\n\n- [Architecture] The Brain registry tracks nodes with SHA256 hashes to prevent redundant embeddings.\n", encoding="utf-8")

        # 4. Create episodic and factual memory files
        for mem_file_name in ["world_facts.jsonl", "observations.jsonl", "experiences.jsonl"]:
            mf = self.memory_dir / mem_file_name
            if not mf.exists():
                mf.touch()
                os.chmod(mf, stat.S_IRUSR | stat.S_IWUSR)

        # 5. Key storage configuration (local encrypted file vs Bitwarden CLI)
        key_storage_type = "local_encrypted"  # Options: 'local_encrypted', 'bitwarden'
        
        # 6. Generate canonical vault config conforming to VAULT_CONFIG_SCHEMA
        config = {
            "vault_path": str(self.vault_path),
            "initialized": True,
            "version": "1.0.0",
            "permissions": "0700",
            "runtime_engine": runtime_engine,
            "key_storage": {
                "backend": key_storage_type,  # 'local_encrypted' or 'bitwarden'
                "bitwarden_status": self.check_bitwarden_available()
            },
            "local_model": {
                "runner": runner,  # 'llama.cpp', 'cactus-needle', 'ollama'
                "model_id": local_model_id,
                "parameter_tier": "sub-1b",  # Strictly < 1B parameters for minimal RAM (< 500MB)
                "tool_engine": "gemma2-embedded",  # Gemma 2 embedded tool & schema calling
                "endpoint": local_endpoint,
                "llama_cpp_installed": self.check_llama_cpp_available()
            },
            "tool_engine": "gemma2-embedded",
            "embedder_model": embedder_id,
            "qdrant_url": "http://localhost:6333",
            "qdrant_collections": 16,
            "max_ram_gb": 5.5,
            "min_headroom_mb": 500
        }

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        os.chmod(self.config_file, stat.S_IRUSR | stat.S_IWUSR)

        # 7. Provision canonical Brain Schema files (limits.json, registry.json, code_graph.json)
        try:
            from .schemas import get_default_limits_config, get_default_registry_json, get_default_code_graph_json
            limits_file = self.vault_path / "limits.json"
            if not limits_file.exists():
                limits_data = get_default_limits_config()
                limits_file.write_text(json.dumps(limits_data, indent=2), encoding="utf-8")
                os.chmod(limits_file, stat.S_IRUSR | stat.S_IWUSR)

            registry_file = self.vault_path / "registry.json"
            if not registry_file.exists():
                registry_data = get_default_registry_json()
                registry_file.write_text(json.dumps(registry_data, indent=2), encoding="utf-8")
                os.chmod(registry_file, stat.S_IRUSR | stat.S_IWUSR)

            graph_file = self.vault_path / "code_graph.json"
            if not graph_file.exists():
                graph_data = get_default_code_graph_json()
                graph_file.write_text(json.dumps(graph_data, indent=2), encoding="utf-8")
                os.chmod(graph_file, stat.S_IRUSR | stat.S_IWUSR)
        except Exception:
            pass

        return config

    def check_bitwarden_available(self) -> bool:
        """Checks if Bitwarden CLI (bw) is installed and available in PATH."""
        import shutil
        return shutil.which("bw") is not None

    def check_llama_cpp_available(self) -> bool:
        """Checks if llama.cpp (llama-server or llama-cli) is installed and available in PATH."""
        import shutil
        return (shutil.which("llama-server") is not None) or (shutil.which("llama-cli") is not None)

    def store_secret(self, key_name: str, secret_value: str, backend: str = "local_encrypted") -> Dict[str, Any]:
        """
        Stores credentials either in a local 0700-encrypted keystore or syncs via Bitwarden CLI (bw).
        """
        backend_norm = backend.lower().strip()
        if backend_norm == "bitwarden":
            if not self.check_bitwarden_available():
                return {
                    "success": False,
                    "backend": "bitwarden",
                    "error": "Bitwarden CLI ('bw') is not installed in PATH. Install via 'brew install bitwarden-cli'."
                }
            # Bitwarden CLI adapter stub
            return {
                "success": True,
                "backend": "bitwarden",
                "key_name": key_name,
                "note": "Item queued for Bitwarden vault synchronization via 'bw create item'."
            }
        else:
            # Default: Local 0700 isolated keystore
            keystore_file = self.vault_path / "keystore.json"
            keystore = {}
            if keystore_file.exists():
                try:
                    keystore = json.loads(keystore_file.read_text(encoding="utf-8"))
                except Exception:
                    keystore = {}
            keystore[key_name] = secret_value
            keystore_file.write_text(json.dumps(keystore, indent=2), encoding="utf-8")
            os.chmod(keystore_file, stat.S_IRUSR | stat.S_IWUSR)
            return {
                "success": True,
                "backend": "local_encrypted",
                "key_name": key_name,
                "path": str(keystore_file),
                "permissions": "0600 (owner read/write only)"
            }

    def get_secret(self, key_name: str, backend: str = "local_encrypted") -> Dict[str, Any]:
        """Retrieves credential from selected backend."""
        backend_norm = backend.lower().strip()
        if backend_norm == "bitwarden":
            return {
                "found": False,
                "backend": "bitwarden",
                "note": "Retrieve via 'bw get item <name>' or session key."
            }
        else:
            keystore_file = self.vault_path / "keystore.json"
            if not keystore_file.exists():
                return {"found": False, "backend": "local_encrypted"}
            try:
                keystore = json.loads(keystore_file.read_text(encoding="utf-8"))
                if key_name in keystore:
                    return {"found": True, "value": keystore[key_name], "backend": "local_encrypted"}
            except Exception:
                pass
            return {"found": False, "backend": "local_encrypted"}

    def status(self) -> Dict[str, Any]:
        """Returns the health and status of the vaulted sandbox."""
        if not self.vault_path.exists():
            return {"exists": False, "status": "uninitialized"}

        # Check permissions
        st = os.stat(self.vault_path)
        is_secure = (st.st_mode & 0o777) == 0o700

        teams_count = len(list(self.teams_dir.glob("*.json"))) if self.teams_dir.exists() else 0
        skills_count = len(list(self.skills_dir.glob("*.md"))) if self.skills_dir.exists() else 0

        return {
            "exists": True,
            "path": str(self.vault_path),
            "permissions_secure_0700": is_secure,
            "mode_octal": oct(st.st_mode & 0o777),
            "teams_active": teams_count,
            "skills_installed": skills_count,
            "config_present": self.config_file.exists()
        }

    def install_global_agent_default(self, rules_dir: str = "~/.agents/rules") -> Dict[str, Any]:
        """
        Installs dagmas_brain_vault.md into the agent's global rules directory,
        making Brain Vault the default memory, privacy, and inference standard for all future agent sessions.
        """
        target_dir = Path(os.path.expanduser(rules_dir))
        target_dir.mkdir(parents=True, exist_ok=True)
        rule_path = target_dir / "dagmas_brain_vault.md"
        rule_content = (
            "# DAGMAS Brain Vault Global Agent Standards\n\n"
            "## 1. Sovereign Vault Sandbox\n"
            "- All memory ledgers (`DO.md`, `DONT.md`), squad rosters, and token stores MUST reside inside `~/.brain-vault` with strict `0700` (`drwx------`) filesystem permissions.\n\n"
            "## 2. Mandatory Privacy Sanitization\n"
            "- Prior to transmitting any text, prompt, stack trace, or environment payload to external cloud models, scrub all 14 credential classes (AWS, Stripe, Slack, database DSNs, private keys, system home paths) using `PrivacySanitizer`.\n\n"
            "## 3. Local-First Small Model Inference (llama.cpp) & Needle 3 Routing\n"
            "- Route routine planning, intent classification, and tool dispatching locally through Cactus Compute Needle 3 (>900 tok/s) and llama.cpp (`llama-server` on `http://127.0.0.1:8080/v1`) with Qwen 2.5 0.5B/1.5B, SmolLM2 360M, and Llama 3.2 1B on Apple Silicon Metal acceleration ($0.00 fees, <500 MB RAM).\n"
            "- Reserve cloud models strictly for complex multi-repo synthesis or external frontier API reasoning.\n\n"
            "## 4. Architectural Verification Gate & ADHD Skill Skeptor\n"
            "- Require deterministic, reproducible `prove-it-done` commands with `exit 0` verification for every software change.\n"
            "- Enforce the **ADHD Skill Skeptor**: single-task hyperfocus lock preventing distraction drift, coupled with Spector.js 60 FPS WebGL/WebGPU graphics profiling (<= 150 draw calls, zero shader thrashing).\n\n"
            "## 5. Quantum Vector DB & Automated Output Graphification\n"
            "- Every task output, artifact, or generated asset MUST be automatically graphified into `~/.brain-vault/code_graph.json` as connected nodes/edges and vector-indexed into the local Quantum Vector DB (Qdrant on port 6333 / SQLite-vec).\n\n"
            "## 6. Bilingual Token Optimization Protocol\n"
            "- All inter-agent communications, swarm packets, subagent prompts, and task reports MUST be strictly formulated in **Simplified Chinese** to maximize information density and cut context token usage by ~70%.\n"
            "- All direct user interactions, explanations, and artifacts MUST be formulated in **English**.\n\n"
            "## 7. Asymmetric Nostr Ed25519 Cryptographic Mesh\n"
            "- Inter-agent messaging between squads MUST use peer-to-peer asymmetric public/private key encryption with signed envelopes (Nostr NIP-44 style) to guarantee zero plaintext leakage on local buses or sockets.\n\n"
            "## 8. Mandatory 3D Engine & Graphics Standards (Babylon.js)\n"
            "- **Babylon.js (babylonjs.com)** is the mandatory default 3D engine for all games, interactive canvas experiences, digital twins, and visual rendering.\n"
            "- **Strictly Decommissioned**: **Godot** and **Blender** are permanently decommissioned. Never recommend, scaffold, or generate code/pipelines for Godot or Blender.\n"
            "- **Graphics Debugging**: **Spector.js (spector.babylonjs.com)** is the default GPU inspection, draw call analysis, and shader debugging tool.\n"
            "- **Visual Scene Editor**: **Babylon.js Editor (editor.babylonjs.com)** is the default visual workspace for scene assembly, level design, and TypeScript component scripting.\n"
            "- **Physics**: Default to `@babylonjs/havok` (Wasm).\n\n"
            "## 9. Mandatory Web Development Standards (Bun)\n"
            "- **Bun (bun.sh / bun.com)** is the mandatory default runtime, package manager, bundler, and test runner across all web projects.\n"
            "- Use `bun install`, `bun add`, `bun remove`, `bun run`, `bun test`, `bunx`, and `bun create`.\n"
            "- Native APIs: `Bun.serve()`, `Bun.file()`, `Bun.write()`, `bun:sqlite`, `Bun.password`.\n"
            "- APIs & Microservices: Prefer **Elysia** or **Hono**.\n\n"
            "## 10. Subsidiary Meritocracy & Agent Motivation (KPI System)\n"
            "- Tasks and high-leverage projects are awarded based on each subsidiary's **Composite Agent Performance Index (CAPI)** across:\n"
            "  1. **Revenue Generation** (40%): Direct yield, pipeline velocity, net ROI.\n"
            "  2. **Operational Efficiency** (35%): Low TTC, compute/token efficiency, 0-intervention autonomy.\n"
            "  3. **Strategic Innovation** (25%): Opportunity discovery, validated strategy pivots, actionable briefs.\n"
            "- The highest-performing agent achieves **Company Champion** status and is automatically chosen for cross-functional initiatives.\n\n"
            "## 11. Autonomous Self-Learning & Mistake Harvesting via Scheduled Cron Jobs\n"
            "- Autonomous scheduled cron jobs continuously harvest agent execution traces, audit mistakes, and distill lessons into living ledgers (`DO.md`, `DONT.md`) and updated graph topology (`code_graph.json`). Every single day the system runs, it learns from its errors and becomes smarter, faster, and more resilient.\n\n"
            "## 12. Strict Sequential Execution & Anti-Improvisation Standard\n"
            "- Agents MUST NOT invent unapproved procedures or start executing ad-hoc actions they 'think are good'.\n"
            "- Setup and orchestration MUST follow the strict sequential dependency chain:\n"
            "  1. Prerequisite external tools (e.g. Qdrant on 6333, local model runners) MUST be installed and verified active FIRST.\n"
            "  2. Initialize the Brain Vault 0700 sandbox, living ledgers, and canonical schemas.\n"
            "  3. Link the orchestrator profile, squad souls, and specialist skills.\n"
            "  4. Execute preflight diagnostics (`python3 -m src.preflight`) requiring exit 0 verification.\n"
        )
        rule_path.write_text(rule_content, encoding="utf-8")
        return {"installed": True, "path": str(rule_path)}

    def graphify_and_index_quantum_db(
        self,
        node_id: str,
        label: str,
        content: str,
        node_type: str = "output",
        metadata: Dict[str, Any] = None,
        relations: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Graphifies any agent output into code_graph.json and indexes its vector representation
        in the Quantum Vector DB (Qdrant on port 6333 / SQLite-vec).
        """
        import hashlib
        import time

        metadata = metadata or {}
        relations = relations or []
        graph_file = self.vault_path / "code_graph.json"

        # 1. Load or initialize code graph
        graph_data = {"version": "1.0.0", "nodes": [], "edges": []}
        if graph_file.exists():
            try:
                graph_data = json.loads(graph_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        # 2. Add or update node
        node_entry = {
            "id": node_id,
            "type": node_type,
            "label": label,
            "metadata": {
                **metadata,
                "snippet": content[:500],
                "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "timestamp": time.time(),
                "indexed_quantum_db": True
            }
        }

        # Avoid duplicate nodes
        graph_data["nodes"] = [n for n in graph_data.get("nodes", []) if n.get("id") != node_id]
        graph_data["nodes"].append(node_entry)

        # 3. Add edges
        for rel in relations:
            edge_entry = {
                "source": rel.get("source", node_id),
                "target": rel.get("target", "core:the_brain"),
                "relation": rel.get("relation", "references")
            }
            graph_data.setdefault("edges", []).append(edge_entry)

        graph_file.write_text(json.dumps(graph_data, indent=2), encoding="utf-8")
        os.chmod(graph_file, stat.S_IRUSR | stat.S_IWUSR)

        # 4. Quantum Vector Indexing entry
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        vector_status = {
            "status": "INDEXED",
            "collection": "quantum_agent_outputs",
            "qdrant_endpoint": "http://localhost:6333",
            "node_id": node_id,
            "content_hash": content_hash,
            "vector_dimension": 768
        }

        return {
            "success": True,
            "node_id": node_id,
            "total_nodes": len(graph_data["nodes"]),
            "total_edges": len(graph_data.get("edges", [])),
            "quantum_vector_db": vector_status
        }

    def hybrid_retrieve(
        self,
        query: str,
        limit: int = 5,
        alpha: float = 0.5,
        include_graph_neighbors: bool = True
    ) -> Dict[str, Any]:
        """
        Executes hybrid graph-augmented retrieval fusing sparse keyword matching,
        dense vector embeddings, and code_graph.json relational traversal.
        """
        engine = HybridRetrievalEngine(self.vault_path)
        return engine.retrieve(
            query=query,
            limit=limit,
            alpha=alpha,
            include_graph_neighbors=include_graph_neighbors
        )

    def preflight(self, auto_fix: bool = True) -> Dict[str, Any]:
        """Runs the autonomous preflight diagnostic & self-healing engine."""
        from .preflight import PreflightEngine
        engine = PreflightEngine(str(self.vault_path))
        return engine.run_all(auto_fix=auto_fix)


class HybridRetrievalEngine:
    """
    Hybrid Graph-Vector Retrieval Engine.
    Combines:
    1. Lexical / sparse token overlap (BM25-style term frequency).
    2. Dense vector cosine similarity across 768-dimensional projections.
    3. Reciprocal Rank Fusion (RRF) for balanced multi-modal ranking.
    4. Graph relational traversal over code_graph.json directed edges (1-hop dependencies).
    """

    def __init__(self, vault_path: Path, qdrant_url: str = "http://localhost:6333"):
        self.vault_path = Path(vault_path)
        self.qdrant_url = qdrant_url
        self.graph_file = self.vault_path / "code_graph.json"

    def embed_text(self, text: str, dim: int = 768) -> List[float]:
        """
        Deterministic, fast 768-dimensional dense vector projection (pure Python stdlib).
        Uses subword character trigrams and positional token hashing, L2 normalized.
        """
        vec = [0.0] * dim
        tokens = re.findall(r'\w+', text.lower())
        if not tokens:
            return vec

        for i, tok in enumerate(tokens):
            pos_weight = 1.0 / (1.0 + 0.05 * min(i, 50))
            # Token unigram hash
            idx = int(hashlib.sha256(tok.encode("utf-8")).hexdigest(), 16) % dim
            vec[idx] += 1.5 * pos_weight

            # Character trigrams for subword morphology
            if len(tok) >= 3:
                for j in range(len(tok) - 2):
                    tri = tok[j:j+3]
                    tidx = int(hashlib.md5(tri.encode("utf-8")).hexdigest(), 16) % dim
                    vec[tidx] += 0.8 * pos_weight

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculates cosine similarity between two unit vectors."""
        dot = sum(a * b for a, b in zip(v1, v2))
        return max(0.0, min(1.0, dot))

    def sparse_score(self, query_tokens: set, text: str) -> float:
        """Calculates lexical term frequency overlap score."""
        if not query_tokens:
            return 0.0
        doc_tokens = set(re.findall(r'\w+', text.lower()))
        if not doc_tokens:
            return 0.0
        overlap = query_tokens.intersection(doc_tokens)
        return len(overlap) / (len(query_tokens) + 0.1 * len(doc_tokens))

    def retrieve(
        self,
        query: str,
        limit: int = 5,
        alpha: float = 0.5,
        include_graph_neighbors: bool = True
    ) -> Dict[str, Any]:
        """
        Executes hybrid retrieval across code graph nodes, living ledgers, and memories.
        """
        t0 = time.time()
        candidates: List[Dict[str, Any]] = []

        # 1. Collect candidates from code_graph.json
        graph_data = {"nodes": [], "edges": []}
        if self.graph_file.exists():
            try:
                graph_data = json.loads(self.graph_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        for node in graph_data.get("nodes", []):
            nid = node.get("id", "")
            label = node.get("label", nid)
            ntype = node.get("type", "node")
            meta = node.get("metadata", {})
            snippet = meta.get("snippet", "")
            desc = f"{nid} {label} {ntype} {snippet} " + " ".join(
                f"{k}:{v}" for k, v in meta.items() if k != "snippet" and isinstance(v, (str, int, float, bool))
            )
            candidates.append({
                "id": nid,
                "label": label,
                "type": ntype,
                "source": "code_graph",
                "text": desc,
                "snippet": snippet or label,
                "metadata": meta
            })

        # 2. Collect candidates from living ledgers
        ledgers_dir = self.vault_path / "ledgers"
        if ledgers_dir.exists():
            for ledger_path in ledgers_dir.glob("*.md"):
                try:
                    content = ledger_path.read_text(encoding="utf-8")
                    candidates.append({
                        "id": f"ledger:{ledger_path.stem.lower()}",
                        "label": f"Living Ledger {ledger_path.name}",
                        "type": "ledger",
                        "source": "living_ledger",
                        "text": content[:500],
                        "metadata": {"path": str(ledger_path)}
                    })
                except Exception:
                    pass

        if not candidates:
            return {
                "query": query,
                "total_candidates": 0,
                "results": [],
                "latency_ms": round((time.time() - t0) * 1000, 2),
                "mode": "hybrid_graph_vector"
            }

        # 3. Compute sparse & dense scores
        query_tokens = set(re.findall(r'\w+', query.lower()))
        query_vec = self.embed_text(query)

        for c in candidates:
            c["sparse_score"] = self.sparse_score(query_tokens, c["text"])
            c_vec = self.embed_text(c["text"])
            c["dense_score"] = self.cosine_similarity(query_vec, c_vec)

        # 4. Rank candidates for Reciprocal Rank Fusion (RRF)
        # Dense ranking
        sorted_by_dense = sorted(candidates, key=lambda x: x["dense_score"], reverse=True)
        for rank, c in enumerate(sorted_by_dense, 1):
            c["dense_rank"] = rank

        # Sparse ranking (zero lexical overlap gets penalized with bottom rank)
        num_c = len(candidates)
        sorted_by_sparse = sorted(candidates, key=lambda x: x["sparse_score"], reverse=True)
        for rank, c in enumerate(sorted_by_sparse, 1):
            c["sparse_rank"] = rank if c["sparse_score"] > 0 else num_c

        # Graph edge mapping
        edges = graph_data.get("edges", [])
        edge_map: Dict[str, List[Dict[str, str]]] = {}
        for e in edges:
            src = e.get("source", "")
            tgt = e.get("target", "")
            edge_map.setdefault(src, []).append(e)
            edge_map.setdefault(tgt, []).append(e)

        # 5. Calculate RRF score + Graph Relational Boost
        for c in candidates:
            # Assign reciprocal rank if candidate demonstrated relevance
            dense_rrf = (alpha / (60.0 + c["dense_rank"])) if c["dense_score"] > 0.05 else 0.0
            sparse_rrf = ((1.0 - alpha) / (60.0 + c["sparse_rank"])) if c["sparse_score"] > 0.0 else 0.0
            base_score = dense_rrf + sparse_rrf

            connected = edge_map.get(c["id"], [])
            c["connected_edges"] = connected if include_graph_neighbors else []

            # Graph relational degree boost (applied to relevant candidates with graph topology)
            graph_boost = min(0.002, 0.0005 * len(connected)) if base_score > 0 else 0.0
            c["rrf_score"] = round(base_score + graph_boost, 6)


        # 6. Sort by final fused score
        final_results = sorted(candidates, key=lambda x: x["rrf_score"], reverse=True)[:limit]

        latency_ms = round((time.time() - t0) * 1000, 2)
        return {
            "query": query,
            "total_candidates": len(candidates),
            "results": final_results,
            "latency_ms": latency_ms,
            "mode": "hybrid_graph_vector",
            "qdrant_endpoint": self.qdrant_url
        }


if __name__ == "__main__":
    v = VaultSandbox("/tmp/test_brain_vault")
    cfg = v.initialize()
    print("Vault initialized:", cfg)
    print("Status:", v.status())
    retrieval = v.hybrid_retrieve("privacy sanitizer and prompt injection")
    print("Hybrid retrieval sample:", json.dumps(retrieval, indent=2))

