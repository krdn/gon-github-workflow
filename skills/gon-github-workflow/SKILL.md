---
name: gon-github-workflow
description: 새 프로젝트 구성과 GitHub 개발 표준의 도입·갱신, 저장소의 작업 기록을 이용한 세션 재개를 지원한다. 단순 질의나 기존 프로젝트의 작은 수정에는 초기화하지 않는다.
---

# GitHub 중심 프로젝트 시작

새 프로젝트는 첫 구현 전에 반드시 `gon-workflow start <절대경로> --repo OWNER/REPO`를 실행한다.
기존 코드·AGENTS·CLAUDE 파일을 먼저 읽는다. 충돌이면 임의 덮어쓰기 없이 수동 통합 PR을 준비한다.
명령을 찾지 못하면 중앙 저장소 `krdn/gon-github-workflow`의 README 설치 절차를 읽는다.

- start는 검토·merge된 중앙 main을 fast-forward하고 원본 버전/문서를 매번 조회한다.
- upstream 변경이나 통신 오류를 무시하고 시작하지 않는다. 중앙 저장소에서 upgrade로 변경 후보를 만들고 docs/upstream-update.md의 영향 검토, 필요한 어댑터 수정, 테스트와 독립 리뷰를 docs/review.md에 기록하고 `record-review --notes docs/review.md --reviewer "실제 리뷰어"`, `validate --reviewed` 후 PR로 반영한다.
- start가 Git 초기화·GitHub 저장소·첫 이슈·Milestone·Project·구성 커밋과 푸시를 완료한다. 새 저장소 기본값은 public이며 비공개가 필요하면 `--visibility private`으로 지정한다. 기존 공개 범위는 보존한다.
- 새 공개 저장소에 main PR·configuration CI·리뷰 대화 해결·강제 푸시/삭제 차단을 구성한다. labels.json의 표준 라벨을 쓰고 일반 진행 상태는 Project에서 관리한다.
- `gon-workflow ready <경로>`로 원격 커밋과 연결을 재조회한다. URL은 `.github/project-setup.json`에 있다.
- AI 조사·계획·구현은 구성이 완료된 후 해당 프로젝트에서 별도로 요청받아 실행한다. 구성만 요청받은 경우 조사나 구현을 시작하지 않는다.
- AI 작업 요청 후 공식 자료를 조사해 docs/start-context.json에 목표, 출처 URL/finding, 결정, 실제 checked_at, status=reviewed를 기록한다. `gon-workflow implementation-ready <경로>`로 조사 기록을 확인한다. 조사하지 않은 내용을 채우지 않는다.
- 세부 작업과 기능별 적용은 생성된 docs/WORKFLOW.md를 따른다. gon-project-lifecycle이 있으면 같은 이슈/문서를 재사용한다.
- 큰 요청은 완료 조건·의존관계로 나누고 `docs/tasks/TEMPLATE.md`를 복사한 작업별 기록을 저장한다. 동등한 기존 기록은 재사용하며 사소한 수정은 STATE만 갱신한다.
- `docs/STATE.md`는 현재 작업 파일·다음 작업·공통 결정·차단 사유의 짧은 목차로 유지한다. 전체 이력을 누적하지 않는다.
- 기존 프로젝트의 새 세션은 적용 AGENTS → STATE → 지정/현재 작업 파일 → 필수 읽기 목록만 먼저 읽고 관련 원격 이슈/PR/CI·브랜치/SHA를 대조한다. 불일치나 필요한 근거만 추가 확인하고 전체 과거 대화·파일·로그를 반복 읽지 않는다. 신규 초기화하지 않는다.
- 작업 경계마다 범위·완료/미완료·검증 명령/결과/SHA·실패·다음 행동을 기록한다. 원격 저장을 확인한 뒤 새 세션 시작 문구를 전달한다. 미커밋 변경·실패·승인을 숨기거나 전환을 완료로 표시하지 않는다.
- 새 세션 자동 생성 기능을 가정하지 않는다. 사용자의 요청 범위와 현재 도구의 세션 전환 권한을 따른다.
- 끝날 때 요약을 커밋·푸시하고 명시된 이슈에 `gon-workflow handoff <경로> --issue URL`로 전달한다. 실제 원격 댓글을 확인한다.
- Buzz를 사용하면 ggw-<project>-<role> 에이전트, ggw-<project>-<topic> 채널을 사용한다. 독립 작업만 분산하고 실제 응답을 GitHub 기록으로 가져온다.
