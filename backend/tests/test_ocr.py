from backend.ocr.ocr_utils import ocr_from_image

# Path to your image
image_path = "moscow.png"  # make sure this file exists in the same folder

# Run OCR
text = ocr_from_image(image_path, lang="rus")

print("OCR output:", text)
