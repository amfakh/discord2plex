# -*- coding: utf-8 -*-
import argparse
import os
import re
import sys
from dotenv import load_dotenv

load_dotenv()


def parse_episode_info(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".mp4", ".mkv", ".webm", ".mov", ".avi"]:
        return None

    name = os.path.splitext(filename)[0]

    # Special handling for "real_134" vs old 134-142 range
    is_real_134 = "real_134" in name.lower()

    if is_real_134:
        ep_num = 134
    else:
        # Regex to find episode number (2 to 3 digits)
        match = re.search(r"(?:YT|Chiikawa_|^|\D)(\d{2,3})(?:\D|$)", name, re.IGNORECASE)
        if not match:
            return None

        ep_num = int(match.group(1))

        # Shift old episodes 134..142 up to 135..143 (filling the gap for real 134)
        if 134 <= ep_num <= 142:
            ep_num += 1

    # Detect version suffixes (v2, _2, etc.)
    v_match = re.search(r"(?:_v?|v)(\d)$", name, re.IGNORECASE)
    v_num = v_match.group(1) if v_match else None
    v_suffix = "_v{}".format(v_num) if (v_num and v_num != "1") else ""

    return ep_num, v_suffix, ext


def main():
    parser = argparse.ArgumentParser(
        description="Standardize Chiikawa episode filenames (e.g., 096.mp4)"
    )
    parser.add_argument(
        "--folder",
        default=os.getenv("DOWNLOAD_DIR", "."),
        help="Target folder containing video files",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply renames directly (default is dry-run mode)",
    )

    args = parser.parse_args()
    folder = os.path.abspath(args.folder)

    if not os.path.exists(folder):
        print("Error: Folder does not exist: {}".format(folder))
        sys.exit(1)

    files = sorted(os.listdir(folder))
    rename_plan = []

    for filename in files:
        result = parse_episode_info(filename)
        if not result:
            continue

        ep_num, v_suffix, ext = result
        new_name = "{:03d}{}{}".format(ep_num, v_suffix, ext)

        if filename != new_name:
            rename_plan.append((ep_num, filename, new_name))

    if not rename_plan:
        print("No files need renaming. Everything is already standardized!")
        return

    # Sort rename plan by episode number DESCENDING (so 142->143 happens before 141->142, avoiding collisions)
    rename_plan.sort(key=lambda x: x[0], reverse=True)

    print("=" * 60)
    print("FOLDER: {}".format(folder))
    print("MODE: {}".format("[APPLY]" if args.apply else "[DRY-RUN - No files changed yet]"))
    print("=" * 60)

    for _, old_file, new_file in rename_plan:
        print("  {}\n  -> {}\n".format(old_file, new_file))

    print("-" * 60)
    print("Total files to rename: {}".format(len(rename_plan)))

    if not args.apply:
        print("\n[*] This was a DRY-RUN preview.")
        print("   To actually rename the files, run with '--apply':")
        print("   uv run rename_episodes.py --folder \"{}\" --apply".format(folder))
    else:
        print("\nRenaming files...")
        for _, old_file, new_file in rename_plan:
            old_path = os.path.join(folder, old_file)
            new_path = os.path.join(folder, new_file)

            if os.path.exists(new_path):
                print("[!] Target file {} already exists. Deleting duplicate {}...".format(new_file, old_file))
                os.remove(old_path)
                continue

            os.rename(old_path, new_path)
            print("[v] Renamed: {} -> {}".format(old_file, new_file))
        print("\n[v] All files renamed successfully!")


if __name__ == "__main__":
    main()
