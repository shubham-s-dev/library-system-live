from fastapi import Header, HTTPException

def verify_admin_key(x_admin_key: str = Header(None)):
    SECRET = "shubham-secret-boss"
    if x_admin_key != SECRET:
        raise HTTPException(status_code=401, detail="🚨 Access Denied! Galat Password.")