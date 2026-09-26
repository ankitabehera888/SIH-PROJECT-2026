import base64
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.schemas.report import LabReportResponse, LabResult
from app.services.voice_service import voice_service


REPORT_DIR = Path(__file__).resolve().parents[2] / "uploads" / "reports"
REPORT_INDEX = REPORT_DIR / "index.json"
MAX_REPORT_SIZE = 25 * 1024 * 1024

REFERENCE_RANGES: dict[str, tuple[float, float, str]] = {
    "hemoglobin": (12.0, 17.5, "g/dL"),
    "wbc": (4.5, 11.0, "10^3/uL"),
    "platelets": (150.0, 400.0, "10^3/uL"),
    "glucose": (70.0, 100.0, "mg/dL"),
    "hba1c": (4.0, 5.6, "%"),
    "creatinine": (0.7, 1.3, "mg/dL"),
    "sodium": (136.0, 145.0, "mEq/L"),
    "potassium": (3.5, 5.0, "mEq/L"),
    "tsh": (0.4, 4.0, "mIU/L"),
    "total cholesterol": (0.0, 200.0, "mg/dL"),
    "ldl": (0.0, 130.0, "mg/dL"),
    "hdl": (40.0, 100.0, "mg/dL"),
    "triglycerides": (0.0, 150.0, "mg/dL"),
}


