"""Real-browser course flow. Starts an isolated Flask server when BASE_URL is unset."""
import os
from pathlib import Path
import threading
import logging
import unittest

from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from network_yaoguai import ROOT, create_app


class BrowserFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        cls.server = None
        cls.base = os.environ.get("BASE_URL")
        if not cls.base:
            cls.server = make_server("127.0.0.1", 0, create_app(), threaded=True)
            cls.base = f"http://127.0.0.1:{cls.server.server_port}"
            threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.engine = sync_playwright().start()
        cls.browser = cls.engine.chromium.launch()
        cls.output = ROOT / ".test-runtime/screenshots"
        cls.output.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.engine.stop()
        if cls.server:
            cls.server.shutdown()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 1000},
                                               permissions=["clipboard-read", "clipboard-write"])
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on("console", lambda message: self.errors.append(message.text)
                     if message.type == "error" else None)

    def tearDown(self):
        self.context.close()

    def visit(self, path):
        response = self.page.goto(self.base + path)
        self.assertEqual(response.status, 200)
        self.page.wait_for_load_state("networkidle")
        self.page.evaluate("document.fonts.ready")

    def test_learning_flow(self):
        self.visit("/network")
        self.assertEqual(self.page.locator("[data-module-card]").count(), 8)
        self.assertIn("Start learning", self.page.locator("[data-resume]").inner_text())
        self.page.screenshot(path=str(self.output / "dashboard-desktop.png"), full_page=True)
        self.page.locator("[data-resume]").click()
        self.page.wait_for_load_state("networkidle")
        self.assertTrue(self.page.url.endswith("/networking-fundamentals/osi-model"))
        self.assertEqual(self.page.locator("details.solution[open]").count(), 0)
        solution = self.page.locator("details.solution")
        self.assertFalse(solution.locator("p").first.is_visible())

        form = self.page.locator('[data-grade="check-1"]')
        for control, value in zip(form.locator('input').all(), ["3", "2", "4", "frame"]):
            control.fill(value)
        form.locator("button").click()
        self.assert_status(form, "Correct.")
        form.locator("input").first.fill("7")
        form.locator("button").click()
        self.assert_status(form, "3/4 correct")
        self.assertEqual(form.locator('[aria-invalid="true"]').count(), 1)

        challenge = self.page.locator('[data-grade="flag-1"]')
        challenge.locator("input").fill("FLAG{wrong}")
        challenge.locator("button").click()
        self.assert_status(challenge, "Flag not accepted")
        challenge.locator("input").fill("FLAG{2-3}")
        challenge.locator("button").click()
        self.assert_status(challenge, "Flag accepted")
        self.assertEqual(self.page.locator("details.solution[open]").count(), 0)

        for activity, answers in (("check-2", ["1", "3", "2", "7"]), ("check-3", ["2", "3", "3/4"])):
            task_form = self.page.locator(f'[data-grade="{activity}"]')
            for control, value in zip(task_form.locator("input").all(), answers):
                control.fill(value)
            task_form.locator("button").click()
            self.assert_status(task_form, "Correct.")

        hints = self.page.locator(".hint").first
        hints.locator("summary").first.click()
        self.assertEqual(hints.locator(".hint-step").count(), 3)
        hints.locator(".hint-step summary").first.click()
        self.assertTrue(hints.locator(".hint-step[open]").is_visible())
        solution.locator("summary").click()
        self.assertTrue(solution.locator("p").first.is_visible())
        solution.locator("summary").click()

        self.assertEqual(self.page.locator("[data-complete]").count(), 0)
        self.page.reload()
        self.page.wait_for_load_state("networkidle")
        self.assertIn("1/34", self.page.locator("[data-progress-count]").inner_text())
        self.page.screenshot(path=str(self.output / "lesson-desktop.png"), full_page=True)
        self.page.locator('a[rel="next"]').click()
        self.assertTrue(self.page.url.endswith("tcp-ip-model"))
        self.page.goto(self.base + "/network")
        self.assertIn("Resume:", self.page.locator("[data-resume]").inner_text())

        self.visit("/network/search?q=EtherType")
        self.assertGreater(self.page.locator(".search-results li").count(), 0)
        result = self.page.locator(".search-results a").first
        destination = result.get_attribute("href")
        result.click()
        self.page.wait_for_url(self.base + destination)
        self.assertEqual(self.page.url, self.base + destination)

        self.visit("/network/nmap/host-discovery")
        block = self.page.locator(".terminal").first
        code = block.locator("pre").inner_text()
        block.locator("[data-copy]").click()
        clipboard = self.page.evaluate("navigator.clipboard.readText()")
        self.assertEqual(clipboard.replace("\r\n", "\n"), code)
        review = self.page.locator("[data-review]").first
        if review.count():
            review.click()
            self.assertEqual(review.get_attribute("aria-pressed"), "true")
        self.visit("/network/nmap/reading-results")
        radio_form = self.page.locator('[data-grade="check-1"]')
        radio_form.locator('input[type="radio"]').nth(1).check()
        radio_form.locator("button").click()
        self.assert_status(radio_form, "Correct.")
        self.assertEqual(self.errors, [])

    def assert_status(self, form, text):
        from playwright.sync_api import expect
        expect(form.locator("[role=status]")).to_contain_text(text)

    def test_mobile_and_all_pages(self):
        course = create_app().extensions["course"]
        for width in (375, 768, 1280):
            self.page.set_viewport_size({"width": width, "height": 900})
            for url in ["/network", *course.pages]:
                with self.subTest(width=width, url=url):
                    response = self.page.goto(self.base + url)
                    self.assertEqual(response.status, 200)
                    self.page.wait_for_load_state("networkidle")
                    self.assertLessEqual(self.page.evaluate("document.documentElement.scrollWidth"),
                                         width, url)
                    self.assertEqual(self.page.locator("details.solution[open]").count(), 0)
            self.visit("/network/nmap/port-scanning")
            self.page.screenshot(path=str(self.output / f"nmap-{width}.png"), full_page=True)
            if width <= 920:
                menu = self.page.locator("[data-course-menu]")
                self.assertFalse(menu.get_attribute("open") is not None)
                menu.locator("summary").first.click()
                self.assertTrue(menu.locator('a[href="/network/course"]').is_visible())
        self.assertEqual(self.errors, [])

    def test_storage_blocked_still_usable(self):
        self.context.add_init_script("""
            Object.defineProperty(window, 'localStorage', {
              get() { throw new Error('Storage blocked'); }
            });
        """)
        self.visit("/network/networking-fundamentals/osi-model")
        self.assertEqual(self.page.locator("[data-complete]").count(), 0)
        self.assertTrue(self.page.locator("article.markdown").is_visible())
        self.assertEqual(self.errors, [])


if __name__ == "__main__":
    unittest.main()
