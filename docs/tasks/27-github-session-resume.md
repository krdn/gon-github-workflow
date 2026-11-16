# 작업: GitHub 기준 세션 운영

기준 이슈: https://github.com/krdn/gon-github-workflow/issues/27

- 상태: 구현·리뷰 완료, PR CI·main 통합 대기.
- 범위·완료 조건: [설계](../plans/github-session-resume.md), #27 체크리스트.
- 필수 자료: [조사](../research/github-session-2026-11.md), workflow.py handoff, install.py, tests/test_handoff.py. 이전 전체 대화는 읽지 않는다.
- 브랜치: feat/github-session-resume. 기준 de13110.
- 검증 경계: ready는 중앙 project-setup 기록 부재로 실패. 재초기화 없이 실제 main SHA·PR26·CI·이슈27 확인.
- 다음 행동: 수정분 리뷰와 PR CI를 확인하고 main 통합·설치·원격 재개 검증을 수행한다.
- 리뷰: Fable5.2/high 우선, 사용량 소진 시에만 Opus5.5/high 사용. 반환 모델을 별도로 확인한다.

## 구현·검증

- 기존 handoff의 원격 검증을 공통화하고 읽기 전용 resume, 계획 파일 검증·native blocked_by·지정 PR/CI 보고를 추가했다.
- 전역 설치 블록·스킬·생성 템플릿에 GitHub 선기록·세션 시작·범위 변경 규칙을 적용했다. 전역 resume 실행 지시는 이 워크플로 적용 프로젝트로 한정한다.
- 초기 resume CLI 검사 RED(명령 부재), 구현 후 전체88건 PASS. 리뷰 후 PR SHA 일치·미게시 설계 검사2건 추가. 최종 검사 결과는 아래 검증 기록을 따른다.
- 기존 validate --reviewed, diff 검사, 스킬 형식 검사 통과. 실제 생성 프로젝트의 문서 링크 검사 통과. 템플릿만 검사할 때의 STATE 링크는 생성 시 제공되므로 생성 결과로 재확인했다.
- STE 문체 검사는 기준 파일 부재로 exit2. ready는 기존 project-setup.json 부재로 실패하며 재초기화하지 않았다.
- 실제 조회: 별도 clean clone의 2d464ea에서 STATE·작업·설계 링크3개 원격 일치, #27 open·선행목록 빈 배열, PR26 MERGED·head 불일치 표시를 확인했다. 실행기는 당시 미커밋 구현본이며 배포 완료 증거가 아니다. session_started=false.
- 리뷰: Fable5.2/high는 사용량 한도 소진(is_error=true, session 4f2ddd00-04a8-4f01-a5d4-fc609a3bff63, 11월19일01시 KST 재설정). 사용자 조건부 승인에 따라 Opus5.5/high로 전환했다. 실제 modelUsage=claude-opus-5-5, session 1027ec03-ac9b-4870-946d-7ec065aaf82d. 차단 코드 결함 없음. 작업 기록 지연·전역 적용 범위 지적을 수정했다. 리뷰어는 제공 자료만 읽고 테스트를 실행하지 않았다.
- 낮은 우선순위: 공통 실패 메시지의 기존 handoff 용어와 중복 plan 링크는 기능 결함이 아니므로 이번에는 유지한다. 테스트 공백2건은 보완했다.
- 보존: 중앙 graphify-out/은 훅이 생성한 미추적 산출물이며 게시·삭제하지 않는다. 실제 원격 검사는 별도 clean clone에서 수행한다.

- 최종 로컬 검사: `python3 -m unittest discover -s tests -v` 90/90 PASS, `validate --reviewed`와 `git diff --check` PASS.
- 수정분 리뷰: 실제 `claude-opus-5-5`/요청 high, session `49da8c0b-320d-4582-8a74-7f9041941c69`, PASS·차단0. 리뷰어는 실행 기록과 수정분만 검토했다. PR head 일치/불일치는 동적으로 self.pr_result를 읽는 fixture와 두 테스트로 확인했다.
