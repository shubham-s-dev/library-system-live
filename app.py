import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="LMS Portal", page_icon="🦁", layout="wide")

API_URL = "https://library-api-shubham.onrender.com"

# --- SESSION STATE INITIALIZATION ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'member_id' not in st.session_state:
    st.session_state['member_id'] = None

# --- AUTH FUNCTIONS ---
def login_ui():
    st.title("🦁 Library Portal Login")
    st.markdown("---")
    
    t1, t2 = st.tabs(["🎓 Student Login", "🛡️ Librarian Access"])
    
    # 1. STUDENT LOGIN
    with t1:
        with st.form("stud_login"):
            email = st.text_input("Registered Email Address")
            if st.form_submit_button("Access Library"):
                if not email:
                    st.warning("Please enter your email.")
                else:
                    try:
                        res = requests.get(f"{API_URL}/members")
                        if res.status_code == 200:
                            members = res.json()
                            
                            # --- FIX IS HERE ---
                            # Hum check kar rahe hain ki m['email'] exist karta hai ya nahi
                            user = next(
                                (m for m in members 
                                 if m.get('email') and m['email'].lower() == email.lower()), 
                                None
                            )
                            # -------------------
                            
                            if user:
                                st.session_state['authenticated'] = True
                                st.session_state['role'] = 'Student'
                                st.session_state['user_name'] = user['name']
                                st.session_state['member_id'] = user['id']
                                st.session_state['user_email'] = user['email']
                                st.success(f"Welcome back, {user['name']}!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Email not found. Please contact Admin.")
                        else:
                            st.error("Server is waking up... Try again in 10s.")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

    # 2. ADMIN LOGIN
    with t2:
        with st.form("admin_login"):
            key = st.text_input("Admin Secret Key", type="password")
            if st.form_submit_button("Unlock Admin Panel"):
                if key == "shubham-secret-boss": # HARDCODED KEY
                    st.session_state['authenticated'] = True
                    st.session_state['role'] = 'Admin'
                    st.session_state['user_name'] = "Head Librarian"
                    st.session_state['admin_key'] = key
                    st.success("Admin Access Granted 🔓")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Invalid Access Key")

def logout():
    st.session_state.clear()
    st.rerun()

# ==========================================
# MAIN APP FLOW
# ==========================================

if not st.session_state['authenticated']:
    login_ui()
