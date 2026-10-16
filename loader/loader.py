# loader.py
from pathlib import Path
from pypdf import PdfReader

# 项目根目录（loader/ 的上一级）下的 notes/，用 __file__ 定位，
# 保证无论从哪个目录启动程序，路径都指向这份笔记库
NOTES_DIR = Path(__file__).resolve().parent.parent / "notes"


def load_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def load_docs(directory: Path = NOTES_DIR) -> list[dict]:
    """返回 [{source, text}, ...]"""
    docs = []
    for path in directory.rglob("*"):
        if path.suffix == ".md":
            docs.append({"source": str(path), "text": load_markdown(path)})
        elif path.suffix == ".pdf":
            docs.append({"source": str(path), "text": load_pdf(path)})
    return docs

