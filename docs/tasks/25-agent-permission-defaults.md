# 새 프로젝트의 Claude·Codex 권한 설정

기준: [이슈 #25](https://github.com/krdn/gon-github-workflow/issues/25). `gon-stock03`에 설정한 값을 새 프로젝트 생성에도 적용한다.

- 범위: 생성기·템플릿·스킬 안내와 테스트. 기존 소비 프로젝트와 전역 설정은 변경하지 않는다.
- 결과: 워크플로 최초 적용 때 없는 `.claude/settings.local.json`에 `bypassPermissions`, 없는 `.codex/config.toml`에 `never`·`danger-full-access`를 생성한다. 기존 워크플로 프로젝트에는 추가하지 않으며 기존 파일·사용자 수정·삭제를 보존한다.
- 게시: Claude 로컬 설정은 관리 해시·seed·자동 게시에서 제외한다. 새 `.gitignore`에 제외 규칙을 넣는다. 새 Codex 파일은 seed이며 Git에서 무시하면 로컬에 보존한다. 기존 Codex 파일은 게시 대상으로 등록하지 않는다.
- 필수 읽기: [README의 생성 기본값](../../README.md#새-프로젝트-시작), `scripts/workflow.py:apply_templates`, `tests/test_workflow.py`, `tests/test_github_setup.py`.
- 시작: main `8e24c9fe9fda3ca3cbc2fe4afda62b77e0294cce`, 브랜치 `feat/agent-permission-defaults`.

## 검증과 한계

2026-11-15 검사 결과:

- 새 테스트는 생성 파일 누락과 링크 경로 미처리로 먼저 실패했다. 구현 후 76개, 리뷰 보완 후 `python3 -B -m unittest discover -s tests -v`: 80개 통과.
- 실제 임시 Git 저장소에서 start·게시·재실행을 검사했다. GitHub API와 upstream은 mock이다. Claude 로컬 설정은 ignored·untracked, 일반 Codex 설정은 tracked이며 재실행 HEAD가 같다. 전역·프로젝트 Git 제외 규칙에서도 게시·재실행을 확인했다.
- `gon-workflow implementation-ready .`, `python3 -B scripts/workflow.py validate --reviewed`, `git diff --check`: 통과.
- 중앙 저장소의 `ready`는 기존 `.github/project-setup.json` 부재로 실패했다. 기존 프로젝트를 초기화하지 않았으며 PR #24 병합·main SHA·main CI를 직접 확인했다.
- STE lint는 `docs/conventions/ste100-writing.md` 부재로 exit 2다. 통과가 아니다.
- [Claude 공식 문서](https://code.claude.com/docs/en/settings-reference#permissions-defaultmode): v2.1.257부터 프로젝트 파일의 bypassPermissions는 적용되지 않는다. 실행 인자 `--permission-mode bypassPermissions` 또는 사용자 설정이 필요하다.
- [Codex 공식 문서](https://learn.chatgpt.com/docs/config-file/config-basic): 프로젝트 설정은 신뢰한 프로젝트에서 읽힌다. 파일 생성으로 실제 세션 권한 적용을 입증하지 않는다.

## 외부 리뷰

초회 실제 반환 모델·canonicalModel은 `claude-opus-5-5`, 요청 effort는 high, `subtype=success`, `is_error=false`였다. 제공 diff·관련 코드 검토이며 도구 실행은 없었다.

- D1: 무시된 Codex 설정의 게시 실패를 재현하고 게시에서 제외했다. 파일은 로컬에 보존한다.
- D2: 기존 `.gitignore` 보존을 유지하고, Claude 제외 규칙이 없으면 `handoff`가 중단된다는 영향을 README·WORKFLOW에 명시했다. 리뷰가 제시한 최소 문서 대응을 적용했다.
- S1·S2: 권한 파일 생성은 최초 적용으로 제한했다. 기존 워크플로 프로젝트에 추가하지 않으며 사용자 삭제도 보존하고 누락 seed를 제거한다.
- 보완 회귀는 수정 전 실패 2·오류 2, 수정 후 80개 전체 통과다. 상대 링크 18개와 JSON/TOML 구문을 확인했다. 임시 생성 파일은 gon-stock03의 두 설정과 바이트가 일치했다.

## 다음 행동

PR CI·병합·중앙 main 동기화 후 이슈 #25에 원격 결과를 기록한다. 이슈가 완료 상태면 다음 요청을 기다린다.

초회 입력 SHA-256: `3e62719313396c069d2693caa11b7aa88d1939c3390724e7b2b6293d013bc918`.
초회 응답 SHA-256: `034ae192f66e96fde95ed671608f78b7d1b9182b66346cc8ab9dc37bcf119c79`.

수정분 리뷰도 실제 반환 모델·canonicalModel `claude-opus-5-5`, 요청 high, success·is_error=false였고 **차단 결함 없음**으로 결론 냈다. D1·D2·S1·S2의 처리를 인정했다.
N1(재적용 시 링크 경로도 차단)은 기존 `safe_path`의 전체 적용 경로 검사 정책을 유지한다. 링크 파일·상위 링크 디렉터리는 보존하며 적용을 중단한다. 링크 예외 처리는 이번 범위에 추가하지 않는다.
N2는 seed 목록이 실제 게시 파일 목록과 다를 수 있다는 정보다. Git에서 제외한 Codex 파일은 로컬에만 있으며 이 동작을 문서와 테스트에 명시했다.

수정분 입력 SHA-256: `34d79d98d150d2a5e1e262ea48278231be3de018c962d941490fbad8ed19c8ba`.
수정분 응답 SHA-256: `5a01c775827c92577dc0f9168e115b1943dbd53cbbe1666490c21c2916bfeebf`.
