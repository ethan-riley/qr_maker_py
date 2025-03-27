import os
import pandas as pd
import cv2
import numpy as np
from PIL import Image
from qrgenerator import create_contact_card, load_image

# Face cropping function using OpenCV with adjustable zoom-out
def crop_to_face(image: Image.Image, size=(80, 80), zoom_out_factor=0.5):
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2RGB)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_RGB2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        padding = int((zoom_out_factor + 0.25) * max(w, h))
        x = max(x - padding, 0)
        y = max(y - padding, 0)
        w = min(w + 2 * padding, cv_image.shape[1] - x)
        h = min(h + 2 * padding, cv_image.shape[0] - y)
        face_image = cv_image[y:y+h, x:x+w]
    else:
        min_side = min(cv_image.shape[:2])
        center_x, center_y = cv_image.shape[1] // 2, cv_image.shape[0] // 2
        half_side = min_side // 2
        face_image = cv_image[center_y - half_side:center_y + half_side, center_x - half_side:center_x + half_side]

    face_image = cv2.resize(face_image, size, interpolation=cv2.INTER_AREA)
    mask = np.zeros((size[1], size[0]), np.uint8)
    cv2.circle(mask, (size[0]//2, size[1]//2), size[0]//2, 255, -1)
    masked_face = cv2.bitwise_and(face_image, face_image, mask=mask)

    final_image = Image.fromarray(masked_face).convert("RGBA")
    final_image.putalpha(Image.fromarray(mask))

    return final_image

# Specify the path to your CSV file
csv_file = 'user_details.csv'

# Load CSV
data = pd.read_csv(csv_file)

# Default values
background_color = "#5046e3"
text_color = "#FFFFFF"
logo_image = "/Users/felipe/personal/qr_pythonv2/qpassLogo.png"
company = "Tech Sphere"

# Ensure placeholder profile image exists at the correct path
#placeholder_profile = load_image("/Users/felipe/personal/contactinfo/user.png")
#if placeholder_profile is None:
#    raise FileNotFoundError("Placeholder profile image 'user.png' was not found.")

created_by = "QPass"

# Iterate over each row in the CSV
for index, row in data.iterrows():
    name = row['Name']
    title = row['Job Title']
    email = row['Email']
    phone = row['Phone']
    company = row['Company']
    background_color= row['bg_color']

    profile_image_path = row.get('Profile image path or url', '')
    if pd.isna(profile_image_path):
        profile_image_path = ''

    profile_image = load_image(profile_image_path)

    # Check if profile image exists
#    if profile_image:
#        # Crop and center profile image in a circle
#        min_side = min(profile_image.size)
#        left = (profile_image.width - min_side) / 2
#        top = (profile_image.height - min_side) / 2
#        right = (profile_image.width + min_side) / 2
#        bottom = (profile_image.height + min_side) / 2
#
#        profile_image = profile_image.crop((left, top, right, bottom))
#        profile_image = profile_image.resize((80, 80), Image.Resampling.LANCZOS)
#    else:
#        profile_image = placeholder_profile.resize((80, 80), Image.Resampling.LANCZOS)

    if profile_image:
        profile_image = crop_to_face(profile_image, size=(80, 80))
#    else:
#        profile_image = crop_to_face(placeholder_profile, size=(80, 80))

    output_filename = f"{name.replace(' ', '_')}_card.png"

    # Create contact card
    create_contact_card(
        name=name,
        title=title,
        email=email,
        phone=phone,
        created_by=created_by,
        company=company,
        background_color=background_color,
        text_color=text_color,
        logo_image=logo_image,
#        profile_image=profile_image,
        output_filename=output_filename
    )

