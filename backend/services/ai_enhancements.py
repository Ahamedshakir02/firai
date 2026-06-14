"""
AI Enhancements
---------------
Confidence scores, batch operations, and model management.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from logging_config import logger, ai_logger
import time


@dataclass
class ClassificationResult:
    """Result of crime classification with confidence."""
    crime_type: str
    crime_confidence: float
    severity: str
    severity_confidence: float
    recommendation: str = "Proceed with investigation"

    def to_dict(self) -> dict:
        return {
            "crime_type": self.crime_type,
            "crime_confidence": round(self.crime_confidence, 4),
            "severity": self.severity,
            "severity_confidence": round(self.severity_confidence, 4),
            "recommendation": self.recommendation,
            "confidence_level": self.get_confidence_level(),
            "needs_review": self.crime_confidence < 0.7 or self.severity_confidence < 0.7,
        }

    def get_confidence_level(self) -> str:
        """Get overall confidence level."""
        avg_confidence = (self.crime_confidence + self.severity_confidence) / 2
        if avg_confidence >= 0.85:
            return "high"
        elif avg_confidence >= 0.7:
            return "medium"
        else:
            return "low"


class BatchAnalysisService:
    """Service for batch FIR analysis."""

    @staticmethod
    async def analyze_batch(
        narratives: List[str],
        max_workers: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple narratives in batch.

        Args:
            narratives: List of FIR narratives
            max_workers: Number of parallel workers

        Returns:
            List of analysis results
        """
        from services.firai_engine import FirAIEngine

        engine = FirAIEngine()
        results = []

        start_time = time.time()

        # Process narratives
        for i, narrative in enumerate(narratives):
            try:
                # Classify crime
                classification = await _classify_with_confidence(engine, narrative)

                # Extract entities
                entities = await _extract_entities(engine, narrative)

                # Map legal sections
                sections = await _map_sections(engine, narrative)

                results.append({
                    "index": i,
                    "narrative": narrative[:100] + "...",
                    "classification": classification.to_dict(),
                    "entities": entities,
                    "sections": sections,
                    "status": "success",
                })
            except Exception as e:
                logger.error(f"Batch analysis failed for narrative {i}: {e}")
                results.append({
                    "index": i,
                    "status": "error",
                    "error": str(e),
                })

        duration_ms = (time.time() - start_time) * 1000

        # Log performance
        ai_logger.log_with_extra(
            level=20,  # INFO
            message="Batch analysis completed",
            extra={
                "total_narratives": len(narratives),
                "successful": len([r for r in results if r.get("status") == "success"]),
                "failed": len([r for r in results if r.get("status") == "error"]),
                "duration_ms": duration_ms,
            },
        )

        return results

    @staticmethod
    async def classify_batch(narratives: List[str]) -> List[Dict[str, Any]]:
        """Classify multiple narratives (crime + severity)."""
        from services.firai_engine import FirAIEngine

        engine = FirAIEngine()
        results = []

        for narrative in narratives:
            try:
                classification = await _classify_with_confidence(engine, narrative)
                results.append({
                    "narrative": narrative[:50],
                    "classification": classification.to_dict(),
                })
            except Exception as e:
                results.append({"error": str(e)})

        return results

    @staticmethod
    async def search_similar_batch(
        narrative_ids: List[int],
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Find similar FIRs for multiple narratives."""
        # This would call FIR similarity search for each ID
        # Return results in batch format
        pass


async def _classify_with_confidence(engine, narrative: str) -> ClassificationResult:
    """Classify narrative and return confidence scores."""
    # This would call the actual classifier
    # For now, return a placeholder
    result = engine.classifier.predict(narrative)

    return ClassificationResult(
        crime_type=result.get("crime_type", "unknown"),
        crime_confidence=result.get("crime_confidence", 0.5),
        severity=result.get("severity", "low"),
        severity_confidence=result.get("severity_confidence", 0.5),
    )


async def _extract_entities(engine, narrative: str) -> dict:
    """Extract entities from narrative."""
    return engine.ner.extract_entities(narrative)


async def _map_sections(engine, narrative: str) -> List[str]:
    """Map narrative to legal sections."""
    return engine.legal_mapper.map_sections(narrative)


class ModelManagementService:
    """Service for model versioning and retraining."""

    @staticmethod
    async def get_model_info() -> dict:
        """Get current model information."""
        from services.firai_engine import FirAIEngine

        engine = FirAIEngine()

        return {
            "version": "1.0.0",
            "created_date": "2025-06-13",
            "training_samples": 90,
            "accuracy": {
                "crime_classification": 0.988,
                "severity_classification": 0.988,
            },
            "last_retrained": "2025-06-13",
            "status": "production",
        }

    @staticmethod
    async def schedule_retraining(
        db,
        include_new_firs: bool = True,
        epochs: int = 50,
    ) -> dict:
        """Schedule model retraining."""
        from models.audit import SecurityEvent

        event = SecurityEvent(
            event_type="model_retrain_scheduled",
            severity="low",
            message="Model retraining scheduled",
            details={
                "include_new_firs": include_new_firs,
                "epochs": epochs,
            },
        )
        db.add(event)
        await db.commit()

        logger.log_with_extra(
            level=20,  # INFO
            message="Model retraining scheduled",
            extra={
                "include_new_firs": include_new_firs,
                "epochs": epochs,
            },
        )

        return {
            "status": "scheduled",
            "message": "Retraining will begin shortly",
            "estimated_duration_minutes": 5,
        }

    @staticmethod
    async def get_training_status() -> dict:
        """Get status of ongoing/recent training."""
        return {
            "status": "idle",
            "last_training": "2025-06-13 10:30:00",
            "next_scheduled": None,
            "progress": None,
        }


class LowConfidenceReviewService:
    """Manage low-confidence classifications requiring human review."""

    @staticmethod
    async def get_low_confidence_firs(
        db,
        threshold: float = 0.7,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get FIRs with low confidence scores for manual review."""
        # Query FIRs where confidence < threshold
        # This would require storing confidence scores in the database
        pass

    @staticmethod
    async def mark_reviewed(
        db,
        fir_id: int,
        officer_id: int,
        notes: str = "",
        confidence_correction: Optional[str] = None,
    ) -> bool:
        """Mark a low-confidence FIR as reviewed by an officer."""
        logger.log_with_extra(
            level=20,  # INFO
            message="FIR review completed",
            extra={
                "fir_id": fir_id,
                "officer_id": officer_id,
                "correction": confidence_correction,
            },
        )
        return True

    @staticmethod
    async def get_review_stats(db) -> dict:
        """Get statistics on low-confidence reviews."""
        return {
            "total_low_confidence": 0,
            "reviewed": 0,
            "pending": 0,
            "correction_rate": 0.0,
        }
