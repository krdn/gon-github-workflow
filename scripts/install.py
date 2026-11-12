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
BLOCK = (MARKER + '\n## 신규 프로젝트 시작 전 확인\n\n'
         '새 프로젝트의 첫 구현 전에 `gon-workflow start <절대경로> --repo OWNER/REPO`를 실행한다.\n'
         '관련 기술의 최신 공식 자료를 조사해 `docs/start-context.json`에 기록하고 '
         '`gon-workflow ready <경로>` 통과 후 구현한다.\n'
         '실패·미반영 업데이트를 무시하지 않는다. gon-github-workflow 스킬과 '
         '기존 gon-project-lifecycle의 같은 이슈·문서를 재사용한다.\n'
         '단순 질의·기존 프로젝트 재개를 신규 초기화로 처리하지 않는다.\n' + END_MARKER)


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
