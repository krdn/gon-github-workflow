#!/usr/bin/env python3
"""GitHub 중심 개발 워크플로. Python 표준 라이브러리와 gh만 사용한다."""
import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'ccpm': 'automazeio/ccpm',
    'spec-kit': 'github/spec-kit',
    'gsd-core': 'open-gsd/gsd-core',
    'gh-aw': 'github/gh-aw',
    'claude-code-action': 'anthropics/claude-code-action',
}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        temporary = Path(stream.name)
    temporary.replace(path)


def run(*args, input_data=None):
    env = dict(os.environ)
    if args[0] == 'git':
        env['GIT_TERMINAL_PROMPT'] = '0'
    result = subprocess.run(args, text=True, capture_output=True, timeout=120,
                            input=input_data, env=env)
    if result.returncode:
        raise ValueError(f'명령 실패 ({args[0]}): {result.stderr.strip()}')
    return result.stdout.strip()


def api(endpoint, missing_ok=False):
    result = subprocess.run(['gh', 'api', '--method', 'GET', endpoint],
                            text=True, capture_output=True, timeout=120)
    if result.returncode:
        if missing_ok and 'HTTP 404' in result.stderr:
            return None
        raise ValueError(f'GitHub 조회 실패: {result.stderr.strip()}')
    return json.loads(result.stdout)


def inspect_sources():
    sources = {}
    for name, repo in SOURCES.items():
        metadata = api(f'repos/{repo}')
        if metadata['full_name'].lower() != repo.lower() or metadata['archived']:
            raise ValueError(f'{repo}: 이전/보관 상태를 먼저 검토하세요.')
        stable = api(f'repos/{repo}/releases/latest', missing_ok=True)
        ref = stable['tag_name'] if stable else metadata['default_branch']
        sha = api(f'repos/{repo}/commits/{quote(ref, safe="")}')['sha']
        doc_sha = api(f'repos/{repo}/commits/{quote(metadata["default_branch"], safe="")}')['sha'] if stable else sha
        readme = api(f'repos/{repo}/readme?ref={doc_sha}')
        content = base64.b64decode(readme['content'])
        sources[name] = {
            'repo': repo, 'ref': ref, 'sha': sha,
            'mode': 'release' if stable else 'branch',
            'readme_sha256': digest(content),
            'url': f'https://github.com/{repo}/tree/{sha}',
            'readme_url': readme['html_url'], 'readme_commit': doc_sha,
        }
    return {'schema': 1, 'sources': sources}


def source_content(lock):
    return {name: {k: v for k, v in row.items() if k not in ('readme_commit', 'readme_url')}
            for name, row in lock['sources'].items()}


def check_updates(current, latest):
    before, after = source_content(current), source_content(latest)
    return sorted(name for name in before.keys() | after.keys()
                  if before.get(name) != after.get(name))


def lock_hash(lock):
    return digest(json.dumps(lock, sort_keys=True).encode())


def record_review(root, notes, reviewer):
    path = safe_path(root, notes)
    if not path.is_file() or not path.read_text(encoding='utf-8').strip() or not reviewer.strip():
        raise ValueError('실제 영향 검토 문서와 리뷰어가 필요합니다.')
    if '영향 검토: 미완료' in path.read_text(encoding='utf-8'):
        raise ValueError('자동 생성된 미검토 보고서는 승인 근거로 사용할 수 없습니다.')
    write_json(root / 'upstream-review.json', {
        'lock_sha256': lock_hash(read_json(root / 'upstreams.lock.json')),
        'notes': notes, 'notes_sha256': digest(path.read_bytes()),
        'reviewer': reviewer, 'checked_at': now(),
    })


def validate_review(root):
    review = read_json(root / 'upstream-review.json')
    lock = read_json(root / 'upstreams.lock.json')
    if review['lock_sha256'] != lock_hash(lock):
        raise ValueError('원본 버전에 대한 영향 검토가 미완료입니다.')
    path = safe_path(root, review['notes'])
    if review['notes_sha256'] != digest(path.read_bytes()) or not review['reviewer'].strip():
        raise ValueError('영향 검토 근거가 변경되거나 누락되었습니다.')


