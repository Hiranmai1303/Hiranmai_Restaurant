"""
Custom CSS & Design System for Restaurant Operations Assistant
Premium Dark SaaS Aesthetic featuring:
- Full Project Title: "AI-Powered Restaurant Operations & Review Assistant" with smooth animated gradients & hover transitions
- Deep Navy / Charcoal (#0B1220) background
- Soft Teal (#14B8A6) & Warm Amber (#F59E0B) accents
- Glassmorphic surface cards with subtle borders & micro-animations
"""
import streamlit as st

CUSTOM_CSS = """
<style>
/* Modern Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #0B1220;
    color: #F8FAFC;
}

/* Base App Background */
.stApp {
    background: radial-gradient(circle at 50% 0%, #111C30 0%, #0B1220 70%);
}

/* Hide default streamlit header decoration */
header[data-testid="stHeader"] {
    background: rgba(11, 18, 32, 0.8) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
}

/* -------------------------------------------------------------------------
   TOP NAVBAR WITH PROJECT TITLE & SMOOTH TRANSITIONS
------------------------------------------------------------------------- */
.navbar-container {
    background: rgba(15, 23, 42, 0.82);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(20, 184, 166, 0.25);
    border-radius: 16px;
    padding: 16px 26px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    box-shadow: 0 12px 36px -10px rgba(0, 0, 0, 0.6), 0 0 20px -5px rgba(20, 184, 166, 0.15);
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeInDown 0.6s ease-out;
}

.navbar-container:hover {
    border-color: rgba(20, 184, 166, 0.45);
    box-shadow: 0 16px 42px -8px rgba(0, 0, 0, 0.7), 0 0 28px -4px rgba(20, 184, 166, 0.25);
    transform: translateY(-2px);
}

@keyframes fadeInDown {
    0% {
        opacity: 0;
        transform: translateY(-12px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

.navbar-brand {
    display: flex;
    align-items: center;
    gap: 16px;
}

.navbar-logo-icon {
    background: linear-gradient(135deg, #14B8A6 0%, #0F766E 100%);
    color: #FFFFFF;
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.45rem;
    box-shadow: 0 6px 18px rgba(20, 184, 166, 0.4);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.navbar-container:hover .navbar-logo-icon {
    transform: rotate(6deg) scale(1.06);
    box-shadow: 0 8px 22px rgba(20, 184, 166, 0.55);
}

.navbar-title-wrapper {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.navbar-project-title {
    font-size: 1.6rem;
    font-weight: 900;
    letter-spacing: -0.025em;
    line-height: 1.2;
    background: linear-gradient(135deg, #FFFFFF 0%, #38BDF8 30%, #2DD4BF 70%, #FBBF24 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: titleShimmer 5s linear infinite;
    text-shadow: 0 0 28px rgba(45, 212, 191, 0.3);
    transition: all 0.3s ease;
}

@keyframes titleShimmer {
    0% {
        background-position: 0% center;
    }
    50% {
        background-position: 100% center;
    }
    100% {
        background-position: 0% center;
    }
}

.navbar-subtitle {
    font-size: 0.8rem;
    color: #94A3B8;
    font-weight: 500;
    letter-spacing: 0.02em;
    display: flex;
    align-items: center;
    gap: 6px;
}

.navbar-subtitle-badge {
    background: rgba(20, 184, 166, 0.15);
    color: #2DD4BF;
    border: 1px solid rgba(20, 184, 166, 0.3);
    padding: 1px 7px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
}

.navbar-right {
    display: flex;
    align-items: center;
    gap: 16px;
}

.ai-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(20, 184, 166, 0.12);
    border: 1px solid rgba(20, 184, 166, 0.35);
    color: #2DD4BF;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 7px 16px;
    border-radius: 9999px;
    letter-spacing: 0.02em;
    transition: all 0.3s ease;
}

.ai-status-pill:hover {
    background: rgba(20, 184, 166, 0.22);
    border-color: rgba(20, 184, 166, 0.6);
    box-shadow: 0 0 14px rgba(20, 184, 166, 0.3);
}

.pulse-dot {
    width: 9px;
    height: 9px;
    background-color: #14B8A6;
    border-radius: 50%;
    box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.7);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.75);
    }
    70% {
        transform: scale(1);
        box-shadow: 0 0 0 9px rgba(20, 184, 166, 0);
    }
    100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(20, 184, 166, 0);
    }
}

.manager-avatar-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.09);
    padding: 7px 14px;
    border-radius: 12px;
    font-size: 0.84rem;
    color: #E2E8F0;
    font-weight: 500;
    transition: all 0.25s ease;
}

.manager-avatar-badge:hover {
    background: rgba(255, 255, 255, 0.09);
    border-color: rgba(255, 255, 255, 0.16);
}

/* -------------------------------------------------------------------------
   WELCOME BANNER
------------------------------------------------------------------------- */
.welcome-banner {
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.09) 0%, rgba(15, 23, 42, 0.65) 100%);
    border: 1px solid rgba(20, 184, 166, 0.25);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.4);
    transition: transform 0.3s ease;
}

.welcome-banner:hover {
    transform: translateY(-2px);
}

.welcome-heading {
    font-size: 1.45rem;
    font-weight: 800;
    color: #F8FAFC;
    margin-bottom: 4px;
    letter-spacing: -0.01em;
}

.welcome-sub {
    font-size: 0.92rem;
    color: #94A3B8;
    line-height: 1.45;
}

/* -------------------------------------------------------------------------
   METRIC KPI CARDS
------------------------------------------------------------------------- */
.metric-card {
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 20px 22px;
    backdrop-filter: blur(14px);
    box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.4);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-3px);
    border-color: rgba(20, 184, 166, 0.45);
    box-shadow: 0 14px 30px -4px rgba(20, 184, 166, 0.18);
}

.metric-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.metric-title {
    color: #94A3B8;
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.metric-icon {
    font-size: 1.25rem;
    opacity: 0.88;
}

.metric-value {
    color: #F8FAFC;
    font-size: 2.1rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.02em;
}

.metric-sub {
    color: #14B8A6;
    font-size: 0.82rem;
    font-weight: 500;
    margin-top: 8px;
    display: flex;
    align-items: center;
    gap: 4px;
}

.metric-sub.amber {
    color: #F59E0B;
}

.metric-sub.rose {
    color: #F87171;
}

.metric-sub.slate {
    color: #94A3B8;
}

/* -------------------------------------------------------------------------
   AI ASSISTANT SEARCH & QUERY CARD
------------------------------------------------------------------------- */
.ai-assistant-card {
    background: linear-gradient(135deg, rgba(17, 24, 39, 0.88) 0%, rgba(15, 23, 42, 0.96) 100%);
    border: 1px solid rgba(20, 184, 166, 0.32);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 22px;
    box-shadow: 0 12px 36px -8px rgba(0, 0, 0, 0.55);
    position: relative;
    transition: border-color 0.3s ease;
}

.ai-assistant-card:hover {
    border-color: rgba(20, 184, 166, 0.5);
}

.ai-assistant-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 6px;
}

.ai-assistant-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #F8FAFC;
    letter-spacing: -0.01em;
}

.ai-assistant-sub {
    font-size: 0.9rem;
    color: #94A3B8;
    margin-bottom: 16px;
    line-height: 1.45;
}

/* -------------------------------------------------------------------------
   STRUCTURED AI RESPONSE CARD
------------------------------------------------------------------------- */
.response-container {
    background: rgba(15, 23, 42, 0.78);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 22px 26px;
    margin-top: 18px;
    margin-bottom: 22px;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
    transition: border-color 0.3s ease;
}

.response-container:hover {
    border-color: rgba(20, 184, 166, 0.3);
}

.response-section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.05rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-top: 16px;
    margin-bottom: 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.response-section-title:first-child {
    margin-top: 0;
}

.response-section-title.teal {
    color: #14B8A6;
}

.response-section-title.amber {
    color: #F59E0B;
}

/* -------------------------------------------------------------------------
   REVIEW & INCIDENT CARDS
------------------------------------------------------------------------- */
.review-card {
    background: rgba(15, 23, 42, 0.68);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 14px;
    transition: all 0.25s ease;
}

.review-card:hover {
    border-color: rgba(20, 184, 166, 0.35);
    background: rgba(20, 29, 48, 0.8);
    transform: translateY(-2px);
}

.review-card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.review-restaurant {
    font-size: 1.02rem;
    font-weight: 700;
    color: #F8FAFC;
}

.review-rating-stars {
    color: #F59E0B;
    font-weight: 600;
    font-size: 0.9rem;
}

.review-text-quote {
    color: #CBD5E1;
    font-size: 0.9rem;
    line-height: 1.5;
    font-style: italic;
    background: rgba(11, 18, 32, 0.55);
    border-left: 3px solid #14B8A6;
    padding: 10px 14px;
    border-radius: 0 6px 6px 0;
    margin: 10px 0;
}

.review-card-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    color: #94A3B8;
}

/* -------------------------------------------------------------------------
   BADGES & STATUS PILLS
------------------------------------------------------------------------- */
.badge-high {
    background: rgba(239, 68, 68, 0.14);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.32);
    padding: 3px 10px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.76rem;
    display: inline-block;
}

.badge-medium {
    background: rgba(245, 158, 11, 0.14);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.32);
    padding: 3px 10px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.76rem;
    display: inline-block;
}

.badge-low {
    background: rgba(20, 184, 166, 0.14);
    color: #2DD4BF;
    border: 1px solid rgba(20, 184, 166, 0.32);
    padding: 3px 10px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.76rem;
    display: inline-block;
}

.badge-category {
    background: rgba(20, 184, 166, 0.12);
    color: #5EEAD4;
    border: 1px solid rgba(20, 184, 166, 0.28);
    padding: 3px 10px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.76rem;
    display: inline-block;
}

/* -------------------------------------------------------------------------
   AGENT TRACE & TIMELINE BOX
------------------------------------------------------------------------- */
.agent-step-box {
    background: #0D1527;
    border-left: 3px solid #14B8A6;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.84rem;
    color: #E2E8F0;
}

/* -------------------------------------------------------------------------
   PAGE HEADERS
------------------------------------------------------------------------- */
.app-header {
    font-size: 1.8rem;
    font-weight: 800;
    color: #F8FAFC;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}

.app-subhead {
    color: #94A3B8;
    font-size: 0.92rem;
    margin-bottom: 22px;
    line-height: 1.4;
}

/* -------------------------------------------------------------------------
   CITATION QUOTE BOX
------------------------------------------------------------------------- */
.citation-box {
    background: rgba(11, 18, 32, 0.6);
    border-left: 3px solid #14B8A6;
    padding: 12px 16px;
    border-radius: 4px;
    margin-top: 8px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    color: #CBD5E1;
    line-height: 1.5;
}

/* -------------------------------------------------------------------------
   PROGRESS / SEVERITY VISUALIZATION BARS
------------------------------------------------------------------------- */
.progress-container {
    background: rgba(255, 255, 255, 0.06);
    border-radius: 9999px;
    height: 8px;
    width: 100%;
    margin-top: 6px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 9999px;
}

.progress-fill.teal {
    background: #14B8A6;
}

.progress-fill.amber {
    background: #F59E0B;
}

.progress-fill.rose {
    background: #EF4444;
}

/* -------------------------------------------------------------------------
   SIDEBAR & LEFT NAVBAR MODERN DESIGN & MICRO-TRANSITIONS
------------------------------------------------------------------------- */
section[data-testid="stSidebar"] {
    background: radial-gradient(ellipse at 50% 0%, #0F1D38 0%, #080D1A 85%) !important;
    border-right: 1px solid rgba(20, 184, 166, 0.22) !important;
    box-shadow: 6px 0 32px rgba(0, 0, 0, 0.55) !important;
}

/* Sidebar Brand Card */
.sidebar-brand-card {
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.16) 0%, rgba(15, 23, 42, 0.88) 100%);
    border: 1px solid rgba(20, 184, 166, 0.35);
    border-radius: 16px;
    padding: 16px 18px;
    margin-bottom: 12px;
    box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.5), 0 0 16px -2px rgba(20, 184, 166, 0.2);
    backdrop-filter: blur(14px);
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.sidebar-brand-card:hover {
    border-color: rgba(20, 184, 166, 0.65);
    transform: translateY(-2px);
    box-shadow: 0 12px 32px -4px rgba(0, 0, 0, 0.6), 0 0 24px -2px rgba(20, 184, 166, 0.35);
}

.sidebar-brand-icon {
    background: linear-gradient(135deg, #14B8A6 0%, #0F766E 100%);
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.45rem;
    box-shadow: 0 4px 16px rgba(20, 184, 166, 0.45);
    transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
    flex-shrink: 0;
}

.sidebar-brand-card:hover .sidebar-brand-icon {
    transform: rotate(8deg) scale(1.08);
}

.sidebar-title-text {
    font-size: 1.12rem;
    font-weight: 900;
    line-height: 1.25;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, #FFFFFF 0%, #2DD4BF 60%, #38BDF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sidebar-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(20, 184, 166, 0.16);
    color: #2DD4BF;
    border: 1px solid rgba(20, 184, 166, 0.35);
    border-radius: 9999px;
    padding: 3px 10px;
    font-size: 0.74rem;
    font-weight: 700;
    margin-top: 6px;
    letter-spacing: 0.02em;
}

/* Sidebar Radio Navigation Items */
section[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 7px;
    padding: 2px 0;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size: 0.90rem !important;
    font-weight: 600 !important;
    color: #CBD5E1 !important;
    padding: 9px 14px !important;
    border-radius: 10px !important;
    background: rgba(255, 255, 255, 0.025) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
    display: flex !important;
    align-items: center !important;
    margin-bottom: 2px !important;
    cursor: pointer !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: linear-gradient(90deg, rgba(20, 184, 166, 0.2) 0%, rgba(15, 23, 42, 0.75) 100%) !important;
    border-color: rgba(20, 184, 166, 0.5) !important;
    color: #FFFFFF !important;
    transform: translateX(6px) !important;
    box-shadow: 0 4px 16px rgba(20, 184, 166, 0.2) !important;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:active {
    transform: scale(0.98) translateX(6px) !important;
}

.sidebar-telemetry-card {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(20, 184, 166, 0.24);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 12px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(12px);
    transition: all 0.3s ease;
}

.sidebar-telemetry-card:hover {
    border-color: rgba(20, 184, 166, 0.45);
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(20, 184, 166, 0.18);
}
</style>
"""

