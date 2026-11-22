"""Render course Markdown, including the source's native disclosures and activities."""
import posixpath
import re
import unicodedata
from collections import Counter
from urllib.parse import unquote, urlsplit

import nh3
from bs4 import BeautifulSoup, NavigableString, Tag
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from .exercises import CHECKS, CHOICES, Question

HEADINGS = re.compile(r"^h[1-6]$")
MD = MarkdownIt("commonmark", {"html": True, "breaks": True}).enable(["table", "strikethrough"])
CLEAN = nh3.Cleaner(
    tags=set("h1 h2 h3 h4 h5 h6 p br strong em s del blockquote ol ul li table thead "
             "tbody tr th td a img pre code hr details summary".split()),
    attributes={"a": {"href", "title"}, "img": {"src", "alt", "title"},
                "ol": {"start"}, "code": {"class"}},
    clean_content_tags={"script", "style", "iframe", "object", "template", "svg", "math"},
    url_schemes={"http", "https", "mailto"},
)
ACTIVITY = re.compile(r"^(?:\d+\.\s*)?(?:mini task|hands-on|exercise|practice|check understanding)", re.I)
CHALLENGE = re.compile(r"\bctf challenge\b|\bbonus challenge\b", re.I)
FLAG = re.compile(r"\bFlag:\s*`(FLAG\{[^{}\r\n]+\})`", re.I)


def parse(source):
    return BeautifulSoup(CLEAN.clean(MD.render(source)), "html.parser")


def make(doc, tag_name, label=None, **attrs):
    node = doc.new_tag(tag_name, attrs=attrs)
    if label is not None:
        node.string = label
    return node


def slug(title):
    value = unicodedata.normalize("NFKC", title).casefold().strip()
    value = "".join(ch for ch in value if ch.isalnum() or ch in "-_ ")
    return re.sub(r"[ -]+", "-", value).strip("-") or "section"


def rewrite_links(doc, page, paths):
    for link in doc.select("a[href]"):
        parts = urlsplit(link["href"])
        raw_path = unquote(parts.path)
        if parts.netloc or parts.scheme or not raw_path.lower().endswith(".md"):
            continue
        target = posixpath.normpath(posixpath.join(page.source.parent.as_posix(), raw_path))
        if target in paths:
            link["href"] = paths[target] + ("#" + parts.fragment if parts.fragment else "")
        else:
            link["href"] = "/network/missing-content"
            link["title"] = "This course link points to an unavailable Markdown page."


def organize(doc, page):
    """Build nested section cards and index visible text before adding controls."""
    primary_heading = doc.find("h1", recursive=False)
    used = Counter()
    stack = [(1, doc)]
    anchor, heading, prose = "", page.title, []
    for node in list(doc.children):
        if isinstance(node, Tag) and HEADINGS.fullmatch(node.name):
            level = int(node.name[1])
            if node is primary_heading:
                node.extract()
                continue
            title = node.get_text(" ", strip=True)
            if prose:
                page.sections.append((anchor, heading, " ".join(prose)))
            anchor, heading, prose = slug(title), title, []
            used[anchor] += 1
            if used[anchor] > 1:
                anchor = f"{anchor}-{used[anchor]}"
            node["id"] = anchor
            if level <= 3:
                page.outline.append((anchor, title, level))
            while len(stack) > 1 and stack[-1][0] >= level:
                stack.pop()
            style = "lsec"
            if CHALLENGE.search(title):
                style += " ctf"
            elif ACTIVITY.match(title):
                style += " task"
            section = make(doc, "section", **{"class": style, "aria-labelledby": anchor})
            stack[-1][1].append(section)
            section.append(node.extract())
            stack.append((level, section))
        else:
            if isinstance(node, Tag) and node.name != "details":
                prose.append(node.get_text(" ", strip=True))
            if stack[-1][1] is not doc:
                stack[-1][1].append(node.extract())
    page.sections.append((anchor, heading, " ".join(prose)))
    if not any(not key for key, _, _ in page.sections):
        page.sections.insert(0, ("", page.title, page.description))


def decorate_blocks(doc):
    for table in doc.find_all("table"):
        wrapper = make(doc, "div", **{"class": "table-scroll", "tabindex": "0",
                                      "role": "region", "aria-label": "Scrollable table"})
        table.wrap(wrapper)
        for header in table.select("thead th"):
            header["scope"] = "col"

    for pre in doc.find_all("pre"):
        code = pre.find("code")
        if not code:
            continue
        language = next((part[9:] for part in code.get("class", []) if part.startswith("language-")), "text")
        labels = {"bash": "Bash", "cmd": "Windows CMD", "text": "Text"}
        if language != "text":
            try:
                lexer = get_lexer_by_name(language, stripnl=False, ensurenl=False)
                highlighted = highlight(code.get_text(), lexer, HtmlFormatter(nowrap=True))
                fragment = BeautifulSoup(highlighted, "html.parser")
                if fragment.get_text() == code.get_text():
                    code.clear()
                    for child in list(fragment.contents):
                        code.append(child.extract())
            except ClassNotFound:
                pass
        wrapper = make(doc, "div", **{"class": "terminal"})
        pre.wrap(wrapper)
        pre["class"] = "code"
        pre["tabindex"] = "0"
        pre["aria-label"] = "Scrollable code or output"
        bar = make(doc, "div", **{"class": "terminal-bar"})
        pre.insert_before(bar)
        bar.append(make(doc, "span", labels.get(language, language)))
        bar.append(make(doc, "button", "Copy", type="button",
                        **{"class": "copy", "data-copy": "", "hidden": "", "aria-label": "Copy code"}))

    for item in doc.find_all("li"):
        body = item.find("p", recursive=False) or item
        first = body.contents[0] if body.contents else None
        match = re.match(r"^\[([ xX])\]\s+", str(first)) if isinstance(first, NavigableString) else None
        if match:
            first.replace_with(str(first)[match.end():])
            checked = match[1].lower() == "x"
            attrs = {"type": "checkbox", "disabled": "", "aria-label": "Checklist item"}
            if checked:
                attrs["checked"] = ""
            body.insert(0, make(doc, "input", **attrs))
            item["class"] = "checklist-item"


