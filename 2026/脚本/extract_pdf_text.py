
import sys
import os

pdf_path = r"d:\Users\HONOR\Desktop\base\2026\2026 MCM Problem B.pdf"

def extract_text(path):
    # Try pypdf (newer)
    try:
        from pypdf import PdfReader
        print("Using pypdf...")
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except ImportError:
        pass

    # Try PyPDF2 (older)
    try:
        import PyPDF2
        print("Using PyPDF2...")
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except ImportError:
        pass
    
    # Try pdfplumber
    try:
        import pdfplumber
        print("Using pdfplumber...")
        with pdfplumber.open(path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text
    except ImportError:
        pass

    return "NO_PDF_LIB"

if __name__ == "__main__":
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
    else:
        content = extract_text(pdf_path)
        print("---START_CONTENT---")
        try:
            # Write bytes directly to stdout buffer to avoid codec errors
            sys.stdout.buffer.write(content.encode('utf-8'))
            print() # Newline
        except Exception as e:
            print(f"Error printing content: {e}")
        print("---END_CONTENT---")
