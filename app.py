import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="LMS Portal", page_icon="🦁", layout="wide")
API_URL = "http://127.0.0.1:8000"

# --- SESSION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'role' not in st.session_state:
    st.session_state['role'] = None

# --- AUTH FUNCTIONS ---
def login_ui():
    st.title("🦁 Library Login")
    t1, t2 = st.tabs(["Student", "Admin"])
    
    with t1:
        email = st.text_input("Student Email")
        if st.button("Student Sign In"):
            try:
                members = requests.get(f"{API_URL}/members").json()
                if isinstance(members, list):
                    user = next((m for m in members if m['email'] == email), None)
                    if user:
                        st.session_state['authenticated'] = True
                        st.session_state['role'] = 'Student'
                        st.session_state['name'] = user['name']
                        st.rerun()
                    else:
                        st.error("Email not found.")
            except:
                st.error("Backend Error")

    with t2:
        key = st.text_input("Admin Key", type="password")
        if st.button("Admin Access"):
            if key == "shubham-secret-boss":
                st.session_state['authenticated'] = True
                st.session_state['role'] = 'Admin'
                st.session_state['key'] = key
                st.rerun()
            else:
                st.error("Wrong Key")

def logout():
    st.session_state['authenticated'] = False
    st.rerun()

# --- MAIN APP LOGIC ---
if not st.session_state['authenticated']:
    login_ui()
else:
    # Sidebar
    st.sidebar.title(f"User: {st.session_state.get('name', 'Admin')}")
    if st.sidebar.button("Logout"):
        logout()
    
    # Menu Options
    if st.session_state['role'] == "Admin":
        menu = st.sidebar.radio("Navigate", ["Dashboard", "Manage Books", "Members", "Loans"])
    else:
        menu = st.sidebar.radio("Navigate", ["Dashboard", "My Profile"])

    # --- DASHBOARD ---
    if menu == "Dashboard":
        st.header("📊 Dashboard")
        try:
            books = requests.get(f"{API_URL}/books").json()
            if isinstance(books, list) and len(books) > 0:
                avail = len([b for b in books if b['status'] == "Available"])
                
                c1, c2 = st.columns(2)
                c1.metric("Total Books", len(books))
                c2.metric("Available", avail)
                
                st.subheader("📚 Gallery")
                cols = st.columns(5)
                for idx, b in enumerate(books):
                    with cols[idx % 5]:
                        with st.container(border=True):
                            st.image(b.get('image_url') or "https://via.placeholder.com/150", use_container_width=True)
                            st.caption(f"{b['title']} ({b['status']})")
            else:
                st.info("Library is empty. Go to 'Manage Books' to add items.")
        except:
            st.error("Could not fetch data.")

    # --- MANAGE BOOKS (Admin) ---
    elif menu == "Manage Books":
        st.header("⚙️ Manage Books")
        
        # 1. Add Book
        with st.expander("➕ Add New Book", expanded=False):
            with st.form("add_b"):
                t = st.text_input("Title")
                a = st.text_input("Author")
                i = st.text_input("Image URL")
                if st.form_submit_button("Add"):
                    res = requests.post(f"{API_URL}/books", json={"title": t, "author": a, "image_url": i})
                    if res.status_code == 201:
                        st.toast("Added!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(res.text)

        # 2. Update/Delete
        try:
            books = requests.get(f"{API_URL}/books").json()
            if books and isinstance(books, list):
                book_map = {f"{b['title']} (ID: {b['id']})": b['id'] for b in books}
                sel = st.selectbox("Select Book to Edit/Delete", ["None"] + list(book_map.keys()))
                
                if sel != "None":
                    bid = book_map[sel]
                    
                    c1, c2 = st.columns(2)
                    if c1.button("🗑️ Delete Book"):
                        headers = {"x-admin-key": st.session_state['key']}
                        requests.delete(f"{API_URL}/books/{bid}", headers=headers)
                        st.toast("Deleted!")
                        time.sleep(1)
                        st.rerun()
                        
            else:
                st.warning("No books found to manage.")
        except Exception as e:
            st.error(f"Error loading books: {e}")

    # --- MEMBERS ---
    elif menu == "Members":
        st.header("👥 Member Directory")
        try:
            members = requests.get(f"{API_URL}/members").json()
            if members and isinstance(members, list):
                st.dataframe(pd.DataFrame(members))
            else:
                st.info("No members found.")
            
            with st.expander("Register New Member"):
                with st.form("add_m"):
                    n = st.text_input("Name")
                    e = st.text_input("Email")
                    p = st.text_input("Phone")
                    if st.form_submit_button("Register"):
                        requests.post(f"{API_URL}/members", json={"name": n, "email": e, "phone": p})
                        st.rerun()
        except:
            st.error("Error loading members.")

    # --- LOANS ---
    elif menu == "Loans":
        st.header("🏦 Issue & Return")
        try:
            books = requests.get(f"{API_URL}/books").json()
            members = requests.get(f"{API_URL}/members").json()
            
            # Safe Lists
            avail_books = {b['title']: b['id'] for b in books if b['status'] == "Available"}
            borrowed_books = {b['title']: b['id'] for b in books if b['status'] == "Borrowed"}
            mem_dict = {m['name']: m['id'] for m in members}

            t1, t2 = st.tabs(["Issue", "Return"])
            
            with t1:
                if avail_books and mem_dict:
                    b = st.selectbox("Book", list(avail_books.keys()))
                    m = st.selectbox("Member", list(mem_dict.keys()))
                    if st.button("Issue"):
                        res = requests.post(f"{API_URL}/loans", json={"book_id": avail_books[b], "member_id": mem_dict[m]})
                        if res.status_code == 201:
                            st.toast("Success!")
                            time.sleep(1)
                            st.rerun()
                else:
                    st.info("Cannot issue (No books or members).")

            with t2:
                if borrowed_books:
                    b = st.selectbox("Return Book", list(borrowed_books.keys()))
                    if st.button("Return"):
                        res = requests.put(f"{API_URL}/loans/return/{borrowed_books[b]}")
                        if res.status_code == 200:
                            st.toast("Returned!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(res.text) 
                else:
                    st.info("No active loans.")
                    
        except Exception as e:
            st.error(f"Error: {e}")