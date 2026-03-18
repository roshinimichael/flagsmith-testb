from django.urls import path
from features.audit.views import FeatureAuditView

urlpatterns = [
    path(
        "<int:pk>/audit/",
        FeatureAuditView.as_view(),
        name="feature-audit",
    ),
]
