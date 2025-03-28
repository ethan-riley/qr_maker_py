import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer, GappedSquareModuleDrawer
from qrcode.image.styledpil import StyledPilImage
import qrcode


def generate_vcard(name, company, email, phone, title="", linkedin=""):
    """
    Generate a simple vCard string from the provided contact information.
    """
    vcard = (
        "BEGIN:VCARD\n"
        "VERSION:3.0\n"
        f"N:{name};;;;\n"    # Last name, first name
        f"FN:{name}\n"       # Formatted name
        f"TITLE:{title}\n"   # Title/Role
        f"EMAIL:{email}\n"
        f"TEL:+{phone}\n"
        f"COMPANY:{company}\n"
    )

    # Add LinkedIn URL if provided
    if linkedin:
        vcard += f"URL;type=WORK:{linkedin}\n"

    vcard += "END:VCARD"
    return vcard

def create_qr_code(data, box_size=4, border=3):
    """
    Creates a QR code image from the provided data (string).
    Returns a PIL Image object (RGBA).
    """
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=border
    )
    qr.add_data(data)
    #qr.make(fit=True)
    #img_qr = qr.make_image(fill_color="black", back_color="white", image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())
    img_qr = qr.make_image(image_factory=StyledPilImage, module_drawer=GappedSquareModuleDrawer())
    return img_qr.convert("RGBA")

def load_image(path_or_url):
    """
    Loads an image from a local path or a URL.
    Returns a PIL Image object (RGBA).
    If the path_or_url is empty or invalid, returns None.
    """
    if not path_or_url.strip():
        return None

    # Detect if it's a URL
    if path_or_url.lower().startswith("http://") or path_or_url.lower().startswith("https://"):
        try:
            response = requests.get(path_or_url, timeout=10)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            return img
        except Exception as e:
            print(f"Could not load image from URL: {e}")
            return None
    else:
        # Otherwise, assume it's a local file path
        if os.path.exists(path_or_url):
            try:
                img = Image.open(path_or_url).convert("RGBA")
                return img
            except Exception as e:
                print(f"Could not open image file: {e}")
                return None
        else:
            print(f"File not found: {path_or_url}")
            return None

def add_rounded_corners(im, radius=30):
    """
    Adds rounded corners to an image.
    Increase/decrease radius as desired.
    """
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)

    alpha = Image.new('L', im.size, 255)
    w, h = im.size

    # Top-left corner
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    # Top-right corner
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    # Bottom-left corner
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    # Bottom-right corner
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))

    im.putalpha(alpha)
    return im

def create_contact_card(
    name,
    title,
    email,
    phone,
    created_by,
    company,
    background_color="#5046e3",
    text_color="#FFFFFF",
    logo_image="/Users/felipe/personal/qr_pythonv2/qpassLogo.png",
    profile_image=None,
    linkedin="",
    output_filename="contact_card.png"
):
    """
    Creates a contact card image with:
    - Background color
    - Logo in top-left
    - Name, Title, Email, Phone
    - "Card Created by ..."
    - A QR code (vCard) near the bottom
    """
    # ------------------
    # 1. Create vCard & QR Code
    # ------------------
    vcard_data = generate_vcard(name, company, email, phone, title=title, linkedin=linkedin)
    qr_img = create_qr_code(vcard_data, box_size=4, border=3)

    # ------------------
    # 2. Create Base Card
    # ------------------
    card_width, card_height = 600, 800
    card = Image.new("RGBA", (card_width, card_height), background_color)
    draw = ImageDraw.Draw(card)

    # ------------------
    # 3. Add Logo (if provided)
    # ------------------
    if logo_image:
        logo_width = 70  # Increased from 120 for better visibility
        aspect_ratio = logo_image.width / logo_image.height
        logo_height = int(logo_width / aspect_ratio)
        logo_resized = logo_image.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
        logo_x, logo_y = 30, 30  # Adjusted position to be more prominent
        card.paste(logo_resized, (logo_x, logo_y), logo_resized)

    # ------------------
    # 4. Define Fonts
    # ------------------
    # For better styling, you can replace these with a TTF font.
    #title_font = ImageFont.load_default()
    #name_font = ImageFont.load_default()
    #info_font = ImageFont.load_default()
    #created_by_font = ImageFont.load_default()
    #company_font = ImageFont.truetype("/Users/felipe/personal/figtree/fonts/ttf/Figtree-ExtraBold.ttf", size=25)
    company_font = ImageFont.truetype("/Users/felipe/personal/WalbaumCom-Roman.ttf", size=25)
    title_font = ImageFont.truetype("/Users/felipe/personal/figtree/fonts/ttf/Figtree-Bold.ttf", size=14)
    name_font = ImageFont.truetype("/Users/felipe/personal/figtree/fonts/ttf/Figtree-Bold.ttf", size=22)
    info_font = ImageFont.truetype("/Users/felipe/personal/figtree/fonts/ttf/Figtree-Bold.ttf", size=14)
    content_font = ImageFont.truetype("/Users/felipe/personal/figtree/fonts/ttf/Figtree-Regular.ttf", size=22)
    created_by_font = ImageFont.truetype("/Users/felipe/personal/figtree/fonts/ttf/Figtree-Bold.ttf", size=12)


    # ------------------
    # 5. Place Text on the Card
    # ------------------
    # Title
    title_x, title_y = 30, 120
    draw.text((title_x, title_y), title, font=title_font, fill=text_color)

    # Name
    name_x, name_y = 30, title_y + 20
    draw.text((name_x, name_y), name, font=name_font, fill=text_color)

    # Email
    email_label = "EMAIL"
    phone_label = "MOBILE"
    email_x, email_y = 30, name_y + 80
    draw.text((email_x, email_y), f"{email_label}", font=info_font, fill=text_color)
    draw.text((email_x, email_y+20), f"{email}", font=content_font, fill=text_color)

    # Phone
    phone_x, phone_y = 30, email_y + 60
    draw.text((phone_x, phone_y), f"{phone_label}:", font=info_font, fill=text_color)
    draw.text((phone_x, phone_y+20), f"+{phone}", font=content_font, fill=text_color)

    # "Card Created by ..." text near the bottom
    created_by_text = f"CARD CREATED BY"
    created_by_x, created_by_y = card_width - 150, email_y
    draw.text((created_by_x, created_by_y), created_by_text, font=info_font, fill=text_color)
    draw.text((created_by_x, created_by_y+20), f"{created_by}", font=content_font, fill=text_color)

    # Company Details
    company_text= f"{company}"
    company_x, company_y = logo_x, 40
    #draw.text((company_x, company_y), company_text, font=company_font, fill=text_color)

    # ------------------
    # 6. Place QR Code
    # ------------------
    qr_size = qr_img.size
    qr_x = (card_width - qr_size[0]) // 2
    qr_y = card_height - qr_size[1] - 120
    card.paste(qr_img, (qr_x, qr_y), qr_img)

    # ------------------
    # 7. Place Profile Image (if provided) or a placeholder
    # ------------------
    if profile_image:
        desired_width = 80
        ratio = profile_image.width / profile_image.height
        desired_height = int(desired_width / ratio)
        profile_resized = profile_image.resize((desired_width, desired_height), Image.Resampling.LANCZOS)
        # Position: 30px from top-right
        profile_x = card_width - desired_width - 30
        profile_y = 100
        card.paste(profile_resized, (profile_x, profile_y), profile_resized)
