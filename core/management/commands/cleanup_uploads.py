import os
import re
import shutil
from pathlib import Path
from datetime import datetime, timezone

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models.fields.files import FieldFile

try:
    from bs4 import BeautifulSoup
    HAVE_BS4 = True
except Exception:
    HAVE_BS4 = False


UPLOAD_URL_PREFIXES = ("/uploads/",)  # add "/media/" here if you ever used it


def _norm_rel(path: str) -> str:
    # Convert "/uploads/x/y.jpg" -> "x/y.jpg"
    for pfx in UPLOAD_URL_PREFIXES:
        if path.startswith(pfx):
            path = path[len(pfx):]
    return path.lstrip("/")


def _extract_upload_paths_from_html(html: str) -> set[str]:
    if not html:
        return set()

    found = set()

    if HAVE_BS4:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["img", "a", "source"]):
            for attr in ("src", "href", "srcset"):
                val = tag.get(attr)
                if not val:
                    continue
                # srcset can be "url 1x, url 2x"
                parts = [v.strip().split(" ")[0] for v in val.split(",")]
                for u in parts:
                    for pfx in UPLOAD_URL_PREFIXES:
                        if u.startswith(pfx):
                            found.add(_norm_rel(u))
    else:
        # fallback regex (works fine for <img src="/uploads/...">)
        for pfx in UPLOAD_URL_PREFIXES:
            pattern = re.compile(re.escape(pfx) + r"[^\"'\s>]+")
            for m in pattern.findall(html):
                found.add(_norm_rel(m))

    return found


class Command(BaseCommand):
    help = "Find orphan files under MEDIA_ROOT (uploads) that are not referenced by DB. Optionally move them to trash."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Move orphan files to --trash-dir. Without this, dry-run only.")
        parser.add_argument("--trash-dir", default="/home/NWU/uploads_trash", help="Where to move orphan files when --apply is used.")
        parser.add_argument("--older-than", default=None, help="Only touch orphans older than YYYY-MM-DD (uses file mtime).")

    def handle(self, *args, **opts):
        media_root = Path(settings.MEDIA_ROOT).resolve()
        trash_dir = Path(opts["trash_dir"]).resolve()

        older_than = None
        if opts["older_than"]:
            older_than = datetime.strptime(opts["older_than"], "%Y-%m-%d").replace(tzinfo=timezone.utc)

        # 1) Collect referenced files from all models with FileField/ImageField
        referenced = set()

        from django.apps import apps
        for model in apps.get_models():
            file_fields = []
            for f in model._meta.get_fields():
                # FileField / ImageField
                if getattr(f, "upload_to", None) is not None and hasattr(f, "attname"):
                    file_fields.append(f)

            if not file_fields:
                continue

            qs = model.objects.all().only(*[f.name for f in file_fields])
            for obj in qs.iterator():
                for f in file_fields:
                    try:
                        ff = getattr(obj, f.name)
                    except Exception:
                        continue
                    if isinstance(ff, FieldFile) and ff.name:
                        referenced.add(ff.name.lstrip("/"))

        # 2) Add CKEditor HTML references (your Event.preview)
        # Adjust import if needed
        try:
            from core.models import Event
            for ev in Event.objects.all().only("preview").iterator():
                referenced |= _extract_upload_paths_from_html(ev.preview)
        except Exception:
            pass

        # Normalize to absolute existing paths
        referenced_abs = set()
        for rel in referenced:
            p = (media_root / rel).resolve()
            # keep only files under media_root
            if str(p).startswith(str(media_root)):
                referenced_abs.add(p)

        # 3) Walk all files under media_root
        all_files = []
        for p in media_root.rglob("*"):
            if p.is_file():
                all_files.append(p)

        orphans = []
        for p in all_files:
            if p not in referenced_abs:
                if older_than:
                    mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
                    if mtime >= older_than:
                        continue
                orphans.append(p)

        self.stdout.write(f"MEDIA_ROOT: {media_root}")
        self.stdout.write(f"Referenced files: {len(referenced_abs)}")
        self.stdout.write(f"All files: {len(all_files)}")
        self.stdout.write(f"Orphans (candidates): {len(orphans)}")

        # Print a small sample
        for p in orphans[:30]:
            self.stdout.write(f"ORPHAN: {p}")

        if not opts["apply"]:
            self.stdout.write(self.style.WARNING("Dry-run only. Add --apply to move orphans to trash."))
            return

        trash_dir.mkdir(parents=True, exist_ok=True)

        moved = 0
        for p in orphans:
            rel = p.relative_to(media_root)
            dest = trash_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(dest))
            moved += 1

        self.stdout.write(self.style.SUCCESS(f"Moved {moved} orphan files to {trash_dir}"))