from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_validation_rules():
    return []
