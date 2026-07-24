#!/usr/bin/env python3
"""Fail-closed validation for the ALISTAIRE portfolio currentness packet."""
from __future__ import annotations
import argparse, copy, json, math, re
from pathlib import Path
from typing import Any

PROFILE_ID='ALISTAIRE-PORTFOLIO-AUTHORITY-CURRENTNESS-v1'
CORRECTION_ID='ALISTAIRE-PORTFOLIO-AUTHORITY-CURRENTNESS-CORRECTION-v2'
STATUS='PORTFOLIO_AUTHORITY_CURRENTNESS_RECONCILED_CONFLICTS_DISSENT_AND_VACANCIES_RECORDED_BINDINGS_UNACCEPTED'
PARENT='39357f4d4df76bf969e08dc8c2c3212766345bce'
BASE_PACKET='0fdf5accfd9525820e94321321ea4c3f1db24c14'
SEEKER='5ddb831250d537622035f04e0e30488ec4fdd15a'
JUSTICE='33db861320c29e71059ec390cbdafe04c8f8793d'
GENOMES_OLD='c29bd681bab680e467903784527776d284469a3d'
GENOMES='75d675d274b504965836aadf8e0792d606d6c3fb'
GENOMES_RUNS={30065914753,30065914758,30065914798}
GENOMES_ARTIFACTS={8586223512,8586223517,8586221536}
SHA=re.compile(r'^[0-9a-f]{40}$')
DIGEST=re.compile(r'^sha256:[0-9a-f]{64}$')
REPOS={'aevespers2/0','aevespers2/1','aevespers2/AionUi','aevespers2/ALISTAIRE-','aevespers2/Alistaire-agi','aevespers2/Bridge','aevespers2/datarepo-temporal-invariants','aevespers2/grok-build-alistaire','aevespers2/JusticeForMe','aevespers2/Misc','aevespers2/qsio-kernel','aevespers2/QSO-DIGITALIS','aevespers2/QSO-FABRIC','aevespers2/qso-field.github.io','aevespers2/QSO-GENOMES','aevespers2/QSO-PAYMENTS','aevespers2/QSO-SEEKER','aevespers2/QSO-STUDIO','aevespers2/QuantumStateObjects'}

class ValidationError(ValueError): pass

def require(ok: bool,msg: str)->None:
    if not ok: raise ValidationError(msg)

def pairs(items):
    out={}
    for k,v in items:
        if k in out: raise ValidationError(f'duplicate JSON key: {k}')
        out[k]=v
    return out

def reject_constant(v): raise ValidationError(f'non-standard numeric constant: {v}')

def load_json(path: Path)->dict[str,Any]:
    try: text=path.read_text(encoding='utf-8',errors='strict')
    except (OSError,UnicodeError) as e: raise ValidationError(f'cannot read strict UTF-8 JSON: {e}') from e
    try: data=json.loads(text,object_pairs_hook=pairs,parse_constant=reject_constant)
    except (json.JSONDecodeError,ValidationError) as e: raise ValidationError(f'invalid JSON: {e}') from e
    require(isinstance(data,dict),'JSON root must be an object')
    return data

load_profile=load_json

def finite(v:Any,path='$')->None:
    if isinstance(v,float): require(math.isfinite(v),f'non-finite number at {path}')
    elif isinstance(v,dict):
        for k,x in v.items(): finite(x,f'{path}.{k}')
    elif isinstance(v,list):
        for i,x in enumerate(v): finite(x,f'{path}[{i}]')

def repo_map(p):
    rows=p.get('repositories'); require(isinstance(rows,list) and len(rows)==19,'exactly 19 repositories required')
    out={}
    for row in rows:
        require(isinstance(row,dict),'repository entry must be object')
        name=row.get('repository'); require(isinstance(name,str) and name,'repository identity missing')
        require(name not in out,f'duplicate repository: {name}'); out[name]=row
        src=row.get('source'); require(isinstance(src,dict),'source missing')
        require(src.get('kind') in {'pull_request','default_branch'},f'{name}: invalid source kind')
        require(isinstance(src.get('sha'),str) and SHA.fullmatch(src['sha']),f'{name}: invalid exact SHA')
        require(src.get('state') in {'open_draft','merged'},f'{name}: invalid state')
        require(src.get('mergeability') in {'mergeable','conflicting','unknown','not_applicable'},f'{name}: invalid mergeability')
        for field in ('corridor','currentness','semantic_owner','route_owner'):
            require(isinstance(row.get(field),str) and row[field],f'{name}: missing {field}')
        for field in ('blockers','vacancies'):
            require(isinstance(row.get(field),list) and row[field],f'{name}: {field} must be non-empty')
    require(set(out)==REPOS,'repository coverage differs from owned portfolio')
    return out

