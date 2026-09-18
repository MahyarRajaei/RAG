# app/rag/extraction.py
import subprocess
from pathlib import Path

from excep.document import ExtractionError
from model.document import MIMEType


def extract_text(file_path: Path, file_type: MIMEType) -> str:
    if file_type in (MIMEType.TXT, MIMEType.MARKDOWN):
        text = file_path.read_text(encoding="utf-8")
    elif file_type == MIMEType.DOCX:
        text = _extract_docx(file_path)
    else:
        raise ExtractionError(file_path.name, "No extractor available.")

    if not text.strip():
        raise ExtractionError(file_path.name, "Extracted text is empty")
    return text


def _extract_docx(file_path: Path) -> str:
    try:
        result = subprocess.run(
            ["pandoc", str(file_path), "-t", "plain"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise ExtractionError(f"Pandoc failed: {e.stderr}") from e
    except subprocess.TimeoutExpired as e:
        raise ExtractionError("Pandoc extraction timed out") from e
