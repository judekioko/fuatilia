"""Data retention: deletes cases that have been closed for longer than the retention period, with their files.
Run daily. The period is stated in the privacy notice (24 months)."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from cases.models import ACTIVE_STATUSES, Case

RETENTION_DAYS = 730


class Command(BaseCommand):
    help = "Delete cases closed more than 24 months ago, including uploaded evidence."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
        old = Case.objects.exclude(status__in=ACTIVE_STATUSES).filter(closed_at__lt=cutoff)
        count = old.count()
        if options["dry_run"]:
            self.stdout.write(f"{count} case(s) would be deleted.")
            return
        for case in old:
            for item in case.evidence.exclude(file=""):
                item.file.delete(save=False)
            case.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} case(s) closed before {cutoff:%Y-%m-%d}."))