def validate_correction(c):
    finite(c)
    require(c.get('profile_id')==CORRECTION_ID,'unexpected correction profile_id')
    require(c.get('base_profile_id')==PROFILE_ID,'correction base profile drift')
    require(c.get('base_packet_generation')==BASE_PACKET,'correction base generation drift')
    require(c.get('reviewed_at')=='2026-07-24','correction review date drift')
    require(c.get('authority_effect')=='NONE','correction authority effect must remain NONE')
    rows=c.get('corrections'); require(isinstance(rows,list) and len(rows)==1,'exactly one bounded correction required')
    row=rows[0]; require(row.get('repository')=='aevespers2/QSO-GENOMES','correction repository drift'); require(row.get('pull_request')==15,'QSO-GENOMES PR drift')
    old=row.get('superseded'); new=row.get('corrected')
    require(isinstance(old,dict) and old.get('sha')==GENOMES_OLD,'superseded QSO-GENOMES head missing')
    require(old.get('disposition')=='SUPERSEDED_EXACT_HEAD_EVIDENCE_PRESERVED','superseded evidence disposition missing')
    require(isinstance(new,dict) and new.get('sha')==GENOMES,'corrected QSO-GENOMES head drift')
    require(new.get('state')=='open_draft' and new.get('mergeability')=='mergeable','QSO-GENOMES candidate state drift')
    require(new.get('currentness')=='multiple_active_lineages','QSO-GENOMES lineage classification drift')
    evidence=row.get('evidence'); require(isinstance(evidence,list) and len(evidence)==3,'QSO-GENOMES evidence set incomplete')
    require({x.get('run_id') for x in evidence}==GENOMES_RUNS,'QSO-GENOMES workflow runs drift')
    require({x.get('artifact_id') for x in evidence}==GENOMES_ARTIFACTS,'QSO-GENOMES artifacts drift')
    for item in evidence: require(isinstance(item.get('digest'),str) and DIGEST.fullmatch(item['digest']),'QSO-GENOMES artifact digest invalid')
    require(isinstance(row.get('preserved_blockers'),list) and len(row['preserved_blockers'])>=3,'QSO-GENOMES blockers not preserved')
    require(isinstance(row.get('vacancies'),list) and len(row['vacancies'])>=3,'QSO-GENOMES vacancies not preserved')
    skills=c.get('fysa_120',{}); require(skills.get('evidence_level')=='applied','correction skill evidence must remain applied'); require(str(skills.get('proposed_refinement','')).startswith('013-K'),'013-K missing')
    require('do not establish competence' in skills.get('authority_boundary',''),'correction skill authority boundary missing')
    safety=c.get('safety_boundaries'); require(isinstance(safety,dict) and safety and all(v is False for v in safety.values()),'correction operational authority flags must remain false')
    return row

def apply_correction(p,c):
    row=validate_correction(c)
    effective=copy.deepcopy(p)
    by=repo_map(effective)
    q=by['aevespers2/QSO-GENOMES']
    require(q['source']['sha']==GENOMES_OLD,'base QSO-GENOMES tuple no longer matches correction source')
    new=row['corrected']
    q['source']['sha']=new['sha']; q['source']['state']=new['state']; q['source']['mergeability']=new['mergeability']; q['currentness']=new['currentness']
    q['correction_history']=[{'superseded_sha':row['superseded']['sha'],'corrected_sha':new['sha'],'disposition':row['superseded']['disposition'],'evidence_runs':sorted(GENOMES_RUNS),'artifact_ids':sorted(GENOMES_ARTIFACTS)}]
    q['blockers']=copy.deepcopy(row['preserved_blockers']); q['vacancies']=copy.deepcopy(row['vacancies'])
    return effective

