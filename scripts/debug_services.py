import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding='utf-8')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from main.models import Service

for slug in ["dentures", "scaling-and-polishing", "general-dentistry"]:
    s = Service.objects.filter(slug=slug).first()
    if s:
        print(f"{slug}: custom_template={repr(s.custom_template)}, is_active={s.is_active}")
    else:
        print(f"{slug}: NOT FOUND")

from django.test import RequestFactory
from main.views import service_detail

rf = RequestFactory()
for slug in ["dentures", "scaling-and-polishing"]:
    req = rf.get(f"/en/services/{slug}/")
    try:
        resp = service_detail(req, slug=slug)
        print(f"Direct view call {slug}: {resp.status_code}")
    except Exception as e:
        import traceback
        print(f"Direct view call {slug} EXCEPTION:")
        traceback.print_exc()
