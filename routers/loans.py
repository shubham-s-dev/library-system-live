from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

router = APIRouter(prefix="/loans", tags=["Loans"])

class LoanSchema(BaseModel):
    book_id: int
    member_id: int

@router.get("/")
def get_loans():
    # Joins ke saath data lao
    return supabase.table("loans").select("*, books(*), members(*)").execute().data

@router.post("/", status_code=201)
def issue_book(loan: LoanSchema):
    # 1. Check Availability
    book = supabase.table("books").select("status").eq("id", loan.book_id).execute()
    if not book.data:
        raise HTTPException(404, "Book not found")
    if book.data[0]['status'] != "Available":
        raise HTTPException(400, "Book is already borrowed")

    # 2. Create Loan & Update Status
    try:
        supabase.table("loans").insert({"book_id": loan.book_id, "member_id": loan.member_id}).execute()
        supabase.table("books").update({"status": "Borrowed"}).eq("id", loan.book_id).execute()
        return {"msg": "Book Issued!"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put("/return/{book_id}")
def return_book(book_id: int):
    # 1. Find Active Loan (return_date IS NULL)
    active_loan = supabase.table("loans").select("*").eq("book_id", book_id).is_("return_date", "null").execute()
    
    # --- SELF HEALING LOGIC 🏳️ ---
    # Agar loan nahi mila, par book 'Borrowed' hai, to zabardasti 'Available' kar do
    if not active_loan.data:
        # Check if book exists
        book_check = supabase.table("books").select("status").eq("id", book_id).execute()
        if book_check.data and book_check.data[0]['status'] == "Borrowed":
            supabase.table("books").update({"status": "Available"}).eq("id", book_id).execute()
            return {"msg": "Glitch Fixed: Book Forcefully Marked Available."}
        
        raise HTTPException(404, "No active loan found for this book.")

    # 2. Normal Return Process
    loan_id = active_loan.data[0]['id']
    now = datetime.now().isoformat()
    
    supabase.table("loans").update({"return_date": now}).eq("id", loan_id).execute()
    supabase.table("books").update({"status": "Available"}).eq("id", book_id).execute()
    
    return {"msg": "Returned Successfully"}