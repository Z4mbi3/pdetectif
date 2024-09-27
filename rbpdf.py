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
    matches = re.findall(r"\d+\s+\d+\s+obj.*?endobj", text, re.DOTALL)

    print("\n\n".join(matches))
    
def match_obj(obj_num, text):
    matches = re.findall(r"%i+\s+\d+\s+obj.*?endobj" % obj_num, text, re.DOTALL)
    
    # Check if no matches were found
    if not matches:
        print(f"No matches found for object {obj_num}.")
    else:
        # Print all matches with double newlines for clarity
        output = "\n\n".join(matches)
        print(f"\n{output}\n")

if __name__ == "__main__":
    match_regex(read_pdf(sys.argv[1]))