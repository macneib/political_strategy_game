"""
Tests for advanced political mechanics.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.advanced_politics import (
    AdvancedPoliticalManager, ConspiracyNetwork, PoliticalFaction, SuccessionCandidate,
    PropagandaCampaign, PoliticalReform, ConspiracyType, FactionType, PoliticalIdeology,
    PropagandaType, SuccessionCrisisType, ConspiracyStatus
)
from src.core.civilization import Civilization
from src.core.leader import Leader, LeadershipStyle
from src.core.advisor_enhanced import AdvisorWithMemory
from src.core.advisor import AdvisorRole, PersonalityProfile


class TestAdvancedPoliticalManager:
    """Test the AdvancedPoliticalManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create a basic AdvancedPoliticalManager."""
        return AdvancedPoliticalManager(civilization_id="test_civ", current_turn=1)
    
    def test_manager_initialization(self, manager):
        """Test manager initializes correctly."""
        assert manager.civilization_id == "test_civ"
        assert manager.current_turn == 1
        assert len(manager.active_conspiracies) == 0
        assert len(manager.political_factions) == 0
        assert manager.political_temperature >= 0.0
        assert manager.information_reliability >= 0.0
    
    def test_create_faction(self, manager):
        """Test faction creation."""
        faction_id = manager.create_faction(
            name="Conservative Party",
            faction_type=FactionType.CONSERVATIVE,
            ideology=PoliticalIdeology.TRADITIONALISM,
            leader_id="advisor_1"
        )
        
        assert faction_id is not None
        assert len(manager.political_factions) == 1
        
        faction = manager._find_faction(faction_id)
        assert faction is not None
        assert faction.name == "Conservative Party"
        assert faction.faction_type == FactionType.CONSERVATIVE
        assert faction.ideology == PoliticalIdeology.TRADITIONALISM
        assert faction.leader_id == "advisor_1"
        assert "advisor_1" in faction.members
    
    def test_join_faction(self, manager):
        """Test advisor joining faction."""
        faction_id = manager.create_faction(
            name="Progressive Party",
            faction_type=FactionType.PROGRESSIVE,
            ideology=PoliticalIdeology.MODERNIZATION
        )
        
        success = manager.join_faction("advisor_2", faction_id)
        assert success
        
        faction = manager._find_faction(faction_id)
        assert "advisor_2" in faction.members
    
    def test_form_conspiracy(self, manager):
        """Test conspiracy formation."""
        conspiracy_id = manager.form_conspiracy(
            leader_id="advisor_1",
            conspiracy_type=ConspiracyType.COUP_ATTEMPT,
            objective="Overthrow current leadership",
            target="leader_1"
        )
        
        assert conspiracy_id is not None
        assert len(manager.active_conspiracies) == 1
        
        conspiracy = manager._find_conspiracy(conspiracy_id)
        assert conspiracy is not None
        assert conspiracy.leader_id == "advisor_1"
        assert conspiracy.conspiracy_type == ConspiracyType.COUP_ATTEMPT
        assert conspiracy.objective == "Overthrow current leadership"
        assert conspiracy.target == "leader_1"
        assert conspiracy.status == ConspiracyStatus.FORMING
    
    def test_conspiracy_recruitment(self, manager):
        """Test conspiracy recruitment."""
        conspiracy_id = manager.form_conspiracy(
            leader_id="advisor_1",
            conspiracy_type=ConspiracyType.POLICY_SABOTAGE,
            objective="Block economic reforms"
        )
        
        # Mock advisor relationships for recruitment
        advisor_relationships = {
            "advisor_1": {
                "advisor_2": {"trust": 0.8, "conspiracy_level": 0.6}
            }
        }
        
        with patch('random.random', return_value=0.5):  # Ensure recruitment succeeds
            success = manager.recruit_to_conspiracy(
                conspiracy_id, "advisor_1", "advisor_2", advisor_relationships
            )
        
        assert success
        conspiracy = manager._find_conspiracy(conspiracy_id)
        assert "advisor_2" in conspiracy.members
    
    def test_launch_propaganda_campaign(self, manager):
        """Test propaganda campaign launch."""
        campaign_id = manager.launch_propaganda_campaign(
            sponsor_id="advisor_1",
            campaign_type=PropagandaType.POLICY_PROMOTION,
            message="Economic reforms will bring prosperity",
            target="economic_policy",
            funding=200.0
        )
        
        assert campaign_id is not None
        assert len(manager.active_propaganda) == 1
        
        campaign = manager.active_propaganda[0]
        assert campaign.sponsor_id == "advisor_1"
        assert campaign.campaign_type == PropagandaType.POLICY_PROMOTION
        assert campaign.message == "Economic reforms will bring prosperity"
        assert campaign.target == "economic_policy"
        assert campaign.funding == 200.0
    
    def test_propose_reform(self, manager):
        """Test political reform proposal."""
        reform_id = manager.propose_reform(
            proposer_id="advisor_1",
            name="Military Reform Act",
            description="Restructure military command",
            reform_scope="military",
            required_votes=3
        )
        
        assert reform_id is not None
        assert len(manager.proposed_reforms) == 1
        
        reform = manager._find_reform(reform_id)
        assert reform is not None
        assert reform.name == "Military Reform Act"
        assert reform.proposer_id == "advisor_1"
        assert reform.required_votes == 3
        assert reform.current_votes == 0
    
    def test_vote_on_reform(self, manager):
        """Test voting on reforms."""
        reform_id = manager.propose_reform(
            proposer_id="advisor_1",
            name="Administrative Reform",
            description="Improve government efficiency",
            reform_scope="administrative"
        )
        
        # Vote in favor
        success = manager.vote_on_reform(reform_id, "advisor_2", support=True)
        assert success
        
        reform = manager._find_reform(reform_id)
        assert reform.current_votes == 1
    
    def test_succession_crisis_trigger(self, manager):
        """Test succession crisis triggering."""
        success = manager.trigger_succession_crisis(SuccessionCrisisType.UNCLEAR_HEIR)
        assert success
        assert manager.succession_crisis_active
        assert manager.succession_crisis_type == SuccessionCrisisType.UNCLEAR_HEIR
        assert manager.political_temperature > 0.4  # Should increase tension
    
    def test_process_turn_conspiracy_detection(self, manager):
        """Test conspiracy detection during turn processing."""
        # Create a conspiracy with high discovery risk
        conspiracy_id = manager.form_conspiracy(
            leader_id="advisor_1",
            conspiracy_type=ConspiracyType.COUP_ATTEMPT,
            objective="Seize power"
        )
        
        conspiracy = manager._find_conspiracy(conspiracy_id)
        conspiracy.discovery_risk = 0.9  # High risk
        
        with patch('random.random', return_value=0.5):  # Ensure detection
            results = manager.process_turn()
        
        assert len(results["conspiracies_detected"]) == 1
        assert results["conspiracies_detected"][0]["id"] == conspiracy_id
        
        # Conspiracy should be moved to history
        assert len(manager.active_conspiracies) == 0
        assert len(manager.conspiracy_history) == 1
    
    def test_process_turn_conspiracy_activation(self, manager):
        """Test conspiracy activation during turn processing."""
        conspiracy_id = manager.form_conspiracy(
            leader_id="advisor_1",
            conspiracy_type=ConspiracyType.POLICY_SABOTAGE,
            objective="Block reforms"
        )
        
        conspiracy = manager._find_conspiracy(conspiracy_id)
        conspiracy.add_member("advisor_2")
        conspiracy.add_member("advisor_3")
        conspiracy.network_strength = 0.6  # High enough for activation
        conspiracy.discovery_risk = 0.0  # Prevent random detection
        
        results = manager.process_turn()
        
        assert len(results["conspiracies_activated"]) == 1
        assert conspiracy.status == ConspiracyStatus.ACTIVE
        assert conspiracy.activation_turn == manager.current_turn
    
    def test_process_turn_propaganda_effects(self, manager):
        """Test propaganda effects during turn processing."""
        campaign_id = manager.launch_propaganda_campaign(
            sponsor_id="advisor_1",
            campaign_type=PropagandaType.CHARACTER_ASSASSINATION,
            message="Target advisor is corrupt",
            target="advisor_2",
            funding=150.0
        )
        
        results = manager.process_turn()
        
        assert len(results["propaganda_effects"]) == 1
        effect = results["propaganda_effects"][0]
        assert effect["target"] == "advisor_2"
        assert "opinion_change" in effect
        
        # Campaign duration should decrease
        assert len(manager.active_propaganda) == 1
        campaign = manager.active_propaganda[0]
        assert campaign.turns_remaining == 2  # Started at 3, decreased by 1
    
    def test_process_turn_reform_passage(self, manager):
        """Test reform passage during turn processing."""
        reform_id = manager.propose_reform(
            proposer_id="advisor_1",
            name="Tax Reform",
            description="Restructure taxation system",
            reform_scope="economic",
            required_votes=2
        )
        
        # Get enough votes
        manager.vote_on_reform(reform_id, "advisor_2", support=True)
        manager.vote_on_reform(reform_id, "advisor_3", support=True)
        
        results = manager.process_turn()
        
        assert len(results["reforms_passed"]) == 1
        assert results["reforms_passed"][0]["name"] == "Tax Reform"
        
        # Reform should be moved to enacted
        assert len(manager.proposed_reforms) == 0
        assert len(manager.enacted_reforms) == 1
    
    def test_political_summary(self, manager):
        """Test political summary generation."""
        # Add some content for a comprehensive summary
        manager.create_faction("Progressives", FactionType.PROGRESSIVE, PoliticalIdeology.MODERNIZATION)
        manager.form_conspiracy("advisor_1", ConspiracyType.COUP_ATTEMPT, "Seize control")
        manager.launch_propaganda_campaign("advisor_2", PropagandaType.LOYALTY_CAMPAIGNS, "Support the leader")
        manager.propose_reform("advisor_3", "Reform Act", "Major reform", "constitutional")
        
        summary = manager.get_political_summary()
        
        assert "civilization_id" in summary
        assert "turn" in summary
        assert "political_temperature" in summary
        assert "information_reliability" in summary
        
        assert summary["factions"]["count"] == 1
        assert summary["conspiracies"]["active"] == 1
        assert summary["propaganda"]["active_campaigns"] == 1
        assert summary["reforms"]["proposed"] == 1


class TestConspiracyNetwork:
    """Test the ConspiracyNetwork class."""
    
    @pytest.fixture
    def conspiracy(self):
        """Create a basic ConspiracyNetwork."""
        return ConspiracyNetwork(
            conspiracy_type=ConspiracyType.COUP_ATTEMPT,
            leader_id="advisor_1",
            objective="Overthrow leader",
            formation_turn=1
        )
    
    def test_conspiracy_initialization(self, conspiracy):
        """Test conspiracy initializes correctly."""
        assert conspiracy.conspiracy_type == ConspiracyType.COUP_ATTEMPT
        assert conspiracy.leader_id == "advisor_1"
        assert conspiracy.objective == "Overthrow leader"
        assert conspiracy.status == ConspiracyStatus.FORMING
        assert len(conspiracy.members) == 0
        assert conspiracy.network_strength >= 0.0
        assert conspiracy.secrecy_level >= 0.0
    
    def test_add_member(self, conspiracy):
        """Test adding members to conspiracy."""
        success = conspiracy.add_member("advisor_2")
        assert success
        assert "advisor_2" in conspiracy.members
        assert conspiracy.network_strength > 0.3  # Should increase
    
    def test_remove_member(self, conspiracy):
        """Test removing members from conspiracy."""
        conspiracy.add_member("advisor_2")
        conspiracy.add_member("advisor_3")
        
        success = conspiracy.remove_member("advisor_2")
        assert success
        assert "advisor_2" not in conspiracy.members
        assert "advisor_3" in conspiracy.members
    
    def test_success_probability_calculation(self, conspiracy):
        """Test conspiracy success probability calculation."""
        # Add members and external support
        conspiracy.add_member("advisor_2")
        conspiracy.add_member("advisor_3")
        conspiracy.external_support["allied_civ"] = 0.5
        
        prob = conspiracy.calculate_success_probability()
        assert 0.0 <= prob <= 1.0
        
        # Higher network strength should increase probability
        original_prob = prob
        conspiracy.network_strength = 0.9
        new_prob = conspiracy.calculate_success_probability()
        assert new_prob > original_prob


class TestPoliticalFaction:
    """Test the PoliticalFaction class."""
    
    @pytest.fixture
    def faction(self):
        """Create a basic PoliticalFaction."""
        return PoliticalFaction(
            name="Militarist Party",
            faction_type=FactionType.MILITARIST,
            ideology=PoliticalIdeology.MILITARISM,
            leader_id="advisor_1"
        )
    
    def test_faction_initialization(self, faction):
        """Test faction initializes correctly."""
        assert faction.name == "Militarist Party"
        assert faction.faction_type == FactionType.MILITARIST
        assert faction.ideology == PoliticalIdeology.MILITARISM
        assert faction.leader_id == "advisor_1"
        assert faction.influence >= 0.0
        assert faction.popularity >= 0.0
    
    def test_political_power_calculation(self, faction):
        """Test political power calculation."""
        # Add members and increase influence
        faction.members.add("advisor_1")
        faction.members.add("advisor_2")
        faction.influence = 0.8
        faction.popularity = 0.7
        faction.cohesion = 0.9
        faction.treasury = 1000.0
        
        power = faction.calculate_political_power()
        assert 0.0 <= power <= 1.0
        assert power > 0.5  # Should be substantial with good stats


class TestCivilizationAdvancedPolitics:
    """Test advanced political integration with Civilization."""
    
    @pytest.fixture
    def civilization(self):
        """Create a test civilization with advanced politics."""
        personality = PersonalityProfile(
            loyalty=0.7,
            ambition=0.5,
            cunning=0.4
        )
        
        leader = Leader(
            name="Test Leader",
            civilization_id="test_civ",
            personality=personality,
            leadership_style=LeadershipStyle.AUTHORITARIAN
        )
        
        civ = Civilization(
            name="Test Empire",
            leader=leader
        )
        
        # Add some test advisors
        for i in range(3):
            advisor = AdvisorWithMemory(
                id=f"advisor_{i+1}",
                name=f"Advisor {i+1}",
                civilization_id="test_civ",
                role=list(AdvisorRole)[i % len(AdvisorRole)],
                personality=PersonalityProfile()
            )
            civ.add_advisor(advisor)
        
        return civ
    
    def test_create_political_faction_integration(self, civilization):
        """Test creating political factions through civilization."""
        faction_id = civilization.create_political_faction(
            name="Test Faction",
            faction_type=FactionType.CONSERVATIVE,
            ideology=PoliticalIdeology.TRADITIONALISM,
            leader_advisor_id="advisor_1"
        )
        
        assert faction_id is not None
        
        # Check faction was created
        factions = civilization.get_political_factions()
        assert len(factions) == 1
        assert factions[0]["name"] == "Test Faction"
        assert factions[0]["leader_id"] == "advisor_1"
    
    def test_form_conspiracy_integration(self, civilization):
        """Test forming conspiracies through civilization."""
        conspiracy_id = civilization.form_conspiracy(
            leader_advisor_id="advisor_1",
            conspiracy_type=ConspiracyType.COUP_ATTEMPT,
            objective="Overthrow leadership",
            target="leader"
        )
        
        assert conspiracy_id is not None
        
        # Check conspiracy was created
        conspiracies = civilization.get_active_conspiracies()
        assert len(conspiracies) == 1
        assert conspiracies[0]["type"] == ConspiracyType.COUP_ATTEMPT
        assert conspiracies[0]["leader_id"] == "advisor_1"
    
    def test_launch_propaganda_campaign_integration(self, civilization):
        """Test launching propaganda campaigns through civilization."""
        campaign_id = civilization.launch_propaganda_campaign(
            sponsor_advisor_id="advisor_1",
            campaign_type=PropagandaType.LOYALTY_CAMPAIGNS,
            message="Support our great leader",
            funding=150.0
        )
        
        assert campaign_id is not None
        
        # Check memories were created
        memories = civilization.memory_manager.recall_memories("advisor_1")
        propaganda_memories = [m for m in memories if "propaganda" in m.tags]
        assert len(propaganda_memories) > 0
    
    def test_political_reform_integration(self, civilization):
        """Test political reforms through civilization."""
        reform_id = civilization.propose_political_reform(
            proposer_id="advisor_1",
            name="Government Restructuring",
            description="Reorganize administrative structure",
            reform_scope="administrative",
            required_votes=2
        )
        
        assert reform_id is not None
        
        # Vote on the reform
        vote1_success = civilization.vote_on_reform(reform_id, "advisor_2", support=True)
        vote2_success = civilization.vote_on_reform(reform_id, "advisor_3", support=True)
        
        assert vote1_success
        assert vote2_success
    
    def test_advanced_politics_turn_processing(self, civilization):
        """Test advanced politics processing during turn advancement."""
        # Create some political content
        faction_id = civilization.create_political_faction(
            "Reformists", FactionType.PROGRESSIVE, PoliticalIdeology.MODERNIZATION, "advisor_1"
        )
        
        conspiracy_id = civilization.form_conspiracy(
            "advisor_2", ConspiracyType.POLICY_SABOTAGE, "Block reforms"
        )
        
        campaign_id = civilization.launch_propaganda_campaign(
            "advisor_3", PropagandaType.POLICY_PROMOTION, "Support reforms"
        )
        
        # Process a turn
        results = civilization.process_turn()
        
        # Check that advanced politics were processed
        assert "advanced_politics" in results
        advanced_results = results["advanced_politics"]
        
        # Should have various political activities
        assert isinstance(advanced_results, dict)
        assert "conspiracies_detected" in advanced_results
        assert "propaganda_effects" in advanced_results
    
    def test_comprehensive_summary_with_advanced_politics(self, civilization):
        """Test that comprehensive summary includes advanced politics."""
        # Add some political content
        civilization.create_political_faction(
            "Test Party", FactionType.TECHNOCRAT, PoliticalIdeology.MODERNIZATION
        )
        
        summary = civilization.get_comprehensive_summary()
        
        assert "advanced_politics" in summary
        assert summary["integration"]["advanced_politics_active"] is True
        
        advanced_summary = summary["advanced_politics"]
        assert "political_temperature" in advanced_summary
        assert "factions" in advanced_summary
        assert "conspiracies" in advanced_summary


class TestAdvancedPoliticsComplexScenarios:
    """Test complex scenarios involving multiple advanced political systems."""
    
    def test_faction_conspiracy_interaction(self):
        """Test interactions between factions and conspiracies."""
        manager = AdvancedPoliticalManager(civilization_id="test", current_turn=1)
        
        # Create competing factions
        conservative_id = manager.create_faction(
            "Conservatives", FactionType.CONSERVATIVE, PoliticalIdeology.TRADITIONALISM, "advisor_1"
        )
        progressive_id = manager.create_faction(
            "Progressives", FactionType.PROGRESSIVE, PoliticalIdeology.MODERNIZATION, "advisor_2"
        )
        
        # Form conspiracy within one faction
        conspiracy_id = manager.form_conspiracy(
            "advisor_1", ConspiracyType.POLICY_SABOTAGE, "Block progressive reforms"
        )
        
        # Recruit faction members to conspiracy
        manager.join_faction("advisor_3", conservative_id)
        advisor_relationships = {
            "advisor_1": {"advisor_3": {"trust": 0.8, "conspiracy_level": 0.7}}
        }
        
        with patch('random.random', return_value=0.3):
            success = manager.recruit_to_conspiracy(
                conspiracy_id, "advisor_1", "advisor_3", advisor_relationships
            )
        
        assert success
        
        # Check that faction and conspiracy are linked
        faction = manager._find_faction(conservative_id)
        conspiracy = manager._find_conspiracy(conspiracy_id)
        
        # Both advisor_1 and advisor_3 should be in the faction and conspiracy
        assert "advisor_1" in faction.members
        assert "advisor_3" in faction.members
        assert "advisor_3" in conspiracy.members
    
    def test_propaganda_and_reform_interaction(self):
        """Test how propaganda affects reform success."""
        manager = AdvancedPoliticalManager(civilization_id="test", current_turn=1)
        
        # Propose a reform
        reform_id = manager.propose_reform(
            "advisor_1", "Economic Liberalization", "Free market reforms", "economic"
        )
        
        # Launch propaganda campaign supporting the reform
        campaign_id = manager.launch_propaganda_campaign(
            "advisor_1", PropagandaType.POLICY_PROMOTION, 
            "Economic reforms will bring prosperity", target="economic_liberalization"
        )
        
        # Process several turns to let propaganda take effect
        for _ in range(3):
            results = manager.process_turn()
        
        # Check that propaganda has affected public opinion
        assert "economic_liberalization" in manager.information_environment
        opinion_change = manager.information_environment["economic_liberalization"]
        assert opinion_change > 0  # Should be positive due to promotional campaign
    
    def test_succession_crisis_with_multiple_candidates(self):
        """Test succession crisis with multiple competing candidates."""
        manager = AdvancedPoliticalManager(civilization_id="test", current_turn=1)
        
        # Create succession candidates
        from src.core.advanced_politics import SuccessionCandidate
        
        candidate1 = SuccessionCandidate(
            advisor_id="advisor_1",
            legitimacy_score=0.7,
            bloodline_claim=0.8,
            appointed_heir=True
        )
        
        candidate2 = SuccessionCandidate(
            advisor_id="advisor_2", 
            legitimacy_score=0.6,
            merit_score=0.9,
            popular_support=0.8
        )
        
        manager.succession_candidates = [candidate1, candidate2]
        
        # Trigger succession crisis
        success = manager.trigger_succession_crisis(SuccessionCrisisType.MULTIPLE_CLAIMANTS)
        assert success
        
        # Check crisis state
        assert manager.succession_crisis_active
        assert manager.succession_crisis_type == SuccessionCrisisType.MULTIPLE_CLAIMANTS
        
        # Compare candidate strengths
        strength1 = candidate1.calculate_succession_strength()
        strength2 = candidate2.calculate_succession_strength()
        
        # Both should have significant strength but through different paths
        assert strength1 > 0.5  # Strong due to bloodline and heir status
        assert strength2 > 0.5  # Strong due to merit and popular support
    
    def test_information_warfare_complex_scenario(self):
        """Test complex information warfare with multiple campaigns."""
        manager = AdvancedPoliticalManager(civilization_id="test", current_turn=1)
        
        # Launch competing propaganda campaigns
        pro_campaign = manager.launch_propaganda_campaign(
            "advisor_1", PropagandaType.CHARACTER_ASSASSINATION,
            "Advisor 2 is corrupt", target="advisor_2", funding=200.0
        )
        
        counter_campaign = manager.launch_propaganda_campaign(
            "advisor_2", PropagandaType.CHARACTER_ASSASSINATION,
            "Advisor 1 is unreliable", target="advisor_1", funding=150.0
        )
        
        # Process turns to see propaganda effects
        for _ in range(4):  # Let campaigns complete
            results = manager.process_turn()
        
        # Both targets should have negative opinion changes
        assert "advisor_2" in manager.information_environment
        assert "advisor_1" in manager.information_environment
        
        # The better-funded campaign should have more effect
        advisor2_impact = abs(manager.information_environment.get("advisor_2", 0))
        advisor1_impact = abs(manager.information_environment.get("advisor_1", 0))
        
        # Information reliability should decrease due to competing false narratives
        assert manager.information_reliability < 0.7
