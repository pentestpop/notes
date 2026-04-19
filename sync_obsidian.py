#!/usr/bin/env python3
"""
sync_obsidian.py
Syncs Obsidian vault notes into the Jekyll notes site.

- Copies the 6 content folders from the Obsidian vault to the notes repo
- Copies images from the Obsidian vault to assets/images/
- Adds/replaces Jekyll front matter on every file
- Ensures each file has a top-level H1 heading
- Fixes image paths to /assets/images/FOLDER/filename
- Regenerates all combined index.md files
"""

import os
import re
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Folder definitions — mirrors the site structure exactly
# ---------------------------------------------------------------------------

TOP_FOLDERS = [
    ("1 - Enumeration",    1),
    ("2 - Exploit",        2),
    ("3 - Post-Exploit",   3),
    ("4 - Web_Application",4),
    ("5 - Unsorted Security", 5),
    ("6 - Misc THM Notes", 6),
]

# Subfolders for 4 - Web_Application
WEB_SUBDIRS = [
    ("00-Specific_Labs",            "Specific Labs",           1),
    ("01-Authentication-and-Session","Authentication and Session", 2),
    ("02-Client-Side",              "Client-Side",             3),
    ("03-Injection",                "Injection",               4),
    ("04-Server-Side",              "Server-Side",             5),
    ("05-HTTP-and-Infrastructure",  "HTTP and Infrastructure", 6),
    ("06-API-and-Modern",           "API and Modern",          7),
    ("07-Caching-and-Browser-Edge", "Caching and Browser Edge",8),
    ("08-Access-Control-and-Logic", "Access Control and Logic",9),
]

