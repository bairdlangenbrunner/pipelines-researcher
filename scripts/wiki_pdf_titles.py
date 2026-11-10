"""List the PDF refs in wiki drafts with a first-page text head so titles can be filled into data/wiki_pdf_titles.json."""
import glob, re, subprocess, sys, os, hashlib, json
drafts = sys.argv[1]
urls = sorted({u for f in glob.glob(drafts + '/*/*.wiki') for u in re.findall(r'url=([^|]+\.pdf)\|', open(f).read(), re.I)})
os.makedirs('work/wiki_pdfs', exist_ok=True)
have = json.load(open('data/wiki_pdf_titles.json')) if os.path.exists('data/wiki_pdf_titles.json') else {}
for u in urls:
    if u in have: continue
    f = 'work/wiki_pdfs/' + hashlib.md5(u.encode()).hexdigest() + '.pdf'
    if not os.path.exists(f):
        subprocess.run(['curl', '-sL', '-m', '60', '-A', 'Mozilla/5.0', '-o', f, u])
    meta = subprocess.run(['pdfinfo', f], capture_output=True, text=True).stdout
    mt = re.search(r'^Title:\s*(.*)$', meta, re.M)
    head = subprocess.run(['pdftotext', '-l', '1', f, '-'], capture_output=True, text=True).stdout
    lines = [l.strip() for l in head.splitlines() if len(l.strip()) > 3][:8]
    print('##', u); print('  meta:', mt.group(1) if mt else None); [print('  |', l[:110]) for l in lines]
