# GitHub 개발 운영

기준 저장소: https://github.com/{{REPO}}
표준 원본: https://github.com/krdn/gon-github-workflow

## 시작

`gon-workflow start . --repo {{REPO}}`는 중앙 main을 갱신하고 원본 버전을 조회한다.
변경 후보가 있으면 중앙 저장소에서 `upgrade`, 영향 검토, 테스트, 독립 리뷰 기록(record-review), PR CI·merge를 먼저 완료한다.
인터넷 오류는 최신 확인 성공이 아니다. 오류를 해결한 뒤 다시 실행한다.

`docs/start-context.json`에 목표, 최신 공식 출처와 확인 내용, 기술 선택, 제약을 기록한다.
`status`를 `reviewed`로 바꾸고 `checked_at`을 실제 확인 시각으로 기록한다.
`gon-workflow ready .`는 24시간 이내의 도구 확인과 조사 기록을 검사한다.
이 검사는 출처 내용의 진실성이나 실제 기술 호환성까지 증명하지 않는다.

GitHub 저장소를 만들거나 기존 remote를 확인한 뒤 첫 목표를 이슈로 기록한다.
큰 작업은 상위 이슈와 하위 이슈, 의존 관계를 사용한다. Projects는 상태 보기다.
원격 저장소 생성은 기본 비공개이며 사용자가 지정한 소유자·공개 범위를 우선한다.

## 작업

1. 이슈: 목표·수용 기준·범위·검증 방법을 기록한다.
2. 큰 기능: `docs/`에 명세와 계획을 쓰고 이슈에서 연결한다.
3. 버그: 재현 → 원인 → 수정 → 원래 증상 재검증을 구분한다.
4. 작업 브랜치와 PR에서 구현하고 CI·필요한 리뷰를 확인한다.
5. 배포: 프로젝트의 실제 Actions·Environment·Release 경로를 사용한다.
6. 마무리: 변경 SHA, 검사 결과, 이슈/PR/배포 링크와 다음 행동을 요약한다.

작은 수정에 전체 명세 절차를 강제하지 않는다. 앱 검증·배포 명령은 실제 스택에 맞게 구성한다.
동작하지 않은 배포 workflow나 빈 성공 job을 완료 증거로 삼지 않는다.

## 인수인계

`docs/STATE.md`는 12,000자 이내로 유지하고 상세 로그는 이슈·PR·Actions로 연결한다.
목표 / 확정 결정 / 완료·미완료 / 실패한 시도 / 검증 근거 / 다음 행동을 기록한다.
커밋·푸시한 뒤 `gon-workflow handoff . --issue https://github.com/{{REPO}}/issues/N`으로 이슈에 전달한다.
다음 AI는 최신 원격 기록을 읽고 실제 코드·CI 상태를 확인한다. 요약만 믿고 완료를 선언하지 않는다.

## 업데이트와 복구

다음 신규 시작 또는 명시적인 표준 갱신 때 `start`를 다시 실행한다.
사용자가 수정한 관리 파일이 있으면 전체 적용을 중단한다. diff를 검토해 별도 PR에서 통합한다.
`workflow-state.json`의 해시만 고쳐 충돌을 숨기지 않는다.
이전 버전 복구는 적용 PR을 revert하고 해당 중앙 revision과 lock을 함께 복구한다.
오래된 원본을 사용하는 예외는 근거와 만료 조건을 이슈에 기록하며, 최신 확인으로 표시하지 않는다.

## 협업과 GitHub 기능

Buzz 에이전트: `ggw-<project>-<role>`, 채널: `ggw-<project>-<topic>`.
역할: coordinator, researcher, implementer, reviewer. 동일 파일 소유권을 겹치지 않는다.
설계 탐색은 Discussions, 확정 결정은 docs, 실행은 Issues, 상태는 Projects, 통합은 PR로 연결한다.
Buzz 응답은 이슈로 옮기고 생성 초안과 실제 저장·응답 확인을 구분한다.
Packages·Pages·배포는 제품에 해당할 때 구성하고, 미적용 사유는 `.github/project-management.md`에 남긴다.
