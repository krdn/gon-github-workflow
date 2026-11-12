---
name: gon-github-workflow
description: 새 프로젝트를 시작하거나 GitHub 개발 표준을 도입·갱신할 때 최신 upstream 확인, 조사 기록, 이슈·PR·인수인계를 연결한다. 단순 질의나 기존 프로젝트의 작은 수정에는 초기화하지 않는다.
---

# GitHub 중심 프로젝트 시작

새 프로젝트는 첫 구현 전에 반드시 `gon-workflow start <절대경로> --repo OWNER/REPO`를 실행한다.
기존 코드·AGENTS·CLAUDE 파일을 먼저 읽는다. 충돌이면 임의 덮어쓰기 없이 수동 통합 PR을 준비한다.
명령을 찾지 못하면 중앙 저장소 `krdn/gon-github-workflow`의 README 설치 절차를 읽는다.

- start는 검토·merge된 중앙 main을 fast-forward하고 원본 버전/문서를 매번 조회한다.
- upstream 변경이나 통신 오류를 무시하고 시작하지 않는다. 중앙 저장소에서 upgrade로 변경 후보를 만들고 docs/upstream-update.md의 영향 검토, 필요한 어댑터 수정, 테스트와 독립 리뷰를 docs/review.md에 기록하고 `record-review --notes docs/review.md --reviewer "실제 리뷰어"`, `validate --reviewed` 후 PR로 반영한다.
- 프로젝트 도메인·프레임워크·외부 API의 현재 공식 자료를 조사한다. docs/start-context.json에 목표, 출처 URL/finding, 결정, 실제 checked_at, status=reviewed를 기록한다. 조사하지 않은 내용을 채우지 않는다.
- `gon-workflow ready <경로>`를 실행한다. 통과는 시작 조건만 뜻한다.
- GitHub remote를 확인한다. 새 저장소는 사용자 지정 범위를 따르고 미지정이면 비공개로 만든다. 이슈, 큰 작업의 하위 이슈/의존성, Project, Milestone을 필요에 맞게 만들고 URL을 재조회한다.
- 세부 작업과 기능별 적용은 생성된 docs/WORKFLOW.md를 따른다. gon-project-lifecycle이 있으면 같은 이슈/문서를 재사용한다.
- 기존 프로젝트 재개는 docs/STATE.md와 최신 원격 이슈/PR/CI를 대조한다. 새 프로젝트로 초기화하지 않는다.
- 끝날 때 요약을 커밋·푸시하고 명시된 이슈에 `gon-workflow handoff <경로> --issue URL`로 전달한다. 실제 원격 댓글을 확인한다.
- Buzz를 사용하면 ggw-<project>-<role> 에이전트, ggw-<project>-<topic> 채널을 사용한다. 독립 작업만 분산하고 실제 응답을 GitHub 기록으로 가져온다.
