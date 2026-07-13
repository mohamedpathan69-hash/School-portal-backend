from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Section, Student, Staff, Notice, Homework, HomeworkStatus,
    LeaveRequest, FeeItem, FeePayment, Message, CalendarEvent, PushToken,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Adds "role" and "phone" to the built-in Django user admin screen,
    # so creating an account and setting its password happens in one place.
    fieldsets = UserAdmin.fieldsets + (
        ('School role', {'fields': ('role', 'phone')}),
    )
    list_display = ('username', 'get_full_name', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('grade', 'section')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'section', 'roll_number', 'parent_contact')
    list_filter = ('section',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'roll_number')


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'subject')
    filter_horizontal = ('sections',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'staff', 'section', 'urgent', 'created_at')
    list_filter = ('urgent', 'section')


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'staff', 'section', 'due_date')
    list_filter = ('section', 'subject')


admin.site.register(HomeworkStatus)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'from_date', 'to_date', 'status')
    list_filter = ('status',)


admin.site.register(FeeItem)
admin.site.register(FeePayment)
admin.site.register(Message)
admin.site.register(CalendarEvent)
admin.site.register(PushToken)
