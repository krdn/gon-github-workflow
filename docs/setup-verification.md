# 프로젝트 구성 자동화 검증

2026-11-13. [요구사항 #9](https://github.com/krdn/gon-github-workflow/issues/9).
기존 start는 파일만 준비했고 Git·GitHub를 만들지 않았다. 이번 변경은 구성 완료까지 연결한다.
AI 조사·계획·구현은 구성 후 대상 프로젝트에서 별도로 요청한다.

- 자동 검사: `python3 -m unittest discover -s tests -v` 36개 통과. 실제 Git/bare remote와 gh 경계 mock을 사용했다.
- 보존·복구: 기존 파일·공개 범위, 다른 origin·상위 저장소 차단, Project 실패 후 재개, PR 실패 후 재개와 중복 방지 확인.
- 표준 검사: `validate --reviewed`, `git diff --check`, 생성 결과의 상대 링크 검사 통과.
- STE lint: 이 저장소에 해당 전용 표준 파일이 없어 실행하지 못했다. 문서 링크와 변경 범위는 직접 확인했다.
- 실사용: 개발 checkout의 CLI로 [test-app](https://github.com/krdn/test-app) 비공개 저장소와 main 커밋 `abefdb3` 생성 확인.
- 연결: [첫 이슈 #1](https://github.com/krdn/test-app/issues/1), Milestone 1, [Project #21](https://github.com/users/krdn/projects/21).
- 기존 docs/STATE.md·docs/start-context.json 해시 보존. 조사 상태는 pending_research이며 AI 작업 미실행.
- 외부 리뷰: claude-opus-5-5 high의 최초 5건과 수정분 재검토의 대소문자 1건을 재현해 수정했다. 마지막 정규식 수정은 회귀 테스트로 직접 검증했으며 추가 독립 재검토는 하지 않았다. [지적 처리](setup-review.md).
- [구성 CI](https://github.com/krdn/test-app/actions/runs/43253415853) 성공. ready 실제 재조회 통과, 미조사 implementation-ready는 차단.
- 중앙 [PR #10](https://github.com/krdn/gon-github-workflow/pull/10) merge: `e75013add2532d064132ba3a7b63267836d5e5d9`. [PR CI](https://github.com/krdn/gon-github-workflow/actions/runs/43255293387)·[main CI](https://github.com/krdn/gon-github-workflow/actions/runs/43255426612) 성공.
- 실제 재설치 완료. Codex/Claude 지침은 백업됐고 관리 블록 외부의 해시가 보존됐다.
- 설치된 `gon-workflow start /home/gon/dev/test-app --repo krdn/test-app`와 `gon-workflow ready /home/gon/dev/test-app` 성공.
- 재실행 전후 test-app HEAD `9d6f2e978bd102bed2d87a56bb68391e18d7bcba` 불변, 작업 트리 깨끗함. 첫 이슈·Milestone·해당 Project 각 1개로 중복 없음.
- 기존 구성 갱신은 [test-app PR #2](https://github.com/krdn/test-app/pull/2)의 CI 확인 후 merge했고 [main 구성 CI](https://github.com/krdn/test-app/actions/runs/43255163664)도 성공.

구성 Actions는 파일과 연결값만 검사한다. 애플리케이션 테스트·배포 성공을 뜻하지 않는다.
