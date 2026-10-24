import csv, json, re

def natural_key(text):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]

with open('output.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

multi_resource_cases = []
differing_cases = []

for r in rows:
    cid = r['case_id']
    steps = json.loads(r['steps_json'])
    # Group steps by (phase, operation, system_id)
    groups = {}
    for s in steps:
        key = (s['phase'], s['operation'], s['system_id'])
        groups.setdefault(key, []).append(s['resource_id'])
    
    case_has_multi = False
    case_differs = False
    multi_groups = []
    for key, rids in groups.items():
        if len(rids) >= 2:
            case_has_multi = True
            lex_sorted = sorted(rids)
            nat_sorted = sorted(rids, key=natural_key)
            diff = (lex_sorted != nat_sorted)
            if diff:
                case_differs = True
            multi_groups.append((key, rids, lex_sorted, nat_sorted, diff))
    
    if case_has_multi:
        multi_resource_cases.append((cid, multi_groups))
    if case_differs:
        differing_cases.append((cid, multi_groups))

print(f"Total cases evaluated: {len(rows)}")
print(f"Cases with at least one (phase, op, system) group having 2+ resources: {len(multi_resource_cases)}")
print(f"Cases where lexical vs natural sorting produces DIFFERENT order: {len(differing_cases)}")
print("\n=== MULTI-RESOURCE GROUPS IN 518 OUTPUT ===")
for cid, m_groups in multi_resource_cases[:20]:
    print(f"\nCase: {cid}")
    for key, rids, lex_sorted, nat_sorted, diff in m_groups:
        print(f"  Group {key}: {rids}")
        print(f"    Lexical: {lex_sorted}")
        print(f"    Natural: {nat_sorted}")
        print(f"    Differs?: {diff}")

if differing_cases:
    print("\n=== CASES WHERE LEXICAL VS NATURAL DIFFERS ===")
    for cid, m_groups in differing_cases:
        print(f"Case: {cid}")
        for key, rids, lex_sorted, nat_sorted, diff in m_groups:
            if diff:
                print(f"  {key}:")
                print(f"    Lex: {lex_sorted}")
                print(f"    Nat: {nat_sorted}")
