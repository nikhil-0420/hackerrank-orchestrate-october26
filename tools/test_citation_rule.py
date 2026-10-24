import csv, json
from collections import defaultdict

with open('dataset/sample_output.csv', 'r', encoding='utf-8') as f:
    sample_rows = list(csv.DictReader(f))

cases = {}
for r in sample_rows:
    cid = r['case_id']
    status = r['deletion_status']
    steps = json.loads(r['steps_json'])
    cases[cid] = (status, steps)

file_citations_per_case = {}
for cid, (status, steps) in cases.items():
    cited_files = set()
    cited_steps = []
    for s in steps:
        ev = s.get('evidence_id')
        if ev:
            cited_files.add(ev)
            cited_steps.append((s['step_no'], s['phase'], s['operation'], s['system_id'], s['resource_id'], s['state'], ev))
    file_citations_per_case[cid] = (cited_files, cited_steps)

print("=== CITATIONS PER CASE IN SAMPLE GROUND TRUTH ===")
for cid in sorted(cases.keys()):
    cfiles, csteps = file_citations_per_case[cid]
    print(f"{cid} ({cases[cid][0]}): {len(cfiles)} distinct files cited: {sorted(list(cfiles))}")
    if len(cfiles) > 1:
        print(f"  >>> MULTI-FILE CASE {cid}:")
        for st in csteps:
            print(f"      step {st[0]} | {st[1]} | {st[2]} | {st[3]} | {st[4]} | {st[5]} | {st[6]}")
