from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.core.dependencies import get_current_user
from app.models.user import User
import base64

router = APIRouter(
    prefix="/upload",
    tags=["Upload - Tải lên tập tin"]
)

@router.post(
    "/",
    summary="Tải lên tập tin ảnh (Base64)",
    description="Chuyển ảnh thành định dạng Base64 và trả về Data URI để lưu trực tiếp vào DB."
)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ hỗ trợ tải lên file ảnh."
        )
    
    file_data = await file.read()
    
    try:
        b64_data = base64.b64encode(file_data).decode("utf-8")
        data_uri = f"data:{file.content_type};base64,{b64_data}"
        return {"success": True, "data": {"url": data_uri}}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý file: {str(e)}"
        )