def validate_lock(lock):
    if lock.get('schema') != 1 or set(lock.get('sources', {})) != set(SOURCES):
        raise ValueError('upstream lock의 원본 목록이 잘못되었습니다.')
    for name, row in lock['sources'].items():
        if row['repo'] != SOURCES[name] or not re.fullmatch('[0-9a-f]{40}', row['sha']):
            raise ValueError(f'{name}: 잘못된 원본 또는 SHA')
        if not re.fullmatch('[0-9a-f]{64}', row['readme_sha256']):
            raise ValueError(f'{name}: 잘못된 문서 해시')


def safe_path(root, relative):
    if Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValueError('잘못된 관리 파일 경로')
    current = root
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f'심볼릭 링크 경로는 변경하지 않습니다: {current}')
    return current


def apply_templates(target, repo, lock, source=ROOT):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('저장소는 OWNER/REPO 형식이어야 합니다.')
    target = target.absolute()
    if any(p.is_symlink() for p in (target, *target.parents)):
        raise ValueError('심볼릭 링크 대상은 변경하지 않습니다.')
    state_path = safe_path(target, '.github/workflow-state.json')
    previous = read_json(state_path) if state_path.exists() else {'files': {}}
    if previous.get('repo', repo) != repo:
        raise ValueError('기존 적용 저장소와 요청한 저장소가 다릅니다.')
    planned = {}
    local_templates = {'.claude/settings.local.json'}
    agent_templates = local_templates | {'.codex/config.toml'}
    seed_templates = {'.github/dependabot.yml', '.infisical.yaml', '.codex/config.toml'} | local_templates
    seeds = set(previous.get('seed_files', [])) | (set(previous['files']) & seed_templates)
    for template in sorted((source / 'templates').rglob('*')):
        if template.is_file():
            rel = template.relative_to(source / 'templates').as_posix()
            data = template.read_text(encoding='utf-8').replace('{{REPO}}', repo).encode()
            path = safe_path(target, rel)
            if rel in agent_templates and state_path.exists():
                if not path.exists():
                    seeds.discard(rel)
                continue
            if rel == '.infisical.yaml':
                legacy = target / '.infisical.json'
                if legacy.is_symlink() or legacy.exists():
                    if not path.exists():
                        seeds.discard(rel)
                    continue
            if rel in seed_templates:
                if not path.exists():
                    planned[rel] = data
                    if rel not in local_templates:
                        seeds.add(rel)
                continue
            if path.exists() and path.read_bytes() != data:
                if previous['files'].get(rel) != digest(path.read_bytes()):
                    raise ValueError(f'파일 충돌: {rel}. 기존 내용을 보존하고 수동 통합하세요.')
            planned[rel] = data
    retired = set(previous['files']) - set(planned) - seed_templates
    if retired:
        raise ValueError(f'관리 파일 제거는 수동 마이그레이션이 필요합니다: {sorted(retired)}')
    defaults = {
        'README.md': f'# {repo.split("/")[-1]}\n\nGitHub 개발 구성을 준비한 프로젝트입니다.\n\n'
                     '[작업 규칙](docs/WORKFLOW.md) · [구성 연결](.github/project-setup.json)\n\n'
                     'AI 조사·계획·구현은 이 프로젝트에서 별도로 요청합니다.\n',
        '.gitignore': '.env\n.env.*\n!.env.example\n.secrets/\n*.key\n*.pem\n*.p12\n*.pfx\n.local/\n__pycache__/\n.claude/settings.local.json\n',
        'docs/STATE.md': '# 작업 인수인계\n\n기준: https://github.com/' + repo + '/issues\n\n'
                         '- 목표: 미작성\n- 현재 작업: 없음 (AI 작업 요청 대기)\n'
                         '- 다음 작업: 미정\n- 작업 파일 양식: [TEMPLATE](tasks/TEMPLATE.md)\n'
                         '- 확정 결정: 없음\n- 완료/미완료: 시작 준비\n'
                         '- 실패한 시도: 없음\n- 검증 근거: 없음\n- 다음 행동: GitHub 구성 완료 후 이 프로젝트에서 AI 작업을 별도로 요청\n',
        'docs/start-context.json': json.dumps({
            'checked_at': now(), 'objective': '', 'sources': [],
            'decisions': '', 'status': 'pending_research',
        }, ensure_ascii=False, indent=2) + '\n',
    }
    for rel, content in defaults.items():
        path = safe_path(target, rel)
        if not path.exists():
            planned[rel] = content.encode()
            seeds.add(rel)
    for rel in ('.github/upstreams.lock.json', '.github/start-check.json'):
        path = safe_path(target, rel)
        if path.exists() and not state_path.exists():
            raise ValueError(f'파일 충돌: {rel}')
    managed = {rel: digest(data) for rel, data in planned.items()
               if rel not in defaults and rel not in seed_templates}
    for rel, data in planned.items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    write_json(target / '.github/upstreams.lock.json', lock)
    write_json(state_path, {'schema': 1, 'repo': repo, 'files': managed, 'seed_files': sorted(seeds)})


