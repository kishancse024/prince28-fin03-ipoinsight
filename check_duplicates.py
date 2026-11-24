import json
from collections import defaultdict

groups = defaultdict(list)
with open("data/manifest.jsonl", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        groups[item["sha256"]].append(item)

duplicates = {h: files for h, files in groups.items() if len({x["url"] for x in files}) > 1}
for sha, files in duplicates.items():
    print(f"\nSHA256: {sha}")
    for item in files:
        print(item["url"])
print(f"\nDuplicate groups: {len(duplicates)}")
print(f"Extra downloads: {sum(len(v) - 1 for v in duplicates.values())}")
