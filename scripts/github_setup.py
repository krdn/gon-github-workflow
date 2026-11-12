"""프로젝트의 Git/GitHub 구성을 생성하고 재조회한다. AI 작업은 실행하지 않는다."""
import json
import re
import subprocess
from pathlib import Path

from workflow import api, digest, read_json, run, safe_path, write_json

MARKER = '<!-- gon-github-workflow:next-task -->'


def git(target, *args):
    return run('git', '-C', str(target), *args)


def mutation(method, endpoint, payload):
    return json.loads(run('gh', 'api', '--method', method, endpoint, '--input', '-',
                          input_data=json.dumps(payload)))


def collection(endpoint):
    rows = []
    separator = '&' if '?' in endpoint else '?'
    page = 1
    while True:
        batch = api(f'{endpoint}{separator}per_page=100&page={page}')
        rows.extend(batch)
        if len(batch) < 100:
            return rows
        page += 1


def origin_repo(value):
    match = re.fullmatch(r'(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([^/]+/[^/]+?)(?:\.git)?/?', value)
    return match.group(1).lower() if match else None


def receipt_file(target):
    path = Path(git(target, 'rev-parse', '--git-path', 'ggw-setup.json'))
    return path if path.is_absolute() else target / path


def remote_url(metadata):
    protocol = run('gh', 'config', 'get', 'git_protocol', '--host', 'github.com')
    return metadata['ssh_url'] if protocol == 'ssh' else metadata['clone_url']


def resume_update(target, repo, default_branch, receipt):
    branch = receipt['update_branch']
    prs = json.loads(run('gh', 'pr', 'list', '--repo', repo, '--head', branch,
                         '--state', 'all', '--json', 'url,state'))
    if prs and prs[0]['state'] == 'MERGED':
        del receipt['update_branch']
        del receipt['update_commit']
        write_json(receipt_file(target), receipt)
        return
    if prs and prs[0]['state'] == 'CLOSED':
        raise ValueError(f'구성 PR이 닫혔습니다. PR을 다시 열어 재개하세요: {prs[0]["url"]}')
    if git(target, 'rev-parse', branch) != receipt['update_commit']:
        raise ValueError('구성 브랜치가 변경되었습니다. 수동으로 PR을 확인하세요.')
    git(target, 'push', '-u', 'origin', branch)
    url = prs[0]['url'] if prs else run(
        'gh', 'pr', 'create', '--repo', repo, '--base', default_branch, '--head', branch,
        '--title', 'chore: GitHub 개발 구성 갱신', '--body', '구성 파일만 갱신합니다. AI 작업은 실행하지 않았습니다.')
    if git(target, 'branch', '--show-current') == branch:
        git(target, 'switch', default_branch)
    raise ValueError(f'기존 저장소의 구성 변경 PR: {url}. 검증·merge·pull 후 재실행하세요.')


