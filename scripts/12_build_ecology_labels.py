#!/usr/bin/env python3
"""Create a conservative final ecology label per ASV."""
import argparse,csv

def rank(tax,p):
    for x in tax.split(';'):
        x=x.strip()
        if x.startswith(p): return x[len(p):]
    return ''
def fallback(tax):
    if not tax or tax=='Unassigned': return 'Unresolved mcrA'
    g,f,o=rank(tax,'g__'),rank(tax,'f__'),rank(tax,'o__')
    if g=='Methanoperedens' or f=='Methanoperedenaceae': return 'ANME-2d / Methanoperedenaceae-related'
    if g.startswith('Methanovorans'): return 'ANME-3 / Methanovorans-related'
    if g.startswith('Methanocomedens'): return 'ANME-2a-related / Methanocomedens'
    return g or (f+'-related' if f else (o+'-related' if o else 'Unresolved mcrA'))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--master',required=True); ap.add_argument('--phylogeny'); ap.add_argument('--output',required=True); a=ap.parse_args()
    phy={r['ASV']:r for r in csv.DictReader(open(a.phylogeny),delimiter='\t')} if a.phylogeny else {}; rows=[]
    for r in csv.DictReader(open(a.master),delimiter='\t'):
        p=phy.get(r['ASV'])
        if p and p.get('phylogenetic_assignment'): label=p['phylogenetic_assignment']; source='phylogeny'; conf=p.get('assignment_confidence','')
        else: label=fallback(r.get('GTDB_taxonomy','')); source='GTDB'; conf=''
        rows.append({'ASV':r['ASV'],'final_ecology_label':label,'label_source':source,'label_confidence':conf})
    with open(a.output,'w',newline='') as out:
        wr=csv.DictWriter(out,fieldnames=list(rows[0]),delimiter='\t'); wr.writeheader(); wr.writerows(rows)
    print('wrote',len(rows),'ASV labels')
if __name__=='__main__': main()
