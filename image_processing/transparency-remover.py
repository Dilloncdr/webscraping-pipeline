from PIL import Image
import os
import numpy as np

input_dir = r'C:\Users\Curve System\Desktop\Code dump\Image_editing\Source'
output_dir = r'C:\Users\Curve System\Desktop\Code dump\Image_editing\Output'
threshold = 80  # adjust if needed (50–100 works best)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for filename in os.listdir(input_dir):
    if not filename.lower().endswith(".png"):
        continue

    in_path = os.path.join(input_dir, filename)
    out_path = os.path.join(output_dir, filename)

    img = Image.open(in_path).convert("RGBA")
    np_img = np.array(img)

    # Extract alpha channel
    alpha = np_img[:, :, 3]

    # Create a mask: 1 = opaque enough, 0 = transparent or semi-transparent
    mask = alpha > threshold

    # Find bounding box of non-transparent region
    coords = np.argwhere(mask)
    if coords.size == 0:
        print(f"⚠️ Skipped {filename} (fully transparent)")
        continue

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1  # +1 to include last pixel

    # Crop and save
    cropped = img.crop((x0, y0, x1, y1))
    cropped.save(out_path)

    print(f"✅ Cropped: {filename}")
