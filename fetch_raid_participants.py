#!/usr/bin/env python3
"""
fetch_raid_participants.py

Download participants data from a Raid-Helper URL and

* Print a two-column list (name, category) in **true signup order** or randomized.
* Filter by one or more statuses, case-insensitive.
* Show the available categories with -c / --categories.

If no status filters are provided, all sign-ups are shown.
Unknown statuses are silently ignored.
"""

from __future__ import annotations
import sys
import argparse
import requests
import random
from typing import List, Dict

JSON_KEY = "signUps"

# ---------- CLI ---------- #

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Fetch Raid-Helper sign-ups and print a two-column list in signup order or randomized."
    )
    p.add_argument("-u", "--url", required=True,
                   help="Raid-Helper URL that returns JSON")
    p.add_argument("-s", "--status", nargs="+", metavar="STATUS",
                   type=str.lower,
                   help="Statuses to include (attending tentative absent …). Case-insensitive.")
    p.add_argument("-c", "--categories", action="store_true",
                   help="List all existing status categories and exit.")
    p.add_argument("-r", "--random", action="store_true",
                   help="Randomize the order of participants.")
    return p.parse_args()

# ---------- I/O ---------- #

def fetch_json(url: str) -> Dict:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

# ---------- Helpers ---------- #

def collect_categories(signups: List[Dict]) -> Dict[str, List[str]]:
    cats: Dict[str, List[str]] = {}
    for entry in signups:
        status = entry.get("className", "").lower()
        cats.setdefault(status, []).append(entry.get("name", ""))
    return cats

def print_categories(cats: Dict[str, List[str]]) -> None:
    for status in sorted(cats):
        print(status)

def print_rows_in_signup_order(signups: List[Dict], wanted: List[str] | None, shuffle: bool) -> None:
    # True signup sequence = ascending position; fall back to entryTime if position missing
    signups = sorted(signups, key=lambda e: (e.get("position", 10**9), e.get("entryTime", 0)))
    if shuffle:
        random.shuffle(signups)
    for entry in signups:
        status = entry.get("className", "").lower()
        if wanted and status not in wanted:
            continue
        name = entry.get("name", "")
        print(f"{name}\t{status}")

# ---------- Main ---------- #

def main() -> None:
    args = parse_args()

    data = fetch_json(args.url)
    signups: List[Dict] = data.get(JSON_KEY, [])

    if args.categories:
        print_categories(collect_categories(signups))
        return

    print_rows_in_signup_order(signups, args.status, shuffle=args.random)

if __name__ == "__main__":
    main()
