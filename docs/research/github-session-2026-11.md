# GitHub 기준 세션 운영 조사

2026-11-17 KST. 기준 [#27](https://github.com/krdn/gon-github-workflow/issues/27), 시작 코드 `de13110`. [설계](../plans/github-session-resume.md).

## 결론

별도 작업 DB나 세션 서비스를 만들지 않는다. GitHub 이슈와 커밋된 작업 기록을 기준으로 하고 기존 handoff 검증을 재사용한다. 새 resume 명령은 기록 일치와 원격 상태를 조회하며 작업 착수 승인이나 세션 실행을 대신하지 않는다.

## 근거

| ID | 확인한 사실 | 설계에 미치는 영향 |
| --- | --- | --- |
| F1 | `scripts/workflow.py` handoff는 Git 루트·origin·clean·브랜치 SHA·GitHub ref·파일 blob을 확인한다. | 공통 검증 함수를 추출해 전달과 재개가 같은 경계를 사용한다. |
| F2 | [Contents API](https://docs.github.com/en/rest/repos/contents#get-repository-content)는 ref를 받아 커밋별 파일을 조회한다. | STATE·작업·명시한 설계 파일을 HEAD의 원격 blob과 비교한다. |
| F3 | [Git refs API](https://docs.github.com/en/rest/git/refs#get-a-reference)는 정확한 ref가 없으면404다. matching-refs는 접두 일치도 반환한다. | 기존 정확한 ref 조회를 유지한다. remote-tracking ref만 신뢰하지 않는다. |
| F4 | [gh pr view](https://cli.github.com/manual/gh_pr_view)는 headRefOid·state·statusCheckRollup을 제공한다. 설치된 gh2.46.0에서 PR26 조회 성공. | 지정한 PR의 SHA·상태·CI를 원문 구조로 보고한다. 미지정/빈 결과는 성공이 아니다. |
| F5 | [이슈 의존성](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies)의 최신 CLI blockedBy는 현재 설치본에서 Unknown JSON field다. | CLI 버전 강제 갱신 없이 기존 gh api를 사용한다. |
| F6 | [의존성 REST](https://docs.github.com/en/rest/issues/issue-dependencies)는 blocked_by를 페이지로 반환한다. #27 실제 조회는 빈 목록이었다. | 기존 collection으로 전체 페이지를 읽고 state/state_reason을 보존한다. 조회 실패를 의존성 없음으로 처리하지 않는다. |
| F7 | [PR 연결](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)의 종료 키워드는 기본 브랜치 통합 시 이슈를 닫는다. | 설계 PR에는 구현 이슈를 닫는 키워드를 쓰지 않는다. 구현·수용 완료 후 종료한다. |
| F8 | install.py는 지정 블록만 교체하고 백업한다. apply_templates는 수정된 관리 파일에 충돌하면 중단한다. | 전역 기본값은 설치기로 갱신하되 소비 프로젝트 일괄 덮어쓰기는 하지 않는다. |

## 선택 비교

점수는 본 작업의 판단이다. 3점이 유리하며 비용 항목은 변경·유지 비용이 낮을수록 높다.

| 대안 | 누락 감지 | 비용 | 기존 호환성 | 합계 |
| --- | --- | --- | --- | --- |
| 문서만 강화 | 1 | 3 | 3 | 7 |
| 문서 + 기존 검증 기반 resume | 3 | 2 | 3 | 8 |
| 별도 작업 DB·세션 자동 실행 서비스 | 3 | 1 | 1 | 5 |

두 번째 안을 선택한다. 공식 관계를 다시 저장하지 않아 동기화 비용이 없다. 대신 문서 내용의 충분성·누락된 설계/PR·사용자 승인까지 자동 판정하지 못한다. 사용자가 지정하지 않은 PR의 전역 탐색이나 세션 생성 자동화는 이번 요구의 필수 조건이 아니다.

## 확인 경계

중앙 저장소의 ready는 project-setup.json 부재로 실패했다. 기존 저장소를 재초기화하지 않았다. GitHub main SHA·이슈27·이전 PR26/CI는 직접 조회했다. 최근 도메인 조사로 implementation-ready를 별도 확인한다. 원본 lock은 변경하지 않는다.

리뷰는 사용자 지정 Fable5.2/high를 우선한다. 사용량 소진이 확인된 경우만 Opus5.5/high로 전환한다. 요청 모델·반환 모델·실패를 별도로 기록한다.
