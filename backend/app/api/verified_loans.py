from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_verified_loans():
    return []
