from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from scripts.seed_catalog import collect_markdown, crypto_entries


def test_actual_python_and_network_course_files_are_discovered():
    python_root = ROOT / "platforms" / "programming" / "python-essentials"
    network_root = ROOT / "platforms" / "network" / "network-essentials"
    python_rows = collect_markdown("programming", python_root)
    network_rows = collect_markdown("network", network_root)
    assert python_rows and network_rows
    python_ids = {row[2] for row in python_rows if row[2]}
    assert any(item.startswith("programming/") for item in python_ids)
    assert all(not item.endswith(".md") for item in python_ids)
    network_ids = {row[2] for row in network_rows if row[2]}
    assert any("/exercise/" in item for item in network_ids)
    assert all(item.startswith("network/") for item in network_ids)


def test_all_four_imported_platforms_have_catalog_activities():
    roots = {
        "linux": ROOT / "platforms" / "linux" / "linux-essentials",
        "programming": ROOT / "platforms" / "programming" / "python-essentials",
    }
    rows = {slug: collect_markdown(slug, source) for slug, source in roots.items()}
    rows["crypto"] = crypto_entries()
    for slug, activities in rows.items():
        ids = {row[2] for row in activities if row[2]}
        assert ids, f"{slug} has no discoverable activities"
        assert all(activity_id.startswith(f"{slug}/") for activity_id in ids)
    assert len(rows["linux"]) > 40
    assert len(rows["programming"]) > 40
    assert len(rows["crypto"]) == 16
