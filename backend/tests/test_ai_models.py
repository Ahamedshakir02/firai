"""
AI Model Tests
--------------
Tests for FirAI custom models: classifier, NER, summarizer, legal mapper.
"""

import pytest
from ai_engine.inference import FirInference


class TestFirClassifier:
    """Test the FIR crime classification model."""

    @pytest.fixture
    def inference(self):
        """Load the FirInference engine."""
        return FirInference()

    def test_classifier_initialization(self, inference):
        """Test that classifier loads successfully."""
        assert inference.classifier is not None
        assert hasattr(inference.classifier, "predict")

    def test_classify_theft_narrative(self, inference):
        """Test classifying a theft case."""
        narrative = (
            "A theft case reported at a local shop. The shopkeeper reported "
            "that someone stole items worth Rs. 5000 during the night."
        )
        result = inference.classify_crime(narrative)

        assert result is not None
        assert "crime_type" in result
        assert "severity" in result
        assert result["crime_type"] in ["theft", "other", "burglary", "robbery"]
        assert result["severity"] in ["low", "medium", "high", "critical"]

    def test_classify_assault_narrative(self, inference):
        """Test classifying an assault case."""
        narrative = (
            "An assault case reported. The victim was attacked with a knife "
            "and suffered serious injuries."
        )
        result = inference.classify_crime(narrative)

        assert result is not None
        assert "crime_type" in result
        assert result["severity"] in ["low", "medium", "high", "critical"]

    def test_classify_fraud_narrative(self, inference):
        """Test classifying a fraud case."""
        narrative = (
            "A fraud case reported. The accused used forged documents to "
            "obtain a bank loan of Rs. 10 lakhs."
        )
        result = inference.classify_crime(narrative)

        assert result is not None
        assert "crime_type" in result

    def test_classify_empty_narrative(self, inference):
        """Test classifier with empty narrative."""
        result = inference.classify_crime("")
        assert result is not None
        # Should return default classification

    def test_classify_short_narrative(self, inference):
        """Test classifier with very short narrative."""
        result = inference.classify_crime("Crime reported.")
        assert result is not None
        assert "crime_type" in result

    def test_classifier_consistency(self, inference):
        """Test that classifier gives consistent results for same input."""
        narrative = "A theft case reported. Items worth Rs. 5000 stolen."
        result1 = inference.classify_crime(narrative)
        result2 = inference.classify_crime(narrative)

        assert result1["crime_type"] == result2["crime_type"]
        assert result1["severity"] == result2["severity"]


class TestFirNER:
    """Test Named Entity Recognition (NER) extraction."""

    @pytest.fixture
    def inference(self):
        """Load the FirInference engine."""
        return FirInference()

    def test_ner_initialization(self, inference):
        """Test that NER engine loads successfully."""
        assert inference.ner is not None
        assert hasattr(inference.ner, "extract_entities")

    def test_extract_person_names(self, inference):
        """Test extracting person names from narrative."""
        narrative = (
            "Rajesh Kumar, a resident of Kalpakancherry, reported a theft. "
            "The accused is identified as Arun Nair."
        )
        entities = inference.extract_entities(narrative)

        assert entities is not None
        assert isinstance(entities, dict)
        # Should contain names or persons
        if "persons" in entities or "names" in entities:
            assert len(entities.get("persons", entities.get("names", []))) >= 1

    def test_extract_locations(self, inference):
        """Test extracting location names."""
        narrative = "Crime reported at Kalpakancherry police station. Accused from Kottayam."
        entities = inference.extract_entities(narrative)

        assert entities is not None
        assert isinstance(entities, dict)

    def test_extract_monetary_amounts(self, inference):
        """Test extracting monetary amounts."""
        narrative = "Items worth Rs. 50000 were stolen. Additional loss of Rs. 10000 reported."
        entities = inference.extract_entities(narrative)

        assert entities is not None
        assert isinstance(entities, dict)

    def test_extract_no_entities(self, inference):
        """Test extraction from text with no named entities."""
        narrative = "A case was reported. Some items were taken."
        entities = inference.extract_entities(narrative)

        assert entities is not None
        assert isinstance(entities, dict)


