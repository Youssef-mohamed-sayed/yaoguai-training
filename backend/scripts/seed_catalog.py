"""Import stable course IDs from the preserved source trees into the catalog."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import select

from app import create_app
from app.extensions import db
from app.models import LearningActivity, Module, Platform

COURSES = {
    "network": ("Yaoguai Network", "Networking concepts, protocols, analysis, and challenges", "network-essentials"),
    "linux": ("Yaoguai Linux", "Linux command line, administration, and practical security skills", "linux-essentials"),
    "programming": ("Yaoguai Programming", "Python foundations, problem solving, automation, and security scripting", "python-essentials"),
}


def heading(path):
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    match = re.search(r"^#\s+(.+?)\s*#*\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else path.stem.replace("-", " ").title()


def collect_markdown(slug, content_root):
    if slug == "network":
        import sys
        sys.path.insert(0, str(ROOT / "platforms" / "network"))
        from network_yaoguai import Course
        course = Course(content_root)
        rows = []
        for module_order, module in enumerate(course.modules.values(), 1):
            module_id = f"network/{module.slug}"
            module_pages = ([module.index] if module.index.questions else []) + module.lessons
            for page_order, page in enumerate(module_pages, 1):
                suffix = page.url.removeprefix("/network/")
                lesson_id = f"network/{suffix}"
                rows.append((module_id, module.index.title, lesson_id, page_order * 100,
                             str(page.source), "lesson", ""))
                for question_order, question_id in enumerate(page.questions, 1):
                    exercise_id = f"{lesson_id}/exercise/{question_id}"
                    rows.append((module_id, module.index.title, exercise_id,
                                 page_order * 100 + question_order, str(page.source), "exercise", ""))
        return rows
    entries = []
    for module_path in sorted((content_root / ".." / content_root.name).iterdir(), key=lambda p: p.name):
        if not module_path.is_dir():
            continue
        module_files = sorted((p for p in module_path.rglob("*.md") if p.name.lower() != "readme.md"), key=lambda p: p.as_posix())
        if not module_files:
            continue
        module_key = f"{slug}/{module_path.name}"
        entries.append((module_key, heading(module_path / "README.md") if (module_path / "README.md").exists() else module_path.name.replace("-", " ").title(),
                        "", 0, "", "", ""))
        for i, lesson in enumerate(module_files, 1):
            rel = lesson.relative_to(content_root / ".." / content_root.name).with_suffix("").as_posix()
            title = heading(lesson)
            kind = "challenge" if "challenge" in rel.lower() or "ctf" in rel.lower() else "exercise" if "exercise" in rel.lower() else "lesson"
            activity_id = f"{slug}/{rel}"
            entries.append((module_key, title, activity_id, i, lesson.as_posix(), kind, ""))
    return entries


def crypto_entries():
    slug = "crypto"
    source = ROOT / "platforms" / slug
    registry = (source / "public/js/registry.js").read_text(encoding="utf-8-sig", errors="replace")
    pattern = re.compile(r'\{\s*id\s*:\s*"([^"]+)"\s*,\s*order\s*:\s*(\d+)\s*,\s*category\s*:\s*"([^"]+)"\s*,\s*title\s*:\s*"([^"]+)"')
    entries = []
    for activity_id, order, category, title in pattern.findall(registry):
        module_id = f"crypto/{category}"
        entries.append((module_id, category.title(), f"crypto/{activity_id}", int(order), title, "lesson", ""))
    if not entries:
        raise RuntimeError("Crypto registry format changed; refusing to seed an empty catalog")
    return entries


def main():
    app = create_app()
    with app.app_context():
        all_entries = {}
        for slug, (name, description, root_name) in COURSES.items():
            course_root = ROOT / "platforms" / slug / root_name
            if not course_root.exists():
                raise FileNotFoundError(course_root)
            all_entries[slug] = (name, description, collect_markdown(slug, course_root))
        all_entries["crypto"] = ("Yaoguai Crypto", "Cryptography, encryption, hashing, encoding, and applied challenges", crypto_entries())
        with db.session.begin():
            platform_by_id = {row.id: row for row in db.session.execute(select(Platform)).scalars()}
            module_by_id = {row.id: row for row in db.session.execute(select(Module)).scalars()}
            activity_by_id = {row.id: row for row in db.session.execute(select(LearningActivity)).scalars()}
            for order, (slug, (name, description, rows)) in enumerate(all_entries.items(), 1):
                platform = platform_by_id.get(slug)
                if not platform:
                    platform = Platform(id=slug, name=name, description=description, sort_order=order)
                    db.session.add(platform)
                else:
                    platform.name, platform.description, platform.sort_order = name, description, order
                module_meta = {}
                for module_id, module_title, activity_id, item_order, source, kind, _unused in rows:
                    module_meta[module_id] = module_title
                    if not activity_id:
                        continue
                    title = module_title if source == "" else (Path(source).stem.replace("-", " ").title() if kind == "challenge" else module_title)
                    if source and slug == "crypto":
                        title = source
                    elif source:
                        source_path = Path(source)
                        if not source_path.is_absolute():
                            source_path = ROOT / "platforms" / slug / ("network-essentials" if slug == "network" else root_name) / source_path
                        title = heading(source_path)
                    module = module_by_id.get(module_id)
                    if not module:
                        module = Module(id=module_id, platform_id=slug,
                                        title=module_title, sort_order=len(module_meta) - 1)
                        module_by_id[module_id] = module
                        db.session.add(module)
                    activity = activity_by_id.get(activity_id)
                    if activity:
                        activity.title, activity.sort_order = title, item_order
                        activity.activity_type = kind
                        activity.min_read_seconds = 15 if kind == "lesson" else 0
                        continue
                    stable_key = activity_id[:160]
                    activity = LearningActivity(id=activity_id, module_id=module_id,
                                                stable_key=stable_key, title=title,
                                                activity_type=kind, sort_order=item_order,
                                                is_required=True,
                                                min_read_seconds=15 if kind == "lesson" else 0)
                    activity_by_id[activity_id] = activity
                    db.session.add(activity)
                for module_id, module_title in module_meta.items():
                    module = module_by_id.get(module_id)
                    if not module:
                        module = Module(id=module_id, platform_id=slug,
                                        title=module_title, sort_order=len(module_meta))
                        db.session.add(module)
                    else:
                        module.title = module_title
        counts = db.session.execute(select(Platform.id,)).all()
        print(f"Catalog seeded for {len(all_entries)} platforms ({len(counts)} total platforms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

