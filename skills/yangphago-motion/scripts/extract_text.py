"""수업 자료(PDF·PPTX·DOCX·TXT)에서 텍스트를 뽑아 UTF-8 파일로 저장한다.

Windows 콘솔(cp949)은 \\xa0 같은 문자를 출력하지 못해 print가 죽는다.
→ 본문은 파일로만 쓰고, 화면에는 파일별 쪽수·글자 수 요약만 출력한다.

사용: python extract_text.py 자료1.pdf 자료2.pptx --out source.txt
"""
import argparse
import sys
from pathlib import Path

# 콘솔 인코딩 오류로 죽지 않게 출력 스트림을 UTF-8로 바꾼다
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def read_pdf(path):
    import fitz
    doc = fitz.open(path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    return pages


def read_pptx(path):
    from pptx import Presentation
    slides = []
    for slide in Presentation(path).slides:
        texts = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                texts.append(shape.text_frame.text)
        slides.append("\n".join(texts))
    return slides


def read_docx(path):
    import docx
    paras = []
    for p in docx.Document(path).paragraphs:
        paras.append(p.text)
    return ["\n".join(paras)]


READERS = {".pdf": read_pdf, ".pptx": read_pptx, ".docx": read_docx}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default="source.txt")
    args = ap.parse_args()

    chunks = []
    for f in args.files:
        path = Path(f)
        reader = READERS.get(path.suffix.lower())
        if reader:
            parts = reader(str(path))
        else:
            parts = [path.read_text(encoding="utf-8", errors="replace")]
        # \xa0(줄바꿈 없는 공백)은 일반 공백으로 바꿔 둔다
        text = "\n".join(parts).replace("\xa0", " ")
        chunks.append(f"===== {path.name}\n{text}")
        print(f"{path.name}: {len(parts)}쪽 · {len(text)}자")

    Path(args.out).write_text("\n\n".join(chunks), encoding="utf-8")
    print(f"→ {args.out}")


if __name__ == "__main__":
    main()
