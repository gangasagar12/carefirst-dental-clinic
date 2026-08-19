import os
from pathlib import Path
import polib

def compile_all():
    base_dir = Path(__file__).resolve().parent.parent
    po_path = base_dir / 'locale' / 'ne' / 'LC_MESSAGES' / 'django.po'
    mo_path = base_dir / 'locale' / 'ne' / 'LC_MESSAGES' / 'django.mo'

    if not po_path.exists():
        print(f"Error: {po_path} not found")
        return

    po = polib.pofile(str(po_path), encoding='utf-8')
    po.metadata = {
        'Project-Id-Version': 'CareFirst Dental 1.0',
        'Report-Msgid-Bugs-To': 'info@carefirst.com',
        'POT-Creation-Date': '2026-08-19 10:20+0545',
        'PO-Revision-Date': '2026-08-19 10:20+0545',
        'Last-Translator': 'CareFirst AI Translator <info@carefirst.com>',
        'Language-Team': 'Nepali <ne@carefirst.com>',
        'Language': 'ne',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=UTF-8',
        'Content-Transfer-Encoding': '8bit',
        'Plural-Forms': 'nplurals=2; plural=(n != 1);',
    }
    po.save_as_mofile(str(mo_path))
    print(f"Successfully compiled {len(po)} phrases into standard gettext .mo file at {mo_path}")

if __name__ == '__main__':
    compile_all()
