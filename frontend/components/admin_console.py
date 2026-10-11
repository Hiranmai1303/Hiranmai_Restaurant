"""
Admin Console Component for Restaurant Operations Assistant
Features:
- User Feedback Repository (review, filter, action, delete)
- CSV Data Ingestion & Fleet Importer (upload, validate, ingest)
- Full SQLite Database CRUD Operations (Create, Read, Update, Delete)
- Live System Logs & Audit Trail
- System Metrics & Fleet Diagnostics
"""
import io
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from frontend.services.api_client import api_client

def render_admin_console():
    """Renders the comprehensive Executive Admin Console."""
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9)); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 16px; padding: 22px 28px; margin-bottom: 24px; box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                        <span style="font-size: 1.6rem;">⚙️</span>
                        <span style="font-size: 1.45rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.01em;">Executive Admin Management Console</span>
                        <span style="background: rgba(245, 158, 11, 0.2); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 6px; padding: 2px 10px; font-size: 0.76rem; font-weight: 700;">ADMIN ROLE</span>
                    </div>
                    <div style="font-size: 0.88rem; color: #94A3B8;">
                        Central administration hub for managing user feedback, ingesting fleet CSV datasets, executing database CRUD operations, inspecting system logs, and analyzing infrastructure telemetry.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 5 Dedicated Admin Tabs
    t_feedback, t_csv, t_crud, t_logs, t_metrics = st.tabs([
        "💬 User Feedback",
        "📁 CSV Data Ingestion",
        "👥 Users Management (CRUD)",
        "📜 System Logs & Audit",
        "📊 System Metrics & Telemetry"
    ])

    # =========================================================================
    # TAB 1: USER FEEDBACK REPOSITORY
    # =========================================================================
    with t_feedback:
        st.markdown("<h4 style='color: #F8FAFC; margin-bottom: 8px;'>📝 Operational Feedback Repository</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8; font-size: 0.86rem; margin-bottom: 16px;'>Continuous quality feedback submitted by managers across RAG diagnostics, recommendations, and multi-agent workflows.</p>", unsafe_allow_html=True)

        # Filters
        f_c1, f_c2, f_c3 = st.columns([1.2, 1.2, 1.0])
        with f_c1:
            status_filter = st.selectbox("Status Filter", ["All", "Pending", "Resolved", "Actioned"], key="fb_status_filter")
        with f_c2:
            type_filter = st.selectbox("Category Filter", ["All", "rag", "root_cause", "recommendation", "multi_agent", "general"], key="fb_type_filter")
        with f_c3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Refresh Feedback", use_container_width=True):
                st.rerun()

        # Fetch Feedbacks
        feedbacks = api_client.get_feedbacks(status=status_filter, feedback_type=type_filter)

        # KPI Summary Cards
        total_fb = len(feedbacks)
        resolved_fb = sum(1 for fb in feedbacks if fb.get("status") == "Resolved")
        avg_rating = round(sum(fb.get("rating", 5) for fb in feedbacks) / total_fb, 1) if total_fb else 5.0
        pending_fb = sum(1 for fb in feedbacks if fb.get("status") == "Pending")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Submissions", f"{total_fb}")
        with m2:
            st.metric("Avg Satisfaction", f"{avg_rating} ★")
        with m3:
            st.metric("Resolved Action Items", f"{resolved_fb}")
        with m4:
            st.metric("Pending Review", f"{pending_fb}")

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        if not feedbacks:
            st.info("No feedback entries found matching the selected filters.")
        else:
            for fb in feedbacks:
                fid = fb.get("feedback_id")
                status = fb.get("status", "Pending")
                badge_color = "#10B981" if status == "Resolved" else ("#F59E0B" if status == "Pending" else "#38BDF8")
                
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 14px 18px; margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-weight: 700; color: #F8FAFC; font-size: 0.95rem;">{fb.get('user_name', 'Operations User')}</span>
                                    <span style="font-size: 0.75rem; color: #94A3B8;">({fb.get('user_role', 'user')})</span>
                                    <span style="background: rgba(20, 184, 166, 0.15); color: #2DD4BF; border-radius: 4px; padding: 2px 6px; font-size: 0.72rem; font-weight: 600;">{fb.get('feedback_type', 'general').upper()}</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span style="color: #F59E0B; font-weight: 700;">{'★' * fb.get('rating', 5)}</span>
                                    <span style="background: rgba(255,255,255,0.06); color: {badge_color}; border: 1px solid {badge_color}44; border-radius: 4px; padding: 2px 8px; font-size: 0.74rem; font-weight: 700;">{status}</span>
                                </div>
                            </div>
                            <div style="font-size: 0.86rem; color: #E2E8F0; margin-bottom: 8px;">
                                "{fb.get('comment', 'No comments entered.')}"
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: #64748B;">
                                <span>Ref: <code>{fid}</code> | Interaction: <code>{fb.get('interaction_id', 'N/A')}</code></span>
                                <span>Logged: {fb.get('timestamp', 'Recent')}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Quick action buttons for this feedback
                    act_c1, act_c2, act_c3 = st.columns([1, 1, 3])
                    with act_c1:
                        if status != "Resolved":
                            if st.button("✅ Mark Resolved", key=f"res_{fid}"):
                                api_client.update_feedback_status(fid, "Resolved")
                                st.success("Marked resolved!")
                                st.rerun()
                    with act_c2:
                        if st.button("🗑️ Delete", key=f"del_{fid}"):
                            api_client.delete_feedback(fid)
                            st.warning("Feedback deleted.")
                            st.rerun()
                    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: CSV DATA INGESTION
    # =========================================================================
    with t_csv:
        st.markdown("<h4 style='color: #F8FAFC; margin-bottom: 8px;'>📁 Fleet Review CSV Ingestion</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8; font-size: 0.86rem; margin-bottom: 16px;'>Import new batches of Yelp customer reviews and operational audit files directly into the centralized SQLite database.</p>", unsafe_allow_html=True)

        col_upload, col_sample = st.columns([1.6, 1.0], gap="medium")

        with col_upload:
            uploaded_file = st.file_uploader(
                "Select CSV File for Fleet Ingestion",
                type=["csv"],
                help="Accepts CSV files with review text, ratings, restaurant names, and categories."
            )

        with col_sample:
            st.markdown(
                """
                <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(20, 184, 166, 0.25); border-radius: 12px; padding: 14px 18px;">
                    <div style="font-weight: 700; color: #14B8A6; font-size: 0.86rem; margin-bottom: 6px;">⚡ Presentation Quick-Demo</div>
                    <div style="font-size: 0.8rem; color: #94A3B8; margin-bottom: 12px;">
                        Need a demonstration dataset right now? Click below to instantly generate and test a live 5-review sample CSV.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            generate_sample = st.button("🧪 Generate & Ingest 5 Sample Reviews", use_container_width=True)

        # Handle Sample Generation
        if generate_sample:
            sample_df = pd.DataFrame([
                {
                    "restaurant_name": "Liberty Bell Tavern",
                    "city": "Philadelphia",
                    "stars": 1.0,
                    "complaint_category": "Waiting Time",
                    "text": "Waited 48 minutes for our appetizers during lunch rush. Server never came back to check."
                },
                {
                    "restaurant_name": "Art Museum Cafe",
                    "city": "Philadelphia",
                    "stars": 2.0,
                    "complaint_category": "Food Quality",
                    "text": "The soup was served lukewarm and the bread was stale. Very disappointing for the price."
                },
                {
                    "restaurant_name": "Reading Market Bakery",
                    "city": "Philadelphia",
                    "stars": 4.0,
                    "complaint_category": "Customer Service",
                    "text": "Great cannolis and pastries, though the checkout line was slightly unorganized."
                },
                {
                    "restaurant_name": "Independence Grill",
                    "city": "Philadelphia",
                    "stars": 1.0,
                    "complaint_category": "Cleanliness & Hygiene",
                    "text": "Tables were sticky and dirty napkins were left under the booth. Needs better sanitation."
                },
                {
                    "restaurant_name": "Rittenhouse Bistro",
                    "city": "Philadelphia",
                    "stars": 5.0,
                    "complaint_category": "Order Accuracy",
                    "text": "Impeccable service and steak cooked to perfection. Staff was exceptionally attentive."
                }
            ])
            with st.spinner("Ingesting sample batch into SQLite..."):
                res = api_client.ingest_csv(sample_df, admin_user=st.session_state.get("username", "admin"))
                if res.get("status") == "success":
                    st.success(f"🎉 {res.get('message')} Total database count is now {res.get('total_reviews'):,} records!")
                else:
                    st.error(res.get("message"))

        # Handle File Upload
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-weight: 700; color: #2DD4BF; margin-bottom: 6px;'>📊 CSV Preview ({len(df)} rows, {len(df.columns)} columns)</div>", unsafe_allow_html=True)
                st.dataframe(df.head(5), use_container_width=True)

                # Column Mapping Verification
                cols = [c.lower() for c in df.columns]
                has_text = any(c in cols for c in ["text", "review_text", "comment", "review", "content"])
                
                if not has_text:
                    st.error("⚠️ The uploaded CSV does not contain a recognizable review text column ('text', 'review_text', or 'content').")
                else:
                    st.success("✅ Schema check passed: Review content column detected.")
                    if st.button("🚀 Ingest CSV to Database", key="btn_ingest_csv", type="primary", use_container_width=True):
                        with st.spinner(f"Ingesting {len(df)} records into SQLite database..."):
                            res = api_client.ingest_csv(df, admin_user=st.session_state.get("username", "admin"))
                            if res.get("status") == "success":
                                st.balloons()
                                st.success(f"🎉 Success: {res.get('rows_ingested')} records ingested! Total reviews in database: {res.get('total_reviews'):,}.")
                            else:
                                st.error(f"Ingestion failed: {res.get('message')}")
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")

    # =========================================================================
    # TAB 3: USER MANAGEMENT (CRUD)
    # =========================================================================
    with t_crud:
        st.markdown("<h4 style='color: #F8FAFC; margin-bottom: 8px;'>👥 User Management & RBAC Operations (CRUD)</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8; font-size: 0.86rem; margin-bottom: 16px;'>Complete administrative control over user accounts: register new operators, update roles & permissions, inspect user directories, and manage access statuses.</p>", unsafe_allow_html=True)

        crud_mode = st.radio(
            "User Management Action",
            ["🔍 User Directory (Read)", "➕ Register New User (Create)", "✏️ Edit User Profile (Update)", "🗑️ Deactivate / Delete (Delete)"],
            horizontal=True
        )

        st.markdown("<hr style='margin: 12px 0 18px 0; border: 0; border-top: 1px solid rgba(255, 255, 255, 0.08);'>", unsafe_allow_html=True)

        # -------------------------------------------------------------
        # 1. READ / SEARCH USERS
        # -------------------------------------------------------------
        if "Read" in crud_mode:
            u_c1, u_c2, u_c3, u_c4 = st.columns([1.5, 1.0, 1.0, 0.8])
            with u_c1:
                search_term = st.text_input("Search Username, Name, Email, or Department", placeholder="e.g. admin, sarah, operations", value="")
            with u_c2:
                role_filter = st.selectbox(
                    "Role Filter",
                    ["All", "admin", "operations_analyst", "store_manager", "user"],
                    index=0
                )
            with u_c3:
                status_filter = st.selectbox(
                    "Status Filter",
                    ["All", "Active", "Inactive", "Suspended"],
                    index=0
                )
            with u_c4:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("🔄 Refresh", key="btn_refresh_users", use_container_width=True):
                    st.rerun()

            # Query Users
            user_data = api_client.list_users(search=search_term, role=role_filter, status=status_filter, limit=50)
            users_list = user_data.get("users", [])
            total_users = user_data.get("total", len(users_list))

            # User Metrics Bar
            act_count = sum(1 for u in users_list if u.get("status") == "Active")
            adm_count = sum(1 for u in users_list if u.get("role") == "admin")
            mgr_count = sum(1 for u in users_list if u.get("role") in ["store_manager", "operations_analyst"])

            um1, um2, um3, um4 = st.columns(4)
            with um1:
                st.metric("Total Registered Users", f"{total_users}")
            with um2:
                st.metric("Active Status", f"{act_count}")
            with um3:
                st.metric("Administrators", f"{adm_count}")
            with um4:
                st.metric("Operations Staff", f"{mgr_count}")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            if users_list:
                df_users = pd.DataFrame(users_list)
                rename_map = {
                    "user_id": "User ID",
                    "username": "Username",
                    "display_name": "Full Name",
                    "role": "Role",
                    "title": "Title",
                    "email": "Email",
                    "department": "Department",
                    "status": "Status",
                    "created_at": "Created At",
                    "last_login": "Last Login"
                }
                df_disp = df_users[[c for c in rename_map.keys() if c in df_users.columns]].rename(columns=rename_map)
                st.dataframe(df_disp, use_container_width=True, hide_index=True)
            else:
                st.info("No user accounts found matching the filter criteria.")

        # -------------------------------------------------------------
        # 2. CREATE / REGISTER USER
        # -------------------------------------------------------------
        elif "Create" in crud_mode:
            st.markdown("<h5 style='color: #14B8A6; margin-bottom: 12px;'>➕ Register New Operational User Account</h5>", unsafe_allow_html=True)
            with st.form("create_user_form"):
                cu_c1, cu_c2 = st.columns(2)
                with cu_c1:
                    new_uname = st.text_input("Username *", placeholder="e.g. rachel.green", value="").strip().lower()
                    new_pass = st.text_input("Initial Password *", type="password", placeholder="Minimum 6 characters", value="")
                    new_display = st.text_input("Full Display Name *", placeholder="e.g. Rachel Green", value="")
                    new_email = st.text_input("Corporate Email *", placeholder="e.g. rachel@restaurantops.ai", value="")
                with cu_c2:
                    new_role = st.selectbox(
                        "Assigned Role *",
                        ["user", "operations_analyst", "store_manager", "admin"],
                        format_func=lambda x: {
                            "admin": "👑 Administrator (Full Platform & Admin Access)",
                            "operations_analyst": "📊 Operations Analyst (Analytics & Forecasting)",
                            "store_manager": "🏪 Store Manager (Store Diagnostics & Reports)",
                            "user": "👤 Standard User (Basic Inquiries & Review Views)"
                        }.get(x, x),
                        index=0
                    )
                    new_title = st.text_input("Job Title", value="Shift Operations Specialist")
                    new_dept = st.selectbox("Department", ["Field Operations", "Store Operations", "Fleet Analytics", "Culinary Operations", "Guest Experience", "Executive Leadership"])
                    new_status = st.selectbox("Initial Account Status", ["Active", "Inactive", "Suspended"], index=0)

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                create_user_submit = st.form_submit_button("💾 Register & Save User Account", type="primary", use_container_width=True)

                if create_user_submit:
                    if not new_uname or not new_pass or not new_display or not new_email:
                        st.error("Please fill in all required fields (Username, Password, Display Name, and Email).")
                    else:
                        payload = {
                            "username": new_uname,
                            "password": new_pass,
                            "role": new_role,
                            "display_name": new_display,
                            "title": new_title,
                            "email": new_email,
                            "department": new_dept,
                            "status": new_status
                        }
                        res = api_client.create_user(payload, admin_user=st.session_state.get("username", "admin"))
                        if res.get("status") == "success":
                            st.success(f"✅ User account <strong>@{new_uname}</strong> created successfully! User ID: <code>{res.get('user_id')}</code>")
                        else:
                            st.error(f"❌ Creation failed: {res.get('message')}")

        # -------------------------------------------------------------
        # 3. UPDATE / EDIT USER
        # -------------------------------------------------------------
        elif "Update" in crud_mode:
            st.markdown("<h5 style='color: #F59E0B; margin-bottom: 12px;'>✏️ Modify User Profile & Permissions</h5>", unsafe_allow_html=True)
            
            # Load users list for selection dropdown
            all_users = api_client.list_users(limit=100).get("users", [])
            user_options = {f"{u.get('display_name')} (@{u.get('username')}) - {u.get('role').upper()}": u for u in all_users}
            
            if not user_options:
                st.warning("No users available to modify.")
            else:
                selected_label = st.selectbox("Select User Account to Modify", list(user_options.keys()))
                target_user = user_options[selected_label]
                target_uid = target_user.get("user_id")

                st.info(f"Editing User Profile: **{target_user.get('display_name')}** (`@{target_user.get('username')}`) | User ID: `#{target_uid}`")

                with st.form("edit_user_profile_form"):
                    eu_c1, eu_c2 = st.columns(2)
                    with eu_c1:
                        e_display = st.text_input("Full Display Name", value=target_user.get("display_name", ""))
                        e_email = st.text_input("Corporate Email", value=target_user.get("email", ""))
                        e_title = st.text_input("Job Title", value=target_user.get("title", ""))
                        e_new_pass = st.text_input("Reset Password (Leave blank to keep existing)", type="password", value="")
                    with eu_c2:
                        role_list = ["admin", "operations_analyst", "store_manager", "user"]
                        cur_role = target_user.get("role", "user")
                        e_role = st.selectbox(
                            "Assigned Role",
                            role_list,
                            index=role_list.index(cur_role) if cur_role in role_list else 3
                        )
                        dept_list = ["Field Operations", "Store Operations", "Fleet Analytics", "Culinary Operations", "Guest Experience", "Executive Leadership"]
                        cur_dept = target_user.get("department", "Field Operations")
                        e_dept = st.selectbox(
                            "Department",
                            dept_list,
                            index=dept_list.index(cur_dept) if cur_dept in dept_list else 0
                        )
                        status_list = ["Active", "Inactive", "Suspended"]
                        cur_stat = target_user.get("status", "Active")
                        e_status = st.selectbox(
                            "Account Status",
                            status_list,
                            index=status_list.index(cur_stat) if cur_stat in status_list else 0
                        )

                    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                    update_user_submit = st.form_submit_button("💾 Save Profile Updates", type="primary", use_container_width=True)

                    if update_user_submit:
                        up_payload = {
                            "display_name": e_display,
                            "email": e_email,
                            "title": e_title,
                            "role": e_role,
                            "department": e_dept,
                            "status": e_status
                        }
                        if e_new_pass.strip():
                            up_payload["password"] = e_new_pass.strip()

                        res = api_client.update_user(target_uid, up_payload, admin_user=st.session_state.get("username", "admin"))
                        if res.get("status") == "success":
                            st.success(f"✅ User profile for <strong>@{target_user.get('username')}</strong> successfully updated!")
                        else:
                            st.error(f"❌ Update failed: {res.get('message')}")

        # -------------------------------------------------------------
        # 4. DELETE / DEACTIVATE USER
        # -------------------------------------------------------------
        elif "Delete" in crud_mode:
            st.markdown("<h5 style='color: #EF4444; margin-bottom: 12px;'>🗑️ Deactivate or Delete User Account</h5>", unsafe_allow_html=True)
            
            all_users_del = api_client.list_users(limit=100).get("users", [])
            del_options = {f"{u.get('display_name')} (@{u.get('username')}) - {u.get('status')}": u for u in all_users_del}
            
            if not del_options:
                st.warning("No users available to remove.")
            else:
                del_label = st.selectbox("Select User Account", list(del_options.keys()))
                del_target = del_options[del_label]
                del_uid = del_target.get("user_id")
                del_uname = del_target.get("username")

                if del_uname == "admin":
                    st.error("🔒 The primary super-administrator account 'admin' is protected and cannot be deleted or deactivated.")
                else:
                    st.warning(f"⚠️ Action on user: **{del_target.get('display_name')}** (`@{del_uname}`) | Role: `{del_target.get('role')}` | Status: `{del_target.get('status')}`")
                    
                    d_c1, d_c2 = st.columns(2)
                    with d_c1:
                        if st.button("🚫 Set Account to Inactive", use_container_width=True):
                            res = api_client.update_user(del_uid, {"status": "Inactive"}, admin_user=st.session_state.get("username", "admin"))
                            if res.get("status") == "success":
                                st.success(f"User @{del_uname} set to Inactive status.")
                            else:
                                st.error(res.get("message"))
                    with d_c2:
                        if st.button("🚨 Permanently Delete User", type="primary", use_container_width=True):
                            res = api_client.delete_user(del_uid, admin_user=st.session_state.get("username", "admin"))
                            if res.get("status") == "success":
                                st.success(f"✅ User @{del_uname} has been permanently deleted from the database.")
                            else:
                                st.error(f"❌ Deletion failed: {res.get('message')}")

    # =========================================================================
    # TAB 4: SYSTEM LOGS & AUDIT TRAIL
    # =========================================================================
    with t_logs:
        st.markdown("<h4 style='color: #F8FAFC; margin-bottom: 8px;'>📜 Live System Logs & Audit Trail</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8; font-size: 0.86rem; margin-bottom: 16px;'>Real-time streaming audit trail capturing user authentication events, model queries, CSV ingestions, and database transactions.</p>", unsafe_allow_html=True)

        l_c1, l_c2, l_c3 = st.columns([1.2, 1.6, 1.0])
        with l_c1:
            level_sel = st.selectbox("Log Level", ["ALL", "INFO", "WARNING", "ERROR", "AUDIT"], index=0)
        with l_c2:
            log_search = st.text_input("Search Logs", placeholder="e.g. Ingestion, User, SQLite", value="")
        with l_c3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Refresh Stream", use_container_width=True):
                st.rerun()

        logs = api_client.get_admin_logs(level=level_sel, search=log_search, limit=80)

        # Terminal Box
        log_html = "<div style='background: #090E17; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 16px; font-family: \"JetBrains Mono\", monospace; font-size: 0.8rem; height: 420px; overflow-y: auto; line-height: 1.6;'>"
        
        if not logs:
            log_html += "<div style='color: #64748B;'>No log records matching criteria.</div>"
        else:
            for item in logs:
                lvl = item.get("level", "INFO")
                if lvl == "ERROR":
                    color = "#EF4444"
                elif lvl == "WARNING":
                    color = "#F59E0B"
                elif lvl == "AUDIT":
                    color = "#38BDF8"
                else:
                    color = "#10B981"

                ts = item.get("timestamp", "")
                src = item.get("source", "System")
                msg = item.get("message", "")
                log_html += f"<div><span style='color: #64748B;'>[{ts}]</span> <span style='color: {color}; font-weight: 700;'>[{lvl}]</span> <span style='color: #A855F7;'>[{src}]</span> <span style='color: #E2E8F0;'>{msg}</span></div>"

        log_html += "</div>"
        st.markdown(log_html, unsafe_allow_html=True)

        # Export logs
        log_text = "\n".join([f"[{e.get('timestamp')}] [{e.get('level')}] [{e.get('source')}] {e.get('message')}" for e in logs])
        st.download_button("📥 Export Audit Log (.log)", data=log_text, file_name="system_audit.log", mime="text/plain")

    # =========================================================================
    # TAB 5: SYSTEM METRICS & TELEMETRY
    # =========================================================================
    with t_metrics:
        st.markdown("<h4 style='color: #F8FAFC; margin-bottom: 8px;'>📊 System Infrastructure & Fleet Telemetry</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8; font-size: 0.86rem; margin-bottom: 16px;'>Deep telemetry on SQLite storage, ChromaDB vector stores, review volume distribution, and AI microservices health.</p>", unsafe_allow_html=True)

        tel = api_client.get_admin_metrics()

        # Telemetry KPI Grid
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Total Fleet Reviews", f"{tel.get('total_reviews', 0):,}")
        with k2:
            st.metric("Identified Complaints", f"{tel.get('complaint_count', 0):,} ({tel.get('complaint_pct', 0)}%)")
        with k3:
            st.metric("Fleet Avg Rating", f"{tel.get('avg_stars', 0.0):.2f} ★")
        with k4:
            st.metric("Database Storage", f"{tel.get('database_size_mb', 0.0)} MB")

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Charts: Categories & Severity
        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            cat_dist = tel.get("category_distribution", {})
            if cat_dist:
                df_cat = pd.DataFrame(list(cat_dist.items()), columns=["Category", "Count"])
                fig_cat = px.bar(
                    df_cat,
                    x="Count",
                    y="Category",
                    orientation="h",
                    title="Complaints by Operational Category",
                    color="Count",
                    color_continuous_scale="Teal"
                )
                fig_cat.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=35, b=20),
                    height=280
                )
                st.plotly_chart(fig_cat, use_container_width=True)

        with c_chart2:
            sev_dist = tel.get("severity_distribution", {})
            if sev_dist:
                df_sev = pd.DataFrame(list(sev_dist.items()), columns=["Severity", "Count"])
                fig_sev = px.pie(
                    df_sev,
                    names="Severity",
                    values="Count",
                    title="Complaint Severity Breakdown",
                    hole=0.45,
                    color_discrete_sequence=["#10B981", "#38BDF8", "#F59E0B", "#F97316", "#EF4444"]
                )
                fig_sev.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=35, b=20),
                    height=280
                )
                st.plotly_chart(fig_sev, use_container_width=True)

        # Infrastructure Health Checklist
        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 18px 22px; margin-top: 10px;">
                <div style="font-size: 0.95rem; font-weight: 700; color: #F8FAFC; margin-bottom: 12px;">🛡️ Service Integrity & Engine Telemetry</div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; font-size: 0.84rem;">
                    <div>
                        <div style="color: #94A3B8;">FastAPI Backend:</div>
                        <div style="color: #10B981; font-weight: 700;">● Online (Port 8000)</div>
                    </div>
                    <div>
                        <div style="color: #94A3B8;">SQLite Storage Engine:</div>
                        <div style="color: #10B981; font-weight: 700;">● Connected (WAL Mode)</div>
                    </div>
                    <div>
                        <div style="color: #94A3B8;">Vector Store:</div>
                        <div style="color: #38BDF8; font-weight: 700;">● {tel.get('chromadb_status', 'ChromaDB Active')}</div>
                    </div>
                    <div>
                        <div style="color: #94A3B8;">Active LLM Model:</div>
                        <div style="color: #F59E0B; font-weight: 700;">● {tel.get('llm_model', 'Gemini 2.5 Flash')}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
