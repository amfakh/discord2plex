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

    # Regex to find episode number (2 to 3 digits)
    match = re.search(r"(?:YT|Chiikawa_|real_|^|\D)(\d{2,3})(?:\D|$)", name, re.IGNORECASE)
    if not match:
        return None

    ep_num = int(match.group(1))

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
            rename_plan.append((filename, new_name))

    if not rename_plan:
        print("No files need renaming. Everything is already standardized!")
        return

    print("=" * 60)
    print("FOLDER: {}".format(folder))
    print("MODE: {}".format("[APPLY]" if args.apply else "[DRY-RUN - No files changed yet]"))
    print("=" * 60)

    for old_file, new_file in rename_plan:
        print("  {}\n  └─> {}\n".format(old_file, new_file))

    print("-" * 60)
    print("Total files to rename: {}".format(len(rename_plan)))

    if not args.apply:
        print("\n💡 This was a DRY-RUN preview.")
        print("   To actually rename the files, run with '--apply':")
        print("   python3 rename_episodes.py --folder \"{}\" --apply".format(folder))
    else:
        print("\nRenaming files...")
        for old_file, new_file in rename_plan:
            old_path = os.path.join(folder, old_file)
            new_path = os.path.join(folder, new_file)

            if os.path.exists(new_path):
                print("[!] Warning: Target file {} already exists, skipping...".format(new_file))
                continue

            os.rename(old_path, new_path)
        print("✨ All files renamed successfully!")


if __name__ == "__main__":
    main()
