from django.urls import path
from .views import SaveFCMTokenView, send_push_notification

urlpatterns = [
    path("save-token/", SaveFCMTokenView.as_view(), name="save_token"),
    path("send-notification/", send_push_notification, name="send_notification"),
]