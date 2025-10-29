# notifications/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes

from firebase_admin import messaging
from .models import FCMToken
from .serializers import FCMTokenSerializer


# -------------------------------------------------
# 1. Save FCM token (called from Flutter)
# -------------------------------------------------
class SaveFCMTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FCMTokenSerializer(data=request.data)
        if serializer.is_valid():
            fcm_token = serializer.save(user=request.user)
            return Response(
                {"message": "Token saved", "token_id": fcm_token.id},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------------
# 2. Send push notification (admin only) - UPDATED FOR NEW API
# -------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAdminUser])
def send_push_notification(request):
    """
    POST body example:
    {
        "user_id": 1,
        "title": "Hello",
        "body": "This is a test",
        "data": {"screen": "profile"}   # optional custom payload
    }
    """
    user_id = request.data.get("user_id")
    title = request.data.get("title", "Notification")
    body = request.data.get("body", "")
    extra_data = request.data.get("data", {})

    # Get token(s) for the user
    queryset = FCMToken.objects.filter(user_id=user_id)
    if not queryset.exists():
        return Response({"error": "No FCM token for this user"}, status=404)

    tokens = list(queryset.values_list("token", flat=True))

    # Build the message
    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data={str(k): str(v) for k, v in extra_data.items()},  # data must be str→str
        tokens=tokens,
    )

    try:
        # NEW: Use send_each_for_multicast() instead of send_multicast()
        batch_response = messaging.send_each_for_multicast(message)
        return Response(
            {
                "success_count": batch_response.success_count,
                "failure_count": batch_response.failure_count,
                "responses": [
                    {
                        "token": tokens[i],
                        "success": r.success,
                        "message_id": r.message_id,
                        "error": str(r.exception) if r.exception else None,
                    }
                    for i, r in enumerate(batch_response.responses)
                ],
            }
        )
    except Exception as e:
        return Response({"error": str(e)}, status=500)