from datetime import datetime, timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from features.bulk_evaluate.serializers import (
    BulkFlagEvaluationRequestSerializer,
    BulkFlagEvaluationResponseSerializer,
)
from features.models import Feature, FeatureState
from environments.models import Environment


class BulkEvaluateView(APIView):
    """POST /api/v1/environments/{environment_key}/flags/bulk-evaluate/"""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, **kwargs) -> Response:
        serializer = BulkFlagEvaluationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        feature_names: list[str] = serializer.validated_data["feature_names"]
        identifier: str = serializer.validated_data.get("identifier", "")

        environment: Environment = request.environment  # type: ignore[attr-defined]

        features = Feature.objects.filter(
            project=environment.project,
            name__in=feature_names,
        ).values_list("name", flat=True)

        known = set(features)

        feature_states = {
            fs.feature.name: fs
            for fs in FeatureState.objects.filter(
                environment=environment,
                feature__name__in=list(known),
                identity=None,
            ).select_related("feature")
        }

        results = []
        for name in feature_names:
            if name not in known:
                results.append(
                    {
                        "feature_name": name,
                        "enabled": False,
                        "value": None,
                        "reason": "UNKNOWN_FLAG",
                    }
                )
                continue

            fs = feature_states.get(name)
            results.append(
                {
                    "feature_name": name,
                    "enabled": fs.enabled if fs else False,
                    "value": fs.get_feature_state_value() if fs else None,
                    "reason": "DEFAULT",
                }
            )

        response_data = {
            "results": results,
            "evaluated_at": datetime.now(timezone.utc),
            "environment_id": environment.id,
        }

        out = BulkFlagEvaluationResponseSerializer(response_data)
        return Response(out.data, status=status.HTTP_200_OK)
