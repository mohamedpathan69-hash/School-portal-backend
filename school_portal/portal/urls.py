from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    MeView, NoticeViewSet, HomeworkViewSet, LeaveRequestViewSet,
    MyFeesView, MessageViewSet, CalendarEventViewSet, PushTokenViewSet,
)

router = DefaultRouter()
router.register('notices', NoticeViewSet, basename='notice')
router.register('homework', HomeworkViewSet, basename='homework')
router.register('leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register('messages', MessageViewSet, basename='message')
router.register('calendar-events', CalendarEventViewSet, basename='calendar-event')
router.register('push-tokens', PushTokenViewSet, basename='push-token')

urlpatterns = [
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/me/', MeView.as_view(), name='me'),
    path('fees/me/', MyFeesView.as_view(), name='my-fees'),
    path('', include(router.urls)),
]
