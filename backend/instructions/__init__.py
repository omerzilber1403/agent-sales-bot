"""
תיקיית הוראות למערכת המכירות
Instructions package for the sales system
"""

from .general_instructions import (
    GENERAL_INSTRUCTIONS,
    MESSAGE_QUALITY_INSTRUCTIONS,
    SALES_STRATEGY_INSTRUCTIONS,
    IMPORTANT_RULES,
    OPENING_MESSAGE_RULE,
    INFORMATION_FIRST_APPROACH,
    PRICING_AND_PRODUCTS_RULES
)

from .b2c_instructions import (
    B2C_SPECIFIC_INSTRUCTIONS,
    B2C_QUESTION_GUIDELINES
)

from .b2b_instructions import (
    B2B_SPECIFIC_INSTRUCTIONS,
    B2B_QUESTION_GUIDELINES
)

from .handoff_instructions import (
    HANDOFF_TRIGGERS,
    SALES_QUESTIONS,
    HANDOFF_RESPONSE,
    should_handoff,
    should_handoff_with_llm
)

from .template_instructions import (
    TEMPLATE_PATTERNS,
    get_template_response,
    match_template
)

from .smart_questions import (
    SMART_QUESTIONS,
    FOLLOW_UP_QUESTIONS,
    CUSTOMER_TYPE_QUESTIONS,
    PRODUCT_QUESTIONS,
    get_smart_question,
    get_contextual_question,
    should_ask_question
)

from .customer_profiling import (
    CUSTOMER_PROFILE_FIELDS,
    PROFILING_QUESTIONS,
    AUTO_DETECTION_PATTERNS,
    extract_customer_info,
    get_next_profiling_question,
    should_continue_profiling,
    get_customer_summary
)

from .conversation_flow import (
    CONVERSATION_STAGES,
    NATURAL_TRANSITIONS,
    NATURAL_BRIDGES,
    get_conversation_stage,
    get_natural_transition,
    get_natural_bridge,
    should_use_bridge,
    get_conversation_flow_guidance
)

__all__ = [
    # General instructions
    "GENERAL_INSTRUCTIONS",
    "MESSAGE_QUALITY_INSTRUCTIONS", 
    "SALES_STRATEGY_INSTRUCTIONS",
    "IMPORTANT_RULES",
    "OPENING_MESSAGE_RULE",
    "INFORMATION_FIRST_APPROACH",
    "PRICING_AND_PRODUCTS_RULES",
    
    # B2C instructions
    "B2C_SPECIFIC_INSTRUCTIONS",
    "B2C_QUESTION_GUIDELINES",
    
    # B2B instructions
    "B2B_SPECIFIC_INSTRUCTIONS",
    "B2B_QUESTION_GUIDELINES",
    
    # Handoff instructions
    "HANDOFF_TRIGGERS",
    "SALES_QUESTIONS",
    "HANDOFF_RESPONSE",
    "should_handoff",
    "should_handoff_with_llm",
    
    # Template instructions
    "TEMPLATE_PATTERNS",
    "get_template_response",
    "match_template",
    
    # Smart questions
    "SMART_QUESTIONS",
    "FOLLOW_UP_QUESTIONS",
    "CUSTOMER_TYPE_QUESTIONS",
    "PRODUCT_QUESTIONS",
    "get_smart_question",
    "get_contextual_question",
    "should_ask_question",
    
    # Customer profiling
    "CUSTOMER_PROFILE_FIELDS",
    "PROFILING_QUESTIONS",
    "AUTO_DETECTION_PATTERNS",
    "extract_customer_info",
    "get_next_profiling_question",
    "should_continue_profiling",
    "get_customer_summary",
    
    # Conversation flow
    "CONVERSATION_STAGES",
    "NATURAL_TRANSITIONS",
    "NATURAL_BRIDGES",
    "get_conversation_stage",
    "get_natural_transition",
    "get_natural_bridge",
    "should_use_bridge",
    "get_conversation_flow_guidance"
]
