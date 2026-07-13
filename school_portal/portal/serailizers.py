from rest_framework import serializers
from .models import (
    User, Section, Student, Staff, Notice, Homework, HomeworkStatus,
    LeaveRequest, FeeItem, FeePayment, Message, CalendarEvent, PushToken,
)


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'grade', 'section']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ['user', 'section', 'roll_number', 'parent_contact']


class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = ['user', 'employee_id', 'subject', 'sections']


class NoticeSerializer(serializers.ModelSerializer):
    posted_by = serializers.CharField(source='staff.user.get_full_name', read_only=True)

    class Meta:
        model = Notice
        fields = ['id', 'staff', 'posted_by', 'section', 'subject', 'title', 'body', 'urgent', 'created_at']
        read_only_fields = ['staff']


class HomeworkSerializer(serializers.ModelSerializer):
    posted_by = serializers.CharField(source='staff.user.get_full_name', read_only=True)
    done = serializers.SerializerMethodField()

    class Meta:
        model = Homework
        fields = ['id', 'staff', 'posted_by', 'section', 'subject', 'title', 'description', 'due_date', 'file', 'created_at', 'done']
        read_only_fields = ['staff']

    def get_done(self, obj):
        # Only meaningful when the requesting user is a student — resolved in the view's context.
        student = self.context.get('student')
        if not student:
            return None
        status = obj.statuses.filter(student=student).first()
        return status.done if status else False


class LeaveRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = ['id', 'student', 'student_name', 'from_date', 'to_date', 'reason', 'status', 'decided_by', 'decided_at', 'created_at']
        read_only_fields = ['student', 'status', 'decided_by', 'decided_at']


class FeeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeItem
        fields = ['id', 'label', 'amount', 'due_date']


class FeePaymentSerializer(serializers.ModelSerializer):
    fee_item = FeeItemSerializer(read_only=True)

    class Meta:
        model = FeePayment
        fields = ['id', 'fee_item', 'status', 'amount_paid', 'paid_at', 'payment_reference']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'text', 'sent_at', 'read_at']
        read_only_fields = ['sender', 'sent_at', 'read_at']


class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = ['id', 'title', 'description', 'event_date', 'created_by']
        read_only_fields = ['created_by']


class PushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushToken
        fields = ['id', 'device_token', 'platform']
