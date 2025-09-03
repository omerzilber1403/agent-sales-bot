from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from ..services.memory import store
from ..services.database_service import get_database_service
from ..services.customer_service import get_customer_service
from ..database.connection import get_db
from datetime import datetime

router = APIRouter(prefix="/api/v1/dev", tags=["dev"])

DEV_HTML = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AGENT Dev UI</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .chat-section, .graph-section { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .customer-selector { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .customer-selector select, .customer-selector input { margin: 5px; padding: 8px; border: 1px solid #ddd; border-radius: 5px; }
        .customer-profile { background: #e9ecef; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .profile-field { margin: 5px 0; }
        .profile-label { font-weight: bold; color: #495057; }
        .chat-container { height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; background: #f8f9fa; }
        .message { margin: 10px 0; padding: 10px; border-radius: 8px; }
        .user-message { background: #007bff; color: white; margin-left: 20px; }
        .bot-message { background: #e9ecef; color: #333; margin-right: 20px; }
        .input-section { margin-top: 15px; }
        .input-section input { width: 70%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .input-section button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .input-section button:hover { background: #0056b3; }
        .graph-container { height: 400px; overflow: auto; }
        .node { padding: 10px; margin: 5px; background: #f8f9fa; border: 1px solid #ddd; border-radius: 5px; }
        .execution-path { background: #fff3cd; padding: 10px; border-radius: 8px; margin: 10px 0; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 15px; text-align: center; border-radius: 8px; }
        .stat-number { font-size: 1.5em; font-weight: bold; color: #007bff; }
        .btn { padding: 8px 15px; margin: 5px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #545b62; }
        .btn-primary { background: #007bff; }
        .btn-primary:hover { background: #0056b3; }
        .btn-success { background: #28a745; }
        .btn-success:hover { background: #218838; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }
        .modal-content { background-color: white; margin: 5% auto; padding: 20px; border-radius: 10px; width: 80%; max-width: 600px; max-height: 80vh; overflow-y: auto; }
        .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
        .close:hover { color: black; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AGENT Dev UI</h1>
            <p>ממשק פיתוח לצ'אטבוט המכירות החכם</p>
        </div>

        <!-- Customer Selector -->
        <div class="customer-selector">
            <h3>בחירת לקוח ושיחה</h3>
            <div>
                <label>חברה:</label>
                <select id="companySelect">
                    <option value="">בחר חברה...</option>
                </select>
                
                <label>לקוח:</label>
                <select id="userSelect">
                    <option value="">בחר לקוח...</option>
                </select>
                
                <button class="btn btn-primary" onclick="startNewConversation()">התחל שיחה חדשה</button>
                <button class="btn" onclick="loadCustomerProfile()">טען פרופיל לקוח</button>
                <button class="btn btn-success" onclick="showCreateCustomerModal()">צור לקוח חדש</button>
            </div>
        </div>

        <!-- Customer Profile Display -->
        <div id="customerProfile" class="customer-profile" style="display: none;">
            <h3>פרופיל לקוח</h3>
            <div id="profileContent"></div>
        </div>

        <div class="main-content">
            <!-- Chat Section -->
            <div class="chat-section">
                <h2>💬 צ'אט</h2>
                <div class="chat-container" id="chatContainer">
                    <div class="message bot-message">שלום! אני נציג המכירות החכם שלך. איך אני יכול לעזור לך היום?</div>
                </div>
                <div class="input-section">
                    <input type="text" id="messageInput" placeholder="הקלד הודעה..." onkeypress="handleKeyPress(event)">
                    <button onclick="sendMessage()">שלח</button>
                </div>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number" id="totalMessages">0</div>
                        <div>הודעות</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="handoffs">0</div>
                        <div>Handoffs</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="conversationCount">0</div>
                        <div>שיחות</div>
                    </div>
                </div>
            </div>

            <!-- Graph Section -->
            <div class="graph-section">
                <h2>🔄 גרף ביצוע</h2>
                <div class="execution-path" id="executionPath">
                    <strong>מסלול ביצוע:</strong> <span id="currentPath">טרם התחיל</span>
                </div>
                <div class="graph-container" id="graphContainer">
                    <div class="node">טוען גרף...</div>
                </div>
                <button class="btn" onclick="loadHistory()">טען היסטוריה</button>
            </div>
        </div>
    </div>

    <!-- Create Customer Modal -->
    <div id="createCustomerModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeCreateCustomerModal()">&times;</span>
            <h2>צור לקוח חדש</h2>
            <form id="createCustomerForm">
                <div class="form-row">
                    <div class="form-group">
                        <label for="customerName">שם מלא *</label>
                        <input type="text" id="customerName" required>
                    </div>
                    <div class="form-group">
                        <label for="customerPhone">טלפון</label>
                        <input type="tel" id="customerPhone" placeholder="050-1234567">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="customerEmail">אימייל</label>
                        <input type="email" id="customerEmail" placeholder="customer@example.com">
                    </div>
                    <div class="form-group">
                        <label for="customerAge">גיל</label>
                        <input type="number" id="customerAge" min="1" max="120">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="customerGender">מגדר</label>
                        <select id="customerGender">
                            <option value="">בחר...</option>
                            <option value="male">זכר</option>
                            <option value="female">נקבה</option>
                            <option value="other">אחר</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="customerLocation">מיקום</label>
                        <input type="text" id="customerLocation" placeholder="עיר, רחוב">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="customerOccupation">תפקיד/מקצוע</label>
                        <input type="text" id="customerOccupation" placeholder="מהנדס, מנהל, סטודנט">
                    </div>
                    <div class="form-group">
                        <label for="customerBudget">תקציב</label>
                        <select id="customerBudget">
                            <option value="">בחר...</option>
                            <option value="low">נמוך</option>
                            <option value="medium">בינוני</option>
                            <option value="high">גבוה</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="customerFamilyStatus">סטטוס משפחה</label>
                        <select id="customerFamilyStatus">
                            <option value="">בחר...</option>
                            <option value="single">רווק/רווקה</option>
                            <option value="married">נשוי/נשואה</option>
                            <option value="parent">הורה</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="customerPreferredContact">עדיפות קשר</label>
                        <select id="customerPreferredContact">
                            <option value="">בחר...</option>
                            <option value="phone">טלפון</option>
                            <option value="email">אימייל</option>
                            <option value="whatsapp">ווטסאפ</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="customerInterests">תחומי עניין (מופרדים בפסיקים)</label>
                    <textarea id="customerInterests" rows="3" placeholder="ספורט, מוזיקה, טכנולוגיה"></textarea>
                </div>
                
                <div class="form-group">
                    <label for="customerNotes">הערות</label>
                    <textarea id="customerNotes" rows="3" placeholder="הערות נוספות על הלקוח..."></textarea>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <button type="submit" class="btn btn-success">צור לקוח</button>
                    <button type="button" class="btn" onclick="closeCreateCustomerModal()">ביטול</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let currentCompanyId = null;
        let currentUserId = null;
        let currentSessionId = null;

        // Initialize on page load
        window.onload = function() {
            loadCompanies();
            loadStats();
        };

        // Load companies
        async function loadCompanies() {
            try {
                const response = await fetch('/api/v1/admin/companies');
                if (response.ok) {
                    const companies = await response.json();
                    const companySelect = document.getElementById('companySelect');
                    companySelect.innerHTML = '<option value="">בחר חברה...</option>';
                    
                    companies.forEach(company => {
                        const option = document.createElement('option');
                        option.value = company.id;
                        option.textContent = company.name;
                        companySelect.appendChild(option);
                    });
                }
            } catch (error) {
                console.error('Error loading companies:', error);
            }
        }

        // Load users when company is selected
        document.getElementById('companySelect').addEventListener('change', function() {
            currentCompanyId = this.value;
            if (currentCompanyId) {
                loadCompanyUsers(currentCompanyId);
            } else {
                document.getElementById('userSelect').innerHTML = '<option value="">בחר לקוח...</option>';
            }
        });

        // Load company users
        async function loadCompanyUsers(companyId) {
            try {
                const response = await fetch(`/api/v1/admin/companies/${companyId}/users`);
                if (response.ok) {
                    const users = await response.json();
                    const userSelect = document.getElementById('userSelect');
                    userSelect.innerHTML = '<option value="">בחר לקוח...</option>';
                    
                    users.forEach(user => {
                        const option = document.createElement('option');
                        option.value = user.id;
                        option.textContent = user.name || user.external_id;
                        userSelect.appendChild(option);
                    });
                }
            } catch (error) {
                console.error('Error loading users:', error);
            }
        }

        // Start new conversation
        async function startNewConversation() {
            if (!currentCompanyId || !currentUserId) {
                alert('בחר חברה ולקוח תחילה');
                return;
            }

            try {
                // Create new conversation in database
                const response = await fetch('/api/v1/dev/conversations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        company_id: currentCompanyId,
                        user_id: currentUserId,
                        channel: 'dev'
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    currentSessionId = data.session_id;
                    
                    // Update UI
                    document.getElementById('chatContainer').innerHTML = '<div class="message bot-message">שלום! אני נציג המכירות החכם שלך. איך אני יכול לעזור לך היום?</div>';
                    document.getElementById('executionPath').innerHTML = '<strong>מסלול ביצוע:</strong> <span id="currentPath">שיחה חדשה התחילה</span>';
                    
                    console.log('New conversation created:', data);
                    
                    // Load customer profile
                    loadCustomerProfile();
                } else {
                    console.error('Failed to create conversation:', response.status);
                    alert('שגיאה ביצירת שיחה חדשה');
                }
            } catch (error) {
                console.error('Error creating conversation:', error);
                alert('שגיאה ביצירת שיחה חדשה');
            }
        }

        // Load customer profile
        async function loadCustomerProfile() {
            if (!currentUserId) {
                alert('בחר לקוח תחילה');
                return;
            }

            try {
                const response = await fetch(`/api/v1/dev/customer/${currentUserId}/profile`);
                if (response.ok) {
                    const profile = await response.json();
                    displayCustomerProfile(profile);
                }
            } catch (error) {
                console.error('Error loading customer profile:', error);
            }
        }

        // Display customer profile
        function displayCustomerProfile(profile) {
            const profileDiv = document.getElementById('customerProfile');
            const contentDiv = document.getElementById('profileContent');
            
            let profileHTML = `
                <div class="profile-field">
                    <span class="profile-label">שם:</span> ${profile.name || 'לא צוין'}
                </div>
                <div class="profile-field">
                    <span class="profile-label">גיל:</span> ${profile.age || 'לא צוין'}
                </div>
                <div class="profile-field">
                    <span class="profile-label">מיקום:</span> ${profile.location || 'לא צוין'}
                </div>
                <div class="profile-field">
                    <span class="profile-label">תפקיד:</span> ${profile.occupation || 'לא צוין'}
                </div>
                <div class="profile-field">
                    <span class="profile-label">תקציב:</span> ${profile.budget_range || 'לא צוין'}
                </div>
                <div class="profile-field">
                    <span class="profile-label">סטטוס משפחה:</span> ${profile.family_status || 'לא צוין'}
                </div>
                <div class="profile-field">
                    <span class="profile-label">שיחות:</span> ${profile.total_conversations || 0}
                </div>
                <div class="profile-field">
                    <span class="profile-label">הודעות:</span> ${profile.total_messages || 0}
                </div>
                <div class="profile-field">
                    <span class="profile-label">שלב המרה:</span> ${profile.conversion_stage || 'חדש'}
                </div>
            `;
            
            contentDiv.innerHTML = profileHTML;
            profileDiv.style.display = 'block';
        }

        // Show create customer modal
        function showCreateCustomerModal() {
            if (!currentCompanyId) {
                alert('בחר חברה תחילה');
                return;
            }
            document.getElementById('createCustomerModal').style.display = 'block';
        }

        // Close create customer modal
        function closeCreateCustomerModal() {
            document.getElementById('createCustomerModal').style.display = 'none';
            document.getElementById('createCustomerForm').reset();
        }

        // Handle create customer form submission
        document.getElementById('createCustomerForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('customerName').value,
                phone: document.getElementById('customerPhone').value,
                email: document.getElementById('customerEmail').value,
                age: document.getElementById('customerAge').value ? parseInt(document.getElementById('customerAge').value) : null,
                gender: document.getElementById('customerGender').value,
                location: document.getElementById('customerLocation').value,
                occupation: document.getElementById('customerOccupation').value,
                budget_range: document.getElementById('customerBudget').value,
                family_status: document.getElementById('customerFamilyStatus').value,
                preferred_contact: document.getElementById('customerPreferredContact').value,
                interests: document.getElementById('customerInterests').value ? document.getElementById('customerInterests').value.split(',').map(s => s.trim()) : [],
                notes: document.getElementById('customerNotes').value
            };

            try {
                const response = await fetch('/api/v1/dev/customers', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        company_id: currentCompanyId,
                        ...formData
                    })
                });

                if (response.ok) {
                    const result = await response.json();
                    alert(`לקוח נוצר בהצלחה! ID: ${result.user_id}`);
                    closeCreateCustomerModal();
                    
                    // Reload users list
                    loadCompanyUsers(currentCompanyId);
                    
                    // Select the new user
                    document.getElementById('userSelect').value = result.user_id;
                    currentUserId = result.user_id;
                    
                    // Automatically start a new conversation with the new user
                    await startNewConversation();
                    
                    // Load customer profile
                    loadCustomerProfile();
                } else {
                    const error = await response.json();
                    alert('שגיאה ביצירת לקוח: ' + error.detail);
                }
            } catch (error) {
                alert('שגיאה ביצירת לקוח: ' + error.message);
            }
        });

        // Send message
        async function sendMessage() {
            if (!currentCompanyId || !currentUserId) {
                alert('בחר חברה ולקוח תחילה');
                return;
            }
            
            if (!currentSessionId) {
                alert('התחל שיחה חדשה תחילה');
                return;
            }

            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;

            // Add user message to chat
            addMessageToChat('user', message);
            input.value = '';

            try {
                console.log('Sending message with:', {
                    company_id: currentCompanyId,
                    user_id: currentUserId,
                    session_id: currentSessionId,
                    message: message,
                    channel: 'dev'
                });
                
                const response = await fetch('/api/v1/agent/reply', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        company_id: currentCompanyId,
                        user_id: currentUserId,
                        session_id: currentSessionId,
                        message: message,
                        channel: 'dev'
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    
                    // Add bot response to chat
                    addMessageToChat('bot', data.text);
                    
                    // Update execution path
                    if (data.execution_path) {
                        document.getElementById('currentPath').textContent = data.execution_path.join(' → ');
                    }
                    
                    // Reload customer profile to see any updates
                    loadCustomerProfile();
                }
            } catch (error) {
                console.error('Error sending message:', error);
                addMessageToChat('bot', 'שגיאה בשליחת ההודעה');
            }
        }

        // Add message to chat
        function addMessageToChat(sender, text) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Handle Enter key
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // Load conversation history
        async function loadHistory() {
            if (!currentUserId) {
                alert('בחר לקוח תחילה');
                return;
            }

            try {
                const response = await fetch(`/api/v1/coach/conversations/${currentUserId}`);
                if (response.ok) {
                    const data = await response.json();
                    displayHistory(data.messages || []);
                }
            } catch (error) {
                console.error('Error loading history:', error);
            }
        }

        // Display conversation history
        function displayHistory(messages) {
            const chatContainer = document.getElementById('chatContainer');
            chatContainer.innerHTML = '';
            
            messages.forEach(msg => {
                const sender = msg.role === 'user' ? 'user' : 'bot';
                addMessageToChat(sender, msg.content);
            });
        }

        // Load stats
        async function loadStats() {
            try {
                const response = await fetch('/api/v1/coach/stats');
                if (response.ok) {
                    const data = await response.json();
                    document.getElementById('totalMessages').textContent = data.total_messages || 0;
                    document.getElementById('handoffs').textContent = data.handoffs || 0;
                    document.getElementById('conversationCount').textContent = data.conversations || 0;
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('createCustomerModal');
            if (event.target === modal) {
                closeCreateCustomerModal();
            }
        }
    </script>
</body>
</html>
"""

@router.get("/", response_class=HTMLResponse)
async def dev_ui():
    """Developer UI for testing the agent - now using React frontend"""
    return HTMLResponse(content="<h1>React Frontend Coming Soon!</h1><p>Please use the React app at <a href='http://localhost:3000'>http://localhost:3000</a></p>")

@router.get("/customer/{user_id}/profile")
async def get_customer_profile(user_id: int):
    """Get customer profile for dev UI"""
    db = next(get_db())
    customer_service = get_customer_service(db)
    profile = customer_service.get_customer_profile(user_id)
    return profile

@router.post("/customers")
async def create_customer(request: Request):
    """Create a new customer for dev testing"""
    try:
        body = await request.json()
        company_id = body.get("company_id")
        
        if not company_id:
            return {"error": "company_id is required"}
        
        db = next(get_db())
        db_service = get_database_service()
        
        # Create new user with all the profile information
        new_user = db_service.create_user(
            company_id=company_id,
            external_id=f"dev_user_{int(datetime.now().timestamp())}",
            name=body.get("name"),
            phone=body.get("phone"),
            email=body.get("email"),
            age=body.get("age"),
            gender=body.get("gender"),
            location=body.get("location"),
            occupation=body.get("occupation"),
            budget_range=body.get("budget_range"),
            family_status=body.get("family_status"),
            preferred_contact=body.get("preferred_contact"),
            interests=body.get("interests", []),
            notes=body.get("notes")
        )
        
        return {"message": "Customer created successfully", "user_id": new_user.id}
        
    except Exception as e:
        return {"error": str(e)}

@router.post("/conversations")
async def create_conversation(request: Request):
    """Create a new conversation for dev testing"""
    try:
        body = await request.json()
        company_id = body.get("company_id")
        user_id = body.get("user_id")
        channel = body.get("channel", "dev")
        
        if not company_id or not user_id:
            return {"error": "company_id and user_id are required"}
        
        db = next(get_db())
        db_service = get_database_service()
        
        # Create new conversation
        conversation = db_service.create_conversation(
            company_id=company_id,
            user_id=int(user_id),
            session_id=f"dev_session_{int(datetime.now().timestamp())}",
            channel=channel
        )
        
        return {
            "message": "Conversation created successfully", 
            "conversation_id": conversation.id,
            "session_id": conversation.session_id
        }
        
    except Exception as e:
        return {"error": str(e)}
