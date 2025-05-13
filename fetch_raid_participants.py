#!/usr/bin/env python3
"""
fetch_raid_participants.py

Download participants data from RAID URL, filter by status (case-insensitive),
print a plain, alphabetically sorted list of participant names,
or list available categories with -c.
If no statuses are specified, all statuses are included.
Wrong statuses are simply ignored (no output for them).
"""
import sys
import argparse
import requests

JSON_KEY = "signUps"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch RAID participants and print names filtered by status."
    )
    parser.add_argument(
        "url",
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


def print_plain_list(categories: dict, wanted: list[str] | None):
    # Determine which statuses to include: either user-specified or all
    if wanted:
        to_show = [st for st in categories.keys() if st.lower() in wanted]
    else:
        to_show = list(categories.keys())

    # Collect names for the chosen statuses
    names = []
    for st in to_show:
        names.extend(categories.get(st, []))

    # Print sorted, plain list (no warnings for wrong statuses)
    for name in sorted(names):
        print(name)


def main():
    args = parse_args()
    raw = fetch_participants(args.url)
    cats = categorize(raw)

    if args.categories:
        print_categories(cats)
        sys.exit(0)

    print_plain_list(cats, args.status)


if __name__ == "__main__":
    main()
