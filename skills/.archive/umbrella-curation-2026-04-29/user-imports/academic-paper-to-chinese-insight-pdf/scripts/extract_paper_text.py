#!/usr/bin/env python3
"""Extract paper text from PDF into markdown using pdfplumber."""

import argparse
import importlib.util
from pathlib import Path


def load_source_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description="Extract academic paper PDF text into markdown")
    parser.add_argument("pdf_path")
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--extractor-script", default="/tmp/skill-pdf-content-extractor/scripts/extract_text.py")
    args = parser.parse_args()

    extractor_module = load_source_module(Path(args.extractor_script), "paper_extract_text")
    extractor = extractor_module.PDFTextExtractor()
    result = extractor.extract_text(args.pdf_path, output_format="markdown")
    if "error" in result:
        raise SystemExit(result["error"])
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result["text"], encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
