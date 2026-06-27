import PyPDF2
import io


def extract_text_from_pdf(file_stream):
    """
    Extracts all text content from an uploaded PDF file.
    file_stream: a file-like object (e.g. from Flask's request.files)
    Returns: extracted text as a single string
    """
    text = ""
    try:
        reader = PyPDF2.PdfReader(file_stream)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
    return text.strip()


def extract_text_from_upload(uploaded_file):
    """
    Takes a Flask FileStorage object, reads it into memory,
    and extracts text using extract_text_from_pdf.
    """
    file_bytes = uploaded_file.read()
    file_stream = io.BytesIO(file_bytes)
    return extract_text_from_pdf(file_stream)