def answer_form(doc, question):
    form = make(doc, "form", **{"class": "answer-form", "data-grade": question.id,
                               "data-kind": question.kind, "hidden": ""})
    for index, (label, _) in enumerate(question.fields):
        field_id = f"field-{question.id}-{index}"
        if question.choices:
            fieldset = make(doc, "fieldset", **{"class": "mc-opts"})
            fieldset.append(make(doc, "legend", label))
            for choice in question.choices:
                option = make(doc, "label", **{"class": "mc-opt"})
                option.append(make(doc, "input", type="radio", name=f"answer-{index}",
                                   value=choice, required=""))
                option.append(NavigableString(f" {choice}"))
                fieldset.append(option)
            form.append(fieldset)
        else:
            form.append(make(doc, "label", label, **{"for": field_id}))
            form.append(make(doc, "input", type="text", name=f"answer-{index}", id=field_id,
                             maxlength="256", required="", autocomplete="off", spellcheck="false"))
    form.append(make(doc, "button", "Submit flag" if question.kind == "challenge" else "Check answer",
                     type="submit", **{"class": "btn btn-primary btn-sm"}))
    form.append(make(doc, "p", **{"class": "task-fb", "role": "status"}))
    return form


def self_check(doc, activity_id, label="Mark exercise practiced"):
    return make(doc, "button", label, type="button",
                **{"data-review": activity_id, "aria-pressed": "false",
                   "class": "btn btn-ghost btn-sm review", "hidden": ""})


def decorate_activities(doc, page):
    checks = solutions = practice = 0
    for details in list(doc.find_all("details")):
        summary = details.find("summary", recursive=False)
        if not summary:
            continue
        title = summary.get_text(" ", strip=True).casefold()
        if "hint" in title:
            details["class"] = "disclosure hint"
            for number, item in enumerate(details.select(":scope > ul > li"), 1):
                step = make(doc, "details", **{"class": "hint-step"})
                step.append(make(doc, "summary", f"Hint {number}"))
                for node in list(item.contents):
                    step.append(node.extract())
                item.append(step)
        elif "solution" in title:
            details["class"] = "disclosure solution"
            solutions += 1
            # Prefer a code span explicitly introduced as the flag, even when the explanation precedes it.
            for code in details.find_all("code"):
                token = code.get_text()
                if not re.fullmatch(r"FLAG\{[^{}\r\n]+\}", token):
                    continue
                link_text = code.parent.get_text(" ", strip=True)
                if not FLAG.search(link_text.replace(token, chr(96) + token + chr(96), 1)):
                    continue
                key = f"flag-{solutions}"
                question = Question(key, (("Flag", (token,)),), kind="challenge")
                page.questions[key] = question
                # Keep the answer box before hints, even when headings separate hints from solution.
                host = details
                parent = details.find_parent("section")
                if parent and page.module == "final-challenges":
                    task_section = doc.select_one('section[aria-labelledby="task"]')
                    if task_section:
                        task_section.append(answer_form(doc, question))
                        break
                prior = details.find_previous_sibling("details", class_="hint")
                (prior or host).insert_before(answer_form(doc, question))
                break
        elif "check" in title or "answer" in title:
            details["class"] = "disclosure explanation"
            checks += 1
            key = (page.url, checks)
            if key in CHECKS:
                question = Question(f"check-{checks}", CHECKS[key], choices=CHOICES.get(key, ()))
                page.questions[question.id] = question
                details.insert_before(answer_form(doc, question))
            else:
                details.insert_after(self_check(doc, f"review-{checks}"))

    for section in doc.select("section.task"):
        if section.select_one(".explanation, .solution, [data-grade], [data-review]"):
            continue
        heading = section.find(HEADINGS, recursive=False)
        if heading and ACTIVITY.match(heading.get_text(" ", strip=True)):
            practice += 1
            section.append(self_check(doc, f"practice-{practice}"))


def compile_page(page, doc, paths):
    rewrite_links(doc, page, paths)
    organize(doc, page)
    decorate_blocks(doc)
    decorate_activities(doc, page)
    page.html = str(doc)