else:
    # --- SIDEBAR ---
    st.sidebar.header(f"👤 {st.session_state['user_name']}")
    st.sidebar.caption(f"Role: {st.session_state['role']}")
    
    if st.sidebar.button("Log Out", icon="🚪"):
        logout()
    
    st.sidebar.divider()
    
    # Menu Selection
    if st.session_state['role'] == "Admin":
        menu = st.sidebar.radio("Navigate", ["Dashboard", "Manage Books", "Members Directory", "Loan System"])
    else:
        menu = st.sidebar.radio("Navigate", ["Dashboard", "My Profile"])

    # --- 1. DASHBOARD (Common) ---
    if menu == "Dashboard":
        st.header("📊 Library Dashboard")
        try:
            books = requests.get(f"{API_URL}/books").json()
            if isinstance(books, list):
                # Metrics
                total = len(books)
                avail = len([b for b in books if b['status'] == 'Available'])
                borrowed = total - avail
                
                c1, c2, c3 = st.columns(3)
                c1.metric("📚 Total Books", total)
                c2.metric("✅ Available", avail)
                c3.metric("🔄 Borrowed", borrowed)
                
                st.divider()
                st.subheader("🔥 Book Gallery")
                
                # Grid View
                cols = st.columns(5)
                for idx, b in enumerate(books):
                    with cols[idx % 5]:
                        with st.container(border=True):
                            img = b.get('image_url') if b.get('image_url') else "https://via.placeholder.com/150"
                            st.image(img, use_container_width=True)
                            st.caption(f"**{b['title']}**")
                            if b['status'] == "Available":
                                st.markdown(":green[Available]")
                            else:
                                st.markdown(":red[Borrowed]")
            else:
                st.info("Library is currently empty.")
        except:
            st.error("Could not connect to Backend.")

    # --- 2. MY PROFILE (Student Only) ---
    elif menu == "My Profile":
        st.header("🎓 Student Profile")
        
        c1, c2 = st.columns([1, 2])
        with c1:
            with st.container(border=True):
                st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
                st.write(f"**Name:** {st.session_state['user_name']}")
                st.write(f"**Email:** {st.session_state['user_email']}")
                st.caption(f"Member ID: {st.session_state['member_id']}")

        with c2:
            st.subheader("📖 My Active Loans")
            try:
                loans = requests.get(f"{API_URL}/loans").json()
                # Filter loans for this specific user that are NOT returned
                my_loans = [
                    {
                        "Book": l['books']['title'],
                        "Issue Date": l['created_at'][:10],
                        "Status": "🔴 Keep Safe"
                    }
                    for l in loans 
                    if l['member_id'] == st.session_state['member_id'] and l['return_date'] is None
                ]
                
                if my_loans:
                    st.table(pd.DataFrame(my_loans))
                else:
                    st.success("You have no pending books to return.")
            except:
                st.error("Could not fetch loan history.")

    # --- 3. MANAGE BOOKS (Admin Only) ---
    elif menu == "Manage Books":
        st.header("⚙️ Inventory Manager")
        
        # Add Book
        with st.expander("➕ Add New Book", expanded=False):
            with st.form("add_b"):
                c1, c2 = st.columns(2)
                t = c1.text_input("Title")
                a = c2.text_input("Author")
                i = st.text_input("Cover Image URL")
                if st.form_submit_button("Add to Library"):
                    payload = {"title": t, "author": a, "image_url": i}
                    requests.post(f"{API_URL}/books", json=payload)
                    st.toast("Book Added!")
                    time.sleep(1)
                    st.rerun()

        # Delete Book
        try:
            books = requests.get(f"{API_URL}/books").json()
            if books:
                book_map = {f"{b['title']} (ID: {b['id']})": b['id'] for b in books}
                
                with st.expander("🗑️ Delete Book", expanded=False):
                    sel_del = st.selectbox("Select Book", list(book_map.keys()))
                    if st.button("Confirm Delete"):
                        bid = book_map[sel_del]
                        headers = {"x-admin-key": st.session_state['admin_key']}
                        res = requests.delete(f"{API_URL}/books/{bid}", headers=headers)
                        if res.status_code == 200:
                            st.toast("Deleted!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Admin Key Error")
        except:
            st.error("Error loading books.")

    # --- 4. MEMBERS DIRECTORY (Admin Only) ---
    elif menu == "Members Directory":
        st.header("👥 Registered Members")
        
        # Add Member
        with st.expander("➕ Register New Student"):
            with st.form("add_mem"):
                n = st.text_input("Full Name")
                e = st.text_input("Email")
                p = st.text_input("Phone")
                if st.form_submit_button("Register"):
                    res = requests.post(f"{API_URL}/members", json={"name": n, "email": e, "phone": p})
                    if res.status_code == 201:
                        st.success("Member Registered!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(res.text)
        
        # View Members
        try:
            members = requests.get(f"{API_URL}/members").json()
            st.dataframe(pd.DataFrame(members), use_container_width=True)
        except:
            st.info("No members found.")

    # --- 5. LOAN SYSTEM (Admin Only) ---
    elif menu == "Loan System":
        st.header("🏦 Circulation Desk")
        
        try:
            books = requests.get(f"{API_URL}/books").json()
            members = requests.get(f"{API_URL}/members").json()
            loans = requests.get(f"{API_URL}/loans").json()
            
            # Active Loans Dashboard
            st.subheader("Live Status")
            active = [l for l in loans if l['return_date'] is None]
            st.metric("Books Currently Out", len(active))
            
            tab1, tab2 = st.tabs(["📤 Issue Book", "📥 Return Book"])
            
            with tab1:
                avail = {b['title']: b['id'] for b in books if b['status'] == "Available"}
                mems = {m['name']: m['id'] for m in members}
                
                if avail:
                    c1, c2 = st.columns(2)
                    b_sel = c1.selectbox("Book", list(avail.keys()))
                    m_sel = c2.selectbox("Student", list(mems.keys()))
                    
                    if st.button("Issue Book"):
                        payload = {"book_id": avail[b_sel], "member_id": mems[m_sel]}
                        requests.post(f"{API_URL}/loans", json=payload)
                        st.toast("Issued Successfully!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info("No books available.")

            with tab2:
                borrowed = {b['title']: b['id'] for b in books if b['status'] == "Borrowed"}
                if borrowed:
                    b_ret = st.selectbox("Select Book to Return", list(borrowed.keys()))
                    if st.button("Process Return"):
                        requests.put(f"{API_URL}/loans/return/{borrowed[b_ret]}")
                        st.toast("Returned Successfully!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info("No active loans.")
                    
        except:
            st.error("System Offline")