class ReportService:
    def __init__(self) -> None:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)

    def list_reports(self) -> list[dict[str, Any]]:
        if not REPORT_INDEX.exists():
            return []
        try:
            return json.loads(REPORT_INDEX.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        return next((report for report in self.list_reports() if report["id"] == report_id), None)

    def upload(self, filename: str, content_type: str, content: bytes) -> dict[str, Any]:
        if not content:
            raise ValueError("Report file is empty")
        if len(content) > MAX_REPORT_SIZE:
            raise ValueError("Report file exceeds 25MB limit")

        extension = Path(filename).suffix.lower()
        allowed = {".pdf", ".jpg", ".jpeg", ".png", ".txt", ".csv"}
        if extension not in allowed:
            raise ValueError("Unsupported report format. Use PDF, JPG, PNG, TXT, or CSV")

        report_id = str(uuid.uuid4())
        stored_name = f"{report_id}{extension}"
        (REPORT_DIR / stored_name).write_bytes(content)
        category = self._category(filename, content_type)
        analysis = self._analyze(filename, content_type, content, extension)
        report = LabReportResponse(
            id=report_id,
            name=filename,
            type=content_type or "application/octet-stream",
            uploadDate=datetime.now(timezone.utc).date().isoformat(),
            size=self._size(len(content)),
            status="processed",
            category=category,
            summary=analysis["summary"],
            results=[LabResult.model_validate(result) for result in self._normalize_results(analysis["results"])],
            aiConnected=analysis["ai_connected"],
            metadata={"stored_name": stored_name},
        ).model_dump()
        reports = [report, *self.list_reports()]
        REPORT_INDEX.write_text(json.dumps(reports, indent=2), encoding="utf-8")
        return report

    def delete(self, report_id: str) -> bool:
        report = self.get_report(report_id)
        if not report:
            return False
        stored_name = (report.get("metadata") or {}).get("stored_name")
        if stored_name:
            (REPORT_DIR / stored_name).unlink(missing_ok=True)
        REPORT_INDEX.write_text(json.dumps([item for item in self.list_reports() if item["id"] != report_id], indent=2), encoding="utf-8")
        return True

    def file_path(self, report_id: str) -> Path | None:
        report = self.get_report(report_id)
        if not report:
            return None
        stored_name = (report.get("metadata") or {}).get("stored_name")
        path = REPORT_DIR / stored_name if stored_name else None
        return path if path and path.exists() else None

    def _analyze(self, filename: str, content_type: str, content: bytes, extension: str) -> dict[str, Any]:
        extracted_text = self._extract_text(content, extension)
        try:
            client = voice_service._client()
        except Exception:
            client = None
        if client:
            try:
                prompt = """Analyze this medical lab report for a patient. Return JSON only with keys summary and results. results must be an array of objects with test, value, range, status. status must be normal, low, high, or unknown. Do not diagnose. Explain abnormal values in patient-friendly language."""
                if content_type.startswith("image/"):
                    source: Any = {
                        "type": "image_url",
                        "image_url": {"url": f"data:{content_type};base64,{base64.b64encode(content).decode('ascii')}"},
                    }
                    user_content: Any = [{"type": "text", "text": prompt}, source]
                else:
                    user_content = f"{prompt}\n\nReport filename: {filename}\nReport text:\n{extracted_text[:16000]}"
                response = client.chat.completions.create(
                    model=settings.OPENAI_MODEL_FAST,
                    messages=[
                        {"role": "system", "content": "You are a careful medical report reader. Never invent values."},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )
                parsed = json.loads(response.choices[0].message.content or "{}")
                return {"summary": str(parsed.get("summary", "Report analyzed. Review results with a clinician.")), "results": self._normalize_results(parsed.get("results", [])), "ai_connected": True}
            except Exception:
                pass
        return {**self._fallback_analysis(filename, extracted_text), "ai_connected": False}

    @staticmethod
    def _extract_text(content: bytes, extension: str) -> str:
        if extension == ".pdf":
            try:
                from pypdf import PdfReader

                import io

                return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(content)).pages)
            except Exception:
                return ""
        if extension in {".txt", ".csv"}:
            return content.decode("utf-8", errors="ignore")
        return ""

    @classmethod
    def _fallback_analysis(cls, filename: str, text: str) -> dict[str, Any]:
        results: list[dict[str, str]] = []
        for name, (minimum, maximum, unit) in REFERENCE_RANGES.items():
            match = re.search(rf"{re.escape(name)}[^\d-]*(-?\d+(?:\.\d+)?)\s*([\w/%^µ]+)?", text, re.IGNORECASE)
            if not match:
                continue
            value = float(match.group(1))
            status = "normal" if minimum <= value <= maximum else "low" if value < minimum else "high"
            results.append({"test": name.title(), "value": f"{match.group(1)} {match.group(2) or unit}", "range": f"{minimum:g}-{maximum:g} {unit}", "status": status})
        summary = f"{filename} uploaded. Review extracted values with a qualified clinician."
        if results:
            abnormal = [result["test"] for result in results if result["status"] != "normal"]
            summary = f"Report analyzed. {len(results)} laboratory value(s) detected."
            if abnormal:
                summary += f" Review flagged result(s): {', '.join(abnormal)}."
        return {"summary": summary, "results": results}

    @staticmethod
    def _normalize_results(raw_results: Any) -> list[dict[str, str]]:
        if not isinstance(raw_results, list):
            return []
        normalized: list[dict[str, str]] = []
        for raw in raw_results:
            if not isinstance(raw, dict):
                continue
            test = raw.get("test") or raw.get("test_name") or raw.get("name")
            value = raw.get("value")
            if test is None or value is None:
                continue
            status = str(raw.get("status", "unknown")).lower()
            if status not in {"normal", "low", "high", "unknown"}:
                status = "unknown"
            normalized.append({
                "test": str(test),
                "value": str(value),
                "range": str(raw.get("range") or raw.get("reference_range") or "Not available"),
                "status": status,
            })
        return normalized

    @staticmethod
    def _category(filename: str, content_type: str) -> str:
        lower = filename.lower()
        if "ecg" in lower or "ekg" in lower:
            return "ECG"
        if content_type.startswith("image/") or any(word in lower for word in ("xray", "x-ray", "scan", "imaging")):
            return "Imaging"
        return "Blood Test"

    @staticmethod
    def _size(size: int) -> str:
        return f"{max(1, size / 1024):.0f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"


report_service = ReportService()
