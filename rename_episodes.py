import argparse
import os
import re
import sys
from dotenv import load_dotenv

load_dotenv()


def parse_episode_info(filename):
    """
    Extracts episode number and optional version suffix from various filename patterns.
    Examples:
        100_sub.mp4 -> ep 100
        121sub.mp4 -> ep 121
        270_EN_Subs.mp4 -> ep 270
        342_EN_Subs_v2.mp4 -> ep 342, v2
        346_EN_subs_2.mp4 -> ep 346, v2
        Chiikawa_261_EN_Subs.mp4 -> ep 261
        real_134_EN_subs.mp4 -> ep 134
        YT144_sub.mp4 -> ep 144
        YT221.mp4 -> ep 221
        96_sub.mp4 -> ep 96
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".mp4", ".mkv", ".webm", ".mov", ".avi"]:
        return None

    name = os.path.splitext(filename)[0]

    # Regex to find episode number (2 to 3 digits)
    # Matches patterns like YT144, Chiikawa_261, real_134, 100_sub, 96_sub, etc.
    match = re.search(r"(?:YT|Chiikawa_|real_|^|\D)(\d{2,3})(?:\D|$)", name, re.IGNORECASE)
    if not match:
        return None

    ep_num = int(match.group(1))

    # Detect version suffixes (v2, _2, etc.)
    v_match = re.search(r"(?:_v?|v)(\d)$", name, re.IGNORECASE)
    v_num = v_match.group(1) if v_match else None
    v_suffix = f"_v{v_num}" if v_num and v_num != "1" else ""

    return ep_num, v_suffix, ext


def main():
    parser = argparse.ArgumentParser(
        description="Standardize Chiikawa episode filenames into Plex format (e.g., Chiikawa - S01E096.mp4)"
    )
    parser.add_argument(
        "--folder",
        default=os.getenv("DOWNLOAD_DIR", "."),
        help="Target folder containing video files (default: DOWNLOAD_DIR from .env or current directory)",
    )
    parser.add_argument(
        "--show-name",
        default="Chiikawa",
        help="Show name prefix for Plex formatting (default: Chiikawa)",
    )
    parser.add_argument(
        "--season",
        type=int,
        default=1,
        help="Season number (default: 1)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply renames directly (default is dry-run mode)",
    )

    args = parser.parse_args()
    folder = os.path.abspath(args.folder)

    if not os.path.exists(folder):
        print(f"Error: Folder does not exist: {folder}")
        sys.exit(1)

    files = sorted(os.listdir(folder))
    rename_plan = []

    for filename in files:
        result = parse_episode_info(filename)
        if not result:
            continue

        ep_num, v_suffix, ext = result
        new_name = f"{ep_num:03d}{v_suffix}{ext}"

        if filename != new_name:
            rename_plan.append((filename, new_name))

    if not rename_plan:
        print("No files need renaming. Everything is already standardized!")
        return

    print("=" * 60)
    print(f"FOLDER: {folder}")
    print(f"MODE: {'[APPLY]' if args.apply else '[DRY-RUN - No files changed yet]'}")
    print("=" * 60)

    for old_file, new_file in rename_plan:
        print(f"  {old_file}\n  └─> {new_file}\n")

    print("-" * 60)
    print(f"Total files to rename: {len(rename_plan)}")

    if not args.apply:
        print("\n💡 This was a DRY-RUN preview.")
        print("   To actually rename the files, run with '--apply':")
        print(f"   python rename_episodes.py --folder \"{folder}\" --apply")
    else:
        print("\nRenaming files...")
        for old_file, new_file in rename_plan:
            old_path = os.path.join(folder, old_file)
            new_path = os.path.join(folder, new_file)

            if os.path.exists(new_path):
                print(f"[!] Warning: Target file {new_file} already exists, skipping...")
                continue

            os.rename(old_path, new_path)
        print("✨ All files renamed successfully!")


if __name__ == "__main__":
    main()
