"""
File text extraction utilities.
Supports PDF (via pdfplumber) and DOCX (via python-docx).
"""

from pathlib import Path


# ── PDF ────────────────────────────────────────────────────────────────────
def extract_pdf(file_bytes: bytes) -> tuple[str, str | None]:
    """
    Extract text from a PDF file given its raw bytes.
    Returns (text, error_message).
    """
    try:
        import pdfplumber
    except ImportError:
        return "", "pdfplumber not installed. Run: pip install pdfplumber"

    import io
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text.strip())
        full_text = "\n\n".join(pages)
        if not full_text.strip():
            return "", "No text could be extracted from this PDF. It may be image-based (scanned)."
        return full_text, None
    except Exception as e:
        return "", f"Failed to read PDF: {e}"


# ── DOCX ───────────────────────────────────────────────────────────────────
def extract_docx(file_bytes: bytes) -> tuple[str, str | None]:
    """
    Extract text from a DOCX file given its raw bytes.
    Returns (text, error_message).
    """
    try:
        from docx import Document
    except ImportError:
        return "", "python-docx not installed. Run: pip install python-docx"

    import io
    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        full_text = "\n\n".join(paragraphs)
        if not full_text.strip():
            return "", "No text could be extracted from this DOCX file."
        return full_text, None
    except Exception as e:
        return "", f"Failed to read DOCX: {e}"


# ── Router ─────────────────────────────────────────────────────────────────
def extract_text(file_bytes: bytes, filename: str) -> tuple[str, str | None]:
    """
    Auto-detect file type and extract text.
    Returns (text, error_message).
    """
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_pdf(file_bytes)
    elif ext in {".docx", ".doc"}:
        return extract_docx(file_bytes)
    else:
        return "", f"Unsupported file type: '{ext}'. Please upload a PDF or DOCX."
