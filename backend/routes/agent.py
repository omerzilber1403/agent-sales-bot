from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional, List
from ..services.memory import store
from ..services.database_service import get_database_service
from ..services.customer_service import get_customer_service
from ..database.connection import get_db
from ..graph.sales_graph_v2 import create_sales_graph, _strip_markdown
from langchain_core.messages import HumanMessage, AIMessage
import json

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

class AgentRequest(BaseModel):
    company_id: Optional[int] = None
    user_id: Optional[str] = None  # Changed from int to str to match JavaScript
    session_id: Optional[str] = None
    message: str
    channel: str = "web"

class AgentResponse(BaseModel):
    text: str
    handoff: bool
    handoff_reason: Optional[str] = None
    tone: str
    execution_path: List[str]

@router.post("/reply", response_model=AgentResponse)
async def agent_reply(request: AgentRequest):
    """Get agent reply for a message"""
    try:
        print(f"DEBUG: ===== AGENT ROUTE CALLED =====")
        print(f"DEBUG: Request received: {request}")
        print(f"DEBUG: company_id={request.company_id}, user_id={request.user_id}, session_id={request.session_id}")
        print(f"DEBUG: message={request.message}, channel={request.channel}")
        
        # Get database service
        print(f"DEBUG: Getting database connection...")
        db = next(get_db())
        print(f"DEBUG: Database connection OK")
        
        print(f"DEBUG: Getting database service...")
        db_service = get_database_service()
        print(f"DEBUG: Database service OK")
        
        print(f"DEBUG: Getting customer service...")
        customer_service = get_customer_service(db)
        print(f"DEBUG: Customer service OK")
    
        # Create or get conversation — requires only company_id + session_id
        print(f"DEBUG: Creating/getting conversation...")
        conversation = None
        if request.company_id and request.session_id:
            print(f"DEBUG: Looking for existing conversation with session_id: {request.session_id}")
            conversation = db_service.get_conversation_by_session(request.session_id)
            if not conversation:
                print(f"DEBUG: No existing conversation found, creating new one...")
                # Resolve numeric user_id — default to 1 for demo/anonymous sessions
                try:
                    uid = int(request.user_id) if request.user_id else 1
                except (ValueError, TypeError):
                    uid = 1
                conversation = db_service.create_conversation(
                    company_id=request.company_id,
                    user_id=uid,
                    session_id=request.session_id,
                    channel=request.channel
                )
                print(f"DEBUG: Created new conversation: {conversation.session_id}, ID: {conversation.id}")
            else:
                print(f"DEBUG: Found existing conversation: {conversation.session_id}, ID: {conversation.id}")
        else:
            print(f"DEBUG: Missing required fields for conversation (need company_id + session_id)")
        
        print(f"DEBUG: Using conversation: {conversation.session_id if conversation else 'None'}, ID: {conversation.id if conversation else 'None'}")
    
        # Extract customer information from message if we have a user_id
        print(f"DEBUG: Extracting customer info...")
        extracted_info = {}
        if request.user_id:
            try:
                user_id_int = int(request.user_id)
                print(f"DEBUG: Converting user_id to int: {request.user_id} -> {user_id_int}")
                extracted_info = customer_service.extract_customer_info_from_message(
                    user_id_int, 
                    request.message
                )
                print(f"DEBUG: Extracted customer info: {extracted_info}")
            except ValueError as e:
                print(f"DEBUG: Invalid user_id format: {request.user_id}, error: {e}")
        else:
            print(f"DEBUG: No user_id provided")
    
        # Get personalized context for the AI (after extracting new info)
        personalized_context = ""
        if request.user_id:
            try:
                user_id_int = int(request.user_id)
                # Get updated context after extracting new information
                personalized_context = customer_service.get_personalized_response_context(user_id_int)
                print(f"DEBUG: Personalized context: {personalized_context}")
            except ValueError:
                print(f"DEBUG: Invalid user_id format: {request.user_id}")
    
        # Get company data first
        company_data = None
        if request.company_id:
            try:
                company = db_service.get_company(request.company_id)
                if company:
                    # Convert company to dict with all fields
                    company_data = {
                        "id": company.id,
                        "name": company.name,
                        "domain": company.domain,
                        "brand_aliases": company.brand_aliases,
                        "timezone": company.timezone,
                        "locale": company.locale,
                        "currency": company.currency,
                        "business_type": company.business_type,
                        "brand_voice": company.brand_voice,
                        "one_line_value": company.one_line_value,
                        "icp": company.icp,
                        "pain_points": company.pain_points,
                        "products": company.products,
                        "pricing_policy": company.pricing_policy,
                        "cta_type": company.cta_type,
                        "booking_link": company.booking_link,
                        "meeting_length_min": company.meeting_length_min,
                        "qualification_rules": company.qualification_rules,
                        "objections_playbook": company.objections_playbook,
                        "handoff_rules": company.handoff_rules,
                        "differentiators": company.differentiators,
                        "competitors_map": company.competitors_map,
                        "discovery_questions": company.discovery_questions,
                        "faq_kb_refs": company.faq_kb_refs,
                        "case_studies": company.case_studies,
                        "refund_sla_policy": company.refund_sla_policy,
                        "language_prefs": company.language_prefs,
                        "quote_long_mode": company.quote_long_mode,
                        "sensitive_topics": company.sensitive_topics,
                        "consent_texts": company.consent_texts,
                        "pii_allowed": company.pii_allowed,
                        "regional_rules": company.regional_rules,
                        "lead_scoring": company.lead_scoring,
                        "analytics_goals": company.analytics_goals,
                        "update_cadence": company.update_cadence,
                        "policy_version": company.policy_version,
                        "owner": company.owner,
                        "custom_fields": company.custom_fields,
                        "custom_prompt": company.custom_prompt,
                        "handoff_message": company.handoff_message,
                        "max_conversations": company.max_conversations
                    }
                    print(f"DEBUG: Using company data for company {request.company_id}: {company.name}")
                else:
                    print(f"DEBUG: Company {request.company_id} not found")
            except Exception as e:
                print(f"DEBUG: Error getting company: {e}")
        
        # Get smart questions to ask (now with company data)
        smart_questions = []
        if request.user_id:
            try:
                user_id_int = int(request.user_id)
                smart_questions = customer_service.get_smart_questions(user_id_int, company_data)
                print(f"DEBUG: Smart questions: {smart_questions}")
            except ValueError:
                print(f"DEBUG: Invalid user_id format: {request.user_id}")
    
        # Create the sales graph with company data
        graph = create_sales_graph(company_data)
        
        # Get conversation history from database
        messages = []
        if conversation:
            # Get all previous messages from the conversation
            previous_messages = db_service.get_conversation_messages(conversation.id)
            
            # Convert database messages to LangChain format
            for msg in previous_messages:
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    messages.append(AIMessage(content=msg.content))
        
        # Add the current message
        messages.append(HumanMessage(content=request.message))
        
        print(f"DEBUG: Loading {len(messages)} messages into graph (including current message)")
        
        # Prepare the input for the graph
        graph_input = {
            "messages": messages,
            "customer_context": personalized_context,
            "smart_questions": smart_questions,
            "extracted_info": extracted_info,
            "company_data": company_data or {}
        }
        
        # Debug: Print graph execution start
        print(f"\n🚀 STARTING GRAPH EXECUTION")
        print(f"📥 Input: messages={len(graph_input['messages'])}, context_length={len(personalized_context)}, questions={len(smart_questions)}")
        
        # Run the graph
        result = graph.invoke(graph_input)
        
        # Debug: Print graph execution result
        print(f"\n🏁 GRAPH EXECUTION COMPLETED")
        print(f"🎯 Final Execution Path: {' → '.join(result.get('execution_path', []))}")
        print(f"💬 Final Response: {result.get('response', '')[:200]}...")
        print(f"🔄 Handoff: {result.get('handoff', False)}")
        print(f"📝 Response Length: {len(result.get('response', ''))}")
        print(f"{'='*60}\n")
        
        print(f"DEBUG: Graph result: {result}")
        
        # Extract the response — strip markdown regardless of which graph node generated it
        response_text = _strip_markdown(result.get("response") or "אני לא מבין את השאלה שלך. איך אני יכול לעזור?")

        # Save message to database if we have a conversation
        if conversation:
            db_service.create_message(
                conversation_id=conversation.id,
                role="user",
                content=request.message,
                execution_path=result.get("execution_path", [])
            )
            
            db_service.create_message(
                conversation_id=conversation.id,
                role="assistant",
                content=response_text,
                execution_path=result.get("execution_path", [])
            )
        
        # Log to memory store for backward compatibility
        store.log(
            str(request.user_id) if request.user_id else "unknown", 
            "user", 
            request.message, 
            handoff=False
        )
        
        store.log(
            str(request.user_id) if request.user_id else "unknown", 
            "assistant", 
            response_text, 
            handoff=False
        )
        
        return AgentResponse(
            text=response_text,
            handoff=bool(result.get("handoff") or False),
            handoff_reason=result.get("handoff_reason"),
            tone=result.get("tone", "friendly"),
            execution_path=result.get("execution_path", [])
        )
        
    except Exception as e:
        print(f"DEBUG: Error in agent reply: {e}")
        error_response = "מצטער, יש בעיה טכנית. אנא נסה שוב מאוחר יותר."
        
        # Save error message to database if we have a conversation
        if conversation:
            db_service.create_message(
                conversation_id=conversation.id,
                role="user",
                content=request.message,
                execution_path=["error"]
            )
            
            db_service.create_message(
                conversation_id=conversation.id,
                role="assistant",
                content=error_response,
                execution_path=["error"]
            )
        
        return AgentResponse(
            text=error_response,
            handoff=False,
            handoff_reason="Technical error",
            tone="apologetic",
            execution_path=["error"]
        )

