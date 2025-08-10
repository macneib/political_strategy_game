"""
Tests for the Personality Drift Detection and Correction system.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from collections import deque

from src.llm.personality_drift import (
    PersonalityDriftDetector, PersonalitySnapshot, PersonalityDrift,
    PersonalityAspect, DriftSeverity, CorrectionStrategy, CorrectionAttempt,
    PersonalityProfile
)
from src.llm.advisors import AdvisorRole, AdvisorPersonality, AdvisorAI
from src.llm.dialogue import EmotionalState
from src.llm.llm_providers import LLMMessage, LLMResponse, LLMProvider


class TestPersonalitySnapshot:
    def test_snapshot_creation(self):
        """Test creating a personality snapshot."""
        snapshot = PersonalitySnapshot(
            timestamp=datetime.now(),
            advisor_name="General Marcus",
            personality_aspects={
                PersonalityAspect.COMMUNICATION_STYLE: 0.8,
                PersonalityAspect.DECISION_MAKING: 0.9
            },
            recent_responses=["Strategic analysis", "Military recommendation"],
            emotional_baseline={"current_emotion": "confident", "intensity": 0.7}
        )
        
        assert snapshot.advisor_name == "General Marcus"
        assert snapshot.personality_aspects[PersonalityAspect.COMMUNICATION_STYLE] == 0.8
        assert len(snapshot.recent_responses) == 2
        assert snapshot.emotional_baseline["current_emotion"] == "confident"
    
    def test_aspect_score_calculation(self):
        """Test calculating aspect scores from responses."""
        snapshot = PersonalitySnapshot(
            timestamp=datetime.now(),
            advisor_name="Test Advisor",
            recent_responses=["Strategic military analysis", "Defensive tactical planning"]
        )
        
        military_traits = ["strategic", "tactical", "military"]
        score = snapshot.calculate_aspect_score(PersonalityAspect.DECISION_MAKING, military_traits)
        
        assert 0.0 <= score <= 1.0
        assert score >= 0.5  # Should be at or above baseline due to trait matches


class TestPersonalityDrift:
    def test_drift_creation(self):
        """Test creating a personality drift instance."""
        baseline_snapshot = PersonalitySnapshot(
            timestamp=datetime.now() - timedelta(days=10),
            advisor_name="Test Advisor",
            personality_aspects={PersonalityAspect.COMMUNICATION_STYLE: 0.9}
        )
        
        current_snapshot = PersonalitySnapshot(
            timestamp=datetime.now(),
            advisor_name="Test Advisor",
            personality_aspects={PersonalityAspect.COMMUNICATION_STYLE: 0.4}
        )
        
        drift = PersonalityDrift(
            advisor_name="Test Advisor",
            aspect=PersonalityAspect.COMMUNICATION_STYLE,
            severity=DriftSeverity.SIGNIFICANT,
            drift_percentage=50.0,
            detection_timestamp=datetime.now(),
            baseline_snapshot=baseline_snapshot,
            current_snapshot=current_snapshot,
            specific_changes=["Communication became less formal", "Decision style changed"],
            potential_causes=["Stress", "External pressure"]
        )
        
        assert drift.advisor_name == "Test Advisor"
        assert drift.aspect == PersonalityAspect.COMMUNICATION_STYLE
        assert drift.severity == DriftSeverity.SIGNIFICANT
        assert drift.drift_percentage == 50.0
        assert len(drift.specific_changes) == 2
        assert len(drift.potential_causes) == 2
    
    def test_drift_description(self):
        """Test getting drift description."""
        drift = PersonalityDrift(
            advisor_name="General Marcus",
            aspect=PersonalityAspect.DECISION_MAKING,
            severity=DriftSeverity.MODERATE,
            drift_percentage=35.0,
            detection_timestamp=datetime.now(),
            baseline_snapshot=Mock(),
            current_snapshot=Mock()
        )
        
        description = drift.get_drift_description()
        assert "General Marcus" in description
        assert "moderate drift" in description
        assert "decision_making" in description
        assert "35.0%" in description


class TestPersonalityProfile:
    def test_profile_creation(self):
        """Test creating a personality profile."""
        profile = PersonalityProfile(
            advisor_name="Diplomat Elena",
            baseline_traits={"communication_consistency": 0.9, "value_consistency": 0.8},
            expected_responses={"diplomatic": ["negotiation", "peaceful resolution"]},
            communication_patterns=["Diplomatic", "Eloquent"],
            value_indicators=["Peace", "Cooperation"]
        )
        
        assert profile.advisor_name == "Diplomat Elena"
        assert profile.baseline_traits["communication_consistency"] == 0.9
        assert "negotiation" in profile.expected_responses["diplomatic"]
        assert "Diplomatic" in profile.communication_patterns
        assert "Peace" in profile.value_indicators
    
    def test_baseline_update(self):
        """Test updating baseline from snapshot."""
        profile = PersonalityProfile(advisor_name="Test Advisor")
        
        snapshot = PersonalitySnapshot(
            timestamp=datetime.now(),
            advisor_name="Test Advisor",
            personality_aspects={
                PersonalityAspect.COMMUNICATION_STYLE: 0.8,
                PersonalityAspect.DECISION_MAKING: 0.7
            },
            recent_responses=["New response pattern", "Updated behavior"]
        )
        
        original_calibration = profile.last_calibration
        profile.update_baseline(snapshot)
        
        assert profile.last_calibration > original_calibration
        assert "communication_style_consistency" in profile.baseline_traits
        assert "recent_patterns" in profile.expected_responses


class TestPersonalityDriftDetector:
    @pytest.fixture
    def mock_llm_manager(self):
        """Create a mock LLM manager."""
        llm_manager = Mock()
        llm_manager.generate = AsyncMock()
        return llm_manager
    
    @pytest.fixture
    def mock_dialogue_system(self):
        """Create a mock dialogue system."""
        dialogue_system = Mock()
        dialogue_system.advisor_council = Mock()
        
        # Create mock advisors
        general_personality = AdvisorPersonality(
            name="General Marcus",
            role=AdvisorRole.MILITARY,
            background="Military strategist",
            personality_traits=["Strategic", "Disciplined", "Loyal"],
            communication_style="Direct and formal",
            expertise_areas=["Military tactics", "Strategic planning"]
        )
        
        general = AdvisorAI(
            personality=general_personality,
            llm_manager=Mock()
        )
        
        dialogue_system.advisor_council.advisors = {"General Marcus": general}
        dialogue_system.get_advisor_emotional_state = Mock(return_value={
            "emotion": "confident",
            "intensity": 0.7
        })
        
        return dialogue_system
    
    @pytest.fixture
    def drift_detector(self, mock_llm_manager, mock_dialogue_system):
        """Create a personality drift detector."""
        return PersonalityDriftDetector(
            llm_manager=mock_llm_manager,
            dialogue_system=mock_dialogue_system
        )
    
    def test_initialization(self, drift_detector):
        """Test detector initialization."""
        assert drift_detector.personality_profiles == {}
        assert len(drift_detector.personality_history) == 0
        assert drift_detector.detected_drifts == []
        assert drift_detector.correction_attempts == []
        assert DriftSeverity.MODERATE in drift_detector.drift_thresholds
    
    def test_initialize_personality_profiles(self, drift_detector, mock_dialogue_system):
        """Test initializing personality profiles for advisors."""
        drift_detector.initialize_personality_profiles(mock_dialogue_system.advisor_council)
        
        assert "General Marcus" in drift_detector.personality_profiles
        profile = drift_detector.personality_profiles["General Marcus"]
        
        assert profile.advisor_name == "General Marcus"
        assert "communication_consistency" in profile.baseline_traits
        assert "role_based" in profile.expected_responses
        assert "Direct and formal" in profile.communication_patterns
        assert "Strategic" in profile.value_indicators
    
    def test_get_role_based_responses(self, drift_detector):
        """Test getting role-based response patterns."""
        military_responses = drift_detector._get_role_based_responses(AdvisorRole.MILITARY)
        diplomatic_responses = drift_detector._get_role_based_responses(AdvisorRole.DIPLOMATIC)
        
        assert "strategic thinking" in military_responses
        assert "tactical analysis" in military_responses
        assert "diplomatic relations" in diplomatic_responses
        assert "negotiation" in diplomatic_responses
    
    @pytest.mark.asyncio
    async def test_capture_personality_snapshot(self, drift_detector, mock_dialogue_system):
        """Test capturing a personality snapshot."""
        # Initialize profiles first
        drift_detector.initialize_personality_profiles(mock_dialogue_system.advisor_council)
        
        # Mock LLM response for personality analysis
        aspect_scores = {
            "communication_style": 0.8,
            "decision_making": 0.9,
            "emotional_responses": 0.7,
            "value_system": 0.8,
            "social_interactions": 0.6,
            "risk_tolerance": 0.7,
            "leadership_style": 0.9,
            "conflict_resolution": 0.8
        }
        
        drift_detector.llm_manager.generate.return_value = LLMResponse(
            content=str(aspect_scores).replace("'", '"'),
            provider=LLMProvider.OPENAI,
            model="mock-model"
        )
        
        # Mock recent interactions
        with patch.object(drift_detector, '_get_recent_interactions', return_value=[
            "Strategic military analysis", "Tactical defense recommendation"
        ]):
            snapshot = await drift_detector.capture_personality_snapshot("General Marcus")
        
        assert snapshot.advisor_name == "General Marcus"
        assert PersonalityAspect.COMMUNICATION_STYLE in snapshot.personality_aspects
        assert PersonalityAspect.DECISION_MAKING in snapshot.personality_aspects
        assert snapshot.emotional_baseline["current_emotion"] == "confident"
        assert len(drift_detector.personality_history["General Marcus"]) == 1
    
    @pytest.mark.asyncio
    async def test_analyze_personality_aspects(self, drift_detector, mock_dialogue_system):
        """Test analyzing personality aspects with LLM."""
        drift_detector.initialize_personality_profiles(mock_dialogue_system.advisor_council)
        
        advisor = mock_dialogue_system.advisor_council.advisors["General Marcus"]
        snapshot = PersonalitySnapshot(
            timestamp=datetime.now(),
            advisor_name="General Marcus",
            recent_responses=["Direct military advice", "Strategic planning input"],
            emotional_baseline={"current_emotion": "confident", "intensity": 0.7}
        )
        
        # Mock LLM response
        aspect_scores = {
            "communication_style": 0.9,
            "decision_making": 0.8,
            "emotional_responses": 0.7,
            "value_system": 0.8,
            "social_interactions": 0.6,
            "risk_tolerance": 0.7,
            "leadership_style": 0.9,
            "conflict_resolution": 0.8
        }
        
        drift_detector.llm_manager.generate.return_value = LLMResponse(
            content=str(aspect_scores).replace("'", '"'),
            provider=LLMProvider.OPENAI,
            model="mock-model"
        )
        
        result = await drift_detector._analyze_personality_aspects(advisor, snapshot)
        
        assert len(result) == len(PersonalityAspect)
        assert all(0.0 <= score <= 1.0 for score in result.values())
        assert PersonalityAspect.COMMUNICATION_STYLE in result
        assert result[PersonalityAspect.COMMUNICATION_STYLE] == 0.9
    
    @pytest.mark.asyncio
    async def test_detect_personality_drift(self, drift_detector, mock_dialogue_system):
        """Test detecting personality drift."""
        drift_detector.initialize_personality_profiles(mock_dialogue_system.advisor_council)
        
        # Create baseline snapshot
        baseline_snapshot = PersonalitySnapshot(
            timestamp=datetime.now() - timedelta(days=10),
            advisor_name="General Marcus",
            personality_aspects={
                PersonalityAspect.COMMUNICATION_STYLE: 0.9,
                PersonalityAspect.DECISION_MAKING: 0.8
            }
        )
        
        # Create current snapshot with significant drift
        current_snapshot = PersonalitySnapshot(
            timestamp=datetime.now(),
            advisor_name="General Marcus",
            personality_aspects={
                PersonalityAspect.COMMUNICATION_STYLE: 0.3,  # Significant drift
                PersonalityAspect.DECISION_MAKING: 0.7      # Slight drift
            }
        )
        
        # Add snapshots to history
        drift_detector.personality_history["General Marcus"].extend([baseline_snapshot, current_snapshot])
        
        # Mock LLM responses for analysis
        drift_detector.llm_manager.generate.side_effect = [
            # Specific changes analysis
            LLMResponse(
                content='["Communication became less formal", "Decision style changed"]',
                provider=LLMProvider.OPENAI,
                model="mock-model"
            ),
            # Drift causes analysis
            LLMResponse(
                content='["Emotional stress", "External pressures", "Recent conflicts"]',
                provider=LLMProvider.OPENAI,
                model="mock-model"
            ),
            # Second round for decision making aspect
            LLMResponse(
                content='["Decision patterns shifted", "Less strategic thinking"]',
                provider=LLMProvider.OPENAI,
                model="mock-model"
            ),
            LLMResponse(
                content='["Workload pressure", "Time constraints"]',
                provider=LLMProvider.OPENAI,
                model="mock-model"
            )
        ]
        
        detected_drifts = await drift_detector.detect_personality_drift("General Marcus")
        
        assert len(detected_drifts) == 2  # Should detect drift in both aspects
        
        communication_drift = next(d for d in detected_drifts if d.aspect == PersonalityAspect.COMMUNICATION_STYLE)
        assert communication_drift.severity == DriftSeverity.SIGNIFICANT
        assert abs(communication_drift.drift_percentage - 60.0) < 0.01  # Handle floating point precision
        
        decision_drift = next(d for d in detected_drifts if d.aspect == PersonalityAspect.DECISION_MAKING)
        assert decision_drift.severity == DriftSeverity.SLIGHT
    
    def test_calculate_drift_severity(self, drift_detector):
        """Test calculating drift severity."""
        assert drift_detector._calculate_drift_severity(0.05) == DriftSeverity.MINIMAL
        assert drift_detector._calculate_drift_severity(0.15) == DriftSeverity.SLIGHT
        assert drift_detector._calculate_drift_severity(0.35) == DriftSeverity.MODERATE
        assert drift_detector._calculate_drift_severity(0.60) == DriftSeverity.SIGNIFICANT
        assert drift_detector._calculate_drift_severity(0.80) == DriftSeverity.SEVERE
    
    def test_select_correction_strategy(self, drift_detector):
        """Test selecting appropriate correction strategy."""
        minimal_drift = Mock()
        minimal_drift.severity = DriftSeverity.MINIMAL
        
        moderate_drift = Mock()
        moderate_drift.severity = DriftSeverity.MODERATE
        
        significant_drift = Mock()
        significant_drift.severity = DriftSeverity.SIGNIFICANT
        
        severe_drift = Mock()
        severe_drift.severity = DriftSeverity.SEVERE
        
        assert drift_detector._select_correction_strategy(minimal_drift) == CorrectionStrategy.REINFORCEMENT_PROMPTING
        assert drift_detector._select_correction_strategy(moderate_drift) == CorrectionStrategy.CONTEXT_INJECTION
        assert drift_detector._select_correction_strategy(significant_drift) == CorrectionStrategy.HISTORICAL_ANCHORING
        assert drift_detector._select_correction_strategy(severe_drift) == CorrectionStrategy.PERSONALITY_RESET
    
    @pytest.mark.asyncio
    async def test_apply_personality_correction(self, drift_detector, mock_dialogue_system):
        """Test applying personality correction."""
        drift_detector.initialize_personality_profiles(mock_dialogue_system.advisor_council)
        
        # Create a drift to correct
        baseline_snapshot = PersonalitySnapshot(
            timestamp=datetime.now() - timedelta(days=5),
            advisor_name="General Marcus",
            personality_aspects={PersonalityAspect.COMMUNICATION_STYLE: 0.9}
        )
        
        current_snapshot = PersonalitySnapshot(
            timestamp=datetime.now() - timedelta(hours=1),
            advisor_name="General Marcus",
            personality_aspects={PersonalityAspect.COMMUNICATION_STYLE: 0.55}
        )
        
        drift = PersonalityDrift(
            advisor_name="General Marcus",
            aspect=PersonalityAspect.COMMUNICATION_STYLE,
            severity=DriftSeverity.MODERATE,
            drift_percentage=35.0,
            detection_timestamp=datetime.now(),
            baseline_snapshot=baseline_snapshot,
            current_snapshot=current_snapshot
        )
        
        # Mock correction generation
        drift_detector.llm_manager.generate.side_effect = [
            # Context injection generation
            LLMResponse(
                content="Personality Reminder: Maintain your direct and formal communication style as established.",
                provider=LLMProvider.OPENAI,
                model="mock-model"
            ),
            # Post-correction snapshot analysis
            LLMResponse(
                content='{"communication_style": 0.8, "decision_making": 0.7, "emotional_responses": 0.6, "value_system": 0.7, "social_interactions": 0.5, "risk_tolerance": 0.6, "leadership_style": 0.8, "conflict_resolution": 0.7}',
                provider=LLMProvider.OPENAI,
                model="mock-model"
            )
        ]
        
        # Mock recent interactions for post-correction snapshot
        with patch.object(drift_detector, '_get_recent_interactions', return_value=[
            "Corrected military advice", "Improved strategic input"
        ]):
            correction = await drift_detector.apply_personality_correction(drift, CorrectionStrategy.CONTEXT_INJECTION)
        
        assert correction.advisor_name == "General Marcus"
        assert correction.strategy == CorrectionStrategy.CONTEXT_INJECTION
        assert correction.target_drift == drift
        assert correction.success_rate is not None
        assert 0.0 <= correction.success_rate <= 1.0
        assert len(correction.applied_corrections) > 0
    
    def test_process_personality_monitoring_turn(self, drift_detector):
        """Test processing one turn of personality monitoring."""
        # Add some mock detected drifts
        severe_drift = PersonalityDrift(
            advisor_name="General Marcus",
            aspect=PersonalityAspect.COMMUNICATION_STYLE,
            severity=DriftSeverity.SEVERE,
            drift_percentage=80.0,
            detection_timestamp=datetime.now(),
            baseline_snapshot=Mock(),
            current_snapshot=Mock()
        )
        
        drift_detector.detected_drifts.append(severe_drift)
        
        results = drift_detector.process_personality_monitoring_turn(["General Marcus", "Diplomat Elena"])
        
        assert "snapshots_captured" in results
        assert "drifts_detected" in results
        assert "corrections_applied" in results
        assert "monitoring_summary" in results
        
        assert "General Marcus" in results["snapshots_captured"]
        assert "Diplomat Elena" in results["snapshots_captured"]
        assert len(results["drifts_detected"]) > 0
    
    def test_calculate_personality_stability(self, drift_detector):
        """Test calculating personality stability."""
        # Create history with stable personality
        stable_snapshots = [
            PersonalitySnapshot(
                timestamp=datetime.now() - timedelta(days=i),
                advisor_name="Test Advisor",
                personality_aspects={
                    PersonalityAspect.COMMUNICATION_STYLE: 0.8 + (i * 0.01),  # Very stable
                    PersonalityAspect.DECISION_MAKING: 0.7 + (i * 0.02)
                }
            )
            for i in range(5)
        ]
        
        drift_detector.personality_history["Test Advisor"].extend(stable_snapshots)
        
        stability = drift_detector._calculate_personality_stability("Test Advisor")
        assert 0.0 <= stability <= 1.0
        assert stability > 0.8  # Should be high for stable personality
        
        # Test with insufficient data
        empty_stability = drift_detector._calculate_personality_stability("Unknown Advisor")
        assert empty_stability == 1.0
    
    def test_get_personality_drift_summary_specific_advisor(self, drift_detector):
        """Test getting drift summary for specific advisor."""
        # Add mock data
        drift = PersonalityDrift(
            advisor_name="General Marcus",
            aspect=PersonalityAspect.COMMUNICATION_STYLE,
            severity=DriftSeverity.MODERATE,
            drift_percentage=35.0,
            detection_timestamp=datetime.now(),
            baseline_snapshot=Mock(),
            current_snapshot=Mock()
        )
        
        correction = CorrectionAttempt(
            correction_id="test_correction",
            advisor_name="General Marcus",
            strategy=CorrectionStrategy.CONTEXT_INJECTION,
            target_drift=drift,
            success_rate=0.8
        )
        
        drift_detector.detected_drifts.append(drift)
        drift_detector.correction_attempts.append(correction)
        
        # Add stable personality history
        stable_snapshots = [
            PersonalitySnapshot(
                timestamp=datetime.now() - timedelta(days=i),
                advisor_name="General Marcus",
                personality_aspects={PersonalityAspect.COMMUNICATION_STYLE: 0.8}
            )
            for i in range(3)
        ]
        drift_detector.personality_history["General Marcus"].extend(stable_snapshots)
        
        summary = drift_detector.get_personality_drift_summary("General Marcus")
        
        assert summary["advisor_name"] == "General Marcus"
        assert summary["total_drifts_detected"] == 1
        assert summary["corrections_attempted"] == 1
        assert summary["correction_success_rate"] == 0.8
        assert len(summary["recent_drifts"]) == 1
        assert summary["personality_stability"] > 0.0
    
    def test_get_personality_drift_summary_overall(self, drift_detector):
        """Test getting overall system drift summary."""
        # Add mock profiles
        drift_detector.personality_profiles["General Marcus"] = PersonalityProfile(advisor_name="General Marcus")
        drift_detector.personality_profiles["Diplomat Elena"] = PersonalityProfile(advisor_name="Diplomat Elena")
        
        # Add mock drifts
        drifts = [
            PersonalityDrift(
                advisor_name="General Marcus",
                aspect=PersonalityAspect.COMMUNICATION_STYLE,
                severity=DriftSeverity.MODERATE,
                drift_percentage=35.0,
                detection_timestamp=datetime.now(),
                baseline_snapshot=Mock(),
                current_snapshot=Mock()
            ),
            PersonalityDrift(
                advisor_name="Diplomat Elena",
                aspect=PersonalityAspect.DECISION_MAKING,
                severity=DriftSeverity.SLIGHT,
                drift_percentage=20.0,
                detection_timestamp=datetime.now(),
                baseline_snapshot=Mock(),
                current_snapshot=Mock()
            )
        ]
        
        correction = CorrectionAttempt(
            correction_id="test_correction",
            advisor_name="General Marcus",
            strategy=CorrectionStrategy.CONTEXT_INJECTION,
            target_drift=drifts[0],
            success_rate=0.7
        )
        
        drift_detector.detected_drifts.extend(drifts)
        drift_detector.correction_attempts.append(correction)
        
        summary = drift_detector.get_personality_drift_summary()
        
        assert summary["total_advisors_monitored"] == 2
        assert summary["total_drifts_detected"] == 2
        assert summary["total_corrections_applied"] == 1
        assert summary["average_correction_success"] == 0.7
        assert summary["advisors_with_active_drifts"] == 2
        assert "drift_severity_distribution" in summary
        assert "most_common_drift_aspects" in summary


if __name__ == "__main__":
    pytest.main([__file__])
