from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional
from ..database.connection import get_db
from ..services.auth_service import AuthService, get_auth_service
from ..services.database_service import DatabaseService, get_database_service
from ..models.company_user import CompanyUser
from ..models.user import User
from ..models.conversation import Conversation
from ..models.message import Message
from datetime import datetime
from ..models.company import Company

router = APIRouter(prefix="/company", tags=["company_dashboard"])

# HTML templates
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Company Login - AGENT</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
        .login-container { max-width: 400px; margin: 50px auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .error { color: red; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>התחברות לחברה</h2>
        <form id="loginForm">
            <div class="form-group">
                <label for="email">אימייל:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">סיסמה:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">התחבר</button>
        </form>
        <div id="error" class="error"></div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/company/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                if (response.ok) {
                    window.location.href = '/company/dashboard';
                } else {
                    const data = await response.json();
                    document.getElementById('error').textContent = data.detail || 'שגיאה בהתחברות';
                }
            } catch (error) {
                document.getElementById('error').textContent = 'שגיאה בהתחברות';
            }
        });
    </script>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Company Dashboard - AGENT</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 0; }
        .header { background: white; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .nav { background: #333; padding: 15px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; padding: 10px; cursor: pointer; }
        .nav a:hover { background: #555; border-radius: 5px; }
        .nav a.active { background: #007bff; border-radius: 5px; }
        .content { padding: 20px; }
        .card { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
        .section { display: none; }
        .section.active { display: block; }
        .user-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #007bff; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px; }
        .btn:hover { background: #0056b3; }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #545b62; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Company Dashboard</h1>
        <p>ברוך הבא למערכת הניהול</p>
    </div>
    
    <div class="nav">
        <a href="#" onclick="showSection('dashboard')" class="active">דשבורד</a>
        <a href="#" onclick="showSection('users')">ניהול משתמשים</a>
        <a href="#" onclick="showSection('analytics')">סטטיסטיקות</a>
        <a href="#" onclick="showSection('settings')">הגדרות</a>
        <a href="#" onclick="logout()">התנתק</a>
    </div>
    
    <div class="content">
        <!-- Dashboard Section -->
        <div id="dashboard" class="section active">
            <div class="card">
                <h2>סטטיסטיקות כלליות</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number" id="totalUsers">0</div>
                        <div>משתמשים</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="totalConversations">0</div>
                        <div>שיחות</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="totalMessages">0</div>
                        <div>הודעות</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Users Section -->
        <div id="users" class="section">
            <div class="card">
                <h2>ניהול משתמשים</h2>
                <button class="btn" onclick="showAddUserForm()">הוסף משתמש חדש</button>
                <div id="usersList"></div>
                
                <div id="addUserForm" style="display: none;">
                    <h3>הוסף משתמש חדש</h3>
                    <div class="form-group">
                        <label for="userName">שם:</label>
                        <input type="text" id="userName" required>
                    </div>
                    <div class="form-group">
                        <label for="userPhone">טלפון:</label>
                        <input type="tel" id="userPhone">
                    </div>
                    <div class="form-group">
                        <label for="userEmail">אימייל:</label>
                        <input type="email" id="userEmail">
                    </div>
                    <button class="btn" onclick="addUser()">הוסף משתמש</button>
                    <button class="btn btn-secondary" onclick="hideAddUserForm()">ביטול</button>
                </div>
            </div>
        </div>

        <!-- Analytics Section -->
        <div id="analytics" class="section">
            <div class="card">
                <h2>סטטיסטיקות מפורטות</h2>
                <div id="analyticsContent">
                    <p>טוען נתונים...</p>
                </div>
            </div>
        </div>

        <!-- Settings Section -->
        <div id="settings" class="section">
            <div class="card">
                <h2>הגדרות חברה</h2>
                <div class="form-group">
                    <label for="companyName">שם החברה:</label>
                    <input type="text" id="companyName">
                </div>
                <div class="form-group">
                    <label for="customPrompt">Prompt מותאם:</label>
                    <textarea id="customPrompt" rows="4" placeholder="הכנס הוראות מותאמות לצ'אטבוט..."></textarea>
                </div>
                <div class="form-group">
                    <label for="handoffMessage">הודעת Handoff:</label>
                    <textarea id="handoffMessage" rows="3" placeholder="הודעה שמוצגת כשמעבירים לנציג אנושי..."></textarea>
                </div>
                <button class="btn" onclick="saveSettings()">שמור הגדרות</button>
            </div>
        </div>
    </div>

    <script>
        // Navigation
        function showSection(sectionId) {
            // Hide all sections
            document.querySelectorAll('.section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Remove active class from all nav items
            document.querySelectorAll('.nav a').forEach(navItem => {
                navItem.classList.remove('active');
            });
            
            // Show selected section
            document.getElementById(sectionId).classList.add('active');
            
            // Add active class to clicked nav item
            event.target.classList.add('active');
            
            // Load section data
            if (sectionId === 'users') {
                loadUsers();
            } else if (sectionId === 'analytics') {
                loadAnalytics();
            } else if (sectionId === 'settings') {
                loadSettings();
            }
        }

        // Dashboard functions
        async function loadDashboard() {
            try {
                const response = await fetch('/company/stats');
                
                if (response.ok) {
                    const data = await response.json();
                    document.getElementById('totalUsers').textContent = data.total_users;
                    document.getElementById('totalConversations').textContent = data.total_conversations;
                    document.getElementById('totalMessages').textContent = data.total_messages;
                }
            } catch (error) {
                console.error('Error loading dashboard:', error);
            }
        }

        // Users functions
        async function loadUsers() {
            try {
                const response = await fetch('/company/users');
                if (response.ok) {
                    const users = await response.json();
                    renderUsers(users);
                }
            } catch (error) {
                console.error('Error loading users:', error);
            }
        }

        function renderUsers(users) {
            const usersList = document.getElementById('usersList');
            if (users.length === 0) {
                usersList.innerHTML = '<p>אין משתמשים עדיין</p>';
                return;
            }

            usersList.innerHTML = users.map(user => `
                <div class="user-item">
                    <strong>${user.name || 'ללא שם'}</strong><br>
                    טלפון: ${user.phone || 'לא צוין'}<br>
                    אימייל: ${user.email || 'לא צוין'}<br>
                    נוצר: ${new Date(user.created_at).toLocaleDateString('he-IL')}
                </div>
            `).join('');
        }

        function showAddUserForm() {
            document.getElementById('addUserForm').style.display = 'block';
        }

        function hideAddUserForm() {
            document.getElementById('addUserForm').style.display = 'none';
        }

        async function addUser() {
            const name = document.getElementById('userName').value;
            const phone = document.getElementById('userPhone').value;
            const email = document.getElementById('userEmail').value;

            if (!name) {
                alert('שם המשתמש הוא שדה חובה');
                return;
            }

            try {
                const response = await fetch('/company/users', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, phone, email })
                });

                if (response.ok) {
                    alert('משתמש נוסף בהצלחה!');
                    hideAddUserForm();
                    loadUsers();
                    // Clear form
                    document.getElementById('userName').value = '';
                    document.getElementById('userPhone').value = '';
                    document.getElementById('userEmail').value = '';
                } else {
                    const error = await response.json();
                    alert('שגיאה: ' + error.detail);
                }
            } catch (error) {
                alert('שגיאה בהוספת משתמש');
            }
        }

        // Analytics functions
        async function loadAnalytics() {
            try {
                const response = await fetch('/company/analytics');
                if (response.ok) {
                    const data = await response.json();
                    renderAnalytics(data);
                }
            } catch (error) {
                console.error('Error loading analytics:', error);
            }
        }

        function renderAnalytics(data) {
            const content = document.getElementById('analyticsContent');
            content.innerHTML = `
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">${data.total_conversations || 0}</div>
                        <div>סה"כ שיחות</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.avg_messages_per_conversation || 0}</div>
                        <div>ממוצע הודעות לשיחה</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.handoff_rate || 0}%</div>
                        <div>אחוז Handoff</div>
                    </div>
                </div>
            `;
        }

        // Settings functions
        async function loadSettings() {
            try {
                const response = await fetch('/company/settings');
                if (response.ok) {
                    const settings = await response.json();
                    document.getElementById('companyName').value = settings.name || '';
                    document.getElementById('customPrompt').value = settings.custom_prompt || '';
                    document.getElementById('handoffMessage').value = settings.handoff_message || '';
                }
            } catch (error) {
                console.error('Error loading settings:', error);
            }
        }

        async function saveSettings() {
            const name = document.getElementById('companyName').value;
            const customPrompt = document.getElementById('customPrompt').value;
            const handoffMessage = document.getElementById('handoffMessage').value;

            try {
                const response = await fetch('/company/settings', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, custom_prompt: customPrompt, handoff_message: handoffMessage })
                });

                if (response.ok) {
                    alert('ההגדרות נשמרו בהצלחה!');
                } else {
                    const error = await response.json();
                    alert('שגיאה: ' + error.detail);
                }
            } catch (error) {
                alert('שגיאה בשמירת ההגדרות');
            }
        }

        function logout() {
            fetch('/company/logout', { method: 'POST' }).then(() => {
                window.location.href = '/company/login';
            });
        }

        // Load dashboard data on page load
        loadDashboard();
    </script>
</body>
</html>
"""

# Routes
@router.get("/login", response_class=HTMLResponse)
async def company_login_page():
    """Company login page"""
    return HTMLResponse(content=LOGIN_HTML)

@router.get("/dashboard", response_class=HTMLResponse)
async def company_dashboard_page():
    """Company dashboard page"""
    return HTMLResponse(content=DASHBOARD_HTML)

@router.post("/login")
async def company_login(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Company login endpoint"""
    try:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        user = auth_service.authenticate_company_user(db, email, password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Set session cookie
        response.set_cookie(
            key="company_user_id",
            value=str(user.id),
            httponly=True,
            max_age=3600  # 1 hour
        )
        
        return {"message": "Login successful"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
async def company_logout(response: Response):
    """Company logout endpoint"""
    response.delete_cookie("company_user_id")
    return {"message": "Logout successful"}

@router.get("/stats")
async def company_stats(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get company statistics"""
    # Get user ID from cookie
    user_id = request.cookies.get("company_user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get user and company
    user = db.query(CompanyUser).filter(CompanyUser.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    company_id = user.company_id
    
    # Count users
    total_users = db.query(User).filter(User.company_id == company_id).count()
    
    # Count conversations
    total_conversations = db.query(Conversation).filter(Conversation.company_id == company_id).count()
    
    # Count messages
    total_messages = db.query(Message).join(Conversation).filter(Conversation.company_id == company_id).count()
    
    return {
        "total_users": total_users,
        "total_conversations": total_conversations,
        "total_messages": total_messages
    }

@router.get("/users")
async def company_users(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get company users"""
    user_id = request.cookies.get("company_user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.query(CompanyUser).filter(CompanyUser.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    company_id = user.company_id
    users = db.query(User).filter(User.company_id == company_id).all()
    
    return [
        {
            "id": u.id,
            "name": u.name,
            "phone": u.phone,
            "email": u.email,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]

@router.post("/users")
async def create_company_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new company user"""
    user_id = request.cookies.get("company_user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.query(CompanyUser).filter(CompanyUser.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    body = await request.json()
    name = body.get("name")
    phone = body.get("phone")
    email = body.get("email")
    
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    
    # Create new user
    new_user = User(
        company_id=user.company_id,
        external_id=f"user_{name}_{int(datetime.now().timestamp())}",
        name=name,
        phone=phone,
        email=email
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully", "user_id": new_user.id}

@router.get("/analytics")
async def company_analytics(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get company analytics"""
    user_id = request.cookies.get("company_user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.query(CompanyUser).filter(CompanyUser.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    company_id = user.company_id
    
    # Get analytics data
    total_conversations = db.query(Conversation).filter(Conversation.company_id == company_id).count()
    total_messages = db.query(Message).join(Conversation).filter(Conversation.company_id == company_id).count()
    
    avg_messages = total_messages / total_conversations if total_conversations > 0 else 0
    handoff_rate = 0  # TODO: Calculate actual handoff rate
    
    return {
        "total_conversations": total_conversations,
        "avg_messages_per_conversation": round(avg_messages, 1),
        "handoff_rate": handoff_rate
    }

@router.get("/settings")
async def company_settings(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get company settings"""
    user_id = request.cookies.get("company_user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.query(CompanyUser).filter(CompanyUser.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    company = db.query(Company).filter(Company.id == user.company_id).first()
    
    return {
        "name": company.name,
        "custom_prompt": company.custom_prompt,
        "handoff_message": company.handoff_message
    }

@router.put("/settings")
async def update_company_settings(
    request: Request,
    db: Session = Depends(get_db)
):
    """Update company settings"""
    user_id = request.cookies.get("company_user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.query(CompanyUser).filter(CompanyUser.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    company = db.query(Company).filter(Company.id == user.company_id).first()
    body = await request.json()
    
    if "name" in body:
        company.name = body["name"]
    if "custom_prompt" in body:
        company.custom_prompt = body["custom_prompt"]
    if "handoff_message" in body:
        company.handoff_message = body["handoff_message"]
    
    db.commit()
    
    return {"message": "Settings updated successfully"}
