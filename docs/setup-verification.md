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
- 설치본 재실행·중앙 PR/CI는 진행 중이다. 완료 근거는 해당 PR과 이슈에 기록한다.

구성 Actions는 파일과 연결값만 검사한다. 애플리케이션 테스트·배포 성공을 뜻하지 않는다.
