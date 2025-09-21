import os
import pdfplumber


def load_slides(folder="data"):
    """Extract text from PDFs in the folder, keep per-page text."""
    docs = []
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            path = os.path.join(folder, file)
            with pdfplumber.open(path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    text = text.strip()
                    if text:
                        # Keep whole page text for context-heavy slides (Teaching team, Assessments, etc.)
                        docs.append({
                            "file": file,
                            "page": page_num,
                            "text": text
                        })
    return docs


def chunk_text(text, chunk_size=200, overlap=50):
    """
    Split text into smaller chunks for TF-IDF.
    Overlap helps preserve context across boundaries.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks
