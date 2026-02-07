from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Prefix set kar diya: Is file ke saare URL '/members' se shuru honge
router = APIRouter(prefix="/members", tags=["Members"])

# --- SCHEMA ---
class MemberSchema(BaseModel):
    name: str
    email: str
    phone: str

# --- ROUTES ---

# 1. Create Member (POST)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_member(member: MemberSchema):
    try:
        # Check: Kya ye email pehle se hai? (Optional Logic)
        existing = supabase.table("members").select("*").eq("email", member.email).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Email already registered!")

        # Insert
        data = supabase.table("members").insert({
            "name": member.name,
            "email": member.email,
            "phone": member.phone
        }).execute()
        
        return {"msg": "Member Registered! 🎉", "data": data.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Get All Members (GET)
@router.get("/")
def get_members():
    try:
        response = supabase.table("members").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Get Single Member (GET)
@router.get("/{member_id}")
def get_single_member(member_id: int):
    response = supabase.table("members").select("*").eq("id", member_id).execute()
    if response.data:
        return response.data[0]
    raise HTTPException(status_code=404, detail="Member not found")