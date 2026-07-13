from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        STAFF = 'staff', 'Staff'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(max_length=10, choices=Role.choices)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"


class Section(models.Model):
    grade = models.CharField(max_length=10)
    section = models.CharField(max_length=5)

    class Meta:
        unique_together = ('grade', 'section')

    def __str__(self):
        return f"Grade {self.grade}-{self.section}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='student_profile')
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    roll_number = models.CharField(max_length=20, blank=True)
    parent_contact = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='staff_profile')
    employee_id = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=100, blank=True)
    sections = models.ManyToManyField(Section, related_name='teachers', blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Notice(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='notices')
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='notices')
    subject = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    urgent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Homework(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='homework')
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='homework')
    subject = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to='homework_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class HomeworkStatus(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='statuses')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='homework_statuses')
    done = models.BooleanField(default=False)
    done_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('homework', 'student')


class LeaveRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='leave_requests')
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    decided_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='decided_leaves')
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class FeeItem(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='fee_items')
    label = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.label} — {self.section}"


class FeePayment(models.Model):
    class Status(models.TextChoices):
        DUE = 'due', 'Due'
        PAID = 'paid', 'Paid'
        OVERDUE = 'overdue', 'Overdue'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_payments')
    fee_item = models.ForeignKey(FeeItem, on_delete=models.CASCADE, related_name='payments')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DUE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['sent_at']


class CalendarEvent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date']


class PushToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_tokens')
    device_token = models.TextField()
    platform = models.CharField(max_length=10, choices=[('android', 'Android'), ('ios', 'iOS')])
    created_at = models.DateTimeField(auto_now_add=True)
