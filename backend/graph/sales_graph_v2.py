from __future__ import annotations
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from ..services.llm import chat
from ..instructions import (
    GENERAL_INSTRUCTIONS,
    MESSAGE_QUALITY_INSTRUCTIONS,
    SALES_STRATEGY_INSTRUCTIONS,
    IMPORTANT_RULES,
    OPENING_MESSAGE_RULE,
    INFORMATION_FIRST_APPROACH,
    B2C_SPECIFIC_INSTRUCTIONS,
    B2C_QUESTION_GUIDELINES,
    B2B_SPECIFIC_INSTRUCTIONS,
    B2B_QUESTION_GUIDELINES,
    should_handoff,
    should_handoff_with_llm,
    HANDOFF_RESPONSE,
    get_template_response,
    match_template
)
import json

def debug_bot_response(node_name: str, user_message: str, bot_response: str):
    """Simple debug function to show user message and bot response"""
    print(f"\n{'='*50}")
    print(f"👤 USER: {user_message}")
    print(f"🤖 BOT ({node_name}): {bot_response}")
    print(f"{'='*50}\n")

def business_type_router(state: AgentState) -> Literal["b2c_sales_agent", "b2b_sales_agent"]:
    """Route to appropriate sales agent based on business type"""
    company_data = state.get("company_data", {})
    business_type = company_data.get("business_type", "B2B").upper()
    print(f"🔀 business_type_router: routing to {'b2c_sales_agent' if business_type == 'B2C' else 'b2b_sales_agent'}")
    return "b2c_sales_agent" if business_type == "B2C" else "b2b_sales_agent"

class AgentState(TypedDict):
    messages: List[BaseMessage]
    customer_context: str
    smart_questions: List[str]
    extracted_info: Dict[str, Any]
    response: str
    handoff: bool
    handoff_reason: str
    tone: str
    execution_path: List[str]
    company_data: Dict[str, Any]