def validate_profile(p):
    finite(p)
    require(p.get('profile_id')==PROFILE_ID,'unexpected profile_id')
    require(p.get('status')==STATUS,'unexpected controlled status')
    require(p.get('reviewed_at')=='2026-07-24','review date drift')
    require(p.get('authority_effect')=='NONE','authority effect must remain NONE')
    require(p.get('snapshot_parent')==PARENT,'snapshot parent drift')
    require('never claim an unknown future SHA' in p.get('snapshot_rule',''),'self-reference-safe snapshot rule missing')
    by=repo_map(p)
    a=by['aevespers2/ALISTAIRE-']; require(a['source']['sha']==PARENT and a['currentness']=='snapshot_parent_generation','ALISTAIRE snapshot classification drift')
    s=by['aevespers2/QSO-SEEKER']; require(s['source']['sha']==SEEKER,'QSO-SEEKER corrected head drift'); require(s.get('body_declared_sha')==SEEKER,'QSO-SEEKER body/metadata mismatch')
    hist=s.get('correction_history'); require(isinstance(hist,list) and len(hist)==1,'QSO-SEEKER correction history missing')
    h=hist[0]; require(h.get('corrected_sha')==SEEKER and h.get('disposition')=='STALE_HEAD_CORRECTED_EXACT_HEAD_VALIDATED','QSO-SEEKER correction disposition missing'); require(len(h.get('evidence_runs',[]))==4,'QSO-SEEKER evidence set incomplete')
    require(any('cancelling concurrency' in x for x in s['blockers']),'QSO-SEEKER remaining workflow debt missing')
    j=by['aevespers2/JusticeForMe']; require(j['source']['sha']==JUSTICE,'JusticeForMe rebind drift'); require(j['currentness']=='current_candidate_resulting_validation_pending','JusticeForMe evidence qualification missing'); require(any('resulting-head workflow evidence' in x for x in j['blockers']),'JusticeForMe pending evidence boundary missing')
    g=by['aevespers2/QSO-GENOMES']; require(g['source']['sha']==GENOMES,'QSO-GENOMES corrected head drift'); require(g['currentness']=='multiple_active_lineages','QSO-GENOMES currentness drift')
    gh=g.get('correction_history'); require(isinstance(gh,list) and len(gh)==1 and gh[0].get('superseded_sha')==GENOMES_OLD,'QSO-GENOMES correction history missing')
    for name in ('aevespers2/0','aevespers2/JusticeForMe'): require(by[name]['source']['mergeability']=='conflicting',f'{name}: current conflict must be preserved')
    for name in ('aevespers2/Alistaire-agi','aevespers2/1','aevespers2/QSO-GENOMES','aevespers2/QuantumStateObjects','aevespers2/QSO-FABRIC','aevespers2/qso-field.github.io'): require(by[name]['currentness']=='multiple_active_lineages',f'{name}: multiple lineage classification missing')
    t=by['aevespers2/datarepo-temporal-invariants']; require(any('Actions execution' in x for x in t['blockers']),'temporal missing-workflow obstruction missing')
    require({x.get('id') for x in p.get('vacancies',[])}=={f'V{i}' for i in range(1,11)},'vacancy coverage must be V1-V10')
    require(p.get('dissent')=='NO_VERIFIED_HUMAN_DISSENT_LOCATED_IN_REVIEWED_CURRENTNESS_SNAPSHOT','dissent boundary missing')
    skills=p.get('fysa_120',{}); require(skills.get('evidence_level')=='applied','skill evidence must remain applied'); require(str(skills.get('proposed_subdivision','')).startswith('013-I'),'013-I missing'); require(str(skills.get('proposed_refinement','')).startswith('013-J'),'013-J missing'); require('do not establish competence' in skills.get('authority_boundary',''),'skill authority boundary missing')
    safety=p.get('safety_boundaries'); require(isinstance(safety,dict) and safety and all(v is False for v in safety.values()),'operational authority flags must remain false')
    return {'result':'PASS','profile_id':PROFILE_ID,'status':STATUS,'repository_count':19,'vacancy_count':10,'corrected_source_count':4,'correction_overlay_count':1,'authority_effect':'NONE'}

def validate_repository(root:Path):
    base=load_json(root/'docs'/'portfolio-authority-currentness-v1.json')
    correction=load_json(root/'docs'/'portfolio-authority-currentness-correction-v2.json')
    report=validate_profile(apply_correction(base,correction))
    guide=(root/'docs'/'portfolio-authority-currentness-review.md').read_text(encoding='utf-8',errors='strict')
    markers=(STATUS,'Authority effect: `NONE`','```mermaid','### Prose equivalent','QSO-SEEKER PR #14 currently resolves to head',GENOMES_OLD,GENOMES,'portfolio-authority-currentness-correction-v2.json','NO_VERIFIED_HUMAN_DISSENT_LOCATED_IN_REVIEWED_CURRENTNESS_SNAPSHOT','V1–V10','013-I — Cross-repository authority-currentness, conflict, dissent, and vacancy reconciliation','013-J — Correction-linked exact-source rebinding and self-reference-safe portfolio snapshots','013-K — Correction-overlay composition for exact-source portfolio snapshots')
    for m in markers: require(m in guide,f'guide marker missing: {m}')
    for r in sorted(REPOS): require(f'`{r}`' in guide,f'guide omits repository: {r}')
    for path in ('taskchain.md','punchlist.md','release.md','changelog.md'):
        text=(root/path).read_text(encoding='utf-8',errors='strict'); require(STATUS in text,f'{path} omits status'); require('portfolio-authority-currentness-review.md' in text,f'{path} omits guide link'); require('013-I' in text,f'{path} omits established subdivision')
    wf=(root/'.github/workflows/portfolio-authority-currentness.yml').read_text(encoding='utf-8',errors='strict')
    for m in ('permissions:\n  contents: read','cancel-in-progress: false','github.event.pull_request.head.sha || github.sha','persist-credentials: false','if: always()','Fail closed after evidence retention'):
        require(m in wf,f'workflow control missing: {m}')
    return report

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]); ap.add_argument('--submitted-sha'); a=ap.parse_args()
    try:
        r=validate_repository(a.root)
        if a.submitted_sha: require(SHA.fullmatch(a.submitted_sha) is not None,'submitted SHA must be 40 lowercase hex'); r['submitted_sha']=a.submitted_sha
        print(json.dumps(r,sort_keys=True,indent=2)); return 0
    except (OSError,UnicodeError,ValidationError) as e:
        print(json.dumps({'result':'FAIL','error':str(e)},sort_keys=True,indent=2)); return 1
if __name__=='__main__': raise SystemExit(main())
