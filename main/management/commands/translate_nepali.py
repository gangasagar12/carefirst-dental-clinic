import os
import re
import struct
from pathlib import Path
from deep_translator import GoogleTranslator
from django.core.management.base import BaseCommand
from django.conf import settings
from main.services.translation_service import DENTAL_NEPALI_GLOSSARY


def compile_po_to_mo(po_filepath: str, mo_filepath: str):
    """
    Pure Python compiler for .po to .mo binary file.
    Does NOT require gettext or msgfmt system binaries.
    """
    messages = {}
    with open(po_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    cur_id = None
    cur_str = None
    reading_id = False
    reading_str = False

    for line in lines:
        line_s = line.strip()
        if line_s.startswith('msgid "'):
            if cur_id is not None and cur_str is not None:
                messages[cur_id] = cur_str
            cur_id = line_s[7:-1]
            cur_str = ""
            reading_id = True
            reading_str = False
        elif line_s.startswith('msgstr "'):
            cur_str = line_s[8:-1]
            reading_id = False
            reading_str = True
        elif line_s.startswith('"') and line_s.endswith('"'):
            inner = line_s[1:-1]
            if reading_id:
                cur_id += inner
            elif reading_str:
                cur_str += inner

    if cur_id is not None and cur_str is not None:
        messages[cur_id] = cur_str

    clean_messages = {}
    for k, v in messages.items():
        if k:
            k_clean = k.replace('\\n', '\n').replace('\\"', '"')
            v_clean = v.replace('\\n', '\n').replace('\\"', '"')
            if v_clean:
                clean_messages[k_clean.encode('utf-8')] = v_clean.encode('utf-8')

    keys = sorted(clean_messages.keys())
    offsets = []
    ids = b''
    strs = b''

    for key in keys:
        val = clean_messages[key]
        offsets.append((len(ids), len(key), len(strs), len(val)))
        ids += key + b'\x00'
        strs += val + b'\x00'

    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)

    koffsets = []
    voffsets = []
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]

    output = struct.pack(
        "Iiiiiii",
        0x950412de,
        0,
        len(keys),
        7 * 4,
        7 * 4 + len(keys) * 8,
        0, 0
    )

    output += struct.pack(str(len(koffsets)) + "i", *koffsets)
    output += struct.pack(str(len(voffsets)) + "i", *voffsets)
    output += ids
    output += strs

    os.makedirs(os.path.dirname(mo_filepath), exist_ok=True)
    with open(mo_filepath, 'wb') as f:
        f.write(output)


class Command(BaseCommand):
    help = "Fast batch translation to Nepali with Deep Translator and compilation to .mo"

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

        self.stdout.write(f"Found {len(translations_map)} from glossary, batch translating {len(to_translate)} with deep_translator...")

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
                    self.stderr.write(f"Batch translate chunk error: {e}")
                    for original in chunk:
                        try:
                            translations_map[original] = translator.translate(original) or original
                        except Exception:
                            translations_map[original] = original

        translated_entries = []
        for phrase in sorted(translations_map.keys()):
            nepali_trans = translations_map[phrase]
            escaped_en = phrase.replace('"', '\\"')
            escaped_ne = nepali_trans.replace('"', '\\"')
            translated_entries.append(f'msgid "{escaped_en}"\nmsgstr "{escaped_ne}"\n')

        locale_dir = base_dir / 'locale' / 'ne' / 'LC_MESSAGES'
        locale_dir.mkdir(parents=True, exist_ok=True)
        po_path = locale_dir / 'django.po'
        mo_path = locale_dir / 'django.mo'

        po_content = """# CareFirst Dental Clinic Nepali Translation
# Generated via Deep Translator (Batch)
msgid ""
msgstr ""
"Project-Id-Version: CareFirst Dental 1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2026-08-19 10:20+0545\\n"
"PO-Revision-Date: 2026-08-19 10:20+0545\\n"
"Last-Translator: CareFirst AI Translator <info@carefirst.com>\\n"
"Language-Team: Nepali <ne@carefirst.com>\\n"
"Language: ne\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

""" + "\n".join(translated_entries)

        with open(po_path, 'w', encoding='utf-8') as f:
            f.write(po_content)

        compile_po_to_mo(str(po_path), str(mo_path))
        self.stdout.write(self.style.SUCCESS(f"Successfully generated {po_path} and compiled {mo_path}!"))
