#!/usr/bin/env python3
"""Extract readable audit text from saved ar5iv HTML or arXiv PDF files."""

from __future__ import annotations

import argparse
import html
import re
from html.parser import HTMLParser
from pathlib import Path


BLOCK_TAGS = {
    "article",
    "br",
    "caption",
    "div",
    "figcaption",
    "figure",
    "footer",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "li",
    "p",
    "section",
    "table",
    "td",
    "th",
    "title",
    "tr",
}
SKIP_TAGS = {"annotation-xml", "math", "script", "style", "svg"}


class Ar5ivTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.fragments: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "math" and not self.skip_depth:
            alttext = attributes.get("alttext")
            if alttext:
                self.fragments.append(f" {alttext} ")
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        if tag in BLOCK_TAGS and not self.skip_depth:
            self.fragments.append("\n")
        if tag == "img" and not self.skip_depth:
            alt = attributes.get("alt")
            if alt:
                self.fragments.append(f" {alt} ")

    def handle_endtag(self, tag: str) -> None:
        if tag in BLOCK_TAGS and not self.skip_depth:
            self.fragments.append("\n")
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.fragments.append(data)

    def text(self) -> str:
        raw = html.unescape("".join(self.fragments))
        lines = []
        for line in raw.splitlines():
            line = re.sub(r"\s+", " ", line).strip()
            if line:
                lines.append(line)
        return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="+")
    args = parser.parse_args()
    for source in args.inputs:
        output = source.with_suffix(".txt")
        if source.suffix.casefold() == ".pdf":
            from pypdf import PdfReader

            pages = [
                page.extract_text(extraction_mode="layout") or ""
                for page in PdfReader(source).pages
            ]
            output.write_text("\n\n".join(pages).strip() + "\n", encoding="utf-8")
        else:
            extractor = Ar5ivTextParser()
            extractor.feed(source.read_text(encoding="utf-8", errors="replace"))
            output.write_text(extractor.text(), encoding="utf-8")
        print(f"{source} -> {output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
