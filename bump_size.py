import re

filepath = r'c:\Users\Chandra kant joshi\Desktop\carefirst\templates\treatments\dental_filling.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The user requested to bump up the small paragraph text for visibility.
# Replacing text-[13px] with text-[15px] globally.
content = content.replace('text-[13px]', 'text-[15px]')

# Also add leading-relaxed to paragraphs if they don't have it, to make the larger text breathe better.
# Actually, it's easier to just do the font size bump for now.

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
