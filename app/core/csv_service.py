import csv

def import_auth(path: str) -> list[str]:
    rows = [r for r in csv.reader(open(path, newline='', encoding='utf-8'))
            if any(c.strip() for c in r)]
    start = 1 if rows and rows[0] and not rows[0][0].strip().lstrip('+').isdigit() else 0
    return [rows[i][0].strip() for i in range(start, min(start+20, len(rows)))]

def export_auth(path: str, nums: list[str]) -> None:
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(["number"])
        for n in nums:
            if n: w.writerow([n])

def import_gsm(path: str) -> list[tuple[str,str]]:
    rows = [r for r in csv.reader(open(path, newline='', encoding='utf-8'))
            if any(c.strip() for c in r)]
    start = 1 if rows and rows[0] and (rows[0][0].lower() in ("label","etiqueta")) else 0
    pairs = []
    for i in range(start, min(start+10, len(rows))):
        lab = rows[i][0].strip() if len(rows[i])>0 else ""
        num = rows[i][1].strip() if len(rows[i])>1 else ""
        pairs.append((lab,num))
    return pairs

def export_gsm(path: str, pairs: list[tuple[str,str]]) -> None:
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(["label","number"])
        for lab, num in pairs:
            if lab or num: w.writerow([lab, num])
