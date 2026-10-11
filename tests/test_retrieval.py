#!/usr/bin/env python3
"""
Unit tests for Hybrid Retrieval & Graph-Augmented Memory (src/vault.py).
Tests:
1. Deterministic dense embedding vector projection and normalization.
2. Cosine similarity calculation.
3. BM25-style sparse token matching.
4. Reciprocal Rank Fusion (RRF) combining dense & sparse scores.
5. 1-hop graph relational expansion from code_graph.json directed edges.
6. End-to-end VaultSandbox.hybrid_retrieve() execution.
7. MCP server tool execution of 'vault_hybrid_retrieve'.
"""

import json
import tempfile
import unittest
from pathlib import Path
from src.vault import VaultSandbox, HybridRetrievalEngine
from src.mcp_server import BrainVaultMCPServer

class TestHybridRetrieval(unittest.TestCase):

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.td.name) / "vault"
        self.vault = VaultSandbox(vault_path=str(self.vault_path))
        self.vault.initialize()
        self.engine = HybridRetrievalEngine(self.vault_path)

    def tearDown(self):
        self.td.cleanup()

    def test_dense_embedding_projection_and_normalization(self):
        text = "Sovereign AI memory indexing with graph topology"
        vec = self.engine.embed_text(text, dim=768)
        self.assertEqual(len(vec), 768)
        # Verify L2 norm is approximately 1.0
        norm = sum(x * x for x in vec) ** 0.5
        self.assertAlmostEqual(norm, 1.0, places=4)

    def test_cosine_similarity(self):
        v1 = self.engine.embed_text("Privacy sanitizer redacts AWS credentials")
        v2 = self.engine.embed_text("Privacy sanitizer redacts AWS credentials")
        v3 = self.engine.embed_text("Babylon.js 3D WebGPU game loop with 60 FPS physics")

        sim_identical = self.engine.cosine_similarity(v1, v2)
        sim_different = self.engine.cosine_similarity(v1, v3)

        self.assertAlmostEqual(sim_identical, 1.0, places=4)
        self.assertLess(sim_different, 0.8)

    def test_sparse_lexical_scoring(self):
        query_tokens = {"sanitizer", "credentials"}
        score_high = self.engine.sparse_score(query_tokens, "The privacy sanitizer scrubs credentials from outgoing prompts")
        score_zero = self.engine.sparse_score(query_tokens, "Unrelated audio synthesis for Solfeggio frequencies")

        self.assertGreater(score_high, 0.0)
        self.assertEqual(score_zero, 0.0)

    def test_hybrid_retrieve_with_graph_expansion(self):
        # 1. Index test nodes and relations
        self.vault.graphify_and_index_quantum_db(
            node_id="artifact:auth_protocol",
            label="Asymmetric Nostr Auth Protocol",
            content="Cryptographic key exchange using Ed25519 envelopes and Nostr signatures.",
            node_type="artifact",
            metadata={"security_level": "high"},
            relations=[{"source": "artifact:auth_protocol", "target": "vault", "relation": "secures"}]
        )

        # 2. Query for Nostr auth
        res = self.vault.hybrid_retrieve(
            query="Nostr Ed25519 cryptographic signatures",
            limit=5,
            alpha=0.6,
            include_graph_neighbors=True
        )

        self.assertTrue(res["mode"], "hybrid_graph_vector")
        self.assertGreaterEqual(res["total_candidates"], 1)
        self.assertLess(res["latency_ms"], 50.0)  # Verify sub-50ms latency (typically <2ms)

        # Top result must match the indexed artifact
        top_match = res["results"][0]
        self.assertEqual(top_match["id"], "artifact:auth_protocol")
        self.assertGreater(top_match["rrf_score"], 0.0)

        # Verify connected edges are traversed
        edge_targets = [e["target"] for e in top_match["connected_edges"]]
        self.assertIn("vault", edge_targets)

    def test_mcp_server_hybrid_retrieve_tool(self):
        server = BrainVaultMCPServer(vault_path=str(self.vault_path))
        # Execute tool via MCP dispatch
        res = server.execute_tool("vault_hybrid_retrieve", {
            "query": "preflight diagnostics and permissions",
            "limit": 3
        })
        self.assertIn("results", res)
        self.assertIn("mode", res)
        self.assertEqual(res["mode"], "hybrid_graph_vector")

if __name__ == "__main__":
    unittest.main()
