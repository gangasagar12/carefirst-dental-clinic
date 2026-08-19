import os
import re
from pathlib import Path
import polib
from deep_translator import GoogleTranslator
from django.core.management.base import BaseCommand
from django.conf import settings
from main.services.translation_service import DENTAL_NEPALI_GLOSSARY


class Command(BaseCommand):
    help = "Fast batch translation to Nepali with Deep Translator and compilation with polib"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Extracting translatable strings from codebase..."))

        base_dir = Path(settings.BASE_DIR)
        extracted_strings = set()

        for en_key in DENTAL_NEPALI_GLOSSARY.keys():
            extracted_strings.add(en_key)

        trans_pattern = re.compile(r'{%\s*(?:trans|blocktrans.*?)\s*["\'](.*?)["\']\s*%}')
        templates_dir = base_dir / 'templates'
        if templates_dir.exists():
            for filepath in templates_dir.rglob('*.html'):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()
                        matches = trans_pattern.findall(text)
                        for m in matches:
                            clean_m = m.strip()
                            if clean_m and len(clean_m) > 1 and not clean_m.startswith('{'):
                                extracted_strings.add(clean_m)
                except Exception:
                    pass

        py_pattern = re.compile(r'_\(\s*["\'](.*?)["\']\s*\)')
        for py_file in base_dir.rglob('*.py'):
            if 'venv' in str(py_file) or '.git' in str(py_file):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                    matches = py_pattern.findall(text)
                    for m in matches:
                        clean_m = m.strip()
                        if clean_m and len(clean_m) > 1:
                            extracted_strings.add(clean_m)
            except Exception:
                pass

        all_phrases = sorted(list(extracted_strings))
        self.stdout.write(f"Total unique phrases to translate: {len(all_phrases)}")

        translations_map = {}
        to_translate = []

        for p in all_phrases:
            if p in DENTAL_NEPALI_GLOSSARY:
                translations_map[p] = DENTAL_NEPALI_GLOSSARY[p]
            else:
                to_translate.append(p)

        if to_translate:
            translator = GoogleTranslator(source='en', target='ne')
            chunk_size = 25
            for i in range(0, len(to_translate), chunk_size):
                chunk = to_translate[i:i + chunk_size]
                try:
                    results = translator.translate_batch(chunk)
                    for original, trans in zip(chunk, results):
                        translations_map[original] = trans or original
                except Exception as e:
                    self.stderr.write(f"Batch chunk error: {e}")
                    for original in chunk:
                        try:
                            translations_map[original] = translator.translate(original) or original
                        except Exception:
                            translations_map[original] = original

        locale_dir = base_dir / 'locale' / 'ne' / 'LC_MESSAGES'
        locale_dir.mkdir(parents=True, exist_ok=True)
        po_path = locale_dir / 'django.po'
        mo_path = locale_dir / 'django.mo'

        po = polib.POFile(encoding='utf-8')
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

        for phrase in sorted(translations_map.keys()):
            entry = polib.POEntry(
                msgid=phrase,
                msgstr=translations_map[phrase]
            )
            po.append(entry)

        po.save(str(po_path))
        po.save_as_mofile(str(mo_path))
        self.stdout.write(self.style.SUCCESS(f"Successfully generated {po_path} and compiled {mo_path} with polib UTF-8!"))
