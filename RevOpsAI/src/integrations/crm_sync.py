"""CRMSyncConnector: Bi-directional CRM synchronization (HubSpot, GoHighLevel, generic webhooks)."""

from dataclasses import dataclass
from typing import Any
import httpx
from RevOpsAI.src.core.models import Prospect


@dataclass
class CRMSyncResult:
    """Outcome of external CRM synchronization."""

    success: bool
    remote_id: str = ""
    error: str = ""


class CRMSyncConnector:
    """Connector formatting and synchronizing qualified/interested prospects into external CRMs."""

    def __init__(
        self,
        crm_type: str,
        endpoint_url: str,
        api_key: str = "",
        http_client: Any | None = None,
    ):
        self.crm_type = crm_type.lower()
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.http_client = http_client or httpx.Client(timeout=10.0)

    def _build_hubspot_payload(self, lead: Prospect) -> dict[str, Any]:
        return {
            "properties": {
                "dealname": f"RevOps Opp - {lead.name}",
                "pipeline": "default",
                "dealstage": "appointmentscheduled" if lead.state.value == "INTERESTED" else "qualifiedtobuy",
                "revops_score": str(lead.score),
                "revops_tenant": lead.tenant_id,
                "website": lead.url,
                "friction_gaps": lead.research_summary,
            }
        }

    def _build_gohighlevel_payload(self, lead: Prospect) -> dict[str, Any]:
        return {
            "title": f"RevOps Opp - {lead.name}",
            "status": "open",
            "monetaryValue": 1500,
            "customFields": [
                {"key": "revops_score", "field_value": lead.score},
                {"key": "website", "field_value": lead.url},
                {"key": "friction_points", "field_value": lead.research_summary},
                {"key": "tenant_id", "field_value": lead.tenant_id},
            ],
        }

    def _build_webhook_payload(self, lead: Prospect) -> dict[str, Any]:
        return {
            "event": "lead_sync",
            "lead": lead.model_dump(),
        }

    def sync_prospect(self, lead: Prospect) -> CRMSyncResult:
        """Construct CRM-specific payload and dispatch to the remote endpoint."""
        if self.crm_type == "hubspot":
            payload = self._build_hubspot_payload(lead)
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        elif self.crm_type == "gohighlevel":
            payload = self._build_gohighlevel_payload(lead)
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        else:
            payload = self._build_webhook_payload(lead)
            headers = {"X-Tenant-Id": lead.tenant_id, "Content-Type": "application/json"}

        try:
            resp = self.http_client.post(self.endpoint_url, json=payload, headers=headers)
            if resp.status_code not in {200, 201}:
                return CRMSyncResult(
                    success=False,
                    error=f"CRM HTTP {resp.status_code}: {resp.text}",
                )

            data = resp.json() if hasattr(resp, "json") else {}
            # Extract remote deal / opportunity ID
            if self.crm_type == "hubspot":
                remote_id = str(data.get("id", ""))
            elif self.crm_type == "gohighlevel":
                remote_id = str(data.get("opportunity", {}).get("id", data.get("id", "")))
            else:
                remote_id = str(data.get("id", "synced"))

            return CRMSyncResult(success=True, remote_id=remote_id)
        except Exception as exc:
            return CRMSyncResult(success=False, error=str(exc))
