# 검증된 인수인계와 세션별 작업 계약

기준: [이슈 #21](https://github.com/krdn/gon-github-workflow/issues/21). 사용자는 gon-stock03의 현재까지 작업을 근거로 중앙 워크플로의 필요한 업그레이드를 요청했다. gon-stock03 #5 개발은 아직 시작하지 않는다.

- [PR #22](https://github.com/krdn/gon-github-workflow/pull/22), 브랜치 `fix/verified-task-handoff`, 기준 main `98d7cb6a51ffaf7e10ec9fb824257d6997cd0654`.
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
- 구현 커밋 `b469bb3918a6af9f7502d352ddddb53415253c42`에서 중앙 이슈에 실제 게시·재조회를 완료했다. 같은 명령 재실행도 [동일 댓글](https://github.com/krdn/gon-github-workflow/issues/21#issuecomment-6887314962)을 반환했고, 원격 댓글 수는 1개였다.
- 해당 구현 커밋의 [PR CI](https://github.com/krdn/gon-github-workflow/actions/runs/43663376891)는 성공했다. 최종 문서 커밋의 CI·merge·설치 결과는 이슈 #21의 최종 전달 기록에서 확인한다.
- 커밋 시 선택적 graphify hook은 설치된 Python 모듈을 찾지 못해 인덱스를 갱신하지 않았다. Git 커밋·기능 검사·CI는 정상 완료했다.

## 다음 행동

이슈 #21과 PR #22에서 최종 CI·merge·중앙 main·설치 확인 결과를 먼저 읽는다. 미완료 절차만 수행하며 모두 확인됐다면 다음 사용자 요청을 기다린다. 수정된 기존 소비 프로젝트 문서는 재초기화하거나 덮어쓰지 않는다. gon-stock03 #5는 별도 개발 요청으로 시작한다.

리뷰 근거 SHA-256: 입력 `8e44749ae929073b7accb31bfa794b2fc1d2d8763c537f9c330848e1e667b8e9`, 응답 `ca8bd6f0582375ca24c86ece292ecf10f0e24ca9fd6f748a44b1fe926daf1c4d`. 리뷰는 제공된 자료를 판단했으며 원격 조회·테스트를 독립 재실행하지 않았다.

수정분 리뷰 SHA-256: 입력 `d757c391b308c98fee737a514f4d06cc5a4ed7ac60fc6196329c55a820964d3c`, 응답 `3c5b33251255176d5465cab3854d02a950b0189fe6f309a340cf23c4dc89683d`.
