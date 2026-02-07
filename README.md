# 🦁 Library Management System (LMS)

A robust, full-stack application to manage library operations including book inventory, member management, and loan circulation. Built with **FastAPI** for the backend engine and **Streamlit** for the interactive frontend.

## 🚀 Features

- **Dashboard:** Real-time analytics of books, members, and active loans.
- **Inventory Management:** Add, Update, and Delete books (Admin protected).
- **Circulation Desk:** Issue and Return books with automatic status updates.
- **Member Directory:** Register and view library members.
- **Smart Security:** Admin-only access for critical operations using API Key headers.
- **Database:** Powered by Supabase (PostgreSQL) for reliable data persistence.

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** Streamlit, Pandas
- **Database:** Supabase (PostgreSQL)
- **Authentication:** Custom Header-based Admin Key
- **Tools:** Git, Pydantic, Requests

## 📂 Project Structure

```text
├── routers/          # API Routes for Books, Members, Loans
├── .gitignore        # Files to exclude from Git
├── app.py            # Streamlit Frontend Application
├── dependencies.py   # Security & Dependency Injection
├── main.py           # FastAPI Backend Entry Point
└── requirements.txt  # Project Dependencies
```

### ⚙️ Installation & Setup

- **Follow these steps to run the project locally:**

### 1. Clone the Repository
```bash
git clone https://github.com/shubham-s-dev/library-system-live.git
```

### 2. Install Dependencies
- **Make sure you have Python installed.**
```bash
    pip install -r requirements.txt
```

### 3. Configure Environment Variables
- **Create a .env file in the root directory and add your Supabase credentials:**
```bash
    SUPABASE_URL=your_supabase_url_here
    SUPABASE_KEY=your_supabase_anon_key_here
```

### 4. Run the Backend (FastAPI)
- **Open a terminal and run:**
```bash
    uvicorn main:app --reload
```
- **Server will start at [http://127.0.0.1:8000](http://127.0.0.1:8000)**

### 5. Run the Frontend (Streamlit)
- **Open a new terminal and run:**

```bash
    streamlit run app.py
```
- **App will open in your browser at http://localhost:8501**
    
### 🔐 Admin Access
- **To access Admin features (Delete/Update/Issue), use the default key configured in the backend (e.g., shubham-secret-boss).**
