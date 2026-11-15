# 검증된 인수인계와 세션별 작업 계약

기준: [이슈 #21](https://github.com/krdn/gon-github-workflow/issues/21). 사용자는 gon-stock03의 현재까지 작업을 근거로 중앙 워크플로의 필요한 업그레이드를 요청했다. gon-stock03 #5 개발은 아직 시작하지 않는다.

- 브랜치: `fix/verified-task-handoff`, 기준 main `98d7cb6a51ffaf7e10ec9fb824257d6997cd0654`.
- 근거: [gon-stock03 계획 검증](https://github.com/krdn/gon-stock03/blob/96f508c14859aa432025f62df42e1d8f94dbf6b4/docs/verification/2026-11-15-session-planning.md). 기존 handoff는 STATE를 복사해 상대 링크·원격 검증을 수동 보완해야 했다. 시작 문구 전달과 새 세션 실행의 차이도 반복 설명했다.
- 결정: 기존 handoff를 보강하고 작업 템플릿을 명확히 한다. 이슈 일괄 생성기·자동 세션 실행기·소비 프로젝트 일괄 덮어쓰기는 추가하지 않는다.
- 필수 읽기: 이슈 #21, `scripts/workflow.py:handoff`, `tests/test_handoff.py`, `templates/docs/WORKFLOW.md`의 세션 절차.

## 변경·검증

- clean Git root·origin·현재 브랜치 origin/GitHub HEAD·로컬/커밋/원격 문서 blob을 검사하고 SHA 고정 링크를 전달한다.
- 선택 작업 `--task`, 게시 없는 `--dry-run`, 댓글 재조회·순차 재실행 재사용을 추가했다. 세션 실행·CI·사용자 수용은 별도라고 표시한다.
- 작업 템플릿에 기존 구현/남은 변경·단일 소유권·선행 통합/수용·후속 이관을 명시한다. 새 대화/resume/fork/탭/전달문/실행을 구분한다.
- 수정 전 재현 6개 테스트에서 실패 8건을 확인했다. 수정 후 handoff 17개와 전체 73개 테스트가 통과했다. 네트워크만 모사하고 Git 저장소·원격 bare repo는 실제로 사용한다.
- `validate --reviewed`, `git diff --check` 통과. upstream 실조회 `changed: []`. 최신 공식 출처와 결정은 `docs/start-context.json`에 기록했고 implementation-ready 통과.
- gon-stock03의 실제 `--dry-run` 통과: `96f508c14859aa432025f62df42e1d8f94dbf6b4` 브랜치·STATE·선택 작업의 원격 일치를 확인했다. 게시·새 세션 실행은 하지 않았다.
- 독립 리뷰 실제 반환 모델: `claude-opus-5-5`, high. PASS. LOW 지적을 수용해 Git URL rewrite와 별개로 GitHub API의 브랜치 SHA를 확인한다. 해당 회귀는 수정 전 실패·수정 후 통과했다. 동일 모델의 수정분 리뷰도 PASS다.
- 실제 게시 검증·PR/CI·merge·설치 반영은 아직 진행 전이다.

## 다음 행동

커밋·푸시 후 이슈 #21에 실제 handoff 게시·재조회·재실행 재사용을 검증한다. PR·CI·merge·중앙 main 및 설치를 확인한다. 수정된 기존 소비 프로젝트 문서는 재초기화하거나 덮어쓰지 않는다.

리뷰 근거 SHA-256: 입력 `8e44749ae929073b7accb31bfa794b2fc1d2d8763c537f9c330848e1e667b8e9`, 응답 `ca8bd6f0582375ca24c86ece292ecf10f0e24ca9fd6f748a44b1fe926daf1c4d`. 리뷰는 제공된 자료를 판단했으며 원격 조회·테스트를 독립 재실행하지 않았다.
