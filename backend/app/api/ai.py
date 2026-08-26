from fastapi import APIRouter
router = APIRouter()

@router.post("/query")
def ai_query():
    return {}
