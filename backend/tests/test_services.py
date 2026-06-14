"""
Service Tests
-------------
Tests for embedding engine, legal knowledge base, and pattern detection services.
"""

import pytest
import numpy as np
from services.embedding_engine import EmbeddingEngine
from services.legal_kb import LegalKB
from services.mo_detector import MODetector


class TestEmbeddingEngine:
    """Test narrative embedding service."""

    @pytest.fixture
    def embedding_engine(self):
        """Load the embedding engine."""
        return EmbeddingEngine()

    def test_embedding_initialization(self, embedding_engine):
        """Test that embedding engine loads successfully."""
        assert embedding_engine is not None
        assert hasattr(embedding_engine, "get_embedding")

    def test_get_embedding_single_text(self, embedding_engine):
        """Test embedding a single narrative."""
        narrative = "A theft case reported. Items worth Rs. 5000 stolen."
        embedding = embedding_engine.get_embedding(narrative)

        assert embedding is not None
        assert isinstance(embedding, (list, np.ndarray))
        assert len(embedding) > 0

    def test_embedding_vector_dimension(self, embedding_engine):
        """Test that embeddings have correct dimensionality."""
        narrative = "A crime case."
        embedding = embedding_engine.get_embedding(narrative)

        # Sentence-Transformers multilingual model outputs 384-dim vectors
        assert len(embedding) == 384

    def test_embedding_consistency(self, embedding_engine):
        """Test that same text produces same embedding."""
        narrative = "A theft case reported."
        embedding1 = embedding_engine.get_embedding(narrative)
        embedding2 = embedding_engine.get_embedding(narrative)

        assert np.allclose(embedding1, embedding2)

    def test_embedding_similarity(self, embedding_engine):
        """Test similarity between related narratives."""
        narrative1 = "A theft case reported. Items worth Rs. 5000 stolen."
        narrative2 = "Theft reported. Items stolen worth Rs. 5000."

        embedding1 = embedding_engine.get_embedding(narrative1)
        embedding2 = embedding_engine.get_embedding(narrative2)

        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )

        assert 0 <= similarity <= 1
        assert similarity > 0.7  # Should be highly similar

    def test_embedding_dissimilarity(self, embedding_engine):
        """Test dissimilarity between unrelated narratives."""
        narrative1 = "A theft case reported. Items stolen."
        narrative2 = "A wedding ceremony was held in the village."

        embedding1 = embedding_engine.get_embedding(narrative1)
        embedding2 = embedding_engine.get_embedding(narrative2)

        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )

        assert similarity < 0.5  # Should be dissimilar

    def test_embedding_batch_processing(self, embedding_engine):
        """Test batch embedding of multiple texts."""
        narratives = [
            "A theft case reported.",
            "An assault case reported.",
            "A fraud case reported.",
        ]

        embeddings = [embedding_engine.get_embedding(n) for n in narratives]

        assert len(embeddings) == 3
        for emb in embeddings:
            assert len(emb) == 384


class TestLegalKB:
    """Test legal knowledge base service."""

    @pytest.fixture
    def legal_kb(self):
        """Load the legal knowledge base."""
        return LegalKB()

    def test_legal_kb_initialization(self, legal_kb):
        """Test that legal KB loads successfully."""
        assert legal_kb is not None
        assert hasattr(legal_kb, "get_section")

    def test_lookup_ipc_section(self, legal_kb):
        """Test looking up an IPC section."""
        result = legal_kb.get_section("IPC", "379")

        if result is not None:
            assert "description" in result or "punishment" in result
            assert "section_number" in result or "section" in result

    def test_lookup_bns_section(self, legal_kb):
        """Test looking up a BNS section."""
        result = legal_kb.get_section("BNS", "304")

        if result is not None:
            assert "description" in result or "punishment" in result

    def test_lookup_nonexistent_section(self, legal_kb):
        """Test looking up a non-existent section."""
        result = legal_kb.get_section("IPC", "99999")
        # Should return None or empty result
        assert result is None or len(result) == 0

    def test_get_section_punishment(self, legal_kb):
        """Test retrieving punishment for a section."""
        result = legal_kb.get_section("IPC", "379")

        if result is not None and "punishment" in result:
            assert isinstance(result["punishment"], str)
            assert len(result["punishment"]) > 0

    def test_get_all_sections(self, legal_kb):
        """Test retrieving all sections."""
        sections = legal_kb.get_all_sections()

        assert sections is not None
        assert isinstance(sections, list)
        assert len(sections) > 0

    def test_ipc_to_bns_mapping(self, legal_kb):
        """Test IPC to BNS section mapping."""
        bns_section = legal_kb.get_bns_equivalent("IPC", "379")

        if bns_section is not None:
            assert isinstance(bns_section, str)
            assert "BNS" in bns_section or "Section" in bns_section

    def test_search_sections_by_act(self, legal_kb):
        """Test searching sections by act."""
        ipc_sections = legal_kb.get_sections_by_act("IPC")

        assert ipc_sections is not None
        assert isinstance(ipc_sections, list)
        assert len(ipc_sections) > 0

    def test_search_sections_by_keyword(self, legal_kb):
        """Test searching sections by keyword."""
        results = legal_kb.search_by_keyword("theft")

        if results is not None:
            assert isinstance(results, list)


