#!/usr/bin/env python3
"""Map genome-derived mcrA reference IDs to GTDB taxonomy."""
import argparse, csv, gzip, re
from pathlib import Path
ACC_RE = re.compile(r'(GC[AF]_\d+\.\d+)')

def norm(x):
    x=x.strip()
    if x.startswith(('RS_','GB_')): x=x[3:]
    m=ACC_RE.search(x); return m.group(1) if m else x

def nover(x): return x.split('.',1)[0]

def fasta_records(path):
    name=None; buf=[]
    for line in open(path):
        line=line.rstrip('\n')
        if line.startswith('>'):
            if name is not None: yield name,''.join(buf)
            name=line[1:].split()[0]; buf=[]
        else: buf.append(line.strip())
    if name is not None: yield name,''.join(buf)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mcra-fasta',required=True); ap.add_argument('--gtdb-taxonomy',required=True)
    ap.add_argument('--gtdb-metadata',required=True); ap.add_argument('--out-prefix',required=True)
    args=ap.parse_args()
    exact={}
    with gzip.open(args.gtdb_taxonomy,'rt') as fh:
        for line in fh:
            acc,tax=line.rstrip('\n').split('\t',1); exact[norm(acc)]=tax
    with gzip.open(args.gtdb_metadata,'rt') as fh:
        r=csv.DictReader(fh,delimiter='\t'); fields=set(r.fieldnames or [])
        ac='accession' if 'accession' in fields else None
        gc='ncbi_genbank_assembly_accession' if 'ncbi_genbank_assembly_accession' in fields else None
        for row in r:
            primary=norm(row[ac]) if ac and row.get(ac) else ''; tax=exact.get(primary)
            if tax and gc and row.get(gc): exact.setdefault(norm(row[gc]),tax)
    relaxed={}
    for acc,tax in exact.items(): relaxed.setdefault(nover(acc),set()).add(tax)
    out=Path(args.out_prefix); out.parent.mkdir(parents=True,exist_ok=True)
    fa=open(str(out)+'_full.fasta','w'); tx=open(str(out)+'_taxonomy.tsv','w')
    un=open(str(out)+'_unmatched.tsv','w'); mp=open(str(out)+'_mapping_details.tsv','w')
    mp.write('mcrA_id\tassembly_accession\tmethod\ttaxonomy\n')
    counts={'exact':0,'version_relaxed':0,'not_in_GTDB':0}; n=0
    for rid,seq in fasta_records(args.mcra_fasta):
        n+=1; m=ACC_RE.search(rid); acc=m.group(1) if m else ''; tax=None; method='not_in_GTDB'
        if acc in exact: tax=exact[acc]; method='exact'
        elif acc:
            c=relaxed.get(nover(acc),set())
            if len(c)==1: tax=next(iter(c)); method='version_relaxed'
        counts[method]+=1; mp.write(f'{rid}\t{acc}\t{method}\t{tax or ""}\n')
        if tax: fa.write(f'>{rid}\n{seq}\n'); tx.write(f'{rid}\t{tax}\n')
        else: un.write(f'{rid}\t{acc}\n')
    for fh in (fa,tx,un,mp): fh.close()
    print('mcrA references:',n); [print(k,v) for k,v in counts.items()]
if __name__=='__main__': main()
