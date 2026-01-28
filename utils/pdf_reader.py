import PyPDF2
import os


def read_pdf(filepath):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"

        return text.strip()
    except Exception as e:
        print(f"❌ Error reading PDF {filepath}: {e}")
        return None


def read_txt(filepath):
    """Read text file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading TXT {filepath}: {e}")
        return None


def read_document(filepath):
    """Read either PDF or TXT file"""
    if filepath.endswith('.pdf'):
        return read_pdf(filepath)
    elif filepath.endswith('.txt'):
        return read_txt(filepath)
    else:
        print(f"⚠️ Unsupported file type: {filepath}")
        return None


def get_all_documents(directory):
    """Get all PDF and TXT files from directory"""
    documents = {}

    if not os.path.exists(directory):
        print(f"⚠️ Directory not found: {directory}")
        return documents

    for filename in os.listdir(directory):
        if filename.endswith(('.pdf', '.txt')):
            filepath = os.path.join(directory, filename)
            print(f"📄 Reading {filename}...")
            content = read_document(filepath)
            if content:
                documents[filename] = content
                print(f"✅ Loaded {filename} ({len(content)} chars)")

    return documents
