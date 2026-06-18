
import re
import zlib

def parse_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        content = f.read()

    # Find all streams
    # PDF stream format:
    # << /Length ... /Filter /FlateDecode >> stream ... endstream
    # We look for "stream" and "endstream"
    
    # Regex to find streams (simple approach)
    # changing to bytes regex
    stream_pattern = re.compile(b'stream[\r\n]+(.*?)[\r\n]+endstream', re.DOTALL)
    
    streams = stream_pattern.findall(content)
    
    extracted_text = []

    print(f"Found {len(streams)} streams.")

    for idx, s in enumerate(streams):
        try:
            # Try to decompress
            decompressed = zlib.decompress(s)
            # functionality to extract text from PDF commands
            # Look for: (text) Tj  or  [ (text) 10 (text) ] TJ
            text_data = extract_text_from_pdf_commands(decompressed)
            if len(text_data) > 5: # filter out tiny bits
                extracted_text.append(text_data)
        except Exception as e:
            # Maybe not zlib compressed or other error
            pass

    full_text = "\n".join(extracted_text)
    return full_text

def extract_text_from_pdf_commands(data):
    # data is bytes
    # We want to find patterns like:
    # (sometext) Tj
    # [(some) -20 (text)] TJ
    
    text_parts = []
    
    # Simple regex for (...) Tj
    # Note: PDF strings can contain escaped parens \( or \)
    # We will do a simple greedy match for now, might miss complex cases
    
    # Convert to string (latin1 usually safe for PDF bytes)
    try:
        s_data = data.decode('latin1')
    except:
        return ""

    # Find text in (...)
    # This regex matches (text) 
    # It catches simple cases. Nested parens are hard with regex.
    paren_text = re.findall(r'\(([^)]+)\)', s_data)
    
    # Filter reasonable text (removes some garbage)
    for txt in paren_text:
        # Check if it looks like meaningful text
        if len(txt) > 0: 
            # PDF often uses custom encodings, but for standard English it's usually ASCII-ish
            # We might see octal escapes like \305
            # Let's try to clean it
            clean = txt.replace(r'\ ', ' ')
            text_parts.append(clean)
            
    return " ".join(text_parts)

path = r"d:\Users\HONOR\Desktop\base\2026\2026 MCM Problem B.pdf"
try:
    print("Attempting to read PDF...")
    text = parse_pdf(path)
    print("---EXTRACTED TEXT---")
    print(text)
    print("---END TEXT---")
except Exception as e:
    print(f"Error: {e}")
