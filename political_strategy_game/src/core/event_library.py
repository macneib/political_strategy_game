"""
Event template library with pre-built political events.
"""

from typing import Dict, List
from .events import EventTemplate, EventType, EventSeverity
from .advisor import AdvisorRole


class EventLibrary:
    """Library of pre-built event templates."""
    
    @staticmethod
    def get_all_templates() -> Dict[str, EventTemplate]:
        """Get all available event templates."""
        templates = {}
        
        # Crisis Events
        templates.update(EventLibrary._get_crisis_templates())
        
        # Economic Events
        templates.update(EventLibrary._get_economic_templates())
        
        # Military Events
        templates.update(EventLibrary._get_military_templates())
        
        # Diplomatic Events
        templates.update(EventLibrary._get_diplomatic_templates())
        
        # Internal Conflict Events
        templates.update(EventLibrary._get_internal_conflict_templates())
        
        # Opportunity Events
        templates.update(EventLibrary._get_opportunity_templates())
        
        return templates
    
    @staticmethod
    def _get_crisis_templates() -> Dict[str, EventTemplate]:
        """Get crisis event templates."""
        templates = {}
        
        # Natural Disaster
        templates['natural_disaster'] = EventTemplate(
            id='natural_disaster',
            title_template='The Great {disaster_type}',
            description_template='A devastating {disaster_type} has struck {location}, causing widespread damage and displacing thousands of citizens. The people look to you for leadership in this dark hour.',
            event_type=EventType.CRISIS,
            severity=EventSeverity.MAJOR,
            frequency_weight=0.8,
            cooldown_turns=20,
            variables={
                'disaster_type': ['earthquake', 'flood', 'hurricane', 'wildfire', 'drought'],
                'location': ['the capital', 'the northern provinces', 'the coastal regions', 'the farming districts', 'the mountain settlements']
            },
            choice_templates=[
                {
                    'title': 'Emergency Relief Effort',
                    'description': 'Deploy all available resources to provide immediate aid and rescue operations.',
                    'consequences': {'treasury': -0.3, 'public_support': 0.4, 'stability': 0.2},
                    'tags': ['relief', 'humanitarian']
                },
                {
                    'title': 'Martial Law Declaration',
                    'description': 'Declare martial law to maintain order and organize systematic reconstruction.',
                    'consequences': {'stability': 0.3, 'public_support': -0.2, 'military_loyalty': 0.1},
                    'required_role': AdvisorRole.MILITARY,
                    'tags': ['martial_law', 'authoritarian']
                },
                {
                    'title': 'Request Foreign Aid',
                    'description': 'Seek assistance from neighboring kingdoms and trading partners.',
                    'consequences': {'treasury': 0.2, 'diplomatic_standing': -0.1, 'debt': 0.2},
                    'required_role': AdvisorRole.DIPLOMATIC,
                    'tags': ['diplomacy', 'foreign_aid']
                }
            ]
        )
        
        # Plague Outbreak
        templates['plague_outbreak'] = EventTemplate(
            id='plague_outbreak',
            title_template='The {plague_name} Spreads',
            description_template='A terrible plague known as the {plague_name} has begun spreading through your realm. Panic is setting in as trade routes close and cities begin implementing quarantine measures.',
            event_type=EventType.CRISIS,
            severity=EventSeverity.CRITICAL,
            frequency_weight=0.4,
            cooldown_turns=30,
            variables={
                'plague_name': ['Red Death', 'Wasting Sickness', 'Burning Fever', 'Silent Plague', 'Bone Rot']
            },
            choice_templates=[
                {
                    'title': 'Strict Quarantine',
                    'description': 'Implement strict quarantine measures and travel restrictions.',
                    'consequences': {'stability': -0.2, 'economy': -0.3, 'plague_spread': -0.5},
                    'tags': ['quarantine', 'health']
                },
                {
                    'title': 'Seek Magical Cure',
                    'description': 'Commission the court mages to research a magical cure.',
                    'consequences': {'treasury': -0.2, 'plague_spread': -0.3, 'public_support': 0.1},
                    'tags': ['magic', 'research']
                },
                {
                    'title': 'Maintain Trade',
                    'description': 'Keep trade routes open to maintain economic stability despite the risk.',
                    'consequences': {'economy': 0.2, 'plague_spread': 0.3, 'merchant_loyalty': 0.2},
                    'tags': ['trade', 'risk']
                }
            ]
        )
        
        return templates
    
    @staticmethod
    def _get_economic_templates() -> Dict[str, EventTemplate]:
        """Get economic event templates."""
        templates = {}
        
        # Trade Route Discovery
        templates['trade_route_discovery'] = EventTemplate(
            id='trade_route_discovery',
            title_template='New {trade_type} Route Discovered',
            description_template='Explorers have discovered a new {trade_type} route to the {destination}. This could bring significant wealth to your realm, but requires investment to secure and develop.',
            event_type=EventType.OPPORTUNITY,
            severity=EventSeverity.MODERATE,
            frequency_weight=1.2,
            cooldown_turns=15,
            variables={
                'trade_type': ['spice', 'silk', 'gold', 'exotic goods', 'precious gems'],
                'destination': ['Eastern Kingdoms', 'Southern Republics', 'Island Nations', 'Desert Emirates', 'Northern Clans']
            },
            choice_templates=[
                {
                    'title': 'Invest Heavily',
                    'description': 'Commit significant resources to secure and develop this trade route.',
                    'consequences': {'treasury': -0.4, 'economy': 0.6, 'trade_influence': 0.3},
                    'required_role': AdvisorRole.ECONOMIC,
                    'tags': ['investment', 'trade']
                },
                {
                    'title': 'Cautious Development',
                    'description': 'Develop the route slowly with minimal risk.',
                    'consequences': {'treasury': -0.1, 'economy': 0.2, 'trade_influence': 0.1},
                    'tags': ['cautious', 'development']
                },
                {
                    'title': 'Grant to Merchants',
                    'description': 'Allow private merchants to develop the route in exchange for taxes.',
                    'consequences': {'treasury': 0.2, 'economy': 0.3, 'merchant_influence': 0.2},
                    'tags': ['privatization', 'merchants']
                }
            ]
        )
        
        # Market Crash
        templates['market_crash'] = EventTemplate(
            id='market_crash',
            title_template='The {market_type} Market Collapses',
            description_template='The {market_type} market has suddenly collapsed due to {crash_reason}. Merchants are in panic, and your treasury faces significant losses.',
            event_type=EventType.CRISIS,
            severity=EventSeverity.MAJOR,
            frequency_weight=0.6,
            cooldown_turns=25,
            variables={
                'market_type': ['grain', 'textile', 'livestock', 'metal', 'lumber'],
                'crash_reason': ['oversupply', 'foreign competition', 'war disruptions', 'disease outbreak', 'magical interference']
            },
            choice_templates=[
                {
                    'title': 'Government Bailout',
                    'description': 'Use treasury funds to stabilize the market and support affected merchants.',
                    'consequences': {'treasury': -0.5, 'economy': 0.3, 'merchant_loyalty': 0.4},
                    'required_role': AdvisorRole.ECONOMIC,
                    'tags': ['bailout', 'intervention']
                },
                {
                    'title': 'Let Market Correct',
                    'description': 'Allow the market to correct itself naturally, despite short-term pain.',
                    'consequences': {'economy': -0.3, 'public_support': -0.2, 'market_stability': 0.2},
                    'tags': ['free_market', 'laissez_faire']
                },
                {
                    'title': 'Impose Price Controls',
                    'description': 'Set government price controls to prevent further collapse.',
                    'consequences': {'economy': -0.1, 'merchant_loyalty': -0.3, 'public_support': 0.2},
                    'tags': ['regulation', 'controls']
                }
            ]
        )
        
        return templates
    
    @staticmethod
    def _get_military_templates() -> Dict[str, EventTemplate]:
        """Get military event templates."""
        templates = {}
        
        # Border Skirmish
        templates['border_skirmish'] = EventTemplate(
            id='border_skirmish',
            title_template='Border Conflict with {enemy_faction}',
            description_template='Reports arrive of armed clashes along your border with the {enemy_faction}. While not yet a full war, tensions are escalating and a response is demanded.',
            event_type=EventType.MILITARY_EVENT,
            severity=EventSeverity.MODERATE,
            frequency_weight=1.0,
            cooldown_turns=10,
            variables={
                'enemy_faction': ['Red Banner Clan', 'Iron Coast Pirates', 'Desert Nomads', 'Mountain Tribes', 'Rebel Province']
            },
            choice_templates=[
                {
                    'title': 'Military Response',
                    'description': 'Send troops to secure the border and show strength.',
                    'consequences': {'military_strength': 0.2, 'enemy_hostility': 0.3, 'treasury': -0.2},
                    'required_role': AdvisorRole.MILITARY,
                    'tags': ['military', 'aggression']
                },
                {
                    'title': 'Diplomatic Resolution',
                    'description': 'Send envoys to negotiate a peaceful resolution.',
                    'consequences': {'diplomatic_standing': 0.2, 'enemy_hostility': -0.1, 'military_morale': -0.1},
                    'required_role': AdvisorRole.DIPLOMATIC,
                    'tags': ['diplomacy', 'peace']
                },
                {
                    'title': 'Fortify Border',
                    'description': 'Focus on defensive preparations rather than aggression.',
                    'consequences': {'border_security': 0.4, 'treasury': -0.3, 'military_readiness': 0.2},
                    'tags': ['defense', 'fortification']
                }
            ]
        )
        
        return templates
    
    @staticmethod
    def _get_diplomatic_templates() -> Dict[str, EventTemplate]:
        """Get diplomatic event templates."""
        templates = {}
        
        # Marriage Proposal
        templates['royal_marriage_proposal'] = EventTemplate(
            id='royal_marriage_proposal',
            title_template='Marriage Proposal from {foreign_house}',
            description_template='The noble House of {foreign_house} has proposed a marriage alliance between their {relative_type} and a member of your court. This could strengthen diplomatic ties or create future complications.',
            event_type=EventType.DIPLOMATIC_EVENT,
            severity=EventSeverity.MODERATE,
            frequency_weight=0.8,
            cooldown_turns=20,
            variables={
                'foreign_house': ['Goldmane', 'Stormwind', 'Ironborn', 'Rosethorne', 'Blackwater'],
                'relative_type': ['eldest daughter', 'second son', 'heir apparent', 'court ward', 'younger sibling']
            },
            choice_templates=[
                {
                    'title': 'Accept Alliance',
                    'description': 'Accept the marriage proposal to strengthen diplomatic ties.',
                    'consequences': {'diplomatic_standing': 0.3, 'foreign_influence': 0.2, 'court_intrigue': 0.1},
                    'required_role': AdvisorRole.DIPLOMATIC,
                    'tags': ['marriage', 'alliance']
                },
                {
                    'title': 'Politely Decline',
                    'description': 'Respectfully decline while maintaining friendly relations.',
                    'consequences': {'diplomatic_standing': -0.1, 'independence': 0.2},
                    'tags': ['decline', 'independence']
                },
                {
                    'title': 'Counter-Proposal',
                    'description': 'Propose alternative terms for the alliance.',
                    'consequences': {'diplomatic_complexity': 0.3, 'negotiation_advantage': 0.2},
                    'tags': ['negotiation', 'counter_offer']
                }
            ]
        )
        
        return templates
    
    @staticmethod
    def _get_internal_conflict_templates() -> Dict[str, EventTemplate]:
        """Get internal conflict event templates."""
        templates = {}
        
        # Noble Rebellion
        templates['noble_rebellion'] = EventTemplate(
            id='noble_rebellion',
            title_template='House {rebel_house} Declares Rebellion',
            description_template='Lord {rebel_name} of House {rebel_house} has declared open rebellion against your rule, citing {grievance}. Several minor houses may join their cause if not handled swiftly.',
            event_type=EventType.INTERNAL_CONFLICT,
            severity=EventSeverity.MAJOR,
            frequency_weight=0.5,
            cooldown_turns=30,
            variables={
                'rebel_house': ['Blackthorn', 'Ravencrest', 'Grimhold', 'Ironwill', 'Darkbane'],
                'rebel_name': ['Aldric', 'Morgana', 'Theron', 'Lyanna', 'Roderick'],
                'grievance': ['excessive taxation', 'dishonored traditions', 'disputed succession', 'trade restrictions', 'religious persecution']
            },
            choice_templates=[
                {
                    'title': 'Military Suppression',
                    'description': 'Crush the rebellion with overwhelming force.',
                    'consequences': {'stability': 0.2, 'noble_loyalty': -0.3, 'military_strength': -0.1, 'treasury': -0.2},
                    'required_role': AdvisorRole.MILITARY,
                    'tags': ['military', 'suppression']
                },
                {
                    'title': 'Negotiate Terms',
                    'description': 'Attempt to resolve the conflict through negotiation and compromise.',
                    'consequences': {'stability': -0.1, 'noble_loyalty': 0.2, 'royal_authority': -0.2},
                    'required_role': AdvisorRole.DIPLOMATIC,
                    'tags': ['negotiation', 'compromise']
                },
                {
                    'title': 'Divide and Conquer',
                    'description': 'Use political maneuvering to turn the rebels against each other.',
                    'consequences': {'court_intrigue': 0.3, 'noble_loyalty': -0.1, 'royal_authority': 0.1},
                    'tags': ['intrigue', 'manipulation']
                }
            ]
        )
        
        return templates
    
    @staticmethod
    def _get_opportunity_templates() -> Dict[str, EventTemplate]:
        """Get opportunity event templates."""
        templates = {}
        
        # Technological Discovery
        templates['tech_discovery'] = EventTemplate(
            id='tech_discovery',
            title_template='{inventor_type} Presents New {invention}',
            description_template='A brilliant {inventor_type} has approached your court with plans for a revolutionary {invention}. The potential benefits are enormous, but the costs and risks are significant.',
            event_type=EventType.OPPORTUNITY,
            severity=EventSeverity.MODERATE,
            frequency_weight=0.7,
            cooldown_turns=25,
            variables={
                'inventor_type': ['alchemist', 'engineer', 'scholar', 'artisan', 'foreign expert'],
                'invention': ['improved siege engine', 'advanced farming technique', 'new metallurgy process', 'magical communication device', 'improved shipbuilding method']
            },
            choice_templates=[
                {
                    'title': 'Fund Development',
                    'description': 'Provide full funding and resources for development.',
                    'consequences': {'treasury': -0.3, 'technology': 0.4, 'innovation': 0.3},
                    'tags': ['research', 'innovation']
                },
                {
                    'title': 'Limited Trial',
                    'description': 'Fund a small-scale trial before full commitment.',
                    'consequences': {'treasury': -0.1, 'technology': 0.2, 'risk': -0.1},
                    'tags': ['cautious', 'trial']
                },
                {
                    'title': 'Decline Offer',
                    'description': 'Politely decline the proposal to avoid risks.',
                    'consequences': {'treasury': 0.0, 'innovation': -0.1, 'missed_opportunities': 0.1},
                    'tags': ['conservative', 'decline']
                }
            ]
        )
        
        return templates
