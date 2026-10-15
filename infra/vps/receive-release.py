#!/usr/bin/python3
"""Root-owned, forced-command SSH receiver. Runs as an isolated non-root user."""
import fcntl
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request

MAX_BYTES = 400 * 1024 * 1024

def validate_manifest(manifest, sha, branch):
    kinds = ['nextjs-standalone', 'static-preview'] if branch == 'dev' else ['nextjs-standalone']
    if manifest.get('kind') not in kinds or manifest != {'commit': sha, 'branch': branch, 'kind': manifest.get('kind')}:
        raise ValueError('Release identity mismatch')

def validate_members(members):
    total = 0
    for member in members:
        path = PurePosixPath(member.name)
        if path.is_absolute() or '..' in path.parts or not path.parts:
            raise ValueError('Unsafe archive path')
        if not (member.isfile() or member.isdir()):
            raise ValueError('Archive links and special files are forbidden; package with dereferenced links')
        if any(p.startswith('.env') or p in ['.ssh', '.git'] for p in path.parts):
            raise ValueError('Secrets/source-control metadata must not be packaged')
        total += member.size
        if total > MAX_BYTES:
            raise ValueError('Expanded artifact too large')

def health(port, sha, environment):
    for _ in range(30):
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/v1/health', timeout=2) as r:
                data = json.load(r).get('data', {})
                if r.status == 200 and data.get('status') == 'ok' and data.get('commit') == sha and data.get('environment') == environment:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False

def main():
    branch = sys.argv[1]
    if branch not in ['dev', 'main']:
        raise ValueError('Invalid environment')
    command = re.fullmatch(r'deploy ([0-9a-f]{40})', os.environ.get('SSH_ORIGINAL_COMMAND', ''))
    if not command:
        raise ValueError('Only deploy SHA is permitted')
    sha = command.group(1)
    root = Path('/srv/usjunkcars') / branch
    environment = 'development' if branch == 'dev' else 'production'
    port = 3401 if branch == 'dev' else 3400
    stage_port = port + 2
    with (root / 'deploy.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with tempfile.TemporaryDirectory(prefix='incoming-', dir=root) as incoming:
            incoming = Path(incoming)
            archive = incoming / 'release.tar.gz'
            with archive.open('wb') as out:
                size = 0
                while chunk := sys.stdin.buffer.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise ValueError('Compressed artifact too large')
                    out.write(chunk)
            stage = incoming / 'app'
            stage.mkdir()
            with tarfile.open(archive) as tf:
                members = tf.getmembers()
                validate_members(members)
                tf.extractall(stage, members=members, filter='data')
            manifest = json.loads((stage / 'release.json').read_text())
            validate_manifest(manifest, sha, branch)
            entry = stage / 'apps/web/server.js'
            if not entry.is_file():
                raise ValueError('Standalone Next.js entrypoint missing')
            cache = stage / 'apps/web/.next/cache'
            cache.parent.mkdir(parents=True, exist_ok=True)
            if cache.is_dir(): shutil.rmtree(cache)
            elif cache.exists(): cache.unlink()
            cache.symlink_to(root / 'cache', target_is_directory=True)
            # Environment files are systemd-compatible KEY=value lines with no multiline values.
            import shlex
            env = {'PATH': '/usr/bin:/bin', 'NODE_ENV': 'production', 'HOSTNAME': '127.0.0.1'}
            for line in Path(f'/etc/usjunkcars/{branch}.env').read_text().splitlines():
                if line.strip() and not line.lstrip().startswith('#'):
                    key, value = shlex.split(line)[0].split('=', 1)
                    env[key] = value
            env.update(PORT=str(stage_port), RELEASE_SHA=sha, APP_ENV=environment)
            candidate = subprocess.Popen(['/usr/local/lib/usjunkcars/node/bin/node', str(entry)], env=env, cwd=stage,
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            try:
                if not health(stage_port, sha, environment):
                    raise ValueError('Candidate health failed; current release unchanged')
            finally:
                try: os.killpg(candidate.pid, signal.SIGTERM)
                except ProcessLookupError: pass
                try: candidate.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(candidate.pid, signal.SIGKILL)
                    candidate.wait()
            # Public repository check also prevents stale runs overtaking a newer reviewed push.
            req = urllib.request.Request(f'https://api.github.com/repos/amfrshawon/usjunkcar/git/ref/heads/{branch}', headers={'User-Agent':'usjunkcars-release'})
            with urllib.request.urlopen(req, timeout=15) as r:
                if json.load(r)['object']['sha'] != sha:
                    raise ValueError('Branch advanced; refusing stale deployment')
            release = root / 'releases' / (sha + '-' + str(time.time_ns()))
            shutil.move(str(stage), release)
            (release / '.release.env').write_text(f'RELEASE_SHA={sha}\n')
            current = root / 'current'
            old = current.resolve() if current.is_symlink() else None
            next_link = root / 'next'
            next_link.unlink(missing_ok=True)
            next_link.symlink_to(release)
            next_link.replace(current)
            service = f'usjunkcars-{branch}.service'
            try:
                subprocess.run(['sudo','-n','/usr/bin/systemctl','restart',service],check=True)
                if not health(port, sha, environment):
                    raise ValueError('Live health failed')
            except Exception:
                current.unlink(missing_ok=True)
                if old:
                    current.symlink_to(old)
                subprocess.run(['sudo','-n','/usr/bin/systemctl','restart',service],check=True)
                raise
            print(f'Deployed {sha} to {branch}; health verified')

if __name__ == '__main__':
    try: main()
    except Exception as error:
        print(f'Deployment refused: {type(error).__name__}: {error}', file=sys.stderr)
        sys.exit(1)