#    else:
#        # Draw a white placeholder circle in the top-right corner
#        placeholder_radius = 40
#        placeholder_center_x = card_width - 50
#        placeholder_center_y = name_y
#        draw.ellipse(
#            [
#                (placeholder_center_x - placeholder_radius, placeholder_center_y - placeholder_radius),
#                (placeholder_center_x + placeholder_radius, placeholder_center_y + placeholder_radius)
#            ],
#            fill="#FFFFFF"
#        )

    # ------------------
    # 8. (Optional) Round the Card Corners
    # ------------------
    card_rounded = add_rounded_corners(card, radius=40)

    # ------------------
    # 9. Save the Final Image
    # ------------------
    card_rounded.save(output_filename, format="PNG")
    print(f"\nContact card saved as {output_filename}.")

if __name__ == "__main__":
    print("=== Contact Card Creator ===")
    name = input("Enter the Name: ")
    title = input("Enter the Job Title: ")
    email = input("Enter the Email: ")
    phone = input("Enter the Phone (Mobile): ")
    company = input("Enter your company: ")
    #created_by = input("Enter the 'Card Created By' label (e.g., 'Tech Sphere'): ")
    created_by="QPass"

    print("\nOptionally, specify a background color and text color in hex format.")
    bg_color = input("Background color (e.g. #5046e3) [default #5046e3]: ") or "#5046e3"
    txt_color = input("Text color (e.g. #FFFFFF) [default #FFFFFF]: ") or "#FFFFFF"

    print("\nSpecify the path or URL for the logo image (top-left).")
    #logo_path_or_url = input("Logo path or URL [leave blank to skip]: ") or "/Users/felipe/personal/contactinfo/qpass.small.png"
    logo_path_or_url = input("Logo path or URL [leave blank to skip]: ") or "/Users/felipe/personal/qr_pythonv2/qpassLogo.png"
    logo_image = load_image(logo_path_or_url)
    print(logo_image.width)

    print("\nSpecify the path or URL for the profile image (top-right).")
    profile_path_or_url = input("Profile image path or URL [leave blank to skip]: ")
    profile_image = load_image(profile_path_or_url)

    output_file = input("\nOutput filename [default: contact_card.png]: ") or "contact_card.png"

    # Create the contact card
    create_contact_card(
        name=name,
        title=title,
        email=email,
        phone=f"+{phone}",
        created_by=created_by,
        company=company,
        background_color=bg_color,
        text_color=txt_color,
        logo_image=logo_image,
        profile_image=profile_image,
        linkedin=profile_path_or_url,  # Using the profile URL as LinkedIn for now in the main function
        output_filename=output_file
    )
