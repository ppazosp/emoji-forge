"""Check Markdown links stay inside the installable skill and resolve."""

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt


def file_links(tokens):
    for token in tokens:
        if token.type == "link_open":
            yield token.attrGet("href")
        elif token.type == "image":
            yield token.attrGet("src")
        if token.children:
            yield from file_links(token.children)


def main():
    root = Path(sys.argv[1]).resolve(strict=True)
    parser = MarkdownIt()
    pages = {}
    for source in sorted(root.rglob("*.md")):
        if any(part.startswith(".") for part in source.relative_to(root).parts):
            continue
        pages[source] = parser.parse(source.read_text(encoding="utf-8"))
    errors = []
    for source, tokens in pages.items():
        for link in file_links(tokens):
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = (source.parent / unquote(url.path)).resolve() if url.path else source
            if not target.is_relative_to(root) or not target.exists():
                errors.append(f"{source.relative_to(root)}: broken skill link {link!r}")
            elif url.fragment and target in pages:
                headings = {
                    re.sub(r"[^\w -]", "", inline.content.lower()).replace(" ", "-")
                    for marker, inline in zip(pages[target], pages[target][1:])
                    if marker.type == "heading_open"
                }
                if unquote(url.fragment) not in headings:
                    errors.append(f"{source.relative_to(root)}: missing heading in {link!r}")
    if errors:
        sys.exit("\n".join(errors))
    print(f"Relative links resolve in {len(pages)} skill documents.")


if __name__ == "__main__":
    main()