def refresh(root, apply=False):
    latest = inspect_sources()
    validate_lock(latest)
    path = root / 'upstreams.lock.json'
    old = read_json(path) if path.exists() else {'schema': 1, 'sources': {}}
    changes = check_updates(old, latest)
    report = {'checked_at': now(), 'changes': changes, 'latest': latest}
    write_json(root / '.local/upstream-check.json', report)
    if apply and changes:
        lines = ['# 원본 업데이트 후보', '', '자동 생성된 후보다. 호환성 검토를 대신하지 않는다.', '']
        for name in changes:
            before = old['sources'].get(name, {})
            after = latest['sources'][name]
            lines += [f'## {name}', '', f'- 이전: {before.get("ref", "없음")} '
                      f'`{before.get("sha", "없음")}`',
                      f'- 후보: {after["ref"]} `{after["sha"]}`',
                      f'- 현재 문서: {after["readme_url"]}']
            if before:
                if before.get('readme_commit') and before.get('readme_sha256') != after['readme_sha256']:
                    lines += [f'- 문서 변경: https://github.com/{after["repo"]}/compare/'
                              f'{before["readme_commit"]}...{after["readme_commit"]}']
                lines += [f'- 변경: https://github.com/{after["repo"]}/compare/'
                          f'{before["sha"]}...{after["sha"]}']
            lines += ['- 영향 검토: 미완료 — 공통 규칙/템플릿/선택적 엔진의 변경 필요 여부를 기록한다.', '']
        (root / 'docs').mkdir(exist_ok=True)
        (root / 'docs/upstream-update.md').write_text('\n'.join(lines), encoding='utf-8')
        write_json(path, latest)
    return latest, changes


def prepare_project(root, target, repo):
    latest, changes = refresh(root)
    if changes:
        raise ValueError('미반영 upstream: ' + ', '.join(changes) +
                         '. 중앙 저장소에서 upgrade → 영향 검토 → 테스트 → PR merge 후 재시도하세요.')
    validate_review(root)
    latest = read_json(root / 'upstreams.lock.json')
    apply_templates(target, repo, latest, root)
    gate_path = target / '.github/start-check.json'
    previous = read_json(gate_path) if gate_path.exists() else {}
    if previous.get('lock_sha256') == lock_hash(latest):
        return
    write_json(gate_path, {
        'checked_at': now(), 'status': 'upstreams_current',
        'lock_sha256': digest(json.dumps(latest, sort_keys=True).encode()),
        'domain_research': 'docs/start-context.json에서 별도 검증',
    })
    print(f'로컬 구성 파일 준비: {target}', flush=True)


def implementation_ready(target):
    gate = read_json(target / '.github/start-check.json')
    context = read_json(target / 'docs/start-context.json')
    for record in (context,):
        timestamp = record.get('checked_at')
        if not isinstance(timestamp, str):
            raise ValueError('확인 시각은 UTC ISO-8601 문자열이어야 합니다.')
        checked = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        if checked.tzinfo is None:
            raise ValueError('확인 시각에 UTC 시간대가 필요합니다.')
        age = (datetime.now(timezone.utc) - checked).total_seconds()
        if not 0 <= age <= 86400:
            raise ValueError('도메인 조사는 24시간 이내 기록이어야 합니다. 조사 기록을 갱신하세요.')
    lock = read_json(target / '.github/upstreams.lock.json')
    if gate['lock_sha256'] != digest(json.dumps(lock, sort_keys=True).encode()):
        raise ValueError('시작 확인 후 lock이 변경되었습니다.')
    if gate['status'] != 'upstreams_current' or context['status'] != 'reviewed':
        raise ValueError('시작 조사/검토가 미완료입니다.')
    if not all(isinstance(context.get(k), str) and context[k].strip() for k in ('objective', 'decisions')) or not context['sources']:
        raise ValueError('목표·최신 출처·결정 기록이 필요합니다.')
    if not isinstance(context['sources'], list):
        raise ValueError('출처는 목록이어야 합니다.')
    for source in context['sources']:
        if not isinstance(source, dict) or not all(
                isinstance(source.get(k), str) and source[k].strip() for k in ('url', 'finding')):
            raise ValueError('출처에는 URL과 확인 내용 문자열이 필요합니다.')
        parsed = urlparse(source['url'])
        if parsed.scheme != 'https' or not parsed.hostname or not source['finding'].strip():
            raise ValueError('출처에는 HTTPS URL과 확인 내용이 필요합니다.')
    print('AI 작업 준비 확인: 구성 시 도구 확인 + 최근 도메인 조사 기록. AI 실행을 뜻하지 않습니다.')


