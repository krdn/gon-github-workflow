#!/usr/bin/env python3
"""중앙 저장소 Actions에서 후보를 하나씩 제안하고 실패한 PR 생성을 재개한다."""
import base64
import json
import os
from pathlib import Path
from workflow import digest, run, source_content


def propose(root):
    os.chdir(root)
    changed = run('git', 'diff', '--name-only', '--', 'upstreams.lock.json')
    if not changed:
        print('원본 변경 없음')
        return
    candidate = json.loads((root / 'upstreams.lock.json').read_text(encoding='utf-8'))
    relevant = source_content(candidate)
    suffix = digest(json.dumps(relevant, sort_keys=True).encode())[:12]
    branch = f'chore/upstream-{suffix}'
    opened = json.loads(run('gh', 'pr', 'list', '--state', 'open', '--limit', '1000',
                            '--json', 'headRefName,url'))
    if any(p['headRefName'].startswith('chore/upstream-') for p in opened):
        print('기존 업데이트 PR을 먼저 검토하세요. 중복 후보를 만들지 않습니다.')
        return
    previous = json.loads(run('gh', 'pr', 'list', '--head', branch, '--state', 'all',
                              '--json', 'number'))
    if previous:
        print('같은 후보가 이미 처리되었습니다. 재제안은 수동으로 판단하세요.')
        return
    remote = run('git', 'ls-remote', '--heads', 'origin', f'refs/heads/{branch}')
    if remote:
        repository = os.environ['GH_REPO']
        encoded = run('gh', 'api', '--method', 'GET',
                      f'repos/{repository}/contents/upstreams.lock.json?ref={branch}',
                      '--jq', '.content')
        if source_content(json.loads(base64.b64decode(encoded))) != relevant:
            raise ValueError('남은 원격 브랜치의 후보 내용이 다릅니다. 수동 확인하세요.')
        print('기존 원격 브랜치에서 PR 생성을 재개합니다.')
    else:
        run('git', 'switch', '-c', branch)
        run('git', 'config', 'user.name', 'github-actions[bot]')
        run('git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
        run('git', 'add', 'upstreams.lock.json', 'docs/upstream-update.md')
        run('git', 'commit', '-m', 'chore: propose upstream workflow updates')
        run('git', 'push', 'origin', branch)
    print(run('gh', 'pr', 'create', '--draft', '--base', 'main', '--head', branch,
              '--title', 'chore: 원본 워크플로 업데이트 검토',
              '--body-file', 'docs/upstream-update.md'))


if __name__ == '__main__':
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise SystemExit('이 명령은 중앙 저장소 Actions 전용입니다.')
    propose(Path(__file__).resolve().parents[1])
