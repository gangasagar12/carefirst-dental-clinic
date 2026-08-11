import os

template_dir = r"c:\Users\Chandra kant joshi\Desktop\carefirst\templates\treatments"
image_dir = r"c:\Users\Chandra kant joshi\Desktop\carefirst\static\serices-image"

# Get list of all images in serices-image
valid_images = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]

for filename in os.listdir(template_dir):
    if not filename.endswith(".html"):
        continue
    
    filepath = os.path.join(template_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace 'images/filename' with 'serices-image/filename' if the file exists in serices-image
    for img in valid_images:
        content = content.replace(f"images/{img}", f"serices-image/{img}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed image paths!")
