import cv2
import numpy as np
import os

# Force UTF-8 for filenames
os.environ["PYTHONUTF8"] = "1"

# --- Directories ---
input_dir = r'C:\Users\Curve System\Desktop\کتاب کودک\نردبان'
output_dir = r'C:\Users\Curve System\Desktop\کتاب کودک\نردبان'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# --- Unicode-safe image reader/writer ---
def imread_unicode(filename):
    try:
        with open(filename, 'rb') as f:
            file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
        return img
    except Exception as e:
        print(f"⚠️ Failed to read {filename}: {e}")
        return None

def imwrite_unicode(filename, img):
    try:
        ext = os.path.splitext(filename)[1]
        result, encoded_img = cv2.imencode(ext, img)
        if result:
            with open(filename, mode='wb') as f:
                encoded_img.tofile(f)
            return True
    except Exception as e:
        print(f"⚠️ Failed to save {filename}: {e}")
    return False

# --- Resize + select template ---
def resize_image(image_path):
    img = imread_unicode(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    height, width = img.shape[:2]
    ratio = height / width

    # Template directory (make sure all files exist here)
    base_dir = r'C:\Users\Curve System\Desktop\Code dump\Image_editing\sizes\Book Ratio- Shadow Template\New'

    if ratio <= 1.08:
        coords = [318, 849, 34, 566]
        base_image_path = os.path.join(base_dir, 'Kheshti-Bozorg-1-(318x849)-(34x566)-531-532.jpg')
        new_width, new_height = 532, 531

    elif ratio > 1.08 and ratio <= 1.2:
        coords = [215, 849, 34, 566]
        base_image_path = os.path.join(base_dir, 'Kheshti-Koochak-1-19-(215x849)-(34x566)-634-532.jpg')
        new_width, new_height = 532, 634

    elif ratio > 1.2 and ratio <= 1.3:
        coords = [200, 849, 34, 566]
        base_image_path = os.path.join(base_dir, 'Rahli--1-23-(649x532)-(190x849)--34-566.jpg')
        new_width, new_height = 532, 649

    elif ratio > 1.3 and ratio <= 1.46:
        coords = [65, 837, 34, 566]
        base_image_path = os.path.join(base_dir, 'Vaziri-1-44-(65x835)-(35x565)-770-530.jpg')
        new_width, new_height = 532, 772

    elif ratio > 1.46 and ratio <= 1.53:
        coords = [56, 846, 34, 566]
        base_image_path = os.path.join(base_dir, 'Roghei-1-48-(56x844)-(34x566)-788-532.jpg')
        new_width, new_height = 532, 790

    elif ratio > 1.53 and ratio <= 1.65:
        coords = [52, 851, 48, 552]
        base_image_path = os.path.join(base_dir, 'Roghei-Koochak-1-58-(51x849)-(49x551)-798-502.jpg')
        new_width, new_height = 504, 799

    else:
        coords = [51, 849, 66, 534]
        base_image_path = os.path.join(base_dir, 'Paltoei-1-706-(51x849)-(66x534)-798-468.jpg')
        new_width, new_height = 468, 798

    if not os.path.exists(base_image_path):
        raise FileNotFoundError(f"Template not found: {base_image_path}")

    image_resized = cv2.resize(img, (new_width, new_height))
    return image_resized, coords, base_image_path

# --- Add to background ---
def add_background(filename):
    image_path = os.path.join(input_dir, filename)
    img, coords, base_image_path = resize_image(image_path)

    base_image = imread_unicode(base_image_path)
    if base_image is None:
        raise ValueError(f"Base image could not be read: {base_image_path}")

    # Match color channels
    if img.shape[-1] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    if base_image.shape[-1] == 4:
        base_image = cv2.cvtColor(base_image, cv2.COLOR_BGRA2BGR)

    base_image[coords[0]:coords[1], coords[2]:coords[3]] = img

    # --- Changed only this line ---
    output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".jpg")
    imwrite_unicode(output_path, base_image)
    print(f"✅ Saved: {output_path}")

# --- Main Loop ---
for filename in os.listdir(input_dir):
    if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        try:
            add_background(filename)
        except Exception as e:
            print(f"⚠️ Failed for {filename}: {e}")

print("🎉 Done! All images processed successfully.")
