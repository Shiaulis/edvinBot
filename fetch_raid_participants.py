#!/usr/bin/env python3
"""
fetch_raid_participants.py

Download participants data from RAID URL, filter by status (case-insensitive),
print a sorted two-column list: name and group/category,
or list available categories with -c.
If no statuses are specified, all statuses are included.
Wrong statuses are simply ignored (no output for them).
Supports --url/-u flag for specifying the RAID Helper URL.
"""
import sys
import argparse
import requests

JSON_KEY = "signUps"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch RAID participants and print two-column list of names and categories."
    )
    parser.add_argument(
        "-u", "--url",
        required=True,
        help="The Raid Helper URL returning JSON"
    )
    parser.add_argument(
        "-s", "--status",
        nargs="+",
        metavar="STATUS",
        type=str.lower,
        help=(
            "One or more statuses to include (e.g. attending tentative absent). "
            "Case-insensitive. If omitted, all statuses are included."
        )
    )
    parser.add_argument(
        "-c", "--categories",
        action="store_true",
        help="List all existing status categories and exit."
    )
    return parser.parse_args()


def fetch_participants(url: str) -> dict:
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def categorize(data: dict) -> dict:
    statuses: dict[str, list[str]] = {}
    for entry in data.get(JSON_KEY, []):
        name = entry.get("name", "")
        status = entry.get("className", "").lower()
        statuses.setdefault(status, []).append(name)
    return statuses


def print_categories(categories: dict):
    for status in sorted(categories.keys()):
        print(status)


def print_two_columns(categories: dict, wanted: list[str] | None):
    # Build list of (name, status) tuples
    rows = []
    for status, names in categories.items():
        if wanted and status not in wanted:
            continue
        for name in names:
            rows.append((name, status))

    # Sort rows by name then status
    for name, status in sorted(rows, key=lambda x: (x[0].lower(), x[1])):
        print(f"{name}\t{status}")


def main():
    args = parse_args()
    raw = fetch_participants(args.url)
    cats = categorize(raw)

    if args.categories:
        print_categories(cats)
        sys.exit(0)

    print_two_columns(cats, args.status)


if __name__ == "__main__":
    main()
