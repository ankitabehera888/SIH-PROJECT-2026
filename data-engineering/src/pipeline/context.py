import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
METADATA_DIR = BASE_DIR / "metadata"
RUNS_DIR = METADATA_DIR / "runs"
STATE_FILE = METADATA_DIR / "pipeline_state.json"

@dataclass
class PipelineContext:
    run_id: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: Optional[str] = None
    pipeline_name: str = "healthcare_etl"
    source: str = "healthcare_dev"
    status: str = "running"
    current_step: int = 0
    step_statuses: Dict[str, str] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def record_step(self, step_name: str, status: str, details: Optional[Dict] = None):
        """Records the status and optional metrics for a pipeline step."""
        self.step_statuses[step_name] = status
        if details:
            self.metrics[step_name] = details

    def record_error(self, step_name: str, error_msg: str):
        """Records a failure error for a specific step."""
        self.errors.append({
            "step": step_name,
            "error": error_msg,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.status = "failed"

    def mark_finished(self, status: str = "success"):
        """Marks the pipeline execution as completed."""
        self.finished_at = datetime.now(timezone.utc).isoformat()
        self.status = status
        self.save_manifest()
        self.update_state()

    def save_manifest(self) -> Path:
        """Persists the execution manifest under metadata/runs/<run_id>.json."""
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        manifest_path = RUNS_DIR / f"{self.run_id}.json"
        data = {
            "run_id": self.run_id,
            "pipeline": self.pipeline_name,
            "source": self.source,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "steps": self.step_statuses,
            "metrics": self.metrics,
            "errors": self.errors,
            "warnings": self.warnings,
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return manifest_path

    def update_state(self) -> Path:
        """Updates metadata/pipeline_state.json with the latest run state."""
        METADATA_DIR.mkdir(parents=True, exist_ok=True)
        state_data = {
            "pipeline": self.pipeline_name,
            "last_run_id": self.run_id,
            "last_status": self.status,
            "last_successful_run": self.finished_at if self.status == "success" else None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        # If there's existing state, preserve last_successful_run if this run failed
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    old_state = json.load(f)
                if self.status != "success":
                    state_data["last_successful_run"] = old_state.get("last_successful_run")
            except Exception:
                pass
                
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2)
        return STATE_FILE
