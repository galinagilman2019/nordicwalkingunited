import json
import os
from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()
_manifest = None

def _load_manifest():
    global _manifest
    if _manifest is None:
        manifest_path = os.path.join(settings.BASE_DIR, 'PP', 'prod', 'rev-manifest.json')

        try:
            with open(manifest_path, 'r') as f:
                _manifest = json.load(f)
                print(f">> Manifest loaded with {len(_manifest)} entries.")
        except FileNotFoundError:
            print(">> Manifest file NOT FOUND:", manifest_path)
            _manifest = {}
        except json.JSONDecodeError as e:
            print(">> Error parsing manifest:", e)
            _manifest = {}

    return _manifest

@register.simple_tag
def hashed_static(path):
    manifest = _load_manifest()
    hashed_path = manifest.get(path, path)
    final_url = static(hashed_path)

    print(f">> hashed_static('{path}') → manifest → '{hashed_path}' → url '{final_url}'")
    return final_url
