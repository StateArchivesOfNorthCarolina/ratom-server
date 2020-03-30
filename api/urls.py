from django.urls import path
from django.conf import settings

from rest_framework_simplejwt import views as jwt_views
from .views import (
    user_detail,
    account_detail,
    AccountListView,
    message_detail,
    messages_batch,
    MessageDocumentView,
    FileDeleteView,
    reset_sample_data,
    ExportDocumentView,
)

# Auth
urlpatterns = [
    path("token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("users/", user_detail, name="user_detail"),
]

# Accounts
urlpatterns += [
    path("accounts/", AccountListView.as_view(), name="account_list"),
    path("accounts/<int:pk>/", account_detail, name="account_detail"),
]

# Files
urlpatterns += [
    path("files/", FileDeleteView.as_view(), name="remove_file"),
]

# Messages
urlpatterns += [
    path(
        "messages/",
        MessageDocumentView.as_view({"get": "list"}),
        name="search_messages",
    ),
    path("messages/<int:pk>/", message_detail, name="message_detail"),
    path("messages/batch/", messages_batch, name="messages_batch"),
]

# Export
urlpatterns += [
    path(
        "export/", ExportDocumentView.as_view({"get": "list"}), name="export_messages",
    )
]

if settings.RATOM_SAMPLE_DATA_ENABLED:
    # Fake data
    urlpatterns += [
        path("reset-sample-data/", reset_sample_data, name="reset_sample_data"),
    ]

ratom_urlpatterns = urlpatterns