def create_sales_graph(company_data: Dict[str, Any] = None):
    """Create the sales agent graph with customer profiling and company data"""
    
    def check_handoff_requirement(state: AgentState) -> AgentState:
        """Check if the message requires human handoff"""
        
        # Add to execution path
        execution_path = state.get("execution_path", [])
        execution_path.append("check_handoff_requirement")
        
        # Check for handoff using the instruction module with LLM
        message_content = state["messages"][-1].content
        needs_handoff = should_handoff_with_llm(message_content)
        
        result = {
            **state,
            "handoff": needs_handoff,
            "handoff_reason": "Handoff trigger detected" if needs_handoff else None,
            "execution_path": execution_path
        }
        
        print(f"🔍 check_handoff_requirement result: handoff={needs_handoff}, reason={result.get('handoff_reason')}")
        return result
    
    def process_message_templates(state: AgentState) -> AgentState:
        """Process message templates and generate appropriate responses"""
        
        execution_path = state.get("execution_path", [])
        execution_path.append("process_message_templates")
        
        message_content = state["messages"][-1].content
        
        # Match template using the instruction module
        matched_template = match_template(message_content)
        
        # Generate response using the instruction module
        response = get_template_response(matched_template, company_data) if matched_template else None
        
        result = {
            **state,
            "response": response or state.get("response", ""),
            "execution_path": execution_path
        }
        
        print(f"🔍 process_message_templates result: response_length={len(result.get('response', ''))}")
        return result
    
    def b2c_sales_agent(state: AgentState) -> AgentState:
        """B2C sales agent with friendly and personal approach"""
        
        execution_path = state.get("execution_path", [])
        execution_path.append("b2c_sales_agent")
        
        # If we already have a response from templates, use it
        if state.get("response"):
            return {
                **state,
                "execution_path": execution_path
            }
        
        # Prepare context for LLM
        customer_context = state.get("customer_context", "")
        smart_questions = state.get("smart_questions", [])
        extracted_info = state.get("extracted_info", {})
        
        # Get company-specific fields to collect
        custom_fields = company_data.get("custom_fields", {}) if company_data else {}
        
        # Build system prompt for B2C approach
        if company_data and company_data.get("custom_prompt"):
            custom_prompt = company_data.get("custom_prompt")
            system_prompt = f"""{custom_prompt}

{GENERAL_INSTRUCTIONS}

{B2C_SPECIFIC_INSTRUCTIONS}

שדות מידע ספציפיים לחברה (אסוף רק את המידע הזה):
{custom_fields.get('description', 'אין שדות מידע ספציפיים מוגדרים')}

רשימת השדות לאסוף:
{chr(10).join([f"- {field}: {desc}" for field, desc in custom_fields.get('fields', {}).items()]) if custom_fields.get('fields') else "אין שדות מוגדרים"}

חשוב: שאל רק על השדות הרשומים למעלה! אל תשאל על מידע אחר!

{MESSAGE_QUALITY_INSTRUCTIONS}

מידע על הלקוח שנאסף:
{chr(10).join([f"- {key}: {value}" for key, value in extracted_info.items()]) if extracted_info else "אין מידע נוסף על הלקוח"}

הקשר הלקוח:
{customer_context}

שאלות חכמות לשאול (אם רלוונטי):
{chr(10).join([f"- {q}" for q in smart_questions]) if smart_questions else "אין שאלות ספציפיות"}

{IMPORTANT_RULES}

{B2C_QUESTION_GUIDELINES}

{INFORMATION_FIRST_APPROACH}

{OPENING_MESSAGE_RULE}

תגובה להודעת הלקוח: {state["messages"][-1].content}"""
        else:
            # Build system prompt using company data even without custom_prompt
            if company_data:
                company_name = company_data.get("name", "החברה")
                business_type = company_data.get("business_type", "B2B")
                one_line_value = company_data.get("one_line_value", "")
                products = company_data.get("products", [])
                
                print(f"DEBUG b2c_sales_agent: Company={company_name}, Business Type={business_type}")
                
                products_info = ""
                if products:
                    products_list = [f"- {p.get('name', '')}: {p.get('description', '')}" for p in products if isinstance(p, dict)]
                    if products_list:
                        products_info = f"""
מוצרים/שירותים:
{chr(10).join(products_list)}
"""
                
                system_prompt = f"""אתה נציג מכירות של {company_name}.

{B2C_SPECIFIC_INSTRUCTIONS}

{one_line_value}

{products_info}

{GENERAL_INSTRUCTIONS}

{MESSAGE_QUALITY_INSTRUCTIONS}

{customer_context}

מידע על הלקוח שנאסף:
{chr(10).join([f"- {key}: {value}" for key, value in extracted_info.items()])}

שאלות חכמות לשאול (אם רלוונטי):
{chr(10).join([f"- {q}" for q in smart_questions])}

{SALES_STRATEGY_INSTRUCTIONS}

{B2C_QUESTION_GUIDELINES}

{INFORMATION_FIRST_APPROACH}

תגובה להודעת הלקוח: {state["messages"][-1].content}"""

        try:
            # Call LLM with full conversation history
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (all messages)
            for msg in state["messages"]:
                if hasattr(msg, 'content'):
                    # Determine role based on message type
                    if hasattr(msg, 'type') and msg.type == 'ai':
                        messages.append({"role": "assistant", "content": msg.content})
                    else:
                        messages.append({"role": "user", "content": msg.content})
                else:
                    # Fallback for string messages
                    messages.append({"role": "user", "content": str(msg)})
            
            # Add reminder about conversation history
            messages.append({
                "role": "system", 
                "content": "זכור: יש לך גישה לכל השיחה הקודמת. השתמש במידע מהשיחה כדי לענות על שאלות הלקוח."
            })
            
            print(f"DEBUG: Sending {len(messages)} messages to B2C LLM (including system prompt)")
            llm_response = chat(messages)
            print(f"DEBUG: B2C LLM response: {llm_response}")
            
            result = {
                **state,
                "response": llm_response,
                "tone": "friendly",
                "execution_path": execution_path
            }
            
            # Debug: Show user message and bot response
            user_message = state["messages"][-1].content
            debug_bot_response("b2c_sales_agent", user_message, llm_response)
            
            return result
        except Exception as e:
            print(f"DEBUG: Error in b2c_sales_agent: {e}")
            return {
                **state,
                "response": "מצטער, יש בעיה טכנית. אנא נסה שוב מאוחר יותר.",
                "tone": "apologetic",
                "execution_path": execution_path
            }
    
    def b2b_sales_agent(state: AgentState) -> AgentState:
        """B2B sales agent with professional and business-focused approach"""
        
        execution_path = state.get("execution_path", [])
        execution_path.append("b2b_sales_agent")
        
        # If we already have a response from templates, use it
        if state.get("response"):
            return {
                **state,
                "execution_path": execution_path
            }
        
        # Prepare context for LLM
        customer_context = state.get("customer_context", "")
        smart_questions = state.get("smart_questions", [])
        extracted_info = state.get("extracted_info", {})
        
        # Get company-specific fields to collect
        custom_fields = company_data.get("custom_fields", {}) if company_data else {}
        
        # Build system prompt for B2B approach
        if company_data and company_data.get("custom_prompt"):
            custom_prompt = company_data.get("custom_prompt")
            system_prompt = f"""{custom_prompt}

{GENERAL_INSTRUCTIONS}

{B2B_SPECIFIC_INSTRUCTIONS}

שדות מידע ספציפיים לחברה (אסוף רק את המידע הזה):
{custom_fields.get('description', 'אין שדות מידע ספציפיים מוגדרים')}

רשימת השדות לאסוף:
{chr(10).join([f"- {field}: {desc}" for field, desc in custom_fields.get('fields', {}).items()]) if custom_fields.get('fields') else "אין שדות מוגדרים"}

חשוב: שאל רק על השדות הרשומים למעלה! אל תשאל על מידע אחר!

{MESSAGE_QUALITY_INSTRUCTIONS}

מידע על הלקוח שנאסף:
{chr(10).join([f"- {key}: {value}" for key, value in extracted_info.items()]) if extracted_info else "אין מידע נוסף על הלקוח"}

הקשר הלקוח:
{customer_context}

שאלות חכמות לשאול (אם רלוונטי):
{chr(10).join([f"- {q}" for q in smart_questions]) if smart_questions else "אין שאלות ספציפיות"}

{IMPORTANT_RULES}

{B2B_QUESTION_GUIDELINES}

{INFORMATION_FIRST_APPROACH}

{OPENING_MESSAGE_RULE}

תגובה להודעת הלקוח: {state["messages"][-1].content}"""
        else:
            # Build system prompt using company data even without custom_prompt
            if company_data:
                company_name = company_data.get("name", "החברה")
                business_type = company_data.get("business_type", "B2B")
                one_line_value = company_data.get("one_line_value", "")
                products = company_data.get("products", [])
                
                print(f"DEBUG b2b_sales_agent: Company={company_name}, Business Type={business_type}")
                
                products_info = ""
                if products:
                    products_list = [f"- {p.get('name', '')}: {p.get('description', '')}" for p in products if isinstance(p, dict)]
                    if products_list:
                        products_info = f"""
מוצרים/שירותים:
{chr(10).join(products_list)}
"""
                
                system_prompt = f"""אתה נציג מכירות של {company_name}.

{B2B_SPECIFIC_INSTRUCTIONS}

{one_line_value}

{products_info}

{GENERAL_INSTRUCTIONS}

{MESSAGE_QUALITY_INSTRUCTIONS}

{customer_context}

מידע על הלקוח שנאסף:
{chr(10).join([f"- {key}: {value}" for key, value in extracted_info.items()])}

שאלות חכמות לשאול (אם רלוונטי):
{chr(10).join([f"- {q}" for q in smart_questions])}

{SALES_STRATEGY_INSTRUCTIONS}

{B2B_QUESTION_GUIDELINES}

{INFORMATION_FIRST_APPROACH}

תגובה להודעת הלקוח: {state["messages"][-1].content}"""

        try:
            # Call LLM with full conversation history
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (all messages)
            for msg in state["messages"]:
                if hasattr(msg, 'content'):
                    # Determine role based on message type
                    if hasattr(msg, 'type') and msg.type == 'ai':
                        messages.append({"role": "assistant", "content": msg.content})
                    else:
                        messages.append({"role": "user", "content": msg.content})
                else:
                    # Fallback for string messages
                    messages.append({"role": "user", "content": str(msg)})
            
            # Add reminder about conversation history
            messages.append({
                "role": "system", 
                "content": "זכור: יש לך גישה לכל השיחה הקודמת. השתמש במידע מהשיחה כדי לענות על שאלות הלקוח."
            })
            
            print(f"DEBUG: Sending {len(messages)} messages to B2B LLM (including system prompt)")
            llm_response = chat(messages)
            print(f"DEBUG: B2B LLM response: {llm_response}")
            
            result = {
                **state,
                "response": llm_response,
                "tone": "professional",
                "execution_path": execution_path
            }
            
            # Debug: Show user message and bot response
            user_message = state["messages"][-1].content
            debug_bot_response("b2b_sales_agent", user_message, llm_response)
            
            return result
        except Exception as e:
            print(f"DEBUG: Error in b2b_sales_agent: {e}")
            return {
                **state,
                "response": "מצטער, יש בעיה טכנית. אנא נסה שוב מאוחר יותר.",
                "tone": "apologetic",
                "execution_path": execution_path
            }
    
    def should_continue(state: AgentState) -> str:
        """Determine if we should continue or end"""
        if state.get("handoff"):
            return "handoff"
        return "continue"
    
    def generate_handoff_response(state: AgentState) -> AgentState:
        """Generate handoff response using the instruction module"""
        
        execution_path = state.get("execution_path", [])
        execution_path.append("generate_handoff_response")
        
        result = {
            **state,
            "response": HANDOFF_RESPONSE,
            "tone": "professional",
            "execution_path": execution_path
        }
        
        # Debug: Show user message and bot response
        user_message = state["messages"][-1].content
        debug_bot_response("generate_handoff_response", user_message, HANDOFF_RESPONSE)
        
        return result
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes with improved names
    workflow.add_node("check_handoff_requirement", check_handoff_requirement)
    workflow.add_node("process_message_templates", process_message_templates)
    workflow.add_node("b2c_sales_agent", b2c_sales_agent)
    workflow.add_node("b2b_sales_agent", b2b_sales_agent)
    workflow.add_node("generate_handoff_response", generate_handoff_response)
    
    # Add edges
    workflow.add_edge("check_handoff_requirement", "process_message_templates")
    workflow.add_conditional_edges(
        "process_message_templates",
        business_type_router,
        {
            "b2c_sales_agent": "b2c_sales_agent",
            "b2b_sales_agent": "b2b_sales_agent"
        }
    )
    workflow.add_conditional_edges(
        "b2c_sales_agent",
        should_continue,
        {
            "handoff": "generate_handoff_response",
            "continue": END
        }
    )
    workflow.add_conditional_edges(
        "b2b_sales_agent",
        should_continue,
        {
            "handoff": "generate_handoff_response",
            "continue": END
        }
    )
    workflow.add_edge("generate_handoff_response", END)
    
    # Set entry point
    workflow.set_entry_point("check_handoff_requirement")
    
    # Compile and return the graph
    return workflow.compile()
