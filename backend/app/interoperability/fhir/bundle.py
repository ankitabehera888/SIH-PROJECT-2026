from datetime import datetime, timezone
from typing import Any, Dict, List
import uuid


class BundleBuilder:
    """Assembles independent FHIR R4 resources into an ABDM-compliant FHIR Bundle."""

    @staticmethod
    def build_collection_bundle(
        resources: List[Dict[str, Any]],
        bundle_id: str = None,
        bundle_type: str = "collection",
    ) -> Dict[str, Any]:
        b_id = bundle_id or str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        entries = []
        for res in resources:
            res_type = res.get("resourceType")
            res_id = res.get("id")
            full_url = f"urn:uuid:{res_id}" if res_id else f"urn:uuid:{uuid.uuid4()}"
            entries.append({
                "fullUrl": full_url,
                "resource": res,
            })

        return {
            "resourceType": "Bundle",
            "id": b_id,
            "identifier": {
                "system": "https://healthcare.gov.in/bundles",
                "value": f"BUNDLE-{b_id}",
            },
            "type": bundle_type,
            "timestamp": now_iso,
            "total": len(entries),
            "entry": entries,
        }
