#!/usr/bin/env python3
"""Combine ASV counts, controls, GTDB taxonomy/hits, and environmental taxonomy/hits."""
import argparse,csv,re

def read_query_taxonomy(path):
    return {r['Feature ID']:(r.get('Taxon',''),r.get('Consensus','')) for r in csv.DictReader(open(path),delimiter='\t')}
def read_ref_tax(path):
    d={}
    for line in open(path):
        p=line.rstrip().split('\t',1)
        if len(p)==2 and p[0] not in {'Feature ID','FeatureID'}: d[p[0]]=p[1]
    return d
def read_best_hits(path):
    d={}
    for line in open(path):
        p=line.rstrip().split('\t')
        if len(p)<12: continue
        rec=(float(p[2]),int(p[3]),p[1]); q=p[0]
        if q not in d or rec[:2]>d[q][:2]: d[q]=rec
    return d
def deepest(tax):
    names={'k__':'Kingdom','d__':'Domain','p__':'Phylum','c__':'Class','o__':'Order','f__':'Family','g__':'Genus','s__':'Species'}; d='Unassigned'
    for item in tax.split(';'):
        item=item.strip()
        for pre,rank in names.items():
            if item.startswith(pre):
                v=item[len(pre):].strip().lower()
                if v and v not in {'unclassified','uncultured','unknown'}: d=rank
    return d

def main():
    ap=argparse.ArgumentParser()
    for x in ['feature-table','env-taxonomy','env-hits','env-ref-taxonomy','gtdb-taxonomy','gtdb-hits','gtdb-ref-taxonomy','output']:
        ap.add_argument('--'+x,required=True)
    a=ap.parse_args(); et=read_query_taxonomy(a.env_taxonomy); gt=read_query_taxonomy(a.gtdb_taxonomy)
    eh=read_best_hits(a.env_hits); gh=read_best_hits(a.gtdb_hits); ert=read_ref_tax(a.env_ref_taxonomy); grt=read_ref_tax(a.gtdb_ref_taxonomy)
    with open(a.feature_table) as fh:
        first=fh.readline()
        if not first.startswith('# Constructed from biom'): fh.seek(0)
        head=fh.readline().rstrip().split('\t'); samples=head[1:]
        ctrl=[i for i,s in enumerate(samples) if re.search(r'blank|ntc',s,re.I)]; bio=[i for i in range(len(samples)) if i not in ctrl]
        rows=[]
        for line in fh:
            p=line.rstrip().split('\t'); asv=p[0]; vals=[float(x) for x in p[1:]]
            br=int(sum(vals[i] for i in bio)); cr=int(sum(vals[i] for i in ctrl)); bp=sum(vals[i]>0 for i in bio); cp=sum(vals[i]>0 for i in ctrl)
            etax,econs=et.get(asv,('','')); gtax,gcons=gt.get(asv,('','')); E=eh.get(asv); G=gh.get(asv)
            epid=ealen=esub=esubtax=''; gpid=galen=gsub=gsubtax=''
            if E: epid,ealen,esub=E; esubtax=ert.get(esub,'')
            if G: gpid,galen,gsub=G; gsubtax=grt.get(gsub,'')
            ibin='No_GTDB_hit' if gpid=='' else ('GTDB_>=95' if gpid>=95 else ('GTDB_90-95' if gpid>=90 else 'GTDB_80-90'))
            priority='control_only' if br==0 else (('HIGH' if br>=10000 else ('MEDIUM' if br>=1000 else 'LOW')) if gpid=='' or gpid<90 else '')
            rows.append({'ASV':asv,'biological_reads':br,'control_reads':cr,'biological_prevalence':bp,'control_prevalence':cp,
              'GTDB_taxonomy':gtax,'GTDB_deepest_rank':deepest(gtax),'GTDB_consensus':gcons,'GTDB_best_hit':gsub,'GTDB_best_identity':gpid,
              'GTDB_best_alignment_length':galen,'GTDB_best_hit_taxonomy':gsubtax,'GTDB_identity_bin':ibin,'environmental_taxonomy':etax,
              'environmental_consensus':econs,'environmental_best_hit':esub,'environmental_best_identity':epid,
              'environmental_best_alignment_length':ealen,'environmental_best_hit_taxonomy':esubtax,'phylogeny_priority':priority})
    rows.sort(key=lambda x:x['biological_reads'],reverse=True)
    with open(a.output,'w',newline='') as out:
        wr=csv.DictWriter(out,fieldnames=list(rows[0]),delimiter='\t'); wr.writeheader(); wr.writerows(rows)
    print('ASVs:',len(rows)); print('Biological reads:',sum(r['biological_reads'] for r in rows))
if __name__=='__main__': main()
