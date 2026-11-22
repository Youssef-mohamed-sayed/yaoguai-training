"""Course-wide integration, content fidelity and security checks."""
import hashlib
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from network_yaoguai import ROOT, create_app
from network_yaoguai.course import Page
from network_yaoguai.markdown_view import MD, compile_page, parse
from app import create_app as create_central_app


class PlatformTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        central = create_central_app({
            "TESTING": True,
            "SECRET_KEY": "network-test-central-secret-with-sufficient-entropy",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "WTF_CSRF_ENABLED": False,
            "SESSION_COOKIE_SECURE": False,
        })
        cls.app = create_app({
            "TESTING": True,
            "CENTRAL_SECRET_KEY": central.secret_key,
            "CENTRAL_SESSION_INTERFACE": central.session_interface,
            "CENTRAL_DATABASE_URI": central.config["SQLALCHEMY_DATABASE_URI"],
            "CENTRAL_COOKIE_SECURE": False,
            "WTF_CSRF_ENABLED": False,
        })
        cls.course = cls.app.extensions["course"]
        cls.client = cls.app.test_client()

    def test_source_content_is_unchanged(self):
        baseline = json.loads((ROOT / "tests/content-sha256.json").read_text())
        for filename, digest in baseline.items():
            self.assertEqual(hashlib.sha256((ROOT / filename).read_bytes()).hexdigest(), digest, filename)

    def test_every_markdown_page_is_indexed_and_loads(self):
        files = {p.relative_to(self.course.root) for p in self.course.root.rglob("*.md")}
        self.assertEqual(files, {p.source for p in self.course.pages.values()})
        for page in self.course.pages.values():
            with self.subTest(page=page.url):
                response = self.client.get(page.url)
                self.assertEqual(response.status_code, 200)
                self.assertIn(page.title, BeautifulSoup(response.data, "html.parser").h1.text)

    def test_dashboard_and_aliases(self):
        for url in ("/", "/network", "/network/course", "/network/challenges"):
            self.assertEqual(self.client.get(url, follow_redirects=True).status_code, 200)
        doc = BeautifulSoup(self.client.get("/network").data, "html.parser")
        self.assertEqual(len(doc.select("[data-module-card]")), 8)
        self.assertEqual(len(self.course.sequence), 34)

    def test_readme_order_and_device_overview(self):
        first = self.course.modules["networking-fundamentals"]
        self.assertEqual([p.source.stem for p in first.lessons],
                         ["osi-model", "tcp-ip-model", "osi-vs-tcpip", "encapsulation"])
        devices = self.course.modules["network-devices"]
        self.assertIn(devices.index, devices.progress_pages)
        self.assertEqual(devices.index.questions["flag-1"].fields[0][1],
                         ("FLAG{firewall_switch}",))

    def test_all_internal_links_and_anchors(self):
        for page in self.course.pages.values():
            document = BeautifulSoup(self.client.get(page.url).data, "html.parser")
            for link in document.select("a[href]"):
                target = urlsplit(link["href"])
                if target.scheme or target.netloc:
                    continue
                with self.subTest(page=page.url, target=link["href"]):
                    path = target.path or page.url
                    response = self.client.get(path, follow_redirects=True)
                    self.assertEqual(response.status_code, 200)
                    self.assertFalse(target.path.endswith(".md"))
                    if target.fragment:
                        destination = BeautifulSoup(response.data, "html.parser")
                        self.assertIsNotNone(destination.find(id=target.fragment))

    def test_source_blocks_disclosures_and_text_are_preserved(self):
        for page in self.course.pages.values():
            source = (self.course.root / page.source).read_text("utf-8")
            before = parse(source)
            after = BeautifulSoup(page.html, "html.parser")
            with self.subTest(page=page.url):
                self.assertEqual([code.get_text() for code in before.select("pre code")],
                                 [code.get_text() for code in after.select("pre code")])
                self.assertEqual(len(before.find_all("table")), len(after.find_all("table")))
                for generated in after.select(".hint-step > summary, .terminal-bar"):
                    generated.decompose()
                for details in before.find_all("details"):
                    text = " ".join(details.get_text(" ", strip=True).split())
                    self.assertIn(text, " ".join(after.get_text(" ", strip=True).split())
                                  .replace("Hint 1 ", "").replace("Hint 2 ", "").replace("Hint 3 ", ""))
                for heading in before.find_all(re.compile(r"^h[2-6]$")):
                    self.assertIn(heading.get_text(" ", strip=True), after.get_text(" ", strip=True))

    def test_solutions_closed_and_flags_not_in_form_attributes(self):
        for page in self.course.pages.values():
            doc = BeautifulSoup(page.html, "html.parser")
            for node in doc.select("details"):
                self.assertFalse(node.has_attr("open"))
            for form in doc.select("[data-grade]"):
                self.assertNotIn("FLAG{", str(form))
        self.assertEqual(sum(q.kind == "challenge" for p in self.course.pages.values()
                             for q in p.questions.values()), 35)

    def test_navigation_is_contiguous(self):
        for position, page in enumerate(self.course.sequence):
            previous, following = self.course.navigate(page)
            self.assertEqual(previous, self.course.sequence[position - 1] if position else None)
            self.assertEqual(following, self.course.sequence[position + 1]
                             if position < len(self.course.sequence) - 1 else None)

    def test_every_answer_key_accepts_correct_and_rejects_wrong(self):
        for page in self.course.pages.values():
            for key, question in page.questions.items():
                with self.subTest(page=page.url, activity=key):
                    payload = {"page": page.url, "activity": key,
                               "answers": [accepted[0] for _, accepted in question.fields]}
                    response = self.client.post("/network/check", json=payload)
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(response.json["correct"])
                    payload["answers"] = ["wrong answer"] * len(question.fields)
                    self.assertFalse(self.client.post("/network/check", json=payload).json["correct"])
                    payload["answers"] = []
                    self.assertEqual(self.client.post("/network/check", json=payload).status_code, 400)

    def test_check_rejects_malformed_and_unknown_inputs(self):
        for payload in ([], None, {"page": []}, {"page": "x", "activity": {}}):
            self.assertEqual(self.client.post("/network/check", json=payload).status_code, 400)
        self.assertEqual(self.client.post("/network/check",
                                         json={"page": "missing", "activity": "x"}).status_code, 404)
        response = self.client.post("/network/check", data="x" * 5000,
                                    content_type="application/json")
        self.assertEqual(response.status_code, 413)

    def test_flags_and_case_sensitive_commands_are_exact(self):
        url = "/network/nmap/service-detection"
        self.assertFalse(self.client.post("/network/check", json={
            "page": url, "activity": "check-2", "answers": ["-sv", "-o"]}).json["correct"])
        self.assertTrue(self.client.post("/network/check", json={
            "page": url, "activity": "check-2", "answers": ["-sV", "-O"]}).json["correct"])

    def test_search_is_actual_content_without_solution_spoilers(self):
        for query in ("TCP", "DNS", "ARP", "Nmap", "Wireshark", "subnetting", "CAM", "EtherType"):
            self.assertTrue(self.course.search(query), query)
            self.assertEqual(self.client.get("/network/search", query_string={"q": query}).status_code, 200)
        self.assertEqual(self.course.search("n3tw0rk_r3c0n_m4st3r"), [])
        response = self.client.get("/network/search?q=%3Cscript%3Ealert(1)%3C/script%3E")
        self.assertNotIn(b"<script>alert(1)</script>", response.data)

    def test_markdown_features_and_sanitization(self):
        source = """# Fixture
## Heading
### Subheading
#### Four
##### Five
###### Six
**Bold**, *italic*, ~~struck~~ and §inline§.

> Quote

- [ ] Checklist
- [x] Completed

| Field | Value |
|---|---|
| Source IP | 10.0.0.1 |

§§§text
PC -- Switch -- Router
  SYN --------->
§§§

<details>
<summary>Show Solution</summary>

**Preserved inside disclosure**

</details>

<script>alert(1)</script>
<img src="x" onerror="alert(1)">
<a href="javascript:alert(1)">Unsafe</a>
""".replace("§", chr(96))
        page = Page(Path("fixture.md"), "/fixture", "Fixture", "", "")
        doc = parse(source)
        compile_page(page, doc, {})
        result = BeautifulSoup(page.html, "html.parser")
        self.assertIsNotNone(result.find("h6"))
        self.assertIsNotNone(result.select_one(".table-scroll table"))
        self.assertEqual(len(result.select("input[type=checkbox]")), 2)
        self.assertIn("  SYN --------->", result.pre.text)
        self.assertIsNotNone(result.select_one("details strong"))
        self.assertFalse(result.select("script, [onerror], [onclick]"))
        self.assertNotIn("javascript:", page.html)

    def test_assets_and_security_headers(self):
        for asset in (ROOT / "public").rglob("*"):
            if asset.is_file():
                path = "/" + asset.relative_to(ROOT / "public").as_posix()
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200, path)
                response.close()
        response = self.client.get("/network")
        self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])
        self.assertFalse(self.app.debug)

    def test_errors_do_not_disclose_paths(self):
        for url in ("/unknown", "/network/no-such-module", "/network/nmap/absent",
                    "/network/nmap/../../main.py", "/assets/../../main.py",
                    "/assets/missing.css"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
            self.assertNotIn(b"Traceback", response.data)
            self.assertNotIn(b"D:\\", response.data)

    def test_missing_sources_fail_safely(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            shutil.copytree(self.course.root, path / "course")
            isolated = create_app({"TESTING": True, "CONTENT_ROOT": path / "course"})
            course = isolated.extensions["course"]
            page = next(iter(course.sequence))
            (course.root / page.source).unlink()
            self.assertEqual(isolated.test_client().get(page.url).status_code, 404)
        with tempfile.TemporaryDirectory() as folder:
            isolated = create_app({"TESTING": True, "CONTENT_ROOT": Path(folder)})
            self.assertEqual(isolated.test_client().get("/network").status_code, 200)

    def test_deployment_manifest(self):
        config = json.loads((ROOT / "vercel.json").read_text())
        self.assertEqual(config["framework"], "flask")
        self.assertIn("main.py", config["functions"])
        self.assertTrue((ROOT / "main.py").is_file())
        self.assertEqual((ROOT / ".python-version").read_text().strip(), "3.13")


if __name__ == "__main__":
    unittest.main()
