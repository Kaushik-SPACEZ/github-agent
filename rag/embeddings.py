"""
Code Embeddings Module
======================
Handles code chunking and embedding generation for RAG.

Embedding strategy (in priority order):
  1. sentence-transformers (if installed + model downloadable)
  2. TF-IDF + TruncatedSVD — semantic 384-dim vectors, no download needed
  3. Random dummy vectors (last resort, for testing only)
"""

import ast
import re
from typing import List, Dict, Tuple
import numpy as np


class CodeEmbedder:
    """
    Generates embeddings for code chunks.

    Uses sentence-transformers when available, falls back to a
    TF-IDF + TruncatedSVD pipeline (sklearn) that produces
    genuine 384-dimensional semantic vectors without any network
    download — so RAG works fully in offline / restricted environments.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize code embedder.

        Args:
            model_name: sentence-transformers model name (used if reachable)
        """
        self.model_name = model_name
        self.model = None
        self.dimension = 384

        # ── Strategy 1: sentence-transformers ────────────────────
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"[RAG] ✅ Loaded sentence-transformers model: {model_name} (dim={self.dimension})")
            return
        except ImportError:
            print("[RAG] sentence-transformers not installed.")
        except Exception as e:
            print(f"[RAG] Could not load sentence-transformers model: {e}")

        # ── Strategy 2: TF-IDF + TruncatedSVD (sklearn) ──────────
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.decomposition import TruncatedSVD
            from sklearn.pipeline import Pipeline

            self._tfidf_pipeline = Pipeline([
                ("tfidf", TfidfVectorizer(
                    analyzer="word",
                    token_pattern=r"[A-Za-z_][A-Za-z0-9_]*",  # code tokens
                    max_features=8000,
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                )),
                ("svd", TruncatedSVD(n_components=self.dimension, random_state=42)),
            ])
            self._tfidf_fitted = False
            self._fit_corpus: List[str] = []  # accumulates texts seen so far
            print(f"[RAG] ✅ Using TF-IDF + TruncatedSVD embeddings (dim={self.dimension})")
            return
        except ImportError:
            print("[RAG] sklearn not available.")

        # ── Strategy 3: random dummy vectors ─────────────────────
        print("[RAG] ⚠️  Falling back to random embeddings (for testing only).")
        self._tfidf_pipeline = None
        self._tfidf_fitted = False
    
    # ── Chunking ──────────────────────────────────────────────────

    def chunk_code(self, code: str, filename: str, chunk_size: int = 500) -> List[Dict]:
        """
        Split code into chunks, preferring AST-based boundaries.

        Tries ast.parse first (preserves exact function/class boundaries).
        Falls back to line-based splitting if the file has syntax errors.

        Args:
            code: Source code string
            filename: Name of the file
            chunk_size: Maximum characters per chunk (used by fallback only)

        Returns:
            List of chunk dicts with metadata
        """
        chunks = self._chunk_ast(code, filename)
        if chunks:
            print(f"[RAG] Chunked {filename} into {len(chunks)} AST chunks")
            return chunks

        # fallback for files with syntax errors
        chunks = self._chunk_lines(code, filename, chunk_size)
        print(f"[RAG] Chunked {filename} into {len(chunks)} line-based chunks (AST failed)")
        return chunks

    def _chunk_ast(self, code: str, filename: str) -> List[Dict]:
        """AST-based chunking: one chunk per top-level function/class."""
        chunks = []
        try:
            tree = ast.parse(code)
            lines = code.splitlines()
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    # Only top-level nodes (avoid nested duplicates)
                    if not any(
                        isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                        for parent in ast.walk(tree)
                        if parent is not node
                        and hasattr(parent, "lineno")
                        and parent.lineno <= node.lineno
                        and hasattr(parent, "end_lineno")
                        and parent.end_lineno >= node.end_lineno
                        and parent is not node
                    ):
                        start = node.lineno - 1
                        end = node.end_lineno
                        chunk_text = "\n".join(lines[start:end])
                        chunks.append({
                            "text": chunk_text,
                            "filename": filename,
                            "chunk_id": len(chunks),
                            "start_line": node.lineno,
                            "end_line": node.end_lineno,
                            "node_type": type(node).__name__,
                            "name": node.name,
                            "size": len(chunk_text),
                        })
        except SyntaxError:
            return []
        return chunks

    def _chunk_lines(self, code: str, filename: str, chunk_size: int) -> List[Dict]:
        """Line-based fallback chunker (original logic)."""
        chunks = []
        lines = code.split("\n")
        current_chunk: List[str] = []
        current_size = 0
        chunk_id = 0

        for i, line in enumerate(lines):
            line_size = len(line) + 1
            if (current_size + line_size > chunk_size and current_chunk) or \
               line.strip().startswith(("def ", "class ", "async def ")):
                if current_chunk:
                    chunk_text = "\n".join(current_chunk)
                    chunks.append({
                        "text": chunk_text,
                        "filename": filename,
                        "chunk_id": chunk_id,
                        "start_line": i - len(current_chunk) + 1,
                        "end_line": i,
                        "node_type": "block",
                        "name": f"block_{chunk_id}",
                        "size": current_size,
                    })
                    chunk_id += 1
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size

        if current_chunk:
            chunk_text = "\n".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "filename": filename,
                "chunk_id": chunk_id,
                "start_line": len(lines) - len(current_chunk) + 1,
                "end_line": len(lines),
                "node_type": "block",
                "name": f"block_{chunk_id}",
                "size": current_size,
            })
        return chunks

    # ── Embedding ─────────────────────────────────────────────────

    def _fit_tfidf(self, texts: List[str]):
        """Fit the TF-IDF pipeline on a corpus of texts."""
        if not hasattr(self, "_tfidf_pipeline") or self._tfidf_pipeline is None:
            return
        # Accumulate all texts seen so far and refit
        self._fit_corpus.extend(texts)
        if len(self._fit_corpus) < 2:
            return
        # Fit TF-IDF first to know actual vocabulary size, then cap SVD components
        from sklearn.feature_extraction.text import TfidfVectorizer
        tfidf_step = self._tfidf_pipeline.named_steps["tfidf"]
        tfidf_step.fit(self._fit_corpus)
        n_features = len(tfidf_step.vocabulary_)
        # n_components must be < min(n_samples, n_features)
        n_components = min(self.dimension, n_features - 1, len(self._fit_corpus) - 1)
        if n_components < 1:
            return
        self._tfidf_pipeline.set_params(svd__n_components=n_components)
        self._tfidf_pipeline.fit(self._fit_corpus)
        self._tfidf_fitted = True

    def _tfidf_encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts with TF-IDF pipeline, padding to self.dimension."""
        if not self._tfidf_fitted:
            self._fit_tfidf(texts)
        if not self._tfidf_fitted:
            return self._dummy_embeddings(len(texts))
        raw = self._tfidf_pipeline.transform(texts).astype("float32")
        # Pad or trim to self.dimension
        if raw.shape[1] < self.dimension:
            pad = np.zeros((raw.shape[0], self.dimension - raw.shape[1]), dtype="float32")
            raw = np.hstack([raw, pad])
        else:
            raw = raw[:, : self.dimension]
        # L2-normalise
        norms = np.linalg.norm(raw, axis=1, keepdims=True)
        return raw / (norms + 1e-8)

    def _dummy_embeddings(self, n: int) -> np.ndarray:
        """Random normalised vectors — last-resort fallback."""
        emb = np.random.randn(n, self.dimension).astype("float32")
        norms = np.linalg.norm(emb, axis=1, keepdims=True)
        return emb / (norms + 1e-8)

    def embed_chunks(self, chunks: List[Dict]) -> np.ndarray:
        """
        Generate embeddings for a list of code chunks.

        Args:
            chunks: List of chunk dicts (must have 'text' field)

        Returns:
            np.ndarray of shape (n_chunks, dimension)
        """
        texts = [c["text"] for c in chunks]

        if self.model is not None:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            return np.array(embeddings, dtype="float32")

        if hasattr(self, "_tfidf_pipeline") and self._tfidf_pipeline is not None:
            if not self._tfidf_fitted:
                self._fit_tfidf(texts)
            return self._tfidf_encode(texts)

        return self._dummy_embeddings(len(texts))

    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query string.

        Args:
            query: Query text

        Returns:
            np.ndarray of shape (1, dimension)
        """
        if self.model is not None:
            embedding = self.model.encode([query], show_progress_bar=False)
            return np.array(embedding, dtype="float32")

        if hasattr(self, "_tfidf_pipeline") and self._tfidf_pipeline is not None:
            if self._tfidf_fitted:
                return self._tfidf_encode([query])
            # Pipeline not fitted yet — return a dummy so retrieval returns []
            return self._dummy_embeddings(1)

        return self._dummy_embeddings(1)

    def process_repository(self, python_files: List[Dict]) -> Tuple[np.ndarray, List[Dict]]:
        """
        Chunk and embed all Python files in a repository.

        Args:
            python_files: List of dicts with 'filename' and 'content'

        Returns:
            Tuple of (embeddings np.ndarray, metadata list)
        """
        all_chunks: List[Dict] = []

        for file_info in python_files:
            chunks = self.chunk_code(file_info["content"], file_info["filename"])
            all_chunks.extend(chunks)

        if not all_chunks:
            return np.array([]), []

        # Fit TF-IDF on the full corpus before embedding
        if (
            self.model is None
            and hasattr(self, "_tfidf_pipeline")
            and self._tfidf_pipeline is not None
            and not self._tfidf_fitted
        ):
            self._fit_tfidf([c["text"] for c in all_chunks])

        embeddings = self.embed_chunks(all_chunks)
        print(f"[RAG] Generated {len(embeddings)} embeddings for repository")
        return embeddings, all_chunks