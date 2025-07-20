import os
import random
from PIL import Image, ImageEnhance
import piexif

def subtly_modify_image(image_path, output_path):
    try:
        # Load image
        img = Image.open(image_path)

        # Slight imperceptible changes
        contrast_factor = random.uniform(0.99, 1.01)
        saturation_factor = random.uniform(0.99, 1.01)

        img = ImageEnhance.Contrast(img).enhance(contrast_factor)
        img = ImageEnhance.Color(img).enhance(saturation_factor)

        # Modify EXIF (only for JPEGs)
        exif_bytes = None
        if image_path.lower().endswith((".jpg", ".jpeg")):
            try:
                exif_dict = piexif.load(img.info.get("exif", b""))
            except:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

            exif_dict["Exif"][piexif.ExifIFD.UserComment] = b"Modified_" + str(random.randint(1000, 9999)).encode()
            exif_bytes = piexif.dump(exif_dict)

        # Save modified image
        img.save(output_path, "JPEG", quality=random.randint(94, 98), exif=exif_bytes)
        print(f"✅ Processed: {output_path}")
    except Exception as e:
        print(f"❌ Failed to process {image_path}: {e}")

def process_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg")):
                input_path = os.path.join(root, file)
                rel_path = os.path.relpath(input_path, input_folder)
                output_path = os.path.join(output_folder, rel_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                subtly_modify_image(input_path, output_path)

# --- USAGE ---
input_dir = "Products"
output_dir = "ModifiedProducts"
process_folder(input_dir, output_dir)
