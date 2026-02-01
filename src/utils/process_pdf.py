import pypdf
import logging

logging.basicConfig(filename='py_log', filemode='w')

def process_pdf(temp_path):
    reader = pypdf.PdfReader(temp_path)

    num_pages = len(reader.pages)
    preview = reader.pages[0].extract_text() or ""
    text = ""
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        text += page_text or ""

    result = {
        'file_type': "pdf",
        "results": {
            "pages": num_pages,
            "preview": preview
        }
    }

    return result