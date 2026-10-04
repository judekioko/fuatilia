"""Emails each user a digest of cases whose follow-up is due. Run once a day (e.g. 7am cron)."""

from collections import defaultdict

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from cases.models import ACTIVE_STATUSES, Case


class Command(BaseCommand):
    help = "Email users about follow-ups that are due today or overdue."

    def add_arguments(self, parser):
        parser.add_argument("--base-url", default="", help="Site address used in links, e.g. https://fuatilia.co.ke")

    def handle(self, *args, **options):
        today = timezone.localdate()
        due = (
            Case.objects.filter(
                status__in=ACTIVE_STATUSES,
                next_follow_up__lte=today,
                owner__email_reminders=True,
                owner__is_active=True,
            )
            .exclude(last_reminded_on=today)
            .select_related("owner")
            .order_by("next_follow_up")
        )
        by_user = defaultdict(list)
        for case in due:
            by_user[case.owner].append(case)

        sent = 0
        for user, cases in by_user.items():
            body = render_to_string(
                "cases/email_reminder.txt",
                {"user": user, "cases": cases, "today": today, "base_url": options["base_url"].rstrip("/")},
            )
            subject = f"Fuatilia: {len(cases)} case{'s' if len(cases) != 1 else ''} to follow up today"
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
            Case.objects.filter(pk__in=[c.pk for c in cases]).update(last_reminded_on=today)
            sent += 1
        total = sum(len(cases) for cases in by_user.values())
        self.stdout.write(self.style.SUCCESS(f"Sent {sent} reminder email(s) covering {total} case(s)."))