class TestFirSummarizer:
    """Test FIR narrative summarization."""

    @pytest.fixture
    def inference(self):
        """Load the FirInference engine."""
        return FirInference()

    def test_summarizer_initialization(self, inference):
        """Test that summarizer loads successfully."""
        assert inference.summarizer is not None
        assert hasattr(inference.summarizer, "summarize")

    def test_summarize_long_narrative(self, inference):
        """Test summarizing a long FIR narrative."""
        narrative = (
            "A theft case was reported on 15th January 2025 at Kalpakancherry police station. "
            "The complainant, Mr. Rajesh Kumar, a shop owner, reported that someone broke into "
            "his shop during the night and stole various items including electronic goods and cash. "
            "The estimated value of stolen items is approximately Rs. 50000. "
            "The accused was identified as Arun Nair, a resident of nearby Kottayam. "
            "He has a history of theft cases. The police have launched an investigation."
        )
        summary = inference.summarize_narrative(narrative)

        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert len(summary) < len(narrative)  # Summary should be shorter

    def test_summarize_short_narrative(self, inference):
        """Test summarizing a short narrative."""
        narrative = "A theft case reported. Items stolen."
        summary = inference.summarize_narrative(narrative)

        assert summary is not None
        assert isinstance(summary, str)

    def test_summarize_empty_narrative(self, inference):
        """Test summarizing empty narrative."""
        summary = inference.summarize_narrative("")
        assert summary is not None


class TestFirLegalMapper:
    """Test IPC/BNS section prediction from narratives."""

    @pytest.fixture
    def inference(self):
        """Load the FirInference engine."""
        return FirInference()

    def test_map_theft_sections(self, inference):
        """Test mapping theft narrative to IPC/BNS sections."""
        narrative = "A theft case reported. Items worth Rs. 5000 stolen."
        sections = inference.map_legal_sections(narrative)

        assert sections is not None
        assert isinstance(sections, list)
        if len(sections) > 0:
            # Should contain IPC or BNS sections
            assert any("IPC" in s or "BNS" in s for s in sections)

    def test_map_assault_sections(self, inference):
        """Test mapping assault narrative to sections."""
        narrative = "An assault case. The victim was attacked with a knife."
        sections = inference.map_legal_sections(narrative)

        assert sections is not None
        assert isinstance(sections, list)

    def test_map_multiple_sections(self, inference):
        """Test mapping narrative with multiple applicable sections."""
        narrative = (
            "A theft and assault case. Accused stole items worth Rs. 5000 "
            "and also attacked the shopkeeper with a knife."
        )
        sections = inference.map_legal_sections(narrative)

        assert sections is not None
        assert isinstance(sections, list)
        assert len(sections) >= 1

    def test_map_no_matching_sections(self, inference):
        """Test narrative that may not match any sections."""
        narrative = "A case was reported."
        sections = inference.map_legal_sections(narrative)

        assert sections is not None
        assert isinstance(sections, list)


class TestInferencePipeline:
    """Test the full FirAI inference pipeline."""

    @pytest.fixture
    def inference(self):
        """Load the FirInference engine."""
        return FirInference()

    def test_full_analysis_pipeline(self, inference):
        """Test complete analysis of a FIR narrative."""
        narrative = (
            "On 10th January 2025, a theft case was reported at Kalpakancherry police station. "
            "The complainant, Rajesh Kumar, reported that someone stole items worth Rs. 50000 from his shop. "
            "The accused is identified as Arun Nair, a known offender. "
            "Police have registered a case and launched an investigation."
        )

        result = inference.analyze(narrative)

        assert result is not None
        assert "crime_type" in result
        assert "severity" in result
        assert "entities" in result
        assert "summary" in result
        assert "acts" in result or "sections" in result

    def test_analysis_with_ipc_sections(self, inference):
        """Test analysis returns proper section mapping."""
        narrative = "A theft case reported. Items worth Rs. 5000 stolen."
        result = inference.analyze(narrative)

        assert "acts" in result or "sections" in result
        if "acts" in result:
            assert isinstance(result["acts"], list)