# Subfolders for 6 - Misc THM Notes
MISC_SUBDIRS = [
    ("DevSecOps",   "DevSecOps",   3),
    ("Misc",        "Misc",        4),
    ("SOC Level 1", "SOC Level 1", 5),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ask_dir(prompt, default=None):
    hint = f" [{default}]" if default else ""
    while True:
        val = input(f"{prompt}{hint}: ").strip()
        if not val and default:
            val = default
        val = os.path.expanduser(val)
        if os.path.isdir(val):
            return os.path.abspath(val)
        print(f"  Directory not found: {val!r}  — please try again.")


def get_title_from_filename(filename):
    name = os.path.splitext(filename)[0]
    # Strip port-number prefixes like "(22) " or "(137,138,445) "
    name = re.sub(r'^\([\d,\s]+\)\s*', '', name)
    return name.strip()


def quote_yaml(value):
    """Wrap a YAML string in double-quotes if it contains special chars."""
    if any(c in str(value) for c in ':{}[]#&*?|>!%@`\'"'):
        return '"' + str(value).replace('"', '\\"') + '"'
    return str(value)


def build_frontmatter(title, parent, nav_order, grand_parent=None, has_children=False):
    lines = [
        "---",
        f"title: {quote_yaml(title)}",
        f"parent: {quote_yaml(parent)}",
    ]
    if grand_parent:
        lines.append(f"grand_parent: {quote_yaml(grand_parent)}")
    lines += [
        f"nav_order: {nav_order}",
        "layout: default",
    ]
    if has_children:
        lines.append("has_children: true")
    lines.append("---")
    return "\n".join(lines)


def build_index_frontmatter(title, nav_order, parent=None, grand_parent=None):
    lines = ["---", f"title: {quote_yaml(title)}"]
    if parent:
        lines.append(f"parent: {quote_yaml(parent)}")
    if grand_parent:
        lines.append(f"grand_parent: {quote_yaml(grand_parent)}")
    lines += [
        f"nav_order: {nav_order}",
        "layout: default",
        "has_children: true",
        "---",
    ]
    return "\n".join(lines)


def strip_frontmatter(content):
    """Remove YAML front matter and return body."""
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            return content[end + 4 :].lstrip("\n")
    return content


def ensure_h1(body, title):
    """Add a # H1 heading at the top if one is missing."""
    stripped = body.lstrip("\n")
    for line in stripped.split("\n"):
        if line.strip():
            if line.strip().startswith("# ") and not line.strip().startswith("## "):
                return stripped  # already has H1
            break
    return f"# {title}\n\n{stripped}"


def find_image_in_vault(image_name, obsidian_dir):
    """Search for an image file anywhere in the Obsidian vault."""
    for root, dirs, files in os.walk(obsidian_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if image_name in files:
            return os.path.join(root, image_name)
    return None


def fix_image_paths(content, assets_images_dir, image_folder_name, obsidian_dir):
    """
    1. Convert Obsidian ![[image.png]] wiki-links to standard markdown
    2. Standardise all local image paths to /assets/images/FOLDER/filename
    3. Copy any found images into assets_images_dir/image_folder_name/
    Returns updated content.
    """
    target_dir = os.path.join(assets_images_dir, image_folder_name)
    os.makedirs(target_dir, exist_ok=True)

    def copy_image(img_name):
        """Find img_name in vault, copy to target_dir.  Returns True if found."""
        dst = os.path.join(target_dir, img_name)
        if os.path.exists(dst):
            return True  # already there
        src = find_image_in_vault(img_name, obsidian_dir)
        if src:
            shutil.copy2(src, dst)
            return True
        return False

    def img_url(img_name):
        safe_name   = img_name.replace(" ", "%20")
        safe_folder = image_folder_name.replace(" ", "%20")
        return f"/assets/images/{safe_folder}/{safe_name}"

    # --- Obsidian wiki-link images: ![[image.png]] or ![[image.png|alt]] ---
    def repl_wiki(m):
        inner = m.group(1).split("|")[0].strip()   # strip optional alt text
        img_name = os.path.basename(inner)
        copy_image(img_name)
        return f"![]({img_url(img_name)})"

    content = re.sub(r"!\[\[([^\]]+)\]\]", repl_wiki, content)

    # --- Standard markdown images: ![alt](path) ---
    def repl_std(m):
        alt  = m.group(1)
        path = m.group(2)
        if path.startswith("http"):
            return m.group(0)                       # leave external URLs alone
        if path.startswith("/assets/images/"):
            return m.group(0)                       # already correct
        img_name = os.path.basename(path.replace("%20", " "))
        copy_image(img_name)
        return f"![{alt}]({img_url(img_name)})"

    content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl_std, content)
    return content


# ---------------------------------------------------------------------------
# File processing
# ---------------------------------------------------------------------------

def process_file(src_path, dst_path, title, parent, nav_order,
                 grand_parent, assets_images_dir, image_folder_name, obsidian_dir):
    """Read a source .md file, apply all transforms, write to destination."""
    with open(src_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    body = strip_frontmatter(content)
    body = fix_image_paths(body, assets_images_dir, image_folder_name, obsidian_dir)
    body = ensure_h1(body, title)

    fm = build_frontmatter(title, parent, nav_order, grand_parent)
    new_content = f"{fm}\n\n{body}"

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(new_content)


# ---------------------------------------------------------------------------
# Index generation
# ---------------------------------------------------------------------------

def get_sorted_files(folder, exclude_index=True):
    """Return list of (nav_order, title, body) sorted by nav_order."""
    results = []
    if not os.path.isdir(folder):
        return results
    for fname in os.listdir(folder):
        if not fname.endswith(".md"):
            continue
        if exclude_index and fname == "index.md":
            continue
        fpath = os.path.join(folder, fname)
        if not os.path.isfile(fpath):
            continue
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        nav_m = re.search(r"^nav_order:\s*(\d+)", content, re.MULTILINE)
        nav_order = int(nav_m.group(1)) if nav_m else 999
        title_m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE)
        title = title_m.group(1).strip("\"'") if title_m else os.path.splitext(fname)[0]
        body = strip_frontmatter(content)
        results.append((nav_order, title, body))
    return sorted(results, key=lambda x: x[0])


def strip_h1(body):
    lines = body.split("\n")
    out = []
    removed = False
    for line in lines:
        if not removed and line.strip().startswith("# ") and not line.strip().startswith("## "):
            removed = True
            continue
        out.append(line)
    return "\n".join(out).lstrip("\n")


def shift_headings(body, levels=1):
    def repl(m):
        hashes = "#" * min(len(m.group(1)) + levels, 6)
        return hashes + m.group(2)
    return re.sub(r"^(#{1,6})([ \t].*)$", repl, body, flags=re.MULTILINE)


def build_combined_index(fm_str, h1_label, file_entries, section_level=2):
    """Combine file entries into one long page."""
    sep = "#" * section_level
    parts = [fm_str, "", f"# {h1_label}", ""]
    for _, title, body in file_entries:
        body_stripped = strip_h1(body)
        body_shifted  = shift_headings(body_stripped, levels=section_level - 1)
        parts += [f"{sep} {title}", "", body_shifted.strip(), "", "---", ""]
    return "\n".join(parts)


def write_index(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [index] {path}")


def rebuild_indexes(notes_dir):
    """Regenerate all combined index.md files from processed content."""
    print("\nRebuilding indexes...")

    # --- Flat top-level folders (1, 2, 3, 5) ---
    flat_folders = [
        ("1 - Enumeration",    1, "Enumeration"),
        ("2 - Exploit",        2, "Exploit"),
        ("3 - Post-Exploit",   3, "Post-Exploit"),
        ("5 - Unsorted Security", 5, "Unsorted Security"),
    ]
    for folder_name, nav_order, h1 in flat_folders:
        folder = os.path.join(notes_dir, folder_name)
        files  = get_sorted_files(folder)
        fm     = build_index_frontmatter(folder_name, nav_order)
        write_index(
            os.path.join(folder, "index.md"),
            build_combined_index(fm, h1, files, section_level=2),
        )

    # --- 4 - Web_Application subfolder indexes ---
    web_root = os.path.join(notes_dir, "4 - Web_Application")
    for dirname, title, nav_order in WEB_SUBDIRS:
        subdir = os.path.join(web_root, dirname)
        files  = get_sorted_files(subdir)
        fm     = build_index_frontmatter(title, nav_order, parent="4 - Web_Application")
        write_index(
            os.path.join(subdir, "index.md"),
            build_combined_index(fm, title, files, section_level=2),
        )

    # 4 - Web_Application top-level index
    fm = build_index_frontmatter("4 - Web_Application", 4)
    parts = [fm, "", "# Web Application", ""]
    for dirname, title, _ in WEB_SUBDIRS:
        subdir = os.path.join(web_root, dirname)
        files  = get_sorted_files(subdir)
        parts += [f"## {title}", ""]
        for _, ftitle, fbody in files:
            body_stripped = strip_h1(fbody)
            body_shifted  = shift_headings(body_stripped, levels=2)
            parts += [f"### {ftitle}", "", body_shifted.strip(), "", "---", ""]
    write_index(os.path.join(web_root, "index.md"), "\n".join(parts))

    # --- 6 - Misc THM Notes subfolder indexes ---
    misc_root = os.path.join(notes_dir, "6 - Misc THM Notes")
    for dirname, title, nav_order in MISC_SUBDIRS:
        subdir = os.path.join(misc_root, dirname)
        files  = get_sorted_files(subdir)
        fm     = build_index_frontmatter(title, nav_order, parent="6 - Misc THM Notes")
        write_index(
            os.path.join(subdir, "index.md"),
            build_combined_index(fm, title, files, section_level=2),
        )

    # 6 - Misc THM Notes top-level index
    fm = build_index_frontmatter("6 - Misc THM Notes", 6)
    parts = [fm, "", "# Misc THM Notes", ""]
    # Root-level files first
    for _, ftitle, fbody in get_sorted_files(misc_root):
        body_stripped = strip_h1(fbody)
        body_shifted  = shift_headings(body_stripped, levels=1)
        parts += [f"## {ftitle}", "", body_shifted.strip(), "", "---", ""]
    # Subdirectories
    for dirname, title, _ in MISC_SUBDIRS:
        subdir = os.path.join(misc_root, dirname)
        files  = get_sorted_files(subdir)
        parts += [f"## {title}", ""]
        for _, ftitle, fbody in files:
            body_stripped = strip_h1(fbody)
            body_shifted  = shift_headings(body_stripped, levels=2)
            parts += [f"### {ftitle}", "", body_shifted.strip(), "", "---", ""]
    write_index(os.path.join(misc_root, "index.md"), "\n".join(parts))


# ---------------------------------------------------------------------------
# Sync a single folder tree
# ---------------------------------------------------------------------------

def sync_folder(obs_folder, notes_folder, folder_title, nav_order_base,
                assets_images_dir, obsidian_dir,
                parent_title=None, grand_parent_title=None, subdirs=None):
    """
    Sync all .md files from obs_folder into notes_folder.
    subdirs: list of (dirname, title, nav_order) for subfolders, or None for flat.
    """
    if not os.path.isdir(obs_folder):
        print(f"  [skip] Not found in vault: {obs_folder}")
        return

    if subdirs:
        # Process root-level files in this folder
        _sync_flat(obs_folder, notes_folder, folder_title, nav_order_base,
                   assets_images_dir, obsidian_dir,
                   parent=folder_title, grand_parent=None,
                   image_folder_name=folder_title)

        # Process each subdirectory
        for dirname, sub_title, sub_nav in subdirs:
            obs_sub   = os.path.join(obs_folder, dirname)
            notes_sub = os.path.join(notes_folder, dirname)
            _sync_flat(obs_sub, notes_sub, sub_title, sub_nav,
                       assets_images_dir, obsidian_dir,
                       parent=folder_title, grand_parent=None,
                       image_folder_name=sub_title)
    else:
        _sync_flat(obs_folder, notes_folder, folder_title, nav_order_base,
                   assets_images_dir, obsidian_dir,
                   parent=folder_title, grand_parent=None,
                   image_folder_name=folder_title)


def _sync_flat(obs_dir, notes_dir_path, parent_title, base_nav,
               assets_images_dir, obsidian_dir,
               parent, grand_parent, image_folder_name):
    """Sync .md files from one flat directory."""
    if not os.path.isdir(obs_dir):
        return

    # Collect existing nav_orders from notes dir so we don't renumber files
    # that already exist (preserves manual ordering).
    existing_nav = {}
    if os.path.isdir(notes_dir_path):
        for fname in os.listdir(notes_dir_path):
            if fname.endswith(".md") and fname != "index.md":
                fpath = os.path.join(notes_dir_path, fname)
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    c = f.read()
                m = re.search(r"^nav_order:\s*(\d+)", c, re.MULTILINE)
                if m:
                    existing_nav[fname] = int(m.group(1))

    # Assign nav_order to incoming files
    used_orders = set(existing_nav.values())
    next_order  = max(used_orders, default=0) + 1

    md_files = sorted(f for f in os.listdir(obs_dir) if f.endswith(".md"))
    for fname in md_files:
        if fname == "index.md":
            continue
        src = os.path.join(obs_dir, fname)
        dst = os.path.join(notes_dir_path, fname)
        title = get_title_from_filename(fname)

        if fname in existing_nav:
            nav_order = existing_nav[fname]
        else:
            while next_order in used_orders:
                next_order += 1
            nav_order = next_order
            used_orders.add(nav_order)
            next_order += 1

        process_file(src, dst, title, parent, nav_order, grand_parent,
                     assets_images_dir, image_folder_name, obsidian_dir)
        print(f"  [sync] {dst}")


# ---------------------------------------------------------------------------
# Sync assets/images
# ---------------------------------------------------------------------------

def sync_images(obs_dir, notes_images_dir):
    """Copy image folders from Obsidian vault assets/images into notes assets/images."""
    obs_images = os.path.join(obs_dir, "assets", "images")
    if not os.path.isdir(obs_images):
        print(f"  [skip] No assets/images found in vault: {obs_images}")
        return

    copied = 0
    for item in os.listdir(obs_images):
        src = os.path.join(obs_images, item)
        dst = os.path.join(notes_images_dir, item)
        if os.path.isdir(src):
            if os.path.isdir(dst):
                # Merge: copy any new files in the subfolder
                for fname in os.listdir(src):
                    fsrc = os.path.join(src, fname)
                    fdst = os.path.join(dst, fname)
                    if os.path.isfile(fsrc) and not os.path.exists(fdst):
                        shutil.copy2(fsrc, fdst)
                        copied += 1
            else:
                shutil.copytree(src, dst)
                copied += len(os.listdir(src))
        elif os.path.isfile(src):
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                copied += 1
    print(f"  [images] Copied {copied} new image file(s) from vault.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== Obsidian → Jekyll Notes Sync ===\n")

    notes_dir    = ask_dir("Notes repo directory",
                           default=os.path.dirname(os.path.abspath(__file__)))
    obsidian_dir = ask_dir("Obsidian vault directory")

    assets_images_dir = os.path.join(notes_dir, "assets", "images")
    os.makedirs(assets_images_dir, exist_ok=True)

    print("\nSyncing content folders...")

    for folder_name, nav_order in TOP_FOLDERS:
        obs_folder   = os.path.join(obsidian_dir, folder_name)
        notes_folder = os.path.join(notes_dir, folder_name)
        print(f"\n{folder_name}")

        if folder_name == "4 - Web_Application":
            sync_folder(obs_folder, notes_folder, folder_name, nav_order,
                        assets_images_dir, obsidian_dir, subdirs=WEB_SUBDIRS)
        elif folder_name == "6 - Misc THM Notes":
            sync_folder(obs_folder, notes_folder, folder_name, nav_order,
                        assets_images_dir, obsidian_dir, subdirs=MISC_SUBDIRS)
        else:
            sync_folder(obs_folder, notes_folder, folder_name, nav_order,
                        assets_images_dir, obsidian_dir)

    print("\nSyncing assets/images...")
    sync_images(obsidian_dir, assets_images_dir)

    rebuild_indexes(notes_dir)

    print("\nDone. Review changes, then commit and push:")
    print("  git add -A && git commit -m 'Sync from Obsidian' && git push")


if __name__ == "__main__":
    main()