def start(root, target, repo, visibility='public'):
    from github_setup import configure, preflight
    metadata = preflight(target, repo)
    prepare_project(root, target, repo)
    configure(target, repo, visibility, metadata)


def ready(target):
    from github_setup import verify
    verify(target)


def verified_checkpoint(target, issue, task=None, plans=()):
    target = target.resolve()
    state = read_json(safe_path(target, '.github/workflow-state.json'))
    repo = state['repo']
    if not re.fullmatch(r'https://github.com/' + re.escape(repo) + r'/issues/[1-9][0-9]*', issue):
        raise ValueError('현재 저장소의 이슈 URL이 필요합니다.')
    from github_setup import git, origin_repo
    if Path(git(target, 'rev-parse', '--show-toplevel')).resolve() != target:
        raise ValueError('인수인계 대상은 Git 저장소 루트여야 합니다.')
    if origin_repo(git(target, 'config', '--get', 'remote.origin.url')) != repo.lower():
        raise ValueError('origin과 현재 저장소가 다릅니다.')
    if git(target, 'status', '--porcelain', '--untracked-files=all'):
        raise ValueError('미커밋 변경이 있습니다. 작업 기록을 커밋·푸시한 뒤 전달하세요.')
    branch = git(target, 'branch', '--show-current')
    if not branch:
        raise ValueError('브랜치가 필요합니다. detached HEAD에서는 전달하지 않습니다.')
    head = git(target, 'rev-parse', 'HEAD')
    remote = git(target, 'ls-remote', '--heads', 'origin', f'refs/heads/{branch}')
    if not remote or remote.split()[0] != head:
        raise ValueError('현재 브랜치와 origin의 SHA가 다릅니다. 커밋·푸시 상태를 확인하세요.')
    reference = api(f'repos/{repo}/git/ref/heads/{quote(branch, safe="")}')
    if reference.get('object', {}).get('sha') != head:
        raise ValueError('GitHub 브랜치와 현재 SHA가 다릅니다. 원격 상태를 확인하세요.')
    path = safe_path(target, 'docs/STATE.md')
    state_body = path.read_text(encoding='utf-8')
    if not state_body.strip() or len(state_body) > 12000:
        raise ValueError('인수인계를 12,000자 이내로 압축하세요. 상세 근거는 링크하세요.')
    files = [('현재 상태', 'docs/STATE.md')]
    for label, relative in ([('선택 작업', task)] if task else []) + [('설계', plan) for plan in plans]:
        path = safe_path(target, relative)
        if not path.is_file() or path.suffix != '.md' or any(c in relative for c in '\r\n`'):
            raise ValueError('작업·설계 파일은 저장소 안의 Markdown 파일이어야 합니다.')
        relative = path.relative_to(target).as_posix()
        files.append((label, relative))
        if label == '선택 작업':
            task = relative
    links = []
    for label, relative in files:
        local = git(target, 'hash-object', '--', relative)
        if git(target, 'rev-parse', f'{head}:{relative}') != local:
            raise ValueError(f'커밋과 전달 파일이 다릅니다: {relative}')
        encoded = quote(relative, safe='/')
        actual = api(f'repos/{repo}/contents/{encoded}?ref={head}')
        if actual.get('type') != 'file' or actual.get('sha') != local:
            raise ValueError(f'원격 전달 파일이 커밋과 다릅니다: {relative}')
        links.append(f'- [{label}](https://github.com/{repo}/blob/{head}/{encoded})')
    number = issue.rsplit('/', 1)[1]
    endpoint = f'repos/{repo}/issues/{number}'
    actual_issue = api(endpoint)
    if actual_issue.get('html_url', '').lower() != issue.lower() or 'pull_request' in actual_issue:
        raise ValueError('인수인계 대상 이슈를 확인할 수 없습니다.')
    return {'repo': repo, 'branch': branch, 'head': head, 'links': links,
            'issue': actual_issue, 'task': task}


