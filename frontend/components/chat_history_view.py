"""
Chat History & Conversation Thread Component for Restaurant Operations Assistant
Provides:
- Persistent SQLite-backed user chat history recording (survives logout & browser refresh)
- Interactive conversational thread (st.chat_message) with quick follow-ups
- Sidebar chat history drawer for switching between past inquiries
- Comprehensive dedicated Full History View with search, category filtering, and report restoring
"""
import time
import datetime
import pandas as pd
from typing import Optional, List, Dict, Any
import streamlit as st

from frontend.services.api_client import api_client

def sync_chat_history_from_db(username: Optional[str] = None) -> list:
    """
    Synchronizes the in-memory st.session_state['chat_history'] with
    persistent SQLite database storage for the authenticated user.
    """
    uname = username or st.session_state.get("username", "user")
    try:
        db_history = api_client.get_chat_history(username=uname, limit=50)
        if db_history:
            st.session_state["chat_history"] = db_history
            return db_history
    except Exception:
        pass

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    return st.session_state["chat_history"]

def record_chat_interaction(
    query: str,
    report: dict,
    user_name: str = "Operations Analyst",
    category: str = None,
    page_source: str = "Central Operations Analyst"
):
    """
    Records an operational query and its AI diagnostic answer to BOTH
    persistent SQLite database and the user's active session state.
    """
    clean_query = query.strip()
    if not clean_query:
        return

    username = st.session_state.get("username", "user")
    user_role = st.session_state.get("user_role", "user")

    # Prevent immediate duplicate at the top of the session list
    if "chat_history" in st.session_state and st.session_state["chat_history"]:
        if st.session_state["chat_history"][0].get("query") == clean_query:
            return

    # Extract summary text
    summary_text = ""
    if isinstance(report, dict):
        summary_text = report.get("executive_summary") or report.get("general_llm_response") or report.get("summary") or ""
    elif isinstance(report, str):
        summary_text = report
        report = {"executive_summary": summary_text}

    cat = category or (report.get("primary_category") if isinstance(report, dict) else "General Operations") or "General Operations"

    # Persist to SQLite
    try:
        saved_entry = api_client.save_chat_interaction(
            query=clean_query,
            report=report,
            username=username,
            user_name=user_name,
            user_role=user_role,
            category=cat,
            page_source=page_source
        )
    except Exception:
        saved_entry = {}

    if not saved_entry:
        # Fallback in-memory entry if DB write failed
        prio = (report.get("priority_tier") if isinstance(report, dict) else "P2 - Standard SLA") or "P2 - Standard SLA"
        neg_pct = report.get("negative_sentiment_pct", 68.0) if isinstance(report, dict) else 68.0
        actions = report.get("recommendations", []) if isinstance(report, dict) else []
        saved_entry = {
            "id": f"inq_{int(time.time() * 1000)}",
            "interaction_id": f"inq_{int(time.time() * 1000)}",
            "timestamp": datetime.datetime.now().strftime("%I:%M %p"),
            "query": clean_query,
            "role": "user",
            "user": user_name,
            "username": username,
            "user_role": user_role,
            "category": cat,
            "page_source": page_source,
            "response": {
                "summary": summary_text[:350] + "..." if len(summary_text) > 350 else summary_text,
                "category": cat,
                "priority": prio,
                "sentiment_score": f"{neg_pct:.1f}% Friction" if isinstance(neg_pct, (int, float)) else str(neg_pct),
                "action_items": actions[:4]
            },
            "report": report
        }

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    st.session_state["chat_history"].insert(0, saved_entry)

    # Log to admin audit trail
    try:
        from backend.app.services.admin_service import log_system_event
        log_system_event(
            "INFO",
            "OperationsAnalyst",
            f"User '{username}' [{page_source}] logged inquiry: '{clean_query[:50]}...' [Category: {cat}]."
        )
    except Exception:
        pass

def render_sidebar_chat_history():
    """Renders the collapsible Chat History drawer inside the Streamlit sidebar."""
    username = st.session_state.get("username", "user")
    if "chat_history" not in st.session_state or not st.session_state["chat_history"]:
        sync_chat_history_from_db(username)

    chat_hist = st.session_state.get("chat_history", [])
    with st.expander(f"💬 Chat History ({len(chat_hist)})", expanded=True):
        if not chat_hist:
            st.caption("No inquiries logged yet.")
        else:
            for idx, item in enumerate(chat_hist[:8]):
                q_text = item.get("query", "")
                short_q = q_text[:28] + ("..." if len(q_text) > 28 else "")
                ts = item.get("timestamp", "")
                cat = item.get("response", {}).get("category") or item.get("category", "Operations")

                if st.button(f"🗨️ {short_q}", key=f"sb_hist_{item.get('id', idx)}_{idx}", use_container_width=True, help=f"[{ts}] {q_text}"):
                    st.session_state["analyst_query"] = q_text
                    if "report" in item and item["report"]:
                        st.session_state["active_report"] = item["report"]
                    st.session_state["nav_selection"] = "🎯 Central Operations Analyst"
                    st.rerun()
                st.caption(f"🕒 {ts} • {cat}")

            c_h1, c_h2 = st.columns(2)
            with c_h1:
                if st.button("➕ New Query", key="sb_btn_new_chat", use_container_width=True):
                    st.session_state["analyst_query"] = ""
                    st.session_state.pop("active_report", None)
                    st.session_state["nav_selection"] = "🎯 Central Operations Analyst"
                    st.rerun()
            with c_h2:
                if st.button("🗑️ Clear", key="sb_btn_clear_chat", use_container_width=True):
                    api_client.clear_chat_history(username=username)
                    st.session_state["chat_history"] = []
                    st.session_state.pop("active_report", None)
                    st.rerun()

            if st.button("💬 Open History Page", key="sb_btn_open_full_hist", use_container_width=True):
                st.session_state["nav_selection"] = "💬 Chat History & Inquiries"
                st.rerun()