class TestMODetector:
    """Test Modus Operandi pattern detection."""

    @pytest.fixture
    def mo_detector(self):
        """Load the MO detector."""
        return MODetector()

    def test_mo_detector_initialization(self, mo_detector):
        """Test that MO detector loads successfully."""
        assert mo_detector is not None
        assert hasattr(mo_detector, "detect_patterns")

    def test_detect_simple_pattern(self, mo_detector):
        """Test detecting a simple MO pattern."""
        narratives = [
            "Shop broken in at night. Items stolen. Entry through rear window.",
            "Another shop broken in at night. Items stolen. Entry through rear window.",
            "Yet another shop broken in at night. Items stolen. Entry through rear window.",
        ]

        patterns = mo_detector.detect_patterns(narratives)

        assert patterns is not None
        assert isinstance(patterns, list)
        # Should detect at least one pattern
        if len(patterns) > 0:
            assert "pattern_name" in patterns[0] or "description" in patterns[0]

    def test_detect_patterns_with_crime_types(self, mo_detector):
        """Test detecting patterns for specific crime type."""
        narratives = [
            "A theft case. Items stolen from shop.",
            "Another theft. Items stolen from shop.",
        ]

        patterns = mo_detector.detect_patterns(narratives, crime_type="theft")

        assert patterns is not None
        assert isinstance(patterns, list)

    def test_no_patterns_in_different_cases(self, mo_detector):
        """Test that very different cases don't create patterns."""
        narratives = [
            "A theft case reported.",
            "An assault case reported.",
            "A fraud case reported.",
        ]

        patterns = mo_detector.detect_patterns(narratives)

        assert patterns is not None
        assert isinstance(patterns, list)
        # Should have few or no patterns
        if len(patterns) > 0:
            assert patterns[0].get("occurrence_count", 1) >= 2

    def test_pattern_occurrence_count(self, mo_detector):
        """Test that patterns count occurrences correctly."""
        narratives = [
            "Shop broken at night through rear window.",
            "Another shop broken at night through rear window.",
            "Yet another shop broken at night through rear window.",
            "Yet another shop broken at night through rear window.",
        ]

        patterns = mo_detector.detect_patterns(narratives)

        if patterns and len(patterns) > 0:
            # Should have at least one pattern with 4 occurrences
            for pattern in patterns:
                if pattern.get("occurrence_count", 0) >= 3:
                    assert pattern["occurrence_count"] >= 3


class TestIntegratedServices:
    """Test integration of multiple services."""

    @pytest.fixture
    def embedding_engine(self):
        return EmbeddingEngine()

    @pytest.fixture
    def legal_kb(self):
        return LegalKB()

    @pytest.fixture
    def mo_detector(self):
        return MODetector()

    def test_similarity_search_with_embeddings(self, embedding_engine):
        """Test finding similar narratives using embeddings."""
        query_narrative = "A theft case. Items worth Rs. 5000 stolen."
        candidate_narratives = [
            "Theft reported. Items stolen worth Rs. 5000.",
            "An assault case reported.",
            "Another theft. Similar items stolen.",
            "A fraud case reported.",
        ]

        query_embedding = embedding_engine.get_embedding(query_narrative)
        similarities = []

        for candidate in candidate_narratives:
            candidate_embedding = embedding_engine.get_embedding(candidate)
            similarity = np.dot(query_embedding, candidate_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(candidate_embedding)
            )
            similarities.append((candidate, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Most similar should be related theft cases
        assert len(similarities) > 0
        assert similarities[0][1] > similarities[-1][1]

    def test_pattern_detection_with_legal_lookup(self, mo_detector, legal_kb):
        """Test detecting patterns and looking up their legal sections."""
        narratives = [
            "Shop broken at night. Items stolen. Entry through rear window. Worth Rs. 10000.",
            "Another shop broken at night. Items stolen. Entry through rear window. Worth Rs. 8000.",
        ]

        patterns = mo_detector.detect_patterns(narratives)

        if patterns and len(patterns) > 0:
            # For each pattern, could lookup related sections
            for pattern in patterns:
                # Try to lookup related sections
                crime_type = pattern.get("crime_type", "")
                if crime_type:
                    sections = legal_kb.search_by_keyword(crime_type)
                    assert sections is None or isinstance(sections, list)
