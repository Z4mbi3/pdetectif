import statistics
import sys

def read_pdf(file):
    with open(file, 'rb') as doc:
        # Try different encodings here (replace 'latin-1' with others if needed)
        try:
            text = doc.read().decode('latin-1')  # Common encoding for Western characters
            print(text)
        except UnicodeDecodeError:
            # Fallback to another encoding if latin-1 fails
            print("Error decoding with latin-1, trying UTF-16")
            try:
                text = doc.read().decode('utf-16')
                print(text)
            except UnicodeDecodeError:
                print("Decoding failed with both encodings")

if __name__ == "__main__":
    read_pdf(sys.argv[1])