#!/usr/bin/env python3
"""
Validator for the Complete List of AI GitHub repository.

Verifies:
1. All Markdown tables in README.md have consistent column counts (zero broken pipes).
2. All numbered AI category tables use the standard 7-column schema.
3. ZERO duplicate AI Names across the entire directory (global uniqueness).
4. ZERO duplicate canonical URLs across the entire directory (global uniqueness).
5. Top summary badge and Directory Statistics counts match actual table rows.
6. All #anchor links and relative file links resolve cleanly.
7. All external links use HTTPS and contain no affiliate/referral parameters.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_CATEGORY_COLS = [
    "AI Name",
    "Creator",
    "What It Does & Key Features",
    "Best For",
    "Free Plan",
    "Pricing",
    "Platforms",
]
FORBIDDEN_QUERY_PARAMS = ("ref=", "aff=", "affiliate=", "utm_source=", "via=", "fpr=")


def github_slugify(heading: str) -> str:
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return s.replace(" ", "-")


def split_md_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def normalize_url(url: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", url.strip().lower()).rstrip("/")


def main() -> int:
    readme = ROOT / "README.md"
    if not readme.exists():
        print("❌ Missing README.md", file=sys.stderr)
        return 1

    lines = readme.read_text(encoding="utf-8").splitlines()
    errors: list[str] = []
    headings: set[str] = set()
    current_heading = ""
    is_numbered_category = False
    expected_cols: int | None = None

    global_seen_names: dict[str, str] = {}
    global_seen_roots: dict[str, tuple[str, str]] = {}
    global_seen_urls: dict[str, tuple[str, str]] = {}

    ai_entry_count = 0
    free_entry_count = 0
    category_count = 0

    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()

        m_head = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if m_head:
            current_heading = m_head.group(2).strip()
            headings.add(github_slugify(current_heading))
            is_numbered_category = bool(re.match(r"^\d+\.\s+", current_heading))
            if is_numbered_category:
                category_count += 1

        if stripped.startswith("|") and stripped.endswith("|"):
            cols = split_md_row(stripped)
            if expected_cols is None:
                expected_cols = len(cols)
                if is_numbered_category and cols != EXPECTED_CATEGORY_COLS:
                    errors.append(
                        f"Line {lineno} ({current_heading}): header {cols} != expected {EXPECTED_CATEGORY_COLS}"
                    )
            else:
                if len(cols) != expected_cols:
                    errors.append(
                        f"Line {lineno} ({current_heading}): expected {expected_cols} columns, got {len(cols)}"
                    )
                if not all(re.match(r"^:?-{2,}:?$", c) for c in cols):
                    if is_numbered_category:
                        ai_entry_count += 1
                        m_cell = re.match(r"^\[([^\]]+)\]\(([^)]+)\)$", cols[0])
                        if not m_cell:
                            errors.append(
                                f"Line {lineno} ({current_heading}): AI Name cell must be [Name](https://...): {cols[0]}"
                            )
                        else:
                            ai_name, ai_url = m_cell.group(1).strip(), m_cell.group(2).strip()
                            norm_name = ai_name.lower()
                            if norm_name in global_seen_names:
                                errors.append(
                                    f"Line {lineno}: Global duplicate AI Name '{ai_name}' in '{current_heading}' "
                                    f"(already in '{global_seen_names[norm_name]}')"
                                )
                            global_seen_names[norm_name] = current_heading

                            root_name = re.sub(r"\(.*?\)", "", norm_name).strip()
                            root_name = re.sub(r"\s+ai$", "", root_name).strip()
                            if root_name in global_seen_roots:
                                prev_name, prev_cat = global_seen_roots[root_name]
                                errors.append(
                                    f"Line {lineno}: Global duplicate brand '{ai_name}' in '{current_heading}' "
                                    f"(conflicts with '{prev_name}' in '{prev_cat}')"
                                )
                            global_seen_roots[root_name] = (ai_name, current_heading)

                            norm_u = normalize_url(ai_url)
                            if norm_u in global_seen_urls:
                                prev_name, prev_cat = global_seen_urls[norm_u]
                                errors.append(
                                    f"Line {lineno}: Global duplicate URL '{ai_url}' for '{ai_name}' "
                                    f"(already used by '{prev_name}' in '{prev_cat}')"
                                )
                            global_seen_urls[norm_u] = (ai_name, current_heading)

                        free_cell = cols[4].lower().strip()
                        if free_cell.startswith("yes") or free_cell.startswith("free") or "open-source" in free_cell or "open-weight" in free_cell:
                            free_entry_count += 1
        else:
            expected_cols = None

        for m_link in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", stripped):
            target = m_link.group(2).strip()
            if target.startswith("http://"):
                errors.append(f"Line {lineno}: insecure http:// URL {target!r} (use https://)")
            elif target.startswith("https://"):
                low = target.lower()
                if any(p in low for p in FORBIDDEN_QUERY_PARAMS):
                    errors.append(f"Line {lineno}: affiliate/tracking parameter detected in {target!r}")
            elif not target.startswith("#"):
                rel = (ROOT / target.lstrip("./")).resolve()
                if not rel.exists():
                    errors.append(f"Line {lineno}: broken relative file link {target!r}")

    for lineno, raw in enumerate(lines, start=1):
        for m_anchor in re.finditer(r"\[([^\]]+)\]\(#([^)]+)\)", raw):
            slug = m_anchor.group(2).strip()
            if slug not in headings:
                errors.append(f"Line {lineno}: broken #anchor link '#{slug}'")

    full_text = "\n".join(lines)
    m_badge = re.search(
        r"`Total Unique AIs:\s*(\d+)`\s*·\s*`Categories:\s*(\d+)`\s*·\s*`Free / Open-Source:\s*(\d+)\s*\([^)]+\)`",
        full_text,
    )
    if not m_badge:
        errors.append("Missing or malformed top summary badge line in README.md")
    else:
        b_total, b_cats, b_free = map(int, m_badge.groups())
        if b_total != ai_entry_count:
            errors.append(f"Badge Total Unique AIs ({b_total}) != actual row count ({ai_entry_count})")
        if b_cats != category_count:
            errors.append(f"Badge Categories ({b_cats}) != actual category count ({category_count})")
        if b_free != free_entry_count:
            errors.append(f"Badge Free/Open-Source ({b_free}) != actual free count ({free_entry_count})")

    m_stat_total = re.search(r"\|\s*\*\*Total Unique AIs Listed\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|", full_text)
    if not m_stat_total or int(m_stat_total.group(1)) != ai_entry_count:
        errors.append("Directory Statistics 'Total Unique AIs Listed' does not match actual row count")

    if errors:
        print("❌ Validation failed:\n", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("✅ Complete List of AI validation passed!")
    print(f"   • AI Categories       : {category_count}")
    print(f"   • Total Unique AIs    : {ai_entry_count}")
    print(f"   • Free / Open-Source  : {free_entry_count} ({free_entry_count / ai_entry_count * 100:.1f}%)")
    print("   • Global Duplicates   : 0 (Names, Brands & URLs verified unique)")
    print("   • Tables & Links      : 100% valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