def render_chat_thread():
    """
    Renders an interactive conversational thread with message bubbles,
    diagnostic summaries, recommendations, and a quick follow-up chat input.
    """
    username = st.session_state.get("username", "user")
    if "chat_history" not in st.session_state or not st.session_state["chat_history"]:
        sync_chat_history_from_db(username)

    curr_chats = st.session_state.get("chat_history", [])
    if not curr_chats:
        st.info("No prior conversation history recorded yet. Enter an inquiry above or select an example prompt to begin!")
    else:
        # Render chronologically from earliest to latest
        for item in reversed(curr_chats):
            q = item.get("query", "")
            resp = item.get("response", {})
            ts = item.get("timestamp", "")
            u_name = item.get("user", "Operations User")
            src = item.get("page_source", "Central Operations Analyst")

            # 1. User Message Turn
            with st.chat_message("user", avatar="👤"):
                st.markdown(
                    f"<div style='display: flex; justify-content: space-between; font-size: 0.82rem; color: #94A3B8; margin-bottom: 4px;'>"
                    f"<span><strong>{u_name}</strong> • <em>{src}</em></span>"
                    f"<span>🕒 {ts}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.markdown(f"<div style='font-size: 0.96rem; color: #F8FAFC; line-height: 1.5;'>{q}</div>", unsafe_allow_html=True)

            # 2. Assistant Message Turn
            with st.chat_message("assistant", avatar="🍽️"):
                cat = resp.get("category", "General Operations")
                prio = resp.get("priority", "Standard SLA")
                sent = resp.get("sentiment_score", "Negative Friction")

                st.markdown(
                    f"""
                    <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 10px;">
                        <span style="background: rgba(20, 184, 166, 0.2); color: #2DD4BF; border: 1px solid rgba(20, 184, 166, 0.4); border-radius: 5px; padding: 2px 8px; font-size: 0.74rem; font-weight: 700;">🏷️ {cat}</span>
                        <span style="background: rgba(245, 158, 11, 0.2); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 5px; padding: 2px 8px; font-size: 0.74rem; font-weight: 700;">⏱️ {prio}</span>
                        <span style="background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 5px; padding: 2px 8px; font-size: 0.74rem; font-weight: 600;">🚨 {sent}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(f"<div style='font-size: 0.92rem; color: #E2E8F0; line-height: 1.6; margin-bottom: 12px;'>{resp.get('summary', '')}</div>", unsafe_allow_html=True)

                actions = resp.get("action_items", [])
                if actions:
                    st.markdown("<strong style='color: #2DD4BF; font-size: 0.86rem;'>📋 Key Recommended SOP Actions:</strong>", unsafe_allow_html=True)
                    for act in actions:
                        st.markdown(f"- {act}")

                # Button to restore full report
                if "report" in item and item["report"]:
                    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
                    if st.button("📊 Open Full Operational Intelligence Report", key=f"btn_chat_rep_{item.get('id')}"):
                        st.session_state["analyst_query"] = q
                        st.session_state["active_report"] = item["report"]
                        st.rerun()

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Quick Follow-Up Chat Input
    followup_query = st.chat_input("Ask a follow-up inquiry or new operational question...")
    if followup_query:
        st.session_state["analyst_query"] = followup_query
        st.session_state["auto_run_query"] = True
        st.rerun()

def render_full_chat_history_page():
    """
    Renders a dedicated, high-aesthetic Full Chat History Page
    with search, category filter, table and conversation bubble views,
    and individual delete actions.
    """
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9)); border: 1px solid rgba(20, 184, 166, 0.3); border-radius: 16px; padding: 22px 28px; margin-bottom: 24px; box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                        <span style="font-size: 1.6rem;">💬</span>
                        <span style="font-size: 1.45rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.01em;">Persistent Operational Chat & Inquiries History</span>
                        <span style="background: rgba(20, 184, 166, 0.2); color: #2DD4BF; border: 1px solid rgba(20, 184, 166, 0.4); border-radius: 6px; padding: 2px 10px; font-size: 0.76rem; font-weight: 700;">SQLITE PERSISTENT</span>
                    </div>
                    <div style="font-size: 0.88rem; color: #94A3B8;">
                        Every managerial inquiry, diagnostic analysis, and task executed across the assistant is permanently saved in SQLite and preserved across logins and sessions.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    username = st.session_state.get("username", "user")
    # Always sync latest from DB
    hist = sync_chat_history_from_db(username)

    # Search & Filter Toolbar
    c_f1, c_f2, c_f3, c_f4 = st.columns([1.6, 1.2, 0.8, 0.8])
    with c_f1:
        search_kw = st.text_input("🔍 Search Past Inquiries & Responses", placeholder="e.g. slow service, patio, cold food, Mon Ami Gabi", value="")
    with c_f2:
        cat_choices = ["All Categories"] + sorted(list(set(item.get("category", "General Operations") for item in hist)))
        sel_cat = st.selectbox("Category Filter", cat_choices, index=0)
    with c_f3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh History", use_container_width=True):
            sync_chat_history_from_db(username)
            st.rerun()
    with c_f4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
            api_client.clear_chat_history(username=username)
            st.session_state["chat_history"] = []
            st.success("Chat history cleared from database.")
            st.rerun()

    # Filter records
    filtered = hist
    if search_kw.strip():
        kw = search_kw.strip().lower()
        filtered = [
            item for item in filtered
            if kw in item.get("query", "").lower() or kw in str(item.get("response", {})).lower()
        ]
    if sel_cat != "All Categories":
        filtered = [item for item in filtered if item.get("category") == sel_cat]

    # Metrics Summary
    tot_inq = len(filtered)
    unique_cats = len(set(item.get("category", "") for item in filtered))
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Logged Inquiries", f"{tot_inq}")
    with m2:
        st.metric("Distinct Categories", f"{unique_cats}")
    with m3:
        st.metric("Storage Engine", "SQLite3 (Persistent)")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    t_thread, t_table = st.tabs(["🗨️ Interactive Dialogue Stream", "📋 Tabular Audit Log"])

    with t_thread:
        if not filtered:
            st.info("No saved inquiries match your filter criteria.")
        else:
            for item in filtered:
                q = item.get("query", "")
                resp = item.get("response", {})
                ts = item.get("timestamp", "")
                src = item.get("page_source", "Operations Assistant")
                cat = item.get("category", "General Operations")
                iid = item.get("interaction_id") or item.get("id")

                with st.container():
                    st.markdown(
                        f"""
                        <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 18px 22px; margin-bottom: 16px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <span style="font-weight: 700; color: #2DD4BF; font-size: 0.95rem;">🗨️ {q}</span>
                                </div>
                                <div style="font-size: 0.78rem; color: #94A3B8;">🕒 {ts} • <em>{src}</em></div>
                            </div>
                            <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 10px;">
                                <span style="background: rgba(20, 184, 166, 0.2); color: #2DD4BF; border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700;">{cat}</span>
                                <span style="background: rgba(245, 158, 11, 0.2); color: #F59E0B; border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700;">{resp.get('priority', 'P2 - SLA')}</span>
                                <span style="background: rgba(239, 68, 68, 0.15); color: #F87171; border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 600;">{resp.get('sentiment_score', 'Friction')}</span>
                            </div>
                            <div style="font-size: 0.9rem; color: #CBD5E1; line-height: 1.6; margin-bottom: 10px;">
                                {resp.get('summary', '')}
                            </div>
                        """,
                        unsafe_allow_html=True
                    )

                    actions = resp.get("action_items", [])
                    if actions:
                        st.markdown("<strong style='color: #2DD4BF; font-size: 0.82rem;'>📋 Action Items:</strong>", unsafe_allow_html=True)
                        for a in actions:
                            st.markdown(f"<span style='font-size: 0.84rem; color: #E2E8F0;'>• {a}</span>", unsafe_allow_html=True)

                    btn_c1, btn_c2 = st.columns([1.5, 6])
                    with btn_c1:
                        if st.button("📊 Open Report", key=f"btn_full_open_{iid}"):
                            st.session_state["analyst_query"] = q
                            if "report" in item and item["report"]:
                                st.session_state["active_report"] = item["report"]
                            st.session_state["nav_selection"] = "🎯 Central Operations Analyst"
                            st.rerun()
                    with btn_c2:
                        if st.button("🗑️ Delete Entry", key=f"btn_full_del_{iid}"):
                            api_client.delete_chat_interaction(iid)
                            sync_chat_history_from_db(username)
                            st.rerun()

                    st.markdown("</div>", unsafe_allow_html=True)

    with t_table:
        if not filtered:
            st.info("No table records.")
        else:
            table_rows = []
            for item in filtered:
                resp = item.get("response", {})
                table_rows.append({
                    "Interaction ID": item.get("interaction_id") or item.get("id"),
                    "Time": item.get("timestamp", ""),
                    "User": item.get("user", ""),
                    "Category": item.get("category", ""),
                    "Page Task": item.get("page_source", ""),
                    "Query Text": item.get("query", ""),
                    "Summary Diagnosis": resp.get("summary", "")[:120] + "..."
                })
            df_hist = pd.DataFrame(table_rows)
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
