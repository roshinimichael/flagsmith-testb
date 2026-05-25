from django.urls import path
from features.bulk_evaluate.views import BulkEvaluateView

urlpatterns = [
    path("", BulkEvaluateView.as_view(), name="bulk-evaluate"),
]
