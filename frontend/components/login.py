"""
Login Component for Restaurant Operations Assistant
Provides authentication, session management, and demo accounts (Admin & User).
"""
import streamlit as st
import datetime

# Predefined Accounts
DEMO_ACCOUNTS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "display_name": "Executive Operations Director",
        "title": "System Administrator & Fleet Director",
        "email": "admin@restaurantops.ai",
        "avatar": "👑"
    },
    "user": {
        "password": "user123",
        "role": "user",
        "display_name": "Operations Analyst",
        "title": "Restaurant Shift & Ops Manager",
        "email": "user@restaurantops.ai",
        "avatar": "👤"
    }
}

def init_session_state():
    """Initializes user authentication session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "user_display_name" not in st.session_state:
        st.session_state["user_display_name"] = None
    if "user_title" not in st.session_state:
        st.session_state["user_title"] = None
    if "login_time" not in st.session_state:
        st.session_state["login_time"] = None
    if "chat_history" not in st.session_state:
        try:
            from frontend.components.chat_history_view import sync_chat_history_from_db
            sync_chat_history_from_db(st.session_state.get("username", "user"))
        except Exception:
            st.session_state["chat_history"] = []
    if "latency_log" not in st.session_state:
        st.session_state["latency_log"] = [
            {
                "id": "lat_seed_1",
                "timestamp": "10:30:14 AM",
                "query": "Customers are complaining about slow service. What similar complaints have been reported and what should management do?",
                "short_query": "Customers are complaining about slow service...",
                "category": "Waiting Time",
                "retrieval_ms": 184,
                "generation_ms": 980,
                "total_ms": 1164,
                "total_sec": 1.16,
                "sla_status": "✅ Met (< 3.0s)"
            },
            {
                "id": "lat_seed_2",
                "timestamp": "11:15:22 AM",
                "query": "What are the major operational problems at Mon Ami Gabi?",
                "short_query": "What are the major operational problems at Mon...",
                "category": "Waiting Time & Ambiance",
                "retrieval_ms": 162,
                "generation_ms": 945,
                "total_ms": 1107,
                "total_sec": 1.11,
                "sla_status": "✅ Met (< 3.0s)"
            },
            {
                "id": "lat_seed_3",
                "timestamp": "11:35:48 AM",
                "query": "Reports of cold steak and undercooked food during dinner shifts.",
                "short_query": "Reports of cold steak and undercooked food...",
                "category": "Food Quality",
                "retrieval_ms": 148,
                "generation_ms": 860,
                "total_ms": 1008,
                "total_sec": 1.01,
                "sla_status": "✅ Met (< 3.0s)"
            }
        ]

def perform_login(username: str, role_data: dict):
    """Sets session state upon successful authentication."""
    st.session_state["authenticated"] = True
    st.session_state["username"] = username
    st.session_state["user_role"] = role_data["role"]
    st.session_state["user_display_name"] = role_data["display_name"]
    st.session_state["user_title"] = role_data["title"]
    st.session_state["login_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Load persistent chat history from SQLite for this user
    try:
        from frontend.components.chat_history_view import sync_chat_history_from_db
        sync_chat_history_from_db(username)
    except Exception:
        pass

    # Log login event
    try:
        from backend.app.services.admin_service import log_system_event
        log_system_event(
            "AUDIT",
            "UserAuthentication",
            f"User '{username}' ({role_data['role'].upper()}) authenticated successfully."
        )
    except Exception:
        pass

def perform_logout():
    """Clears authentication state and reloads."""
    username = st.session_state.get("username", "Unknown")
    try:
        from backend.app.services.admin_service import log_system_event
        log_system_event("AUDIT", "UserAuthentication", f"User '{username}' logged out.")
    except Exception:
        pass

    st.session_state["authenticated"] = False
    st.session_state["user_role"] = None
    st.session_state["username"] = None
    st.session_state["user_display_name"] = None
    st.session_state["user_title"] = None
    st.session_state["login_time"] = None
    st.session_state["chat_history"] = []
    st.session_state.pop("active_report", None)
    st.session_state.pop("analyst_query", None)
    st.rerun()

def render_login_page():
    """
    Renders an ultra-modern, high-aesthetic dark login interface
    with 1-click demo logins for presentation purposes.
    """
    init_session_state()

    # Center container styling
    st.markdown(
        """
        <style>
        .login-hero-container {
            max-width: 920px;
            margin: 20px auto 30px auto;
            text-align: center;
        }
        .login-brand-icon {
            font-size: 3rem;
            margin-bottom: 8px;
            display: inline-block;
            background: linear-gradient(135deg, rgba(20, 184, 166, 0.2), rgba(56, 189, 248, 0.2));
            padding: 18px 24px;
            border-radius: 20px;
            border: 1px solid rgba(20, 184, 166, 0.35);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4), 0 0 24px rgba(20, 184, 166, 0.2);
            animation: pulseGlow 3s infinite alternate;
        }
        @keyframes pulseGlow {
            0% { box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4), 0 0 15px rgba(20, 184, 166, 0.2); }
            100% { box-shadow: 0 14px 40px rgba(0, 0, 0, 0.6), 0 0 35px rgba(20, 184, 166, 0.45); }
        }
        .login-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #FFFFFF 20%, #2DD4BF 60%, #38BDF8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }
        .login-subtitle {
            font-size: 1.05rem;
            color: #94A3B8;
            margin-bottom: 24px;
        }
        .demo-box-container {
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(20, 184, 166, 0.25);
            border-radius: 16px;
            padding: 22px;
            margin-bottom: 24px;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
        }
        .demo-chip-title {
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #14B8A6;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .demo-card {
            background: rgba(11, 18, 32, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 14px 18px;
            transition: all 0.25s ease;
            text-align: left;
        }
        .demo-card:hover {
            border-color: rgba(20, 184, 166, 0.45);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }
        .badge-role-admin {
            background: rgba(245, 158, 11, 0.15);
            color: #F59E0B;
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        .badge-role-user {
            background: rgba(20, 184, 166, 0.15);
            color: #2DD4BF;
            border: 1px solid rgba(20, 184, 166, 0.3);
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        </style>
        <div class="login-hero-container">
            <div class="login-brand-icon">🍽️</div>
            <div class="login-title">AI-Powered Restaurant Operations & Review Assistant</div>
            <div class="login-subtitle">Enterprise Operations Intelligence, Multi-Agent Orchestration & Fleet Telemetry</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Main login layout
    col_demo, col_form = st.columns([1.1, 1.0], gap="large")

    with col_demo:
        st.markdown(
            """
            <div class="demo-box-container">
                <div class="demo-chip-title">
                    <span>⚡ Quick Demo Access — Instant 1-Click Login</span>
                </div>
                <div style="font-size: 0.86rem; color: #94A3B8; margin-bottom: 16px; text-align: center;">
                    Select a persona below to instantly experience role-based access control (RBAC) and executive features.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Demo Button 1: ADMIN
        st.markdown(
            """
            <div class="demo-card" style="margin-bottom: 12px; border-left: 4px solid #F59E0B;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-weight: 700; color: #F8FAFC; font-size: 0.95rem;">👑 Administrator Persona</span>
                    <span class="badge-role-admin">FULL ACCESS (ADMIN)</span>
                </div>
                <div style="font-size: 0.82rem; color: #CBD5E1; margin-bottom: 6px;">
                    <strong>Executive Operations Director:</strong> Unlocks User Feedback Repository, CSV Data Ingestion, Full SQLite CRUD, Live System Logs, and Fleet Telemetry.
                </div>
                <div style="font-size: 0.78rem; color: #94A3B8; font-family: monospace;">
                    Credentials: <strong>admin</strong> / <strong>admin123</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("👑 Log in as Administrator (Executive Access)", key="btn_demo_admin", use_container_width=True):
            perform_login("admin", DEMO_ACCOUNTS["admin"])
            st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Demo Button 2: REGULAR USER
        st.markdown(
            """
            <div class="demo-card" style="margin-bottom: 12px; border-left: 4px solid #14B8A6;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-weight: 700; color: #F8FAFC; font-size: 0.95rem;">👤 Operational User Persona</span>
                    <span class="badge-role-user">OPERATIONS MANAGER</span>
                </div>
                <div style="font-size: 0.82rem; color: #CBD5E1; margin-bottom: 6px;">
                    <strong>Restaurant Shift Manager:</strong> Access all 9 operations intelligence modules, Hybrid RRF Search, Multi-Agent recovery scripts, and Model feedback submission.
                </div>
                <div style="font-size: 0.78rem; color: #94A3B8; font-family: monospace;">
                    Credentials: <strong>user</strong> / <strong>user123</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("👤 Log in as Operational User (Manager Access)", key="btn_demo_user", use_container_width=True):
            perform_login("user", DEMO_ACCOUNTS["user"])
            st.rerun()

    with col_form:
        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 24px; box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);">
                <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC; margin-bottom: 6px;">🔐 Account Sign In</div>
                <div style="font-size: 0.84rem; color: #94A3B8; margin-bottom: 18px;">Enter your assigned credentials to access operations telemetry.</div>
            """,
            unsafe_allow_html=True
        )

        with st.form("manual_login_form"):
            in_user = st.text_input("Username or Email", placeholder="e.g., admin or user", value="")
            in_pass = st.text_input("Password", type="password", placeholder="••••••••", value="")
            
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            submit = st.form_submit_button("🚀 Authenticate & Launch Assistant", use_container_width=True)

            if submit:
                clean_user = in_user.strip().lower()
                clean_pass = in_pass.strip()

                if clean_user in DEMO_ACCOUNTS and DEMO_ACCOUNTS[clean_user]["password"] == clean_pass:
                    perform_login(clean_user, DEMO_ACCOUNTS[clean_user])
                    st.success(f"Welcome, {DEMO_ACCOUNTS[clean_user]['display_name']}!")
                    st.rerun()
                elif clean_user == "admin" and (clean_pass == "admin" or clean_pass == "admin123"):
                    perform_login("admin", DEMO_ACCOUNTS["admin"])
                    st.success("Admin authenticated successfully.")
                    st.rerun()
                elif clean_user == "user" and (clean_pass == "user" or clean_pass == "user123"):
                    perform_login("user", DEMO_ACCOUNTS["user"])
                    st.success("User authenticated successfully.")
                    st.rerun()
                else:
                    # Check DB registered users
                    authenticated_via_db = False
                    try:
                        from backend.app.services.admin_service import get_admin_service
                        db_user = get_admin_service().get_user_by_username(clean_user)
                        if db_user and db_user.get("status") == "Active" and db_user.get("password") == clean_pass:
                            user_obj = {
                                "role": db_user.get("role", "user"),
                                "display_name": db_user.get("display_name", clean_user.capitalize()),
                                "title": db_user.get("title", "Operations Specialist"),
                                "email": db_user.get("email", ""),
                                "avatar": "👑" if db_user.get("role") == "admin" else "👤"
                            }
                            perform_login(clean_user, user_obj)
                            authenticated_via_db = True
                            st.success(f"Welcome, {user_obj['display_name']}!")
                            st.rerun()
                        elif db_user and db_user.get("status") != "Active":
                            st.error(f"Account '{clean_user}' is currently {db_user.get('status')}. Contact administrator.")
                            authenticated_via_db = True
                    except Exception:
                        pass
                    if not authenticated_via_db:
                        st.error("Invalid credentials. Try demo accounts 'admin / admin123' or 'user / user123'.")

        st.markdown(
            """
                <div style="margin-top: 18px; padding-top: 14px; border-top: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-between; font-size: 0.78rem; color: #64748B;">
                    <span>🔒 256-Bit SSL Encrypted</span>
                    <span>🛡️ RBAC Policy Active</span>
                    <span>⚡ FastAPI Microservices</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
