from fastapi import APIRouter, HTTPException, status, Depends
from dependencies import verify_admin_key
from pydantic import BaseModel
from typing import Optional
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# 1. Setup Database Connection (Local to this file)
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 2. Create Router (Not App)
# 'prefix' ka matlab: Is file ke saare URLs ke aage '/books' khud lag jayega
router = APIRouter(prefix="/books", tags=["Books"])

# 3. Schema (Local)
class BookSchema(BaseModel):
    title: str
    image_url: str = "https://via.placeholder.com/150"
    author: Optional[str] = "Unknown"

# 4. Routes (Notice: @app ki jagah @router use karenge)
# Aur "/books" hatayenge kyunki prefix me laga diya hai

@router.get("/")  # URL banega: /books/
def get_books(q: Optional[str] = None):
    try:
        if q:
            response = supabase.table("books").select("*").ilike("title", f"%{q}%").execute()
        else:
            response = supabase.table("books").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{book_id}") # URL banega: /books/12
def get_single_book(book_id: int):
    response = supabase.table("books").select("*").eq("id", book_id).execute()
    data = response.data
    if data: return data[0]
    raise HTTPException(status_code=404, detail="Book not found.")

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_new_book(book: BookSchema):
    try:
        data = supabase.table("books").insert({
            "title": book.title,
            "image_url": book.image_url,
            "author": book.author,
            "status": "Available"
        }).execute()
        return {"msg": "Created!", "data": data.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{book_id}", dependencies=[Depends(verify_admin_key)]) 
def update_book(book_id: int, updated_data: BookSchema):
    try:
        changes = {
            "title": updated_data.title, 
            "image_url": updated_data.image_url, 
            "author": updated_data.author
        }
        response = supabase.table("books").update(changes).eq("id", book_id).execute()
        if len(response.data) > 0: return {"msg": "Updated", "data": response.data}
        raise HTTPException(status_code=404, detail="Book ID invalid.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{book_id}", dependencies=[Depends(verify_admin_key)])
def delete_book(book_id: int):
    try:
        response = supabase.table("books").delete().eq("id", book_id).execute()
        if len(response.data) > 0: return {"msg": "Deleted"}
        raise HTTPException(status_code=404, detail="Book not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))