def apply_custom_styles():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def render_navbar(active_page: str = "Dashboard", user_name: str = None, user_role: str = None):
    """
    Renders Top Navigation Bar with the official project name:
    'AI-Powered Restaurant Operations & Review Assistant' with smooth transitions.
    """
    if user_name is None:
        user_name = st.session_state.get("user_display_name", "Operations Director")
    current_role = user_role or st.session_state.get("user_role", "user")
    role_icon = "👑" if current_role == "admin" else "👤"
    role_label = "Executive Admin" if current_role == "admin" else "Operations Manager"

    st.markdown(
        f"""
        <div class="navbar-container">
            <div class="navbar-brand">
                <div class="navbar-logo-icon">🍽️</div>
                <div class="navbar-title-wrapper">
                    <div class="navbar-project-title">AI-Powered Restaurant Operations & Review Assistant</div>
                    <div class="navbar-subtitle">
                        <span class="navbar-subtitle-badge">Production GenAI</span>
                        <span>Multi-Agent Operations & Review Intelligence Platform</span>
                    </div>
                </div>
            </div>
            <div class="navbar-right">
                <div class="ai-status-pill">
                    <div class="pulse-dot"></div>
                    AI Assistant Online
                </div>
                <div class="manager-avatar-badge" style="gap: 8px;">
                    <span>{role_icon}</span>
                    <span>{user_name} ({role_label})</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
