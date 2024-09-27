import sys, re

def read_pdf(file):
    with open(file, 'rb') as doc:
        try:
            text = doc.read().decode('latin-1')  # Common encoding for Western characters
            return text
        except UnicodeDecodeError:
            # Fallback to another encoding if latin-1 fails
            print("Error decoding with latin-1, trying UTF-16")
            try:
                text = doc.read().decode('utf-16')
                return text
            except UnicodeDecodeError:
                print("Decoding failed with both encodings")

def match_regex(text):
    matches = re.findall(r'stream([\s\S]*?)endstream', text)

    for match in matches:
        print("Captured Content:", match)

if __name__ == "__main__":
    print(read_pdf(sys.argv[1]))