"""Package the approved static site and its assets; never repo metadata.

dev  -> private preview (dev domain, submissions/contact links blocked)
main -> public static site, only when infra/deployment.json sets staticProduction
"""
import json, os, pathlib, re, shutil, tarfile, tempfile
root = pathlib.Path(__file__).resolve().parents[1]
sha = os.environ['GITHUB_SHA']
assert re.fullmatch('[0-9a-f]{40}', sha)
branch = os.environ['GITHUB_REF_NAME']
assert branch in ('dev', 'main'), 'Unknown branch'
if branch == 'main':
    assert json.loads((root/'infra/deployment.json').read_text())['staticProduction'] is True, 'Static production site is switched off'
with tempfile.TemporaryDirectory() as tmp:
    stage = pathlib.Path(tmp)
    app = stage / 'apps/web'
    public = app / 'public'
    public.mkdir(parents=True)
    for name in ['index.html','clone.css','clone.js','peddle-offer.js','sitemap.xml','robots.txt','css','external','frontend','images','locations','about','faq','contact','privacy-policy']:
        source = root / name
        if source.is_dir(): shutil.copytree(source, public/name)
        else: shutil.copy2(source, public/name)
    pages=sorted(public.glob('**/index.html'))
    if branch == 'dev':
        for p in pages+[public/'clone.js']:
            p.write_text(p.read_text().replace('www.usjunkcars.com','dev.usjunkcars.si').replace('usjunkcars.com','usjunkcars.si'))
        for page in pages:
            page.write_text(page.read_text().replace('</body>','<script src="/preview-guard.js"></script></body>'))
    if branch == 'dev': (public/'preview-guard.js').write_text('''
document.addEventListener('submit', event => {event.preventDefault(); event.stopImmediatePropagation(); alert('Design preview only. Search and lead submissions are not connected yet.');}, true);
document.addEventListener('click', event => {
  const link=event.target.closest('a'); if(!link) return;
  const target=link.getAttribute('href') || link.getAttribute('xlink:href') || '';
  if (/^(tel:|mailto:|https?:)/i.test(target) && !target.startsWith(location.origin)) {
    event.preventDefault(); event.stopImmediatePropagation(); alert('Design preview only. External contact links are disabled.');
  }
}, true);
''')
    shutil.copy2(root/'infra/vps/preview-server.cjs',app/'server.js')
    (stage/'release.json').write_text(json.dumps({'commit':sha,'branch':branch,'kind':'static-preview' if branch == 'dev' else 'static-site'}))
    with tarfile.open(root/'release.tar.gz','w:gz',dereference=True) as tf:
        tf.add(stage/'apps',arcname='apps')
        tf.add(stage/'release.json',arcname='release.json')
print('Packaged private dev preview' if branch == 'dev' else 'Packaged public static site for production')