def preflight(target, repo):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('저장소는 OWNER/REPO 형식이어야 합니다.')
    if any(p.is_symlink() for p in (target, *target.parents)):
        raise ValueError('심볼릭 링크 대상은 변경하지 않습니다.')
    if (target / '.git').is_symlink():
        raise ValueError('Git 디렉터리 심볼릭 링크는 변경하지 않습니다.')
    if not (target / '.git').exists():
        parent = next(p for p in (target, *target.parents) if p.is_dir())
        probe = subprocess.run(['git', '-C', str(parent), 'rev-parse', '--show-toplevel'],
                               text=True, capture_output=True, timeout=30)
        if probe.returncode == 0:
            raise ValueError('다른 Git 저장소 안에 새 프로젝트를 만들 수 없습니다.')
    else:
        if Path(git(target, 'rev-parse', '--show-toplevel')).resolve() != target.resolve():
            raise ValueError('프로젝트 경로와 Git 루트가 다릅니다.')
        if git(target, 'status', '--porcelain', '--untracked-files=no'):
            path = receipt_file(target)
            pending = read_json(path).get('pending_files', {}) if path.exists() else {}
            changed = set(git(target, 'diff', '--no-renames', '--name-only', '-z').split('\0'))
            changed.update(git(target, 'diff', '--cached', '--no-renames', '--name-only', '-z').split('\0'))
            changed.discard('')
            if any(name not in pending or not safe_path(target, name).is_file() or
                   digest((target / name).read_bytes()) != pending[name] for name in changed):
                raise ValueError('기존 Git 변경을 먼저 정리하세요. 자동으로 커밋하지 않습니다.')
        if 'origin' in git(target, 'remote').splitlines():
            origin = git(target, 'config', '--get', 'remote.origin.url')
            if origin_repo(origin) != repo.lower():
                raise ValueError('origin과 요청한 GitHub 저장소가 다릅니다.')
    metadata = api(f'repos/{repo}', missing_ok=True)
    if metadata:
        if metadata['full_name'].lower() != repo.lower() or metadata['archived']:
            raise ValueError('저장소 이전/보관 상태를 확인하세요.')
        if not metadata.get('has_issues', True):
            raise ValueError('기존 저장소의 Issues가 꺼져 있습니다. 활성화 후 재실행하세요.')
        url = git(target, 'config', '--get', 'remote.origin.url') if (
            (target / '.git').exists() and 'origin' in git(target, 'remote').splitlines()
        ) else remote_url(metadata)
        if not (target / '.git').exists() and run('git', 'ls-remote', '--heads', url):
            raise ValueError('기존 GitHub 저장소를 먼저 clone한 경로에서 실행하세요.')
        if (target / '.git').exists():
            path = receipt_file(target)
            receipt = read_json(path) if path.exists() else {}
            if receipt.get('update_branch'):
                resume_update(target, repo, metadata['default_branch'], receipt)
            branch = git(target, 'branch', '--show-current')
            if branch != metadata['default_branch']:
                raise ValueError('기본 브랜치에서 구성을 적용하세요.')
            remote = run('git', 'ls-remote', '--heads', url, f'refs/heads/{branch}')
            if remote and git(target, 'rev-parse', 'HEAD') != remote.split()[0]:
                raise ValueError('원격 기본 브랜치와 동기화한 뒤 재실행하세요.')
    return metadata


