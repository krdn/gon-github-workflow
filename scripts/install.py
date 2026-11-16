#!/usr/bin/env python3
"""사용자 범위 CLI·스킬·시작 지침 설치. 기존 파일은 백업하고 보존한다."""
import argparse
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = '<!-- gon-github-workflow -->'
END_MARKER = '<!-- /gon-github-workflow -->'
BLOCK = (MARKER + '\n## GitHub 기준 프로젝트 운영\n\n'
         '새 프로젝트의 첫 구현 전에 `gon-workflow start <절대경로> --repo OWNER/REPO`를 실행한다.\n'
         '`gon-workflow ready <경로>`로 GitHub 구성을 확인한다. AI 조사·계획·구현은 '
         '구성 완료 후 해당 프로젝트에서 별도로 요청받아 실행한다.\n'
         'AI 작업을 요청받으면 공식 자료를 `docs/start-context.json`에 기록하고 '
         '`gon-workflow implementation-ready <경로>` 통과 후 구현한다.\n'
         '실패·미반영 업데이트를 무시하지 않는다. gon-github-workflow 스킬과 '
         '기존 gon-project-lifecycle의 같은 이슈·문서를 재사용한다.\n'
         '단순 질의·기존 프로젝트 재개를 신규 초기화로 처리하지 않는다.\n'
         '이 워크플로의 프로젝트는 Infisical을 비밀 키·인증서·권한 접근의 기본 플랫폼으로 사용한다. '
         '프로젝트의 `docs/INFISICAL.md`를 따르고 비밀값을 코드·대화·로그에 남기지 않는다.\n'
         '모든 계획된 설계·구현은 GitHub 이슈에 범위·완료 조건을 먼저 기록하고, 설계·작업 파일을 커밋·푸시해 원격 링크로 연결한다. 대화나 로컬 파일만을 작업 기준으로 삼지 않는다.\n'
         '이 워크플로를 적용한 프로젝트의 새 세션은 `gon-workflow resume <경로> --issue URL --task docs/tasks/N-task.md`로 원격 기록을 확인한다. 별도 설계는 `--plan`, 관련 PR은 `--pr`로 모두 지정한다. 같은 세션에서 계속할 때도 이슈·문서·검증 기록을 갱신한다.\n'
         '필요한 추가 개선은 현재 목표와의 관계·완료 조건을 먼저 기록하고 범위 안에서 구현한다. 독립 기능은 후속 이슈로 분리한다. 이슈 등록은 거래·배포·삭제 등 별도 실행 승인을 뜻하지 않는다.\n'
         '큰 요청은 저장소의 작업별 기록으로 나누고 `docs/STATE.md`는 현재 작업의 짧은 목차로 유지한다.\n'
         '새 세션은 현재 작업 파일·필수 읽기 목록·관련 이슈/PR/CI만 먼저 확인한다. '
         '전체 과거 대화·작업 파일·로그를 반복 읽지 않는다.\n'
         '인수인계 문구 전달과 새 대화 실행을 구분하고 실제 생성·실행을 확인한 세션만 시작했다고 보고한다.\n' + END_MARKER)


def install(home, codex_home):
    skill = ROOT / 'skills/gon-github-workflow'
    links = {
        home / '.local/bin/gon-workflow': ROOT / 'bin/gon-workflow',
        codex_home / 'skills/gon-github-workflow': skill,
        home / '.claude/skills/gon-github-workflow': skill,
    }
    guidance = [codex_home / 'AGENTS.md', home / '.claude/CLAUDE.md']
    for path, target in links.items():
        if path.exists() or path.is_symlink():
            if not path.is_symlink() or path.resolve() != target:
                raise ValueError(f'기존 설치와 충돌: {path}')
    changes = {}
    for path in guidance:
        if path.is_symlink():
            raise ValueError(f'지침 심볼릭 링크는 수동 통합하세요: {path}')
        old = path.read_text(encoding='utf-8') if path.exists() else ''
        if MARKER in old:
            if old.count(MARKER) != 1 or old.count(END_MARKER) != 1:
                raise ValueError(f'지침 블록 경계가 잘못되었습니다: {path}')
            before, rest = old.split(MARKER, 1)
            _, after = rest.split(END_MARKER, 1)
            new = before + BLOCK + after
        else:
            new = old + '\n\n' + BLOCK + '\n'
        if new != old:
            changes[path] = new
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup = home / '.local/state/gon-github-workflow/backups' / stamp
    for path, new in changes.items():
        if path.exists():
            backup.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup / ('codex-AGENTS.md' if path == guidance[0] else 'claude-CLAUDE.md'))
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
            stream.write(new)
            temporary = Path(stream.name)
        if path.exists():
            shutil.copymode(path, temporary)
        temporary.replace(path)
    for path, target in links.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_symlink():
            path.symlink_to(target)
    print(f'설치 확인: {home / ".local/bin/gon-workflow"}')
    print(f'기존 지침 백업 위치(변경 시): {backup}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home())
    args = parser.parse_args()
    codex = Path(os.environ.get('CODEX_HOME', str(args.home / '.codex')))
    install(args.home, codex)
