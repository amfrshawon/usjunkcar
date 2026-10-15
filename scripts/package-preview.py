"""Package only the approved static homepage and its assets; never repo metadata."""
import json, os, pathlib, re, shutil, tarfile, tempfile
root = pathlib.Path(__file__).resolve().parents[1]
sha = os.environ['GITHUB_SHA']
assert re.fullmatch('[0-9a-f]{40}', sha)
assert os.environ['GITHUB_REF_NAME'] == 'dev', 'Preview cannot target main'
with tempfile.TemporaryDirectory() as tmp:
    stage = pathlib.Path(tmp)
    app = stage / 'apps/web'
    public = app / 'public'
    public.mkdir(parents=True)
    for name in ['index.html','clone.css','clone.js','css','external','frontend','images']:
        source = root / name
        if source.is_dir(): shutil.copytree(source, public/name)
        else: shutil.copy2(source, public/name)
    for name in ['index.html','clone.js']:
        p=public/name
        p.write_text(p.read_text().replace('www.usjunkcars.com','dev.usjunkcars.si').replace('usjunkcars.com','usjunkcars.si'))
    page=public/'index.html'
    page.write_text(page.read_text().replace('</body>','<script src="/preview-guard.js"></script></body>'))
    (public/'preview-guard.js').write_text('''
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
    (stage/'release.json').write_text(json.dumps({'commit':sha,'branch':'dev','kind':'static-preview'}))
    with tarfile.open(root/'release.tar.gz','w:gz',dereference=True) as tf:
        tf.add(stage/'apps',arcname='apps')
        tf.add(stage/'release.json',arcname='release.json')
print('Packaged private dev homepage preview')
