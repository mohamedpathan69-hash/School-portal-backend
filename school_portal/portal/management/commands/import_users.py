import csv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from portal.models import User, Student, Staff, Section


class Command(BaseCommand):
    help = (
        "Bulk-create student or staff accounts from a CSV file.\n\n"
        "CSV columns (header row required):\n"
        "  username,email,password,first_name,last_name,role,phone,"
        "grade,section,roll_number,parent_contact,employee_id,subject\n\n"
        "role must be 'student' or 'staff'.\n"
        "grade/section are only used for students (e.g. grade=8, section=B).\n"
        "employee_id/subject are only used for staff.\n\n"
        "Usage: python manage.py import_users sample_users.csv"
    )

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str)

    def handle(self, *args, **options):
        path = options['csv_path']
        created, skipped = 0, 0

        try:
            f = open(path, newline='', encoding='utf-8')
        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")

        with f:
            reader = csv.DictReader(f)
            required = {'username', 'password', 'role'}
            if not required.issubset(reader.fieldnames or []):
                raise CommandError(f"CSV must include at least these columns: {required}")

            for row_num, row in enumerate(reader, start=2):  # row 1 is the header
                username = row.get('username', '').strip()
                role = row.get('role', '').strip().lower()

                if not username or not row.get('password'):
                    self.stderr.write(f"Row {row_num}: missing username or password — skipped")
                    skipped += 1
                    continue

                if User.objects.filter(username=username).exists():
                    self.stderr.write(f"Row {row_num}: username '{username}' already exists — skipped")
                    skipped += 1
                    continue

                if role not in ('student', 'staff'):
                    self.stderr.write(f"Row {row_num}: role must be 'student' or 'staff' — skipped")
                    skipped += 1
                    continue

                with transaction.atomic():
                    user = User(
                        username=username,
                        email=row.get('email', '').strip(),
                        first_name=row.get('first_name', '').strip(),
                        last_name=row.get('last_name', '').strip(),
                        phone=row.get('phone', '').strip(),
                        role=role,
                    )
                    user.set_password(row['password'])  # hashes it — never store plain text
                    user.save()

                    if role == 'student':
                        section = None
                        grade, sec = row.get('grade', '').strip(), row.get('section', '').strip()
                        if grade and sec:
                            section, _ = Section.objects.get_or_create(grade=grade, section=sec)
                        Student.objects.create(
                            user=user,
                            section=section,
                            roll_number=row.get('roll_number', '').strip(),
                            parent_contact=row.get('parent_contact', '').strip(),
                        )
                    else:
                        Staff.objects.create(
                            user=user,
                            employee_id=row.get('employee_id', '').strip(),
                            subject=row.get('subject', '').strip(),
                        )

                created += 1

        self.stdout.write(self.style.SUCCESS(f"Done. Created {created} account(s), skipped {skipped}."))
