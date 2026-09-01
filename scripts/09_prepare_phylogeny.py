#!/usr/bin/env python3
"""Prepare targeted mcrA phylogeny input for HIGH/MEDIUM low-identity ASVs."""
import argparse,csv
from pathlib import Path
from collections import defaultdict

def read_fasta(path):
    d={}; name=None; buf=[]
    for line in open(path):
        line=line.strip()
        if line.startswith('>'):
            if name is not None: d[name]=''.join(buf)
            name=line[1:].split()[0]; buf=[]
        else: buf.append(line)
    if name is not None: d[name]=''.join(buf)
    return d
def read_tax(path):
    d={}
    for line in open(path):
        p=line.rstrip().split('\t',1)
        if len(p)==2 and p[0] not in {'Feature ID','FeatureID'}: d[p[0]]=p[1]
    return d

def main():
    ap=argparse.ArgumentParser()
    for x in ['master','asv-fasta','gtdb-fasta','gtdb-taxonomy','env-fasta','env-taxonomy','env-hits','outdir']: ap.add_argument('--'+x,required=True)
    a=ap.parse_args(); out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
    candidates={r['ASV']:r for r in csv.DictReader(open(a.master),delimiter='\t') if r['phylogeny_priority'] in {'HIGH','MEDIUM'}}
    asv=read_fasta(a.asv_fasta); gseq=read_fasta(a.gtdb_fasta); eseq=read_fasta(a.env_fasta); gtax=read_tax(a.gtdb_taxonomy); etax=read_tax(a.env_taxonomy)
    hits=defaultdict(list)
    for line in open(a.env_hits):
        p=line.rstrip().split('\t')
        if len(p)>=12 and p[0] in candidates: hits[p[0]].append((float(p[2]),int(p[3]),p[1]))
    selected=set()
    for q,arr in hits.items():
        seen=set()
        for ident,alen,s in sorted(arr,key=lambda x:(x[0],x[1]),reverse=True):
            if s in seen: continue
            seen.add(s); selected.add(s)
            if len(seen)==3: break
    selected &= set(eseq)
    with open(out/'mcrA_phylogeny_input.fasta','w') as fh:
        for rid in candidates: fh.write(f'>ASV_{rid}\n{asv[rid]}\n')
        for rid,seq in gseq.items(): fh.write(f'>GTDB_{rid}\n{seq}\n')
        for rid in sorted(selected): fh.write(f'>ENV_{rid}\n{eseq[rid]}\n')
    with open(out/'tree_metadata.tsv','w',newline='') as fh:
        fields=['tree_id','type','biological_reads','GTDB_identity','priority','taxonomy']; wr=csv.DictWriter(fh,fieldnames=fields,delimiter='\t'); wr.writeheader()
        for rid,row in candidates.items(): wr.writerow({'tree_id':f'ASV_{rid}','type':'ASV','biological_reads':row['biological_reads'],'GTDB_identity':row['GTDB_best_identity'],'priority':row['phylogeny_priority'],'taxonomy':row['GTDB_taxonomy']})
        for rid in gseq: wr.writerow({'tree_id':f'GTDB_{rid}','type':'GTDB_reference','taxonomy':gtax.get(rid,'')})
        for rid in selected: wr.writerow({'tree_id':f'ENV_{rid}','type':'environmental_reference','taxonomy':etax.get(rid,'')})
    print('candidate ASVs:',len(candidates),'GTDB refs:',len(gseq),'environmental refs:',len(selected),'total:',len(candidates)+len(gseq)+len(selected))
if __name__=='__main__': main()
