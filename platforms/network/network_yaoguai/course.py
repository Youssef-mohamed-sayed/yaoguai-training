"""Discover course pages and derive order from the original README links."""
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote, urlsplit

from .markdown_view import compile_page, parse

LOG = logging.getLogger(__name__)
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


@dataclass
class Page:
    source: Path
    url: str
    title: str
    difficulty: str
    description: str
    module: str = ""
    kind: str = "lesson"
    html: str = ""
    outline: list = field(default_factory=list)
    sections: list = field(default_factory=list)
    questions: dict = field(default_factory=dict)


@dataclass
class Module:
    number: str
    slug: str
    index: Page
    lessons: list[Page]

    @property
    def progress_pages(self):
        return ([self.index] if self.index.questions else []) + self.lessons


class Course:
    def __init__(self, root):
        self.root = root.resolve()
        self.pages = {}
        self.by_source = {}
        self.modules = {}
        docs = {}
        self.overview = self._read(root / "README.md", "/network/course", "overview", "", docs)
        overview_links = self._local_links(self.overview, docs)
        directories = sorted(root.iterdir()) if root.is_dir() else []
        directories = [p for p in directories if p.is_dir() and
                       re.fullmatch(r"\d+-[a-z0-9-]+", p.name)]
        directories.sort(key=lambda p: (self._order(overview_links, p.name + "/README.md"), p.name))

        for directory in directories:
            number, slug = directory.name.split("-", 1)
            if not SLUG.fullmatch(slug) or slug in self.modules:
                continue
            url = f"/network/{slug}"
            index = self._read(directory / "README.md", url, "module", slug, docs)
            if not index:
                continue
            index.title = re.sub(r"^Module \d+\s+[—–-]\s+", "", index.title)
            link_order = self._local_links(index, docs)
            lessons = []
            for lesson in sorted(directory.glob("*.md"),
                                 key=lambda p: (self._order(link_order, p.name), p.name)):
                if lesson.name.lower() == "readme.md" or not SLUG.fullmatch(lesson.stem):
                    continue
                page = self._read(lesson, f"{url}/{lesson.stem}", "lesson", slug, docs)
                if page:
                    lessons.append(page)
            self.modules[slug] = Module(number, slug, index, lessons)

        for url, doc in docs.items():
            compile_page(self.pages[url], doc, self.by_source)
        self.sequence = [page for module in self.modules.values() for page in module.progress_pages]
        self.positions = {page.url: index for index, page in enumerate(self.sequence)}

    @staticmethod
    def _order(links, name):
        try:
            return links.index(name)
        except ValueError:
            return len(links)

    @staticmethod
    def _local_links(page, docs):
        if page is None:
            return []
        return [unquote(urlsplit(link["href"]).path) for link in docs[page.url].select("a[href]")]

    def _read(self, path, url, kind, module, docs):
        try:
            source = path.resolve().relative_to(self.root)
            doc = parse(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, ValueError):
            LOG.warning("Course source unavailable: %s", path.name)
            return None
        heading = doc.find("h1")
        title = heading.get_text(" ", strip=True) if heading else path.stem.replace("-", " ").title()
        quote = doc.find("blockquote")
        difficulty = ""
        if quote:
            match = re.match(r"Difficulty:\s*(.+?)(?:\s*\||$)", quote.get_text(" ", strip=True))
            if match:
                difficulty = match[1]
        paragraph = doc.find("p", recursive=False)
        description = paragraph.get_text(" ", strip=True) if paragraph else ""
        page = Page(source, url, title, difficulty, description, module, kind)
        self.by_source[source.as_posix()] = url
        self.pages[url] = page
        docs[url] = doc
        return page

    def navigate(self, page):
        position = self.positions.get(page.url)
        if position is None:
            return None, None
        previous = self.sequence[position - 1] if position else None
        following = self.sequence[position + 1] if position + 1 < len(self.sequence) else None
        return previous, following

    def search(self, query):
        terms = re.findall(r"[\w-]+", query.casefold())[:10]
        if not terms:
            return []
        results = []
        for page in self.pages.values():
            best = None
            title = page.title.casefold()
            for anchor, heading, body in page.sections:
                name, content = heading.casefold(), body.casefold()
                if not all(term in f"{title} {name} {content}" for term in terms):
                    continue
                score = sum(8 * (term in title) + 4 * (term in name) + (term in content)
                            for term in terms)
                if best is None or score > best[0]:
                    segments = re.split(r"(?<=[.!?])\s+", body)
                    snippet = max(segments, key=lambda part: sum(term in part.casefold() for term in terms))
                    best = (score, page, anchor, heading, snippet[:200] + ("…" if len(snippet) > 200 else ""))
            if best:
                results.append(best)
        return sorted(results, key=lambda item: -item[0])[:35]
