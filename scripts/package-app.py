"""Build and package the Next.js standalone release for the VPS receiver.

CI (deploy job):  pnpm run ci:package   -> release.tar.gz with apps/web/server.js, release.json
Local/tests:      python3 scripts/package-app.py --stage DIR --env development [--no-build]
"""
import argparse, json, os, pathlib, re, shutil, subprocess, sys, tarfile, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
WEB = ROOT / 'apps/web'


def build(env: str) -> None:
    subprocess.run(['pnpm', '--filter', '@usjunkcars/web', 'build'], cwd=ROOT, check=True,
                   env=dict(os.environ, APP_ENV=env, NEXT_TELEMETRY_DISABLED='1'))


def assemble(stage: pathlib.Path) -> None:
    """Standalone server plus its static assets, with every symlink resolved (the receiver rejects links)."""
    standalone = WEB / '.next/standalone'
    if not (standalone / 'apps/web/server.js').is_file():
        sys.exit('Standalone build missing; run the build first')
    shutil.copytree(standalone, stage, symlinks=False, dirs_exist_ok=True)
    shutil.copytree(WEB / '.next/static', stage / 'apps/web/.next/static', symlinks=False, dirs_exist_ok=True)
    shutil.copytree(WEB / 'public', stage / 'apps/web/public', symlinks=False, dirs_exist_ok=True)
    shutil.rmtree(stage / 'apps/web/.next/cache', ignore_errors=True)
    leaked = [p for p in stage.rglob('*') if p.name.startswith('.env') or p.name in ('.git', '.ssh')]
    if leaked:
        sys.exit(f'Refusing to package secrets or repository metadata: {leaked[:3]}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', help='assemble into this directory instead of writing release.tar.gz')
    parser.add_argument('--env', help='APP_ENV for a local build (CI derives it from the branch)')
    parser.add_argument('--no-build', action='store_true')
    args = parser.parse_args()

    if args.stage:
        if not args.no_build:
            build(args.env or 'development')
        assemble(pathlib.Path(args.stage))
        return

    sha, branch = os.environ['GITHUB_SHA'], os.environ['GITHUB_REF_NAME']
    if not re.fullmatch('[0-9a-f]{40}', sha):
        sys.exit('Invalid commit')
    target = json.loads((ROOT / 'infra/deployment.json').read_text())['environments'].get(branch)
    if not target:
        sys.exit(f'No deployment target for {branch}')
    if os.environ.get('APP_ENV') != target['environment'] or os.environ.get('SITE_URL') != target['origin']:
        sys.exit(f'APP_ENV/SITE_URL must be {target["environment"]}/{target["origin"]} for {branch}')

    build(target['environment'])
    with tempfile.TemporaryDirectory() as tmp:
        stage = pathlib.Path(tmp) / 'stage'
        assemble(stage)
        (stage / 'release.json').write_text(json.dumps({'commit': sha, 'branch': branch, 'kind': 'nextjs-standalone'}))
        with tarfile.open(ROOT / 'release.tar.gz', 'w:gz', dereference=True) as tf:
            for item in sorted(stage.iterdir()):
                tf.add(item, arcname=item.name)
    print(f'Packaged {target["environment"]} release {sha[:7]} for {target["origin"]}')


if __name__ == '__main__':
    main()