def configure(target, repo, visibility, metadata):
    owner, name = repo.split('/')
    if not (target / '.git').exists():
        git(target, 'init', '-b', 'main')
    git(target, 'var', 'GIT_AUTHOR_IDENT')
    git(target, 'var', 'GIT_COMMITTER_IDENT')
    receipt_path = receipt_file(target)
    receipt = read_json(receipt_path) if receipt_path.exists() else {}
    if metadata is None:
        print(f'GitHub 저장소 생성: {repo} ({visibility})', flush=True)
        run('gh', 'repo', 'create', repo, f'--{visibility}')
        receipt['created_repository'] = True
        write_json(receipt_path, receipt)
        metadata = api(f'repos/{repo}')
    if 'origin' not in git(target, 'remote').splitlines():
        git(target, 'remote', 'add', 'origin', remote_url(metadata))
    if not git(target, 'branch', '--list'):
        git(target, 'branch', '-m', metadata['default_branch'])
    elif git(target, 'branch', '--show-current') != metadata['default_branch']:
        raise ValueError('로컬 기본 브랜치를 확인하세요. 커밋·푸시는 하지 않았습니다. '
                         f'기존 이력을 보존하고 {metadata["default_branch"]} 브랜치에서 재실행하세요.')
    if not metadata.get('has_issues', True):
        raise ValueError('기존 저장소의 Issues가 꺼져 있습니다. 활성화 후 재실행하세요.')
    if receipt.get('created_repository') and not metadata.get('has_discussions'):
        mutation('PATCH', f'repos/{repo}', {'has_discussions': True})

    print('GitHub 이슈·Milestone·Project 연결 중', flush=True)
    milestones = collection(f'repos/{repo}/milestones?state=all')
    milestone = next((m for m in milestones if m.get('description') == MARKER), None)
    if milestone is None:
        milestone = mutation('POST', f'repos/{repo}/milestones', {
            'title': '첫 AI 작업', 'description': MARKER,
        })
    labels = collection(f'repos/{repo}/labels')
    if not any(label['name'].lower() == 'workflow:ai' for label in labels):
        mutation('POST', f'repos/{repo}/labels', {
            'name': 'workflow:ai', 'color': '1d76db', 'description': '구성 후 별도로 요청할 AI 작업',
        })
    issues = collection(f'repos/{repo}/issues?state=all')
    issue = next((i for i in issues if not i.get('pull_request') and MARKER in (i.get('body') or '')), None)
    if issue is None:
        issue = mutation('POST', f'repos/{repo}/issues', {
            'title': 'AI 조사·계획·구현 요청 대기', 'milestone': milestone['number'],
            'labels': ['workflow:ai'],
            'body': MARKER + '\n\n프로젝트 구성과 AI 실행은 별도 단계입니다.\n\n'
                    '- 현재: 사용자 목표 미지정, AI 작업 미실행\n'
                    '- [ ] 이 프로젝트에서 목표를 별도로 요청\n'
                    '- [ ] 관련 공식 자료 조사 및 계획 기록\n'
                    '- [ ] 구현·검증·PR 전달\n\n'
                    '구성 정보: `.github/project-setup.json` · 작업 규칙: `docs/WORKFLOW.md`',
        })
    projects = json.loads(run('gh', 'project', 'list', '--owner', owner, '--format', 'json', '--limit', '1000'))
    if projects['totalCount'] > len(projects['projects']):
        raise ValueError('Project 목록이 잘렸습니다. 전체 목록 확인 후 구성하세요.')
    project = next((p for p in projects['projects'] if p['title'] == f'ggw-{name}' and not p['closed']), None)
    if project is None:
        project = json.loads(run('gh', 'project', 'create', '--owner', owner,
                                 '--title', f'ggw-{name}', '--format', 'json'))
    number = str(project['number'])
    run('gh', 'project', 'link', number, '--owner', owner, '--repo', repo)
    items = json.loads(run('gh', 'project', 'item-list', number, '--owner', owner,
                           '--format', 'json', '--limit', '1000'))
    if items['totalCount'] > len(items['items']):
        raise ValueError('Project 항목 목록이 잘렸습니다.')
    if not any(i.get('content', {}).get('url') == issue['html_url'] for i in items['items']):
        run('gh', 'project', 'item-add', number, '--owner', owner, '--url', issue['html_url'])
    setup = {'schema': 1, 'repo': repo, 'repository_url': metadata['html_url'],
             'issue_url': issue['html_url'], 'milestone_number': milestone['number'],
             'project_number': project['number'], 'project_url': project['url'],
             'ai_execution': 'not_started'}
    path = safe_path(target, '.github/project-setup.json')
    if not path.exists() or read_json(path) != setup:
        write_json(path, setup)
    publish(target, repo, metadata['default_branch'])
    verify(target)
    print(f'구성 완료: {metadata["html_url"]}\nProject: {project["url"]}\n첫 이슈: {issue["html_url"]}')
    print(f'다음: {target}에서 AI 조사·계획·구현을 별도로 요청하세요. AI는 실행하지 않았습니다.')


