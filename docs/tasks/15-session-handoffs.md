# 작업 #15: 세션별 작업 기록과 선택적 재개

- 상태: 완료 (2026-11-13)
- 목표: 큰 요청을 저장소의 작업별 파일로 나누고 새 세션이 현재 작업만 먼저 읽는다.
- 완료 조건: 생성 템플릿·스킬·설치 안내 반영, 기록 보존 검사, PR/main CI·설치·생성 결과 확인.
- 허용 범위: 문서·초기 문구·작업 파일 양식. 세션 실행기·자동 종료·새 과금 경로·기존 프로젝트 일괄 갱신은 제외.
- 의존관계: 없음. 기존 GitHub Issue/PR/CI·handoff 사용.
- 이슈: https://github.com/krdn/gon-github-workflow/issues/15
- 구현: [PR #16](https://github.com/krdn/gon-github-workflow/pull/16) 병합. 구현 SHA: `6e19cf29b4471b184f44fd5fddbdc1a943c58c3c`.

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
- 전달: PR/main CI 통과. [main CI](https://github.com/krdn/gon-github-workflow/actions/runs/43428967707). 원격 main과 로컬 중앙 checkout SHA 일치.
- 설치: 현재 PC의 Codex·Claude 스킬 링크와 전역 안내 반영 확인. 기존 안내의 관리 블록 밖 내용 보존, 백업 2개 확인.
- 설치본 실증: 임시 폴더의 작업 양식 생성, 기존 작업/STATE를 변경한 뒤 재적용해 바이트 보존 확인. 실제 새 GitHub 저장소 생성은 이 변경 검증에서 실행하지 않았다.
- 미검증: 실제 새 AI 세션의 지침 준수와 토큰 절감량. 정적 검사·파일 생성 성공과 구분한다.

## 다음 행동

이 작업은 완료했다. 재실행하지 않는다. 새 프로젝트는 다음 start에서 양식을 받는다. 기존 프로젝트는 다음 작업부터 현재 기록을 보존하며 필요한 작업 파일만 도입한다. 실제 토큰 절감량 평가는 별도 요청에서 측정한다.

## 새 세션 시작 문구

> docs/STATE.md와 docs/tasks/15-session-handoffs.md, Issue #15의 최신 PR/CI만 먼저 확인하고 완료 여부를 확인하고 미완료 행동이 있을 때만 이어가줘. 기존 전체 기록은 다시 읽지 말아줘.
