#!/usr/bin/env python3
"""Assign conservative phylogenetic labels to targeted mcrA ASVs.

Requires Biopython. This script automates the principal clade logic used in the
project. It is intentionally conservative: the short (~417 bp) mcrA tree is used
for local placement, not deep evolutionary reconstruction.
"""
import argparse, csv
from Bio import Phylo


def support_pair(clade):
    """IQ-TREE treefile internal labels are commonly SH-aLRT/UFBoot."""
    if clade.name and '/' in str(clade.name):
        try:
            a,b=str(clade.name).split('/',1)
            return float(a),float(b)
        except ValueError:
            pass
    return '', ''


def extract_rank(tax, prefix):
    for item in (tax or '').split(';'):
        item=item.strip()
        if item.startswith(prefix):
            return item[len(prefix):]
    return ''


def related_label(tax):
    if not tax or tax == 'Unassigned':
        return 'Unresolved environmental mcrA lineage'
    g=extract_rank(tax,'g__'); f=extract_rank(tax,'f__'); o=extract_rank(tax,'o__')
    if g:
        return g + '-related'
    if f:
        return f + '-related'
    if o:
        return o + '-related'
    return 'Unresolved environmental mcrA lineage'


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--treefile', required=True, help='IQ-TREE ML tree with SH-aLRT/UFBoot labels')
    ap.add_argument('--tree-metadata', required=True)
    ap.add_argument('--master', required=True)
    ap.add_argument('--output', required=True)
    args=ap.parse_args()

    tree=Phylo.read(args.treefile,'newick')
    meta={r['tree_id']:r for r in csv.DictReader(open(args.tree_metadata), delimiter='\t')}
    master={r['ASV']:r for r in csv.DictReader(open(args.master), delimiter='\t')}
    terminals={t.name:t for t in tree.get_terminals()}

    def anchor_ids(test):
        return [tid for tid,r in meta.items()
                if r.get('type')=='GTDB_reference' and tid in terminals and test(r.get('taxonomy',''))]

    def anchored_clade(test):
        ids=anchor_ids(test)
        if len(ids)<2:
            return set(),('', ''),None
        mrca=tree.common_ancestor(ids)
        asvs={t.name[4:] for t in mrca.get_terminals() if t.name and t.name.startswith('ASV_')}
        return asvs,support_pair(mrca),mrca

    anme2d,sup2d,_=anchored_clade(lambda t:'f__Methanoperedenaceae' in t)
    anme3,sup3,_=anchored_clade(lambda t:'g__Methanovorans' in t)

    candidates=[r for r in meta.values() if r.get('type')=='ASV']
    rows=[]
    for r in candidates:
        asv=r['tree_id'].removeprefix('ASV_')
        m=master.get(asv,{})
        gtax=m.get('GTDB_taxonomy',r.get('taxonomy',''))
        ident=m.get('GTDB_best_identity',r.get('GTDB_identity',''))

        if asv in anme2d:
            label='ANME-2d / Methanoperedenaceae-related'; confidence='High'
            basis='Inside GTDB-anchored Methanoperedenaceae clade'; sh,uf=sup2d
        elif asv in anme3:
            label='ANME-3 / Methanovorans-related'; confidence='High'
            basis='Inside GTDB-anchored Methanovorans clade'; sh,uf=sup3
        elif 'f__Methanocomedenaceae' in (gtax or ''):
            label='ANME-2a-related / Methanocomedens'; confidence='Moderate'
            basis='GTDB Methanocomedenaceae placement; interpret locally'; sh=uf=''
        elif not gtax or gtax=='Unassigned':
            label='Unresolved environmental mcrA lineage'; confidence='Low'
            basis='No stable named GTDB placement; retain environmental evidence'; sh=uf=''
        else:
            label=related_label(gtax); confidence='Moderate'
            basis='Conservative GTDB-related placement; inspect local tree for manuscript claims'; sh=uf=''

        rows.append({
            'ASV':asv,
            'biological_reads':m.get('biological_reads',r.get('biological_reads','')),
            'priority':r.get('priority',''),
            'phylogenetic_assignment':label,
            'assignment_confidence':confidence,
            'assignment_basis':basis,
            'clade_SH_aLRT':sh,
            'clade_UFBoot':uf,
            'GTDB_vsearch_identity':ident,
            'GTDB_vsearch_taxonomy':gtax,
        })

    with open(args.output,'w',newline='') as out:
        wr=csv.DictWriter(out,fieldnames=list(rows[0]),delimiter='\t')
        wr.writeheader(); wr.writerows(rows)

    from collections import Counter
    c=Counter(x['phylogenetic_assignment'] for x in rows)
    print('ASVs:',len(rows))
    for k,n in c.most_common(): print(f'{k}: {n}')
    print('ANME-2d support:',sup2d)
    print('ANME-3 support:',sup3)

if __name__=='__main__':
    main()
