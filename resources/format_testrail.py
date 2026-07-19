import json, re

def clean(html):
    if not html:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', html)
    text = re.sub(r'<li>', '\n  - ', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

with open(r'C:\Users\ReddyA41\Desktop\AgenticAgent\resources\testrail_cases.json', encoding='utf-8') as f:
    data = json.load(f)

lines = []
lines.append("DUNE TEST CATALOGUE — Section 9339201")
lines.append("=" * 70)

for idx, c in enumerate(data['cases'], 1):
    lines.append(f"\nTest Case {idx} of {data['size']}")
    lines.append(f"ID      : C{c['id']}")
    lines.append(f"Title   : {c['title']}")
    lines.append("-" * 70)

    preconds = clean(c.get('custom_preconds') or '')
    if preconds:
        lines.append("Pre-conditions:")
        for ln in preconds.splitlines():
            if ln.strip():
                lines.append(f"  {ln.strip()}")
        lines.append("")

    steps = c.get('custom_steps_separated') or []
    if steps:
        lines.append("Steps:")
        for i, s in enumerate(steps, 1):
            content  = clean(s.get('content', ''))
            expected = clean(s.get('expected', '') or '')
            lines.append(f"\n  Step {i}:")
            for ln in content.splitlines():
                if ln.strip():
                    lines.append(f"    {ln.strip()}")
            if expected:
                lines.append(f"    Expected Result:")
                for ln in expected.splitlines():
                    if ln.strip():
                        lines.append(f"      {ln.strip()}")

    lines.append("\n" + "=" * 70)

output = '\n'.join(lines)
out_path = r'C:\Users\ReddyA41\Desktop\AgenticAgent\resources\testrail_cases.txt'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(output)
print(f"Written to {out_path}")
print(f"Total characters: {len(output)}")
