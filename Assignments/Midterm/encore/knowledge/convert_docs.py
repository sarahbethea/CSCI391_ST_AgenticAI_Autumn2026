"""
Turn the downloaded documentation pages (knowledge/raw/*.html) into Markdown files in knowledge/corpus/.

    python knowledge/convert_docs.py

Run once after downloading. Only the main article of each page is kept (no menus, footers, or
tables of contents), and headings are kept as Markdown headings, so the section-based chunker can
split on them. Each ListenBrainz API endpoint ("GET /1/explore/lb-radio") becomes its own heading,
so one endpoint's documentation stays together in one section.
"""

from html.parser import HTMLParser
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parent
RAW_DIR = KNOWLEDGE_DIR / "raw"
CORPUS_DIR = KNOWLEDGE_DIR / "corpus"

LB_BASE = "https://listenbrainz.readthedocs.io/en/latest/"
MB_BASE = "https://musicbrainz.org/doc/"

SKIP_TAGS = {"script", "style", "nav", "noscript", "form", "button"}
SKIP_CLASSES = {"headerlink", "toc", "mw-editsection", "hierarchy-links", "wy-breadcrumbs"}
BLOCK_TAGS = {"p", "div", "li", "dd", "tr", "pre", "table", "ul", "ol", "dl", "blockquote", "section"}


class ArticleToMarkdown(HTMLParser):
    """Collect the text inside the page's main article, as Markdown."""

    def __init__(self, is_main_container):
        super().__init__(convert_charrefs=True)
        self.is_main_container = is_main_container   # function(tag, attrs) -> True for the article's outer div
        self.inside = False
        self.div_depth = 0              # nesting depth inside the article, to know where it ends
        self.skip_tag = None            # while set, we are inside an element we don't want
        self.skip_depth = 0
        self.heading_level = 0          # 1-4 while inside a heading
        self.in_pre = False
        self.in_endpoint = False        # inside a <dt> that names an API endpoint
        self.dl_stack = []              # one entry per open <dl>: True if it is an endpoint list
        self.pending_bullet = False     # an <li> started; put "- " before its first text
        self.lines = []
        self.current = ""

    def flush(self):
        text = self.current if self.in_pre else " ".join(self.current.split())
        if text.strip():
            if self.pending_bullet:
                text = "- " + text
                self.pending_bullet = False
            self.lines.append(text)
        self.current = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set((attrs.get("class") or "").split())

        if not self.inside:
            if self.is_main_container(tag, attrs):
                self.inside = True
                self.div_depth = 1
            return

        if tag == "div":
            self.div_depth += 1

        if self.skip_tag:
            if tag == self.skip_tag:
                self.skip_depth += 1
            return
        if tag in SKIP_TAGS or classes & SKIP_CLASSES or attrs.get("id") in ("toc", "mw-toc-heading"):
            self.skip_tag = tag
            self.skip_depth = 1
            return

        if tag in ("h1", "h2", "h3", "h4"):
            self.flush()
            self.heading_level = int(tag[1])
        elif tag == "dl":
            self.flush()
            self.dl_stack.append("http" in classes)
        elif tag == "dt" and self.dl_stack and self.dl_stack[-1]:
            # Sphinx's HTTP domain: <dl class="http get"><dt>GET /1/...</dt>. Make it a heading.
            # Only the endpoint's own <dt>: "Parameters:" lists nested inside stay in its section.
            self.flush()
            self.in_endpoint = True
        elif tag == "pre":
            self.flush()
            self.in_pre = True
        elif tag == "br":
            self.flush()
        elif tag in ("td", "th"):
            self.current += " | "
        elif tag in BLOCK_TAGS:
            self.flush()
            if tag == "li":
                self.pending_bullet = True

    def handle_startendtag(self, tag, attrs):
        if self.inside and not self.skip_tag and tag == "br":
            self.flush()

    def handle_endtag(self, tag):
        if not self.inside:
            return

        if self.skip_tag:
            if tag == self.skip_tag:
                self.skip_depth -= 1
                if self.skip_depth == 0:
                    self.skip_tag = None
            if tag == "div":
                self.div_depth -= 1
            return

        if tag in ("h1", "h2", "h3", "h4") and self.heading_level:
            text = " ".join(self.current.split())
            self.current = ""
            if text:
                self.lines.append("")
                self.lines.append("#" * self.heading_level + " " + text)
            self.heading_level = 0
        elif tag == "dt" and self.in_endpoint:
            text = " ".join(self.current.split())
            self.current = ""
            if text:
                self.lines.append("")
                self.lines.append("### " + text)
            self.in_endpoint = False
        elif tag == "dl" and self.dl_stack:
            self.dl_stack.pop()
            self.flush()
        elif tag == "pre":
            self.flush()
            self.in_pre = False
        elif tag in BLOCK_TAGS:
            self.flush()

        if tag == "div":
            self.div_depth -= 1
            if self.div_depth == 0:
                self.flush()
                self.inside = False

    def handle_data(self, data):
        if self.inside and not self.skip_tag:
            self.current += data


def is_listenbrainz_article(tag, attrs):
    return tag == "div" and attrs.get("itemprop") == "articleBody"


def is_musicbrainz_article(tag, attrs):
    return tag == "div" and attrs.get("id") == "content"


def source_url(raw_name: str) -> str:
    """lb_users_api_core.html -> https://listenbrainz.readthedocs.io/en/latest/users/api/core.html"""
    stem = raw_name[3:-5]
    if raw_name.startswith("lb_"):
        # File names replaced "/" with "_"; the page paths only use "_" in no other place we downloaded.
        path = stem.replace("users_api_", "users/api/").replace("users_", "users/").replace("general_", "general/")
        return LB_BASE + path + ".html"
    else:
        return MB_BASE + stem.replace("MusicBrainz_API_", "MusicBrainz_API/")


def convert(raw_path: Path) -> str:
    if raw_path.name.startswith("lb_"):
        parser = ArticleToMarkdown(is_listenbrainz_article)
        site = "ListenBrainz documentation"
    else:
        parser = ArticleToMarkdown(is_musicbrainz_article)
        site = "MusicBrainz documentation"
    parser.feed(raw_path.read_text(encoding="utf-8", errors="replace"))
    parser.flush()

    # Drop runs of blank lines, and give every file a title and its source on top.
    body = []
    for line in parser.lines:
        if line == "" and body and body[-1] == "":
            continue
        body.append(line.rstrip())
    # The title: the page's own <h1> on ListenBrainz; built from the page path on MusicBrainz,
    # whose <h1> is a breadcrumb trail (skipped) rather than the page name.
    if raw_path.name.startswith("mb_"):
        title = raw_path.stem[3:].replace("_API_", " API: ").replace("_", " ")
    else:
        title = next((line[2:] for line in body if line.startswith("# ")), raw_path.stem)
    # Drop the page's own top heading(s); we write exactly one title line ourselves.
    body = [line for line in body if not (line.startswith("# ") and line[2:] == title)]
    header = [f"<!-- source: {source_url(raw_path.name)} -->", f"<!-- site: {site} -->", "", f"# {title}"]
    return "\n".join(header + body).strip() + "\n"


def main() -> None:
    CORPUS_DIR.mkdir(exist_ok=True)
    for raw_path in sorted(RAW_DIR.glob("*.html")):
        markdown = convert(raw_path)
        out = CORPUS_DIR / (raw_path.stem + ".md")
        out.write_text(markdown, encoding="utf-8")
        print(f"{out.name:<45} {len(markdown.split()):>6} words")


if __name__ == "__main__":
    main()
