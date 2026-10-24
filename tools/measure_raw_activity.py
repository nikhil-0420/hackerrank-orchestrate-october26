import csv
from collections import Counter
from pathlib import Path

p = Path("dataset/system_activity.csv")

with open(p, "rb") as f:
    byte_lines = f.readlines()
print(f"Line count and wc -l: {len(byte_lines)}")

rows = list(csv.DictReader(open(p, encoding="utf-8")))
print(f"CSV data rows (excluding header): {len(rows)}")

counts = Counter(r["event_type"] for r in rows)
print("\nCounter of event_type:")
for k, v in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print("\n=== LINK_RESOURCE_IDENTITY ROWS ===")
for r in rows:
    if r["event_type"] == "LINK_RESOURCE_IDENTITY":
        print(f"activity_id: {r['activity_id']} | event_time: {r['event_time']} | source: {r['source_system']} | target: {r['target_system']} | resource_id: {r['resource_id']} | reported_result: {r['reported_result']}")
        print(f"  details: {r['details']}")

print("\n=== CLASSIFY_REQUEST ROWS ===")
for r in rows:
    if r["event_type"] == "CLASSIFY_REQUEST":
        print(f"activity_id: {r['activity_id']} | event_time: {r['event_time']} | source: {r['source_system']} | target: {r['target_system']} | resource_id: {r['resource_id']} | reported_result: {r['reported_result']}")
        print(f"  details: {r['details']}")
