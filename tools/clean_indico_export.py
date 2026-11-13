#!/usr/bin/env python3
"""Turn an Indico "offline website" export into a static site for GitHub Pages.

The script copies the export to OUT_SITE, except the attachments under
``material/``. These are copied to OUT_ASSETS with unique, URL-safe names so
they can be uploaded as GitHub Release assets, and their links are rewritten to
the release download URLs. It also removes the parts of the Indico pages that
make no sense in a static archive (registration section, links to pages that
are not part of the export, login/timezone/language widgets) and adds a link
back to the list of all workshop editions.

Only the Python standard library is used. Usage example:

    python3 tools/clean_indico_export.py \
        /scratch/.../OfflineWebsite-Workshop_... docs/workshops/2026-03 \
        /scratch/.../release-assets --release-tag workshop-2026-03

At the end, a report lists remaining local links that do not resolve and
absolute site-rooted links (``/...``). The script exits with status 1 if there
are any.
"""

import argparse
import html
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

DEFAULT_REPO = "iterorganization/IMAS-Data-Mapping"

# Header of non-conference pages (e.g. author details): Indico toolbar with
# home/category/management buttons, timezone and language selectors, login.
GENERIC_HEADER_RE = re.compile(
    r'<div class="header">\s*.*?</header>\s*</div>\s*(?=<main)', re.S)
FOOTER_RE = re.compile(r'<footer class="footer\s*">.*?</footer>\s*', re.S)
# "Registration" section of the event description: heading and everything up
# to the next heading or the end of the description block.
REG_SECTION_RE = re.compile(
    r'<h([1-6])>\s*Registration\s*</h\1>.*?(?=<h[1-6][ >]|\s*</div>)', re.S | re.I)
# Same section in the plain-text copies of the description (ld+json, meta).
REG_TEXT_RE = re.compile(r'\s*Registration Registration is[^"]*?(?=")')
LOGIN_TITLE_RE = re.compile(r'\s*title="Log in to see their email address"')
HREF_RE = re.compile(r'(href|src)="([^"]*)"')
MATERIAL_HREF_RE = re.compile(r'href="(material/[^"]+)"')
# Pages/files of the export that are not published: the scientific programme
# (unused), the iCalendar exports (pointless for a past event, and full of
# links to the Indico server) and the PDF exports of the timetable (no
# generated PDFs in git).
SKIPPED_FILES = ("program.html",)
SKIPPED_SUFFIXES = (".ics", ".pdf")
PROGRAM_MENU_RE = re.compile(
    r'<li class="menuConfTitle[^"]*">\s*<a href="program\.html"\s*>[^<]*</a>\s*')
ICS_LINK_RE = re.compile(r'\s*<a href="[^"]*\.ics"[^>]*></a>')
# "Export to PDF" icon buttons (local .pdf links without content) and the PDF
# references in the timetable data.
PDF_BUTTON_RE = re.compile(r'\s*<a href="(?!https?:)[^"]*\.pdf"[^>]*>\s*</a>')
TT_PDF_JSON_RE = re.compile(r'"pdf":"[^"]*\.pdf"')
# The JS timetable draws its own "PDF" toolbar button: neutralise its action
# and hide it once the timetable is drawn.
TT_DRAW = "timetable.postDraw();"
TT_HIDE_PDF = (TT_DRAW + """
                // Archived copy: no PDF export of the timetable.
                $('#timetable').find('*').filter(function() {
                    return this.children.length === 0 && $.trim($(this).text()) === 'PDF';
                }).each(function() {
                    var el = $(this);
                    while (el.parent().length && $.trim(el.parent().text()) === 'PDF') {
                        el = el.parent();
                    }
                    el.hide();
                });""")
TT_ARGS = "var timetableArgs = ["
TT_NOOP_PDF = ("if (window.DisplayTimeTable) { DisplayTimeTable.prototype.pdf = function() {}; }\n"
               "            " + TT_ARGS)
# Metadata pointing back to the Indico server (logo, canonical event URL).
OG_IMAGE_RE = re.compile(r'\s*<meta property="og:image" content="[^"]*">')
LD_JSON_URL_RE = re.compile(r',"url":"[^"]*"(?=}\s*</script>)')

BANNER = (
    '<div class="archive-banner" style="padding:0.5em 1em;background:#eef3f8;'
    'border-bottom:1px solid #c9d6e3;font-size:0.95em;">'
    '<a href="../../index.html">&larr; All IMAS Data Mapping workshops</a>'
    ' &middot; Archived copy of the Indico event page; registration and'
    ' interactive features are not available.</div>\n')


