#!/usr/bin/env python3
"""Create QIIME 2 paired-end manifests and a provenance sample map.

The filename patterns are project-specific and intentionally explicit. If future
sequencing files use a different naming convention, add a new parser rather than
silently guessing.
"""
import argparse, csv, re
from pathlib import Path


def mate_for(r1: Path) -> Path:
    name = r1.name
    replacements = [
        ('_R1_001.fastq.gz', '_R2_001.fastq.gz'),
        ('_R1.fastq.gz', '_R2.fastq.gz'),
    ]
    for old,new in replacements:
        if old in name:
            r2 = r1.with_name(name.replace(old,new))
            if not r2.exists():
                raise FileNotFoundError(f'Missing mate for {r1.name}: expected {r2.name}')
            return r2
    raise ValueError(f'Cannot infer R2 filename from {r1.name}')


def parse_sepjan(name):
    m = re.match(r'^2860mcrA-\d+-(\d+)-(Sep24|Jan25)mcrA-(.+?)_S\d+_L\d+_R1\.fastq\.gz$', name)
    if m:
        source_id, month, site_sample = m.groups()
        return f'{month}-{site_sample}', source_id, month, site_sample, False
    m = re.match(r'^2860mcrA-\d+-(blank[^_]+)_S\d+_L\d+_R1\.fastq\.gz$', name, re.I)
    if m:
        ctrl = m.group(1)
        return f'SepJan-{ctrl}', '', 'control', ctrl, True
    raise ValueError(f'Unrecognized Sep-Jan filename: {name}')


def parse_aprjul(name):
    m = re.match(r'^3744b_\d+_(\d+)-(Apr25|Jul25)-(.+?)_S\d+_L\d+_R1_001\.fastq\.gz$', name)
    if m:
        source_id, month, site_sample = m.groups()
        return f'{month}-{site_sample}', source_id, month, site_sample, False
    m = re.match(r'^3744b_\d+_(Blank\d+|NTC\d+)_S\d+_L\d+_R1_001\.fastq\.gz$', name, re.I)
    if m:
        ctrl = m.group(1)
        return f'AprJul-{ctrl}', '', 'control', ctrl, True
    raise ValueError(f'Unrecognized Apr-Jul filename: {name}')


def build(folder, run, parser, out_manifest, out_map):
    folder = Path(folder).resolve()
    rows = []
    for r1 in sorted(folder.glob('*R1*.fastq.gz')):
        sample, source_id, month, site_sample, is_control = parser(r1.name)
        r2 = mate_for(r1)
        rows.append((sample, str(r1.resolve()), str(r2.resolve()), run,
                     source_id, month, site_sample, str(is_control).lower()))
    if not rows:
        raise RuntimeError(f'No R1 FASTQ files found in {folder}')
    ids = [x[0] for x in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError('Duplicate canonical sample IDs detected')

    with open(out_manifest, 'w', newline='') as fh:
        wr = csv.writer(fh, delimiter='\t')
        wr.writerow(['sample-id','forward-absolute-filepath','reverse-absolute-filepath'])
        for x in rows:
            wr.writerow(x[:3])

    with open(out_map, 'w', newline='') as fh:
        wr = csv.writer(fh, delimiter='\t')
        wr.writerow(['sample-id','run','source-id','month','site-sample','is-control','forward','reverse'])
        for sample,fwd,rev,run,source_id,month,site_sample,is_control in rows:
            wr.writerow([sample,run,source_id,month,site_sample,is_control,fwd,rev])
    print(f'{run}: {len(rows)} libraries')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sepjan', required=True)
    ap.add_argument('--aprjul', required=True)
    ap.add_argument('--outdir', required=True)
    args = ap.parse_args()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    build(args.sepjan, 'SepJan', parse_sepjan, out/'manifest_SepJan.tsv', out/'sample_map_SepJan.tsv')
    build(args.aprjul, 'AprJul', parse_aprjul, out/'manifest_AprJul.tsv', out/'sample_map_AprJul.tsv')

if __name__ == '__main__':
    main()
