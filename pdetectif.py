import pymupdf, argparse, sys, re, os, time
from PIL import Image
from pyzbar.pyzbar import decode

# Util
def list_to_dict(list):
    """
    Converts a list into a dictionary with keys as list elements and values as 0.

    Args:
        list: The input list.

    Returns:
        dict: The created dictionary.
    """
    dictionary = {}
    for item in list:
        dictionary[item] = 0
    return dictionary

# Variables
PDF_KEYWORDS = [
    "obj", "xref", "trailer", "startxref",
    "/Page", "/Encrypt", "/JS", "/JavaScript", "/AA", "/OpenAction", "/JBIG2Decode",
    "/RichMedia", "/Launch", "/XFA"
]

dict_keywords = list_to_dict(PDF_KEYWORDS)

def extract_objects(doc_path):
    """
    Extracts all objects from a PDF document.

    Args:
        doc_path (str): Path to the PDF document.

    Returns:
        str: A string containing all extracted objects.
    """
    doc = pymupdf.open(doc_path)
    objects = ""

    xreflen = doc.xref_length()
    for xref in range(1, xreflen):
        try:
            objects += "\n\nobj %i 0 R | (stream: %s)\n\n" % (xref, doc.xref_is_stream(xref))
            objects += doc.xref_object(xref, compressed=False)
        except:
            pymupdf.TOOLS.mupdf_display_errors(False)
    return objects


# ============== TODO: Code rewrite ==============
def extract_single_object(doc_path, obj):
    """
    Extracts a single object from a PDF document by its number.

    Args:
        doc_path (str): Path to the PDF document.
        obj (int): Number of the object to extract.

    Returns:
        str: The extracted object, or None if not found.
    """
    doc = pymupdf.open(doc_path)
    try:
        object = doc.xref_object(obj)
        return object
    except RuntimeError:
        print("Object not found")
# =================================================

def format_keywords(keywords):
    """
    Formats the extracted keywords for better readability.

    Args:
        keywords (dict): A dictionary containing keywords and their counts.

    Returns:
        str: The formatted string.
    """
    formatted_objects = ""
    for keyword in keywords:
        formatted_objects += "\n{}{}{}".format(keyword, (" " * (15 - len(keyword))) ,keywords[keyword])
    return formatted_objects

def extract_keywords(doc_path, keywords):
    """
    Extracts the occurrences of predefined keywords from a PDF document.

    Args:
        doc_path (str): Path to the PDF document.
        keywords (list): List of keywords to search for.

    Returns:
        dict: A dictionary containing the keyword and its count.
    """
    objects = extract_objects(doc_path)
    found_keywords = dict_keywords

    # Pattern matching
    for keyword in keywords:
        pattern = r"\b{}\b".format(keyword)
        matches = re.findall(pattern, objects)
        found_keywords[keyword] = len(matches)
    return found_keywords

# Extract specific types from text (e.g. "URL", "EMAIL")
def extract_from_text(doc_path, type):
    """
    Extracts specific types of text (e.g., URLs, emails) from a PDF document.

    Args:
        doc_path (str): Path to the PDF document.
        type (str): The type of text to extract ("URL" or "EMAIL").
    """
    if type == "URL":
        regex = r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
    if type == "EMAIL":
        regex = r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
    text = ""
    matches = []
    with pymupdf.open(doc_path) as doc:
        for page in doc:
            text += page.get_text()
    for match in re.finditer(regex, text):
        match = match.group()
        print("[+] Found:", match)
        matches.append(match)
    print("[*] Total extracted", len(matches))

# Visual Functionality
def convert_to_images(doc_path):
    """
    Converts a PDF document into images and decodes QR codes.

    Args:
        doc_path (str): Path to the PDF document.

    Returns:
        dict: A dictionary containing decoded QR codes per page.
    """
    doc = pymupdf.open(doc_path)
    out_dir = "{}".format(str(time.time()))
    os.mkdir(out_dir)
    os.chdir(out_dir)
    try:
        for page in doc:
            pix = page.get_pixmap()
            pix.save("page-%i.png" % page.number)
    except RuntimeError:
        print("Error converting PDF to image files")
    return decode_qr_codes("./")

# Decodes QR codes found in a folder
def decode_qr_codes(path):
    """
    Decodes QR codes from image files in a given directory.

    Args:
        path (str): Path to the directory containing image files.

    Returns:
        dict: A dictionary containing decoded QR code data per page.
    """
    decoded_data = {}
    page_number = 0

    for filename in os.listdir(path):
        page_number += 1  # Increment page number for each image

        try:
            img_path = os.path.join(path, filename)
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            qrcodes = decode(img)

            if qrcodes:  # Check if any QR code was found
                decoded_data[f"page-{page_number}"] = []
                for qrcode in qrcodes:
                    decoded_data[f"page-{page_number}"].append(
                        qrcode.data.decode('utf-8')
                    )
            else:
                print(f"No QR codes found in image: {filename}")
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except Exception as e:
            print(f"Error processing image: {filename} - {e}")
    return decoded_data # Returns all QR data of the PDF document

# --------Application functionality--------
def command_line():
    description = "Python PDF analysis tool"
    parser = argparse.ArgumentParser(prog="pdetectif.py", description=description)
    parser.add_argument("-k", "--keywords", action="store_true", default=False,
                    help="Extract predefined keywords")
    parser.add_argument("-x", "--extract_object", type=int,
                    help="Extract a specific object by number (requires -k)")
    parser.add_argument("-i", "--images", action="store_true", default=False,
                    help="Convert PDF pages to images and decode QR codes")
    parser.add_argument("-o", "--objects", action="store_true", default=False,
                    help="Extract all objects from the PDF")
    parser.add_argument("-u", "--urls", action="store_true", default=False,
                    help="Extract all urls from the PDF")
    parser.add_argument("-m", "--emails", action="store_true", default=False,
                    help="Extract all emails from the PDF")
    parser.add_argument("pdf_file", help="Path to the PDF document")
    
    args = parser.parse_args()
    
    if args.keywords: 
        extraction = extract_keywords(args.pdf_file, PDF_KEYWORDS)
        if args.extract_object:
            # Check object number validity and call extract_single_object()
            if 1 <= args.extract_object <= len(extraction):
                specific_object = extract_single_object(args.pdf_file, args.extract_object)
                print(f"Object {args.extract_object}: {specific_object}")
            else:
                print(f"Invalid object number: {args.extract_object}")
        else:
            print(format_keywords(extraction))
    elif args.objects:
        objects = extract_objects(args.pdf_file)
        print(objects)
    elif args.images:
        converted = convert_to_images(args.pdf_file)
        print(converted)
    elif args.urls:
        extract_from_text(args.pdf_file, "URL")
    elif args.emails:
        extract_from_text(args.pdf_file, "EMAIL")
    else:
        extraction = extract_keywords(args.pdf_file, PDF_KEYWORDS)
        print(format_keywords(extraction))

if __name__ == "__main__":
    command_line()