def asset_name(rel_path):
    """Release asset name for ``material/<n>-contribution/<id>-<name>.<ext>``.

    GitHub replaces unsupported characters in asset names, so slugify the
    name ourselves to keep the link and the uploaded asset identical.
    """
    stem, dot, ext = Path(rel_path).name.rpartition(".")
    if not dot:
        stem, ext = ext, ""
    stem = re.sub(r"[^A-Za-z0-9.-]+", "_", stem).strip("_.")
    stem = re.sub(r"\.{2,}", ".", stem)
    return f"{stem}.{ext.lower()}" if ext else stem


def clean_page(text, release_url, assets, src_dir, out_assets):
    def material(match):
        rel = html.unescape(match.group(1))
        src = src_dir / rel
        if not src.is_file():  # keep it, the report will flag it
            return match.group(0)
        name = asset_name(rel)
        if name in assets and assets[name] != src:
            sys.exit(f"Asset name clash: {name} ({assets[name]} vs {src})")
        if name not in assets:
            assets[name] = src
            shutil.copy2(src, out_assets / name)
        return f'href="{release_url}/{urllib.parse.quote(name)}"'

    text = MATERIAL_HREF_RE.sub(material, text)
    text = GENERIC_HEADER_RE.sub('<div class="header"></div>\n', text)
    text = FOOTER_RE.sub("", text)
    text = REG_SECTION_RE.sub("", text)
    text = REG_TEXT_RE.sub("", text)
    text = LOGIN_TITLE_RE.sub("", text)
    text = PROGRAM_MENU_RE.sub("", text)
    text = ICS_LINK_RE.sub("", text)
    text = PDF_BUTTON_RE.sub("", text)
    text = TT_PDF_JSON_RE.sub('"pdf":null', text)
    text = text.replace(TT_DRAW, TT_HIDE_PDF).replace(TT_ARGS, TT_NOOP_PDF)
    text = OG_IMAGE_RE.sub("", text)
    text = LD_JSON_URL_RE.sub("", text)
    text = text.replace('<main class="main">', BANNER + '<main class="main">', 1)
    return text


def check_links(site):
    problems = []
    for page in sorted(site.rglob("*.html")):
        for _, link in HREF_RE.findall(page.read_text(encoding="utf-8")):
            link = html.unescape(link)
            if re.match(r"^(https?:|mailto:|#|data:|javascript:)", link) or not link:
                continue
            if link.startswith("/"):
                problems.append((page.name, link, "site-rooted link"))
                continue
            target = urllib.parse.unquote(link.split("#")[0])
            if target and not (page.parent / target).exists():
                problems.append((page.name, link, "missing target"))
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("export_dir", type=Path, help="unzipped Indico export (folder containing index.html)")
    ap.add_argument("out_site", type=Path, help="output folder, e.g. docs/workshops/2026-03")
    ap.add_argument("out_assets", type=Path, help="output folder for release assets (outside the repo)")
    ap.add_argument("--release-tag", required=True, help="e.g. workshop-2026-03")
    ap.add_argument("--repo", default=DEFAULT_REPO, help=f"GitHub repo (default {DEFAULT_REPO})")
    args = ap.parse_args()

    src = args.export_dir.resolve()
    if not (src / "index.html").is_file():
        sys.exit(f"{src} does not contain index.html")
    for out in (args.out_site, args.out_assets):
        if out.exists() and any(out.iterdir()):
            sys.exit(f"{out} exists and is not empty")
        out.mkdir(parents=True, exist_ok=True)

    def ignore(d, names):
        if Path(d) != src:
            return []
        return [n for n in names if n == "material" or n in SKIPPED_FILES
                or n.endswith(SKIPPED_SUFFIXES)]

    shutil.copytree(src, args.out_site, dirs_exist_ok=True, ignore=ignore)

    release_url = f"https://github.com/{args.repo}/releases/download/{args.release_tag}"
    assets = {}
    for page in sorted(args.out_site.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        page.write_text(clean_page(text, release_url, assets, src, args.out_assets),
                        encoding="utf-8")

    unused = sorted(p.relative_to(src) for p in (src / "material").rglob("*")
                    if p.is_file() and p not in assets.values())
    print(f"{len(assets)} release assets written to {args.out_assets}")
    for p in unused:
        print(f"WARNING: attachment not linked from any page (not copied): {p}")

    problems = check_links(args.out_site)
    for page, link, why in problems:
        print(f"LINK {why}: {page}: {link}")
    print(f"{len(problems)} link problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
