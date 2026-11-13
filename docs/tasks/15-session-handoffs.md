# 작업 #15: 세션별 작업 기록과 선택적 재개

- 상태: 검증 완료, PR 전달 준비
- 목표: 큰 요청을 저장소의 작업별 파일로 나누고 새 세션이 현재 작업만 먼저 읽는다.
- 완료 조건: 생성 템플릿·스킬·설치 안내 반영, 기록 보존 검사, PR/main CI·설치·생성 결과 확인.
- 허용 범위: 문서·초기 문구·작업 파일 양식. 세션 실행기·자동 종료·새 과금 경로·기존 프로젝트 일괄 갱신은 제외.
- 의존관계: 없음. 기존 GitHub Issue/PR/CI·handoff 사용.
- 이슈: https://github.com/krdn/gon-github-workflow/issues/15
- 브랜치: feat/session-task-handoffs. 기준 SHA: 691fcace852bd64aeb96dda0f5a33a59f65c6205. 구현 SHA·PR은 이슈의 최신 전달 기록 확인.

## 먼저 읽을 자료

- `templates/docs/WORKFLOW.md`의 세션별 작업과 재개 절
- `templates/docs/tasks/TEMPLATE.md`
- `skills/gon-github-workflow/SKILL.md`
- 필요할 때만 `scripts/workflow.py:apply_templates`, `scripts/install.py:BLOCK`, `tests/test_workflow.py`의 생성·보존 테스트

## 현재 결과

- STATE를 현재/다음 작업의 짧은 목차로 정의하고 작업별 목표·범위·완료조건·읽을 자료·검증/미검증·실패·다음 행동을 별도 저장한다.
- 새 세션은 지정 작업·필수 자료·관련 원격 상태를 우선 확인한다. 전체 과거 대화·작업 파일·로그를 반복해서 읽지 않는다.
- 생성 양식과 기존 작업/STATE 보존 테스트를 추가했다. 전체 테스트 50개 통과.
- 작업 규모: 기존 실행 로직을 유지하는 문서·템플릿·초기 문구 변경. 별도 모델 리뷰 대상인 코드 기능/버그 수정으로 분류하지 않았다.
- 실패: 중앙 저장소에 `type:feature` 라벨이 없어 이슈 생성이 실패했고, 기존 `enhancement` 라벨로 생성했다.
- 미검증: 실제 새 AI 세션의 지침 준수와 토큰 절감량. 정적 검사·파일 생성 성공과 구분한다.

## 다음 행동

PR의 실제 변경 SHA와 CI를 확인한 뒤 병합하고 중앙 main을 갱신한다. 설치기는 기존 전역 지침을 백업하며 Codex·Claude의 같은 스킬 원본을 사용한다. 기존 프로젝트는 새 start를 강제하지 않고 필요할 때 작업 기록만 도입한다.

## 새 세션 시작 문구

> docs/STATE.md와 docs/tasks/15-session-handoffs.md, Issue #15의 최신 PR/CI만 먼저 확인하고 미완료 행동부터 이어가줘. 기존 전체 기록은 다시 읽지 말아줘.
