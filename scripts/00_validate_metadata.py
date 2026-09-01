#!/usr/bin/env python3
"""Basic structural validation of a metadata TSV.

This script intentionally works on an exported TSV rather than directly reading Excel,
so it can run in the QIIME environment without pandas/openpyxl.

Example:
    python scripts/00_validate_metadata.py metadata.tsv \
        --sample-column sample-id --month-column month --site-column site
"""
import argparse, csv, re, sys
from collections import Counter


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('metadata')
    ap.add_argument('--sample-column', default='sample-id')
    ap.add_argument('--month-column', default='month')
    ap.add_argument('--site-column', default='site')
    args = ap.parse_args()

    with open(args.metadata, newline='', encoding='utf-8-sig') as fh:
        rows = list(csv.DictReader(fh, delimiter='\t'))

    if not rows:
        raise SystemExit('ERROR: metadata contains no rows')

    for col in (args.sample_column, args.month_column, args.site_column):
        if col not in rows[0]:
            raise SystemExit(f'ERROR: missing column: {col}')

    ids = [r[args.sample_column].strip() for r in rows if r[args.sample_column].strip()]
    duplicates = [x for x,n in Counter(ids).items() if n > 1]

    problems = []
    for i,r in enumerate(rows, start=2):
        sid = r[args.sample_column].strip()
        month = r[args.month_column].strip()
        site = r[args.site_column].strip()
        if not sid:
            continue
        if re.search(r'blank|ntc', sid, re.I):
            continue
        m = re.match(r'^(Sep24|Jan25|Apr25|Jul25)-(.+)$', sid)
        if not m:
            problems.append((i, sid, 'sample ID does not match canonical pattern'))
            continue
        id_month, id_site = m.groups()
        if month and month != id_month:
            problems.append((i, sid, f'month mismatch: ID={id_month}, metadata={month}'))
        if site and site != id_site and not id_site.startswith(site + '-'):
            problems.append((i, sid, f'site mismatch: ID={id_site}, metadata={site}'))

    print(f'Rows: {len(rows)}')
    print(f'Unique non-empty sample IDs: {len(set(ids))}')
    print(f'Duplicate sample IDs: {len(duplicates)}')
    if duplicates:
        print('  ' + '\n  '.join(sorted(duplicates)))
    print(f'Structural mismatches: {len(problems)}')
    for p in problems[:100]:
        print(f'  line {p[0]}: {p[1]} — {p[2]}')

    if duplicates or problems:
        sys.exit(1)


if __name__ == '__main__':
    main()
