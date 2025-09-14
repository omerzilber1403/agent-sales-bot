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
    INFORMATION_FIRST_APPROACH
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

__all__ = [
    # General instructions
    "GENERAL_INSTRUCTIONS",
    "MESSAGE_QUALITY_INSTRUCTIONS", 
    "SALES_STRATEGY_INSTRUCTIONS",
    "IMPORTANT_RULES",
    "OPENING_MESSAGE_RULE",
    "INFORMATION_FIRST_APPROACH",
    
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
    "match_template"
]
