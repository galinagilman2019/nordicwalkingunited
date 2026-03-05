import shutil
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand

from core.management.commands.cleanup_uploads import (
    _extract_upload_paths_from_html,
    UPLOAD_URL_PREFIXES,
)

class Command(BaseCommand):
    help = "Copy only DB-referenced upload files from OLD_MEDIA_ROOT to current MEDIA_ROOT."

    def add_arguments(self, parser):
        parser.add_argument("--old-media-root", required=True, help="Old uploads root path on disk")
        parser.add_argument("--apply", action="store_true", help="Actually copy (otherwise dry-run).")

    def handle(self, *args, **opts):
        old_root = Path(opts["old_media_root"]).resolve()
        new_root = Path(settings.MEDIA_ROOT).resolve()

        from django.apps import apps
        referenced = set()

        # 1) FileField/ImageField paths
        for model in apps.get_models():
            file_fields = [f for f in model._meta.get_fields() if getattr(f, "upload_to", None) is not None and hasattr(f, "attname")]
            if not file_fields:
                continue
            qs = model.objects.all().only(*[f.name for f in file_fields])
            for obj in qs.iterator():
                for f in file_fields:
                    ff = getattr(obj, f.name, None)
                    if getattr(ff, "name", None):
                        referenced.add(ff.name.lstrip("/"))

        # 2) CKEditor HTML (Event.preview)
        try:
            from core.models import Event
            for ev in Event.objects.all().only("preview").iterator():
                referenced |= _extract_upload_paths_from_html(ev.preview)
        except Exception:
            pass

        referenced = sorted(set(referenced))

        self.stdout.write(f"Old root: {old_root}")
        self.stdout.write(f"New root: {new_root}")
        self.stdout.write(f"Referenced paths: {len(referenced)}")

        copied = 0
        missing = 0

        for rel in referenced:
            src = (old_root / rel).resolve()
            dst = (new_root / rel).resolve()

            if not src.exists():
                self.stdout.write(self.style.WARNING(f"MISSING: {src}"))
                missing += 1
                continue

            if dst.exists():
                continue

            self.stdout.write(f"COPY: {src} -> {dst}")
            if opts["apply"]:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1

        if not opts["apply"]:
            self.stdout.write(self.style.WARNING("Dry-run only. Add --apply to actually copy."))

        self.stdout.write(self.style.SUCCESS(f"Copied: {copied}, Missing: {missing}"))