@router.get("/graph")
async def get_graph():
    """Get the current graph structure"""
    graph = create_sales_graph()
    
    # Extract graph information
    nodes = []
    edges = []
    descriptions = {}
    
    # This is a simplified representation - in a real implementation,
    # you'd want to extract this from the actual graph structure
    nodes = [
        {"id": "START", "label": "התחלה", "type": "start"},
        {"id": "detect_handoff", "label": "בדיקת Handoff", "type": "decision"},
        {"id": "match_templates", "label": "התאמת תבניות", "type": "process"},
        {"id": "llm_fallback", "label": "LLM Fallback", "type": "process"},
        {"id": "END", "label": "סיום", "type": "end"}
    ]
    
    edges = [
        {"from": "START", "to": "detect_handoff"},
        {"from": "detect_handoff", "to": "llm_fallback"},
        {"from": "match_templates", "to": "llm_fallback"},
        {"from": "llm_fallback", "to": "END"}
    ]
    
    descriptions = {
        "detect_handoff": "בודק אם השאלה דורשת handoff (מחיר, זמינות וכו')",
        "match_templates": "מנסה להתאים תבניות מוכנות (ברכות, מידע, פגישות)",
        "llm_fallback": "אם אין התאמה, משתמש ב-LLM או נותן תשובה כללית"
    }
    
    return {
        "nodes": nodes,
        "edges": edges,
        "descriptions": descriptions
    }
