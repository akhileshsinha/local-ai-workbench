from services.document_processor import extract_text

file_path = "Medical Insurance Card.pdf"

text = extract_text(file_path)

print(text[:3000])