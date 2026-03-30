"""Audit trail for feature flag changes.

GET /api/v1/projects/{project_pk}/features/{pk}/audit/
Returns a list of change events for a specific feature flag.
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from features.models import Feature


class FeatureAuditView(APIView):
    """Return the change history for a single feature flag."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, project_pk: int, pk: int) -> Response:
        feature = Feature.objects.filter(
            pk=pk,
            project_id=project_pk,
        ).first()

        if feature is None:
            return Response({"detail": "Not found."}, status=404)

        # Build audit log from AuditLog if available, otherwise empty
        from audit.models import AuditLog  # type: ignore[import]

        entries = (
            AuditLog.objects.filter(
                related_object_id=str(pk),
                related_object_type="Feature",
                project_id=project_pk,
            )
            .order_by("-created_date")
            .values(
                "id",
                "created_date",
                "log",
                "author__email",
                "environment__name",
            )[:100]
        )

        data = [
            {
                "id": e["id"],
                "timestamp": e["created_date"],
                "message": e["log"],
                "author": e["author__email"],
                "environment": e["environment__name"],
            }
            for e in entries
        ]

        return Response(
            {
                "feature_id": pk,
                "feature_name": feature.name,
                "audit_log": data,
                "total": len(data),
            }
        )
