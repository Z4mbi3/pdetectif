import pymupdf, sys, re

PDF_keywords = [
    "object", "xref", "trailer", "startxref",
    "/Page", "/Encrypt", "/JS", "/JavaScript", "/AA", "/OpenAction", "/JBIG2Decode",
    "RichMedia", "/Launch", "/XFA"
]

dict_keywords = {
    "object": 0, "xref": 0, "trailer": 0, "startxref": 0,
    "/Page": 0, "/Encrypt": 0, "/JS": 0, "/JavaScript": 0, "/AA": 0, "/OpenAction": 0, "/JBIG2Decode": 0,
    "RichMedia": 0, "/Launch": 0, "/XFA": 0
}

def extract_objects(doc_path):
    doc = pymupdf.open(doc_path)
    objects = ""
    
    xreflen = doc.xref_length()
    for xref in range(1, xreflen):
        try:
            objects += "\n\nobject %i | (stream: %s)\n\n" % (xref, doc.xref_is_stream(xref))
            objects += doc.xref_object(xref, compressed=False)
        except:
            pymupdf.TOOLS.mupdf_display_errors(False)
    return objects

def extract_keywords(doc_path, keywords):
    objects = extract_objects(doc_path)
    found_keywords = dict_keywords

    for keyword in keywords:
        pattern = r"\b{}\b".format(keyword)
        matches = re.findall(pattern, objects)
        found_keywords[keyword] = len(matches)
    print(found_keywords)




if __name__ == "__main__":
    pages = extract_objects(sys.argv[1])
    print(pages)

    extract_keywords(sys.argv[1], PDF_keywords)