# 선택적 원격 AI 실행

기본 제품은 로컬 Claude/Codex와 결정적 GitHub Actions로 동작한다.
원격 AI 엔진은 인증·사용 비용이 확인된 프로젝트에서만 추가한다.
동일 이슈/PR 이벤트에 gh-aw와 Claude Code Action을 동시에 연결하지 않는다.

## gh-aw

[잠긴 버전](../upstreams.lock.json)의 github/gh-aw 설치·인증 문서를 읽는다.
`gh extension install github/gh-aw --pin <잠긴 ref>`로 설치하고 지원하는 엔진 하나를 선택한다.
공식 quickstart로 인증을 설정한 뒤 Markdown workflow를 작성하고 `gh aw compile`로 검증한다.
생성된 lock workflow도 PR에 포함한다. read-only 조사와 허용된 결과 쓰기를 구분한다.
초기 용도는 실패한 CI 요약 또는 주간 이슈 정리다. 실제 배포 명령은 일반 Actions에 둔다.

## Claude Code Action

[잠긴 버전](../upstreams.lock.json)의 anthropics/claude-code-action 문서를 읽는다.
공식 setup에 따라 엔진 자격 증명을 GitHub Secret으로 설정하고 `uses`를 잠긴 전체 SHA로 고정한다.
기본은 수동 실행 또는 명시적 멘션으로 제한하고, fork 이벤트에 write 권한·비밀값을 전달하지 않는다.
PR 리뷰와 이슈 답변의 실제 결과를 확인한 후 정기 실행을 추가한다.

두 엔진은 이 저장소에서 유료 호출하거나 배포하지 않았다. 구성 안내는 실행 성공의 근거가 아니다.
