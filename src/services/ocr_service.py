import pytesseract
from PIL import Image

def process_file(file):
    image = Image.open(file)

    text = pytesseract.image_to_string(image, lang='rus')

    return {"result": text}