def resume(target, issue, task, plans=(), prs=()):
    from github_setup import collection
    checkpoint = verified_checkpoint(target, issue, task, plans)
    repo = checkpoint['repo']
    if checkpoint['issue'].get('state') != 'open':
        raise ValueError('재개 기준은 열린 이슈여야 합니다. 종료 사유와 후속 작업을 확인하세요.')
    task_body = safe_path(target.resolve(), checkpoint['task']).read_text(encoding='utf-8')
    if not re.search(re.escape(issue) + r'(?![A-Za-z0-9_/?#])', task_body):
        raise ValueError('선택 작업 파일에 기준 이슈의 정확한 URL을 기록하세요.')
    dependencies = collection(f'repos/{repo}/issues/{issue.rsplit("/", 1)[1]}/dependencies/blocked_by')
    pull_requests = []
    for pr in dict.fromkeys(prs):
        if not re.fullmatch(r'https://github.com/' + re.escape(repo) + r'/pull/[1-9][0-9]*', pr):
            raise ValueError('현재 저장소의 PR URL이 필요합니다.')
        result = json.loads(run('gh', 'pr', 'view', pr, '--repo', repo, '--json',
                               'url,state,headRefOid,isDraft,reviewDecision,statusCheckRollup'))
        if (result.get('url', '').lower() != pr.lower() or
                not re.fullmatch(r'[0-9a-f]{40}', result.get('headRefOid', '')) or
                result.get('state') not in ('OPEN', 'CLOSED', 'MERGED') or
                'statusCheckRollup' not in result):
            raise ValueError('PR 조회 결과를 확인할 수 없습니다.')
        result['head_matches_checkpoint'] = result['headRefOid'] == checkpoint['head']
        pull_requests.append(result)
    report = {
        'checked_at': now(), 'repo': repo, 'branch': checkpoint['branch'],
        'head': checkpoint['head'], 'links': checkpoint['links'],
        'issue': {key: checkpoint['issue'].get(key) for key in ('html_url', 'title', 'state')},
        'blocked_by': [{key: row.get(key) for key in ('html_url', 'title', 'state', 'state_reason')}
                       for row in dependencies],
        'pull_requests': pull_requests, 'session_started': False,
        'limitations': ['기록의 원격 일치 확인이며 작업 승인·세션 생성·수용·배포 성공이 아닙니다.',
                        '설계·PR 미지정은 없음/검증 성공을 뜻하지 않습니다. 필수 자료를 직접 확인하세요.',
                        'CI 실패·대기·빈 결과와 선행 이슈의 종료 사유·통합·수용을 별도로 판단하세요.',
                        '현재 시점 관측이며 잠금이 아닙니다. 작업 소유권과 변경 여부를 확인하세요.'],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


def handoff(target, issue, task=None, dry_run=False):
    from github_setup import collection, mutation
    checkpoint = verified_checkpoint(target, issue, task)
    repo, head, links, task = (checkpoint[key] for key in ('repo', 'head', 'links', 'task'))
    endpoint = f'repos/{repo}/issues/{issue.rsplit("/", 1)[1]}'
    selected = f'`{task}`' if task else 'STATE의 현재 작업 파일'
    prompt = (f'같은 저장소의 AGENTS.md와 docs/STATE.md, {selected}을 읽고 '
              f'{issue} 및 관련 PR·CI의 현재 상태를 확인해 다음 행동부터 이어가줘. '
              '필수 자료만 먼저 읽고 선행 조건·사용자 승인·검증 결과를 추정하지 마.')
    body = ('## 작업 인수인계\n\n'
            f'- 기준 커밋: `{head}`\n' + '\n'.join(links) + '\n\n'
            '### 새 대화에서 사용할 시작 문구\n\n> ' + prompt + '\n\n'
            '기록 전달이며 새 세션 생성·실행은 하지 않습니다. '
            'CI·사용자 수용·배포·제품 동작은 관련 근거로 별도 확인합니다.\n')
    if dry_run:
        print('미리보기: 원격 파일 확인 완료, 댓글 게시·새 세션 실행은 미실행.\n\n' + body)
        return
    comments = collection(endpoint + '/comments')
    comment = next((row for row in comments if row.get('body') == body), None)
    if comment is None:
        comment = mutation('POST', endpoint + '/comments', {'body': body})
    comment_id = comment['id']
    if not isinstance(comment_id, int) or comment_id <= 0:
        raise ValueError('게시 결과의 댓글 ID를 확인할 수 없습니다. 이슈를 직접 확인하세요.')
    url = f'{issue}#issuecomment-{comment_id}'
    try:
        actual = api(f'repos/{repo}/issues/comments/{comment_id}')
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        raise ValueError(f'댓글이 존재할 수 있으나 원격 확인에 실패했습니다: {url}. '
                         '재실행은 같은 본문의 댓글을 재사용합니다.') from error
    if (actual.get('body') != body or actual.get('html_url', '').lower() != url.lower() or
            actual.get('issue_url', '').lower() != f'https://api.github.com/{endpoint}'.lower()):
        raise ValueError(f'댓글의 본문·대상이 예상과 다릅니다. 원격 기록을 확인하세요: {url}')
    print(f'기록 전달·원격 확인 완료: {url}\n새 세션 생성·실행: 미실행')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('check')
    commands.add_parser('upgrade')
    p = commands.add_parser('validate')
    p.add_argument('--reviewed', action='store_true')
    p = commands.add_parser('record-review')
    p.add_argument('--notes', required=True)
    p.add_argument('--reviewer', required=True)
    p = commands.add_parser('start')
    p.add_argument('path', type=Path)
    p.add_argument('--repo', required=True)
    p.add_argument('--visibility', choices=['private', 'public'], default='public',
                   help='새 저장소 공개 범위(기본 public). 기존 저장소는 변경하지 않습니다.')
    p = commands.add_parser('ready')
    p.add_argument('path', type=Path)
    p = commands.add_parser('implementation-ready')
    p.add_argument('path', type=Path)
    p = commands.add_parser('handoff')
    p.add_argument('path', type=Path)
    p.add_argument('--issue', required=True)
    p.add_argument('--task', help='저장소 기준 작업 Markdown 경로')
    p.add_argument('--dry-run', action='store_true', help='원격 검증 후 전달문만 출력, 게시하지 않음')
    p = commands.add_parser('resume', help='원격 작업 기록·선행 관계·지정 PR/CI 확인 (읽기 전용)')
    p.add_argument('path', type=Path)
    p.add_argument('--issue', required=True)
    p.add_argument('--task', required=True, help='기준 이슈 URL을 포함한 작업 Markdown 경로')
    p.add_argument('--plan', action='append', default=[], help='검증할 설계 Markdown 경로 (반복 가능)')
    p.add_argument('--pr', action='append', default=[], help='확인할 같은 저장소 PR URL (반복 가능)')
    args = parser.parse_args()
    if args.command in ('check', 'upgrade'):
        _, changed = refresh(ROOT, args.command == 'upgrade')
        print(json.dumps({'changed': changed}, ensure_ascii=False))
        return 2 if changed and args.command == 'check' else 0
    if args.command == 'record-review':
        record_review(ROOT, args.notes, args.reviewer)
    elif args.command == 'validate':
        validate_lock(read_json(ROOT / 'upstreams.lock.json'))
        if args.reviewed:
            validate_review(ROOT)
        print('lock 검증 통과')
    elif args.command == 'start':
        start(ROOT, args.path.absolute(), args.repo, args.visibility)
    elif args.command == 'ready':
        ready(args.path.resolve())
    elif args.command == 'implementation-ready':
        implementation_ready(args.path.resolve())
    elif args.command == 'resume':
        resume(args.path.resolve(), args.issue, args.task, args.plan, args.pr)
    elif args.command == 'handoff':
        handoff(args.path.resolve(), args.issue, args.task, args.dry_run)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(f'오류: {error}', file=sys.stderr)
        sys.exit(1)
