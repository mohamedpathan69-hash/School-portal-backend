from django.utils import timezone
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q

from .models import (
    Notice, Homework, HomeworkStatus, LeaveRequest, FeePayment,
    Message, CalendarEvent, PushToken, Student, Staff,
)
from .serializers import (
    NoticeSerializer, HomeworkSerializer, LeaveRequestSerializer,
    FeePaymentSerializer, MessageSerializer, CalendarEventSerializer,
    PushTokenSerializer, UserSerializer,
)
from .permissions import IsStaffOrReadOnlyOwn


class MeView(APIView):
    """GET /api/v1/users/me/ — current user's profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class NoticeViewSet(viewsets.ModelViewSet):
    serializer_class = NoticeSerializer
    permission_classes = [IsStaffOrReadOnlyOwn]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'staff':
            return Notice.objects.filter(staff__user=user)
        if user.role == 'student':
            section = getattr(user.student_profile, 'section', None)
            return Notice.objects.filter(Q(section=section) | Q(section__isnull=True))
        return Notice.objects.all()

    def perform_create(self, serializer):
        serializer.save(staff=self.request.user.staff_profile)


class HomeworkViewSet(viewsets.ModelViewSet):
    serializer_class = HomeworkSerializer
    permission_classes = [IsStaffOrReadOnlyOwn]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'staff':
            return Homework.objects.filter(staff__user=user)
        if user.role == 'student':
            section = getattr(user.student_profile, 'section', None)
            return Homework.objects.filter(Q(section=section) | Q(section__isnull=True))
        return Homework.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        if user.is_authenticated and user.role == 'student':
            context['student'] = user.student_profile
        return context

    def perform_create(self, serializer):
        serializer.save(staff=self.request.user.staff_profile)

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        """PATCH /api/v1/homework/{id}/status/  body: {"done": true}"""
        homework = self.get_object()
        student = request.user.student_profile
        done = bool(request.data.get('done', False))
        obj, _ = HomeworkStatus.objects.update_or_create(
            homework=homework, student=student,
            defaults={'done': done, 'done_at': timezone.now() if done else None},
        )
        return Response({'homework': homework.id, 'done': obj.done})


class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return LeaveRequest.objects.filter(student=user.student_profile)
        if user.role == 'staff':
            sections = user.staff_profile.sections.all()
            return LeaveRequest.objects.filter(student__section__in=sections)
        return LeaveRequest.objects.all()

    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student_profile)

    @action(detail=True, methods=['patch'])
    def decide(self, request, pk=None):
        """PATCH /api/v1/leave-requests/{id}/decide/  body: {"status": "approved"}"""
        leave = self.get_object()
        new_status = request.data.get('status')
        if new_status not in ('approved', 'rejected'):
            return Response({'error': 'status must be approved or rejected'}, status=status.HTTP_400_BAD_REQUEST)
        leave.status = new_status
        leave.decided_by = request.user.staff_profile
        leave.decided_at = timezone.now()
        leave.save()
        return Response(LeaveRequestSerializer(leave).data)


class MyFeesView(APIView):
    """GET /api/v1/fees/me/ — fee summary + breakdown for the logged-in student."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = request.user.student_profile
        payments = FeePayment.objects.filter(student=student).select_related('fee_item')
        total = sum(p.fee_item.amount for p in payments)
        paid = sum(p.amount_paid for p in payments)
        return Response({
            'total': total,
            'paid': paid,
            'due': total - paid,
            'breakdown': FeePaymentSerializer(payments, many=True).data,
        })


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Message.objects.filter(Q(sender=user) | Q(receiver=user))
        other_id = self.request.query_params.get('with')
        if other_id:
            qs = qs.filter(Q(sender_id=other_id) | Q(receiver_id=other_id))
        return qs

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class CalendarEventViewSet(viewsets.ModelViewSet):
    serializer_class = CalendarEventSerializer
    permission_classes = [IsAuthenticated]
    queryset = CalendarEvent.objects.all()

    def get_queryset(self):
        qs = CalendarEvent.objects.all()
        month = self.request.query_params.get('month')  # format YYYY-MM
        if month:
            year, mon = month.split('-')
            qs = qs.filter(event_date__year=year, event_date__month=mon)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PushTokenViewSet(viewsets.ModelViewSet):
    serializer_class = PushTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PushToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
