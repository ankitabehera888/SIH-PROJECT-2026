from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Lab Reports"])


@router.get("")
def list_reports():
    return report_service.list_reports()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_report(file: UploadFile = File(...)):
    try:
        content = await file.read()
        return report_service.upload(file.filename or "medical-report", file.content_type or "", content)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.get("/{report_id}")
def get_report(report_id: str):
    report = report_service.get_report(report_id)
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found")
    return report


@router.get("/{report_id}/download")
def download_report(report_id: str):
    report = report_service.get_report(report_id)
    path = report_service.file_path(report_id)
    if not report or not path:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report file not found")
    return FileResponse(path, media_type=report["type"], filename=report["name"])


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: str):
    if not report_service.delete(report_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found")
