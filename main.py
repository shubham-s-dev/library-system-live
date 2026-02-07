from fastapi import FastAPI, Header, HTTPException
from routers import books, members, loans
from fastapi.middleware.cors import CORSMiddleware

# --- SECURITY GUARD ---
def verify_admin_key(api_key: str = Header(None, alias="x-admin-key")):

    SECRET_PASSWORD = "shubham-secret-boss"
    
    if api_key != SECRET_PASSWORD:
        raise HTTPException(status_code=401, detail="🚨 Unauthorized! You don't have the Admin Key.")
    
    return True

# --- Start API ---
app = FastAPI(
    title="Library API (Modular)",
    version="2.0"
)

# --- CORS SETTINGS (The VIP List) ---
origins = [
    "http://localhost:8501",    
    "http://127.0.0.1:8501",    
    "*"                 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,        
    allow_methods=["*"],           
    allow_headers=["*"],            
)

# --- REGISTER ROUTERS ---
app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)

@app.get("/", tags=["General"])
def home():
    return {"status": "Online", "mode": "Modular API 🏗️"}