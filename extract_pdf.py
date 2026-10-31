import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

pdf_path = '/Users/kumar/Downloads/document (1) (2) (1).pdf'
extracted_text = extract_text_from_pdf(pdf_path)
with open('pdf_text.txt', 'w') as f:
    f.write(extracted_text)
print("Text extracted to pdf_text.txt")