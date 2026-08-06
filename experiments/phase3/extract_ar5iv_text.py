#!/usr/bin/env python3
"""Extract readable audit text from saved ar5iv HTML or arXiv PDF files."""

from __future__ import annotations

import argparse
import html
import re
from html.parser import HTMLParser
from pathlib import Path


BREAK_TAGS = {
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
    "tr",
}
SKIP_TAGS = {"script", "style", "svg"}


class Ar5ivTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag in BREAK_TAGS:
            self.parts.append("\n")
        if tag == "img":
            alt = dict(attrs).get("alt")
            if alt:
                self.parts.append(f" {alt} ")

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if not self.skip_depth and tag in BREAK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        value = html.unescape("".join(self.parts))
        value = re.sub(r"[ \t\f\v]+", " ", value)
        value = re.sub(r" *\n *", "\n", value)
        value = re.sub(r"\n{3,}", "\n\n", value)
        return value.strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
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
            text_parser = Ar5ivTextParser()
            text_parser.feed(source.read_text(encoding="utf-8"))
            output.write_text(text_parser.text(), encoding="utf-8")
        print(f"{source} -> {output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
