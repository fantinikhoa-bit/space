
import zipfile
import re
import os
import xml.etree.ElementTree as ET

def extract_text_from_docx(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as zf:
            xml_content = zf.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            
            # Identify the namespace
            namespaces = dict([node for _, node in ET.iterparse(io.BytesIO(xml_content), events=['start-ns'])])
            
            # Text is usually in <w:t> tags
            text_parts = []
            for elem in tree.iter():
                if elem.tag.endswith('}t'):
                    if elem.text:
                        text_parts.append(elem.text)
                elif elem.tag.endswith('}p'):
                    text_parts.append('\n') # New line for paragraphs
            
            return ''.join(text_parts)
    except Exception as e:
        return f"Error reading docx directly: {e}"

if __name__ == "__main__":
    import io
    docx_path = r"d:\Users\HONOR\Desktop\base\数据.docx"
    output_path = r"d:\Users\HONOR\Desktop\base\data_content.txt"
    
    if not os.path.exists(docx_path):
        print(f"File not found: {docx_path}")
    else:
        content = extract_text_from_docx(docx_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Content written to {output_path}")
