# 작업 인수인계

- [#30](https://github.com/krdn/gon-github-workflow/issues/30) 전역 설치 지침의 적용 범위를 명시했다. 임시 홈에서 Codex·Claude 지침 보존과 재설치 결과 동일성을 확인했고, 단위 테스트 90건과 lock 검증을 통과했다.

- 현재 작업: [#27 GitHub 기준 세션 운영](tasks/27-github-session-resume.md), feat/github-session-resume.
- 필수 읽기: 작업 파일·조사·설계, #27과 연결 PR/CI.
- 다음 행동: [#27](https://github.com/krdn/gon-github-workflow/issues/27)·[PR28](https://github.com/krdn/gon-github-workflow/pull/28)의 최신 통합·설치 결과를 확인한다. 미완료 단계만 이어가고 완료라면 후속 요청을 기다린다.
- 검증: 90건·Opus5.5 수정분 리뷰·64799c0 PR CI·정확한 구현의 실제 원격 resume 확인 PASS.
- 범위: 전역/생성 규칙과 읽기 전용 재개 검증. 소비 프로젝트 자동 덮어쓰기와 실제 세션 생성 없음.
- 이전: [#25 권한 기본값](tasks/25-agent-permission-defaults.md), PR26 main 통합/CI 성공 확인.
