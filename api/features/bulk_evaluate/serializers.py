from rest_framework import serializers


class BulkFlagEvaluationRequestSerializer(serializers.Serializer):
    """Request body for POST /api/v1/flags/bulk-evaluate/"""

    feature_names = serializers.ListField(
        child=serializers.CharField(max_length=2000),
        min_length=1,
        max_length=100,
        help_text="Feature flag names to evaluate (max 100).",
    )
    identifier = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Optional identity identifier for personalised flag values.",
    )


class FlagEvaluationResultSerializer(serializers.Serializer):
    feature_name = serializers.CharField()
    enabled = serializers.BooleanField()
    value = serializers.JSONField(allow_null=True)
    reason = serializers.ChoiceField(
        choices=["DEFAULT", "IDENTITY_OVERRIDE", "UNKNOWN_FLAG"],
    )


class BulkFlagEvaluationResponseSerializer(serializers.Serializer):
    results = FlagEvaluationResultSerializer(many=True)
    evaluated_at = serializers.DateTimeField()
    environment_id = serializers.IntegerField()