def publish(target, repo, default_branch):
    state = read_json(target / '.github/workflow-state.json')
    files = set(state['files']) | set(state.get('seed_files', [])) | {
        '.github/workflow-state.json', '.github/upstreams.lock.json',
        '.github/start-check.json', '.github/project-setup.json',
    }
    for path in files:
        safe_path(target, path)
    remote = git(target, 'ls-remote', '--heads', 'origin', f'refs/heads/{default_branch}')
    path = receipt_file(target)
    receipt = read_json(path) if path.exists() else {}
    receipt['pending_files'] = {name: digest((target / name).read_bytes()) for name in files}
    write_json(path, receipt)
    original_branch = git(target, 'branch', '--show-current')
    has_commits = bool(git(target, 'branch', '--list'))
    branch = None
    try:
        git(target, 'add', '--', *sorted(files))
        changed = git(target, 'diff', '--cached', '--name-only')
        if changed and remote:
            content = ''.join(name + receipt['pending_files'][name] for name in sorted(files))
            branch = 'chore/ggw-setup-' + digest(content.encode())[:12]
            git(target, 'switch', '-c', branch)
        if changed:
            git(target, 'commit', '-m', 'chore: configure GitHub workflow')
    except (ValueError, subprocess.TimeoutExpired):
        if has_commits:
            git(target, 'reset', '-q', '--', *sorted(files))
        else:
            git(target, 'rm', '--cached', '--ignore-unmatch', '-q', '--', *sorted(files))
        if branch and git(target, 'branch', '--show-current') == branch:
            git(target, 'switch', original_branch)
            if git(target, 'rev-parse', branch) == git(target, 'rev-parse', original_branch):
                git(target, 'branch', '-d', branch)
        raise
    del receipt['pending_files']
    if changed and remote:
        receipt.update(update_branch=branch, update_commit=git(target, 'rev-parse', 'HEAD'))
    write_json(path, receipt)
    if changed and remote:
        resume_update(target, repo, default_branch, receipt)
    if not remote:
        git(target, 'push', '-u', 'origin', f'HEAD:{default_branch}')
    local = git(target, 'rev-parse', 'HEAD')
    remote = git(target, 'ls-remote', '--heads', 'origin', f'refs/heads/{default_branch}')
    if not remote or remote.split()[0] != local:
        raise ValueError('로컬 HEAD와 원격 기본 브랜치가 다릅니다. 변경을 보존하고 동기화 후 재시도하세요.')


def verify(target):
    path = safe_path(target, '.github/project-setup.json')
    if not path.exists():
        raise ValueError('GitHub 구성이 미완료입니다. start를 실행하세요.')
    setup = read_json(path)
    repo = setup['repo']
    if origin_repo(git(target, 'config', '--get', 'remote.origin.url')) != repo.lower():
        raise ValueError('구성 기록과 origin이 다릅니다.')
    metadata = api(f'repos/{repo}')
    head = git(target, 'rev-parse', 'HEAD')
    remote = git(target, 'ls-remote', '--heads', 'origin', 'refs/heads/' + metadata['default_branch'])
    if not remote or remote.split()[0] != head:
        raise ValueError('구성 커밋이 원격 기본 브랜치와 다릅니다.')
    if git(target, 'status', '--porcelain', '--untracked-files=no'):
        raise ValueError('커밋되지 않은 변경이 있습니다.')
    if not re.fullmatch(re.escape(f'https://github.com/{repo}/issues/') + r'\d+',
                        setup['issue_url'], flags=re.IGNORECASE):
        raise ValueError('첫 이슈가 다른 저장소를 가리킵니다.')
    issue = json.loads(run('gh', 'issue', 'view', setup['issue_url'], '--json', 'url,milestone'))
    if (issue['url'] != setup['issue_url'] or not issue['milestone'] or
            issue['milestone'].get('number') != setup['milestone_number']):
        raise ValueError('첫 이슈 또는 Milestone 연결을 확인하세요.')
    owner = repo.split('/')[0]
    items = json.loads(run('gh', 'project', 'item-list', str(setup['project_number']),
                           '--owner', owner, '--format', 'json', '--limit', '1000'))
    if items['totalCount'] > len(items['items']):
        raise ValueError('Project 항목 목록이 잘렸습니다.')
    if not any(i.get('content', {}).get('url') == setup['issue_url'] for i in items['items']):
        raise ValueError('Project의 첫 이슈 연결을 확인하세요.')
    print('구성 확인 통과: Git 원격 커밋·GitHub 이슈·Milestone·Project. AI 작업은 별도입니다.')
