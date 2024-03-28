import os
from google.cloud import vision
import re
from PIL import Image

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] ='/Users/bryanmawan/Documents/colonFourNew/colonFourNewProject/colonfour-2e3334af074b.json'
WORD = re.compile(r"\w+")

def detect_text(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # for non-dense text 
    # response = client.text_detection(image=image)
    # for dense text
    response = client.document_text_detection(image=image)
    texts = response.text_annotations
    ocr_text = []

    for text in texts:
        ocr_text.append(f"\r\n{text.description}")

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    return ocr_text

image_path = "colonFourNewProject/Screenshot 2024-04-15 at 22.47.33.png"
text = detect_text(image_path)

for line in text:
    print(line)

# Displaying the image
image = Image.open(image_path)
image.show()
