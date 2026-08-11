import os

template_dir = r"c:\Users\Chandra kant joshi\Desktop\carefirst\templates\treatments"

for filename in os.listdir(template_dir):
    if not filename.endswith(".html"):
        continue
    
    filepath = os.path.join(template_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Fix section-py
    content = content.replace('class="section-py', 'class="py-5')
    
    # Increase the padding for the main sections so they don't overlap
    content = content.replace('<section class="py-5', '<section class="py-5 my-3')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed layout padding!")
