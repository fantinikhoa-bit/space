
import sys
import os
import re

pdf_path = r"d:\Users\HONOR\Desktop\base\2026\2026 MCM Problem B.pdf"

def extract_strings(path):
    with open(path, 'rb') as f:
        data = f.read()
    # Find sequences of 4 or more printable characters
    # This is a heuristic to get text from binary
    import string
    printable = set(string.printable.encode('ascii'))
    
    # Simple state machine or regex
    # Regex on bytes is easiest
    # printable includes whitespace, we want text
    
    # Try simple latin1 decode and regex
    try:
        text = data.decode('latin1')
    except:
        text = data.decode('utf-8', errors='ignore')

    # Look for patterns that look like sentences or titles
    # PDF text is often inside parentheses () or streams BT ... ET
    # But compressed streams won' usually show up.
    # If the PDF is compressed (FlateDecode), this won't work well.
    # However, let's try.
    
    # Alternative: Use 'strings' logic
    chars = []
    for byte in data:
        if 32 <= byte <= 126 or byte in (9, 10, 13):
            chars.append(chr(byte))
        else:
            chars.append(' ')
    
    raw_text = "".join(chars)
    # Collapse spaces
    clean_text = re.sub(r'\s+', ' ', raw_text)
    
    return clean_text

if __name__ == "__main__":
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
    else:
        content = extract_strings(pdf_path)
        print("---START_CONTENT---")
        # Print a subset or formatted
        # Just print it all, the buffer is large but manageable usually for these problems (usually < 20KB text)
        print(content[:5000]) # First 5000 chars might contain headers
        print("...")
        print(content[-5000:]) # Last 5000
        print("---END_CONTENT---")
