import json, re

with open(r'c:\Users\ReddyA41\Desktop\AgenticAgent\resources\testrail_raw.txt', encoding='utf-8') as f:
    content = f.read()

# The snapshot line contains a doubly-escaped JSON string like: "{\"offset\":0,...}"
# Grab everything from the opening quote+brace to end of line, then json.loads the quoted string
m = re.search(r'generic \[ref=\w+\]: (\"\{.+)', content)
if not m:
    raise RuntimeError("Could not find JSON snapshot line")
# The captured group is a JSON-encoded string (starts/ends with "); decode it
quoted = m.group(1).rstrip()
# Remove trailing " if present (may be cut off if file is complete)
if not quoted.endswith('"'):
    quoted = quoted + '"'
# json.loads will unescape the \" and \/ sequences
inner = json.loads(quoted)
data = json.loads(inner)

clean = lambda s: re.sub(r'<[^>]+>', ' ', s or '').replace('&nbsp;', ' ').strip()

print(f'Total cases: {data["size"]}')
for c in data['cases']:
    steps = c.get('custom_steps_separated') or []
    title = c['title']
    preconds = clean(c.get('custom_preconds') or '')
    print(f'\n=== [{c["id"]}] {title} ===')
    if preconds:
        print(f'  PRE: {preconds[:300]}')
    for i, s in enumerate(steps, 1):
        ct = clean(s.get('content', ''))
        et = clean(s.get('expected', '') or '')
        print(f'  STEP {i}: {ct[:300]}')
        if et:
            print(f'    EXPECTED: {et[:300]}')

with open(r'c:\Users\ReddyA41\Desktop\AgenticAgent\resources\testrail_cases.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
print('\nSaved to testrail_cases.json')
