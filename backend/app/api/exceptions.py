from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_exceptions():
    return []
