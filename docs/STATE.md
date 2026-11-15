# 작업 인수인계

- 현재 작업: [#25 Claude·Codex 권한 기본값](tasks/25-agent-permission-defaults.md). 생성·보존·게시 테스트 80개 통과. 외부 리뷰 지적과 수정분 검토를 완료했다. PR·CI·main 최종 결과는 이슈 #25에서 확인한다.
- 결정: 워크플로 최초 적용 때 없는 파일만 생성한다. Claude 로컬 파일은 게시하지 않고 새 Codex 파일은 seed로 등록한다. 기존 설정과 사용자 수정·삭제는 보존한다.
- 다음 행동: 작업 파일의 리뷰·검증 기록과 [이슈 #25](https://github.com/krdn/gon-github-workflow/issues/25)의 PR·main 최종 상태를 확인한다. 통합 완료 후 다음 요청을 기다린다.
- 시작 기준: `8e24c9fe9fda3ca3cbc2fe4afda62b77e0294cce`. 브랜치 `feat/agent-permission-defaults`.
- 한계: Claude 프로젝트 파일의 bypassPermissions는 최신 버전에서 적용되지 않는다. 실행 방법은 생성 WORKFLOW에 기록했다. Codex 설정은 프로젝트 신뢰가 필요하다. 런타임 권한 적용은 미검증이다.
- 이전 완료: [그래프·메모리 #23](tasks/23-graph-memory-review.md), [PR #24](https://github.com/krdn/gon-github-workflow/pull/24). 그래프 DB 도입 보류 결정은 유지한다. [인수인계 #21](tasks/21-verified-handoff.md)·[Infisical #19](tasks/19-infisical-default.md)·[세션 기록 #15](tasks/15-session-handoffs.md)는 필요할 때만 읽는다.
