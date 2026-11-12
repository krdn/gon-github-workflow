# 작업 인수인계

## 신규 공개 저장소·라벨 정책 — 2026-11-13

기준: [#12](https://github.com/krdn/gon-github-workflow/issues/12).
신규 저장소 기본값은 public이며 명시적인 private 옵션과 기존 공개 범위는 보존한다.
[labels.json](../labels.json)의 9개를 구성하고, 이번 버전의 새 저장소에만 미사용 기본 라벨을 최초 한 번 정리한다.
새 공개 저장소 main의 PR·configuration CI·대화 해결·강제 푸시/삭제 차단과 병합 후 head 자동 삭제를 설정한다.
사용 중인 라벨·사용자 정의 이름·기존 보호 규칙·구버전 저장소의 설정은 보존한다.
검증: 49개 테스트, CLI 기본 public, 실패 재개·동명 라벨 재생성 보존, 표준 lock·문서 링크 검사 통과.
외부 리뷰: 실제 claude-opus-5-5 high. 반복 정리 지적을 재현·수정했고 수정분 재검토 PASS. 이후 원격 재생성 시 이전 완료 표시를 재사용하는 경계 사례도 재현·수정하고 직접 테스트했다.
실제 대상 test-app은 세션 중 404로 바뀌었다. 새 정책의 실제 GitHub 생성·보호·삭제 결과는 아직 미검증이며 기존 실증 기록과 구분한다.


## 프로젝트 구성 자동화 — 2026-11-13

기준: [#9](https://github.com/krdn/gon-github-workflow/issues/9).
start가 Git/GitHub와 첫 이슈·Milestone·Project·구성 푸시를 완료하도록 수정했다.
ready는 구성 재조회이며, AI 조사 검사는 implementation-ready로 분리했다.
AI 조사·계획·구현은 구성 완료 후 해당 프로젝트에서 별도 요청을 받는다.
PR #10 병합, 36개 테스트와 PR/main CI 통과, 현재 PC 재설치 완료.
설치본으로 test-app start·ready 성공, 원격 커밋 일치·자원 중복 없음·기존 조사/인수인계 보존 확인.
AI 작업은 미실행이며 다음 요청을 기다린다. 근거는 [구성 검증 기록](setup-verification.md)에 있다.

## 최초 표준 전달 — 2026-11-12

확인일: 2026-11-12. 기준 작업: [#1](https://github.com/krdn/gon-github-workflow/issues/1).

- 목표: GitHub 중심 AI 개발 표준, upstream 검토 업그레이드, 신규 프로젝트 시작 게이트.
- 결정: 원본 전체 설치 대신 역할·상태 계약을 조합한다. 공개 저장소 유지. 원격 유료 AI 엔진은 선택 항목이다.
- 구현: [PR #5](https://github.com/krdn/gon-github-workflow/pull/5) merge. 구현 revision `d870ef5d6111ea46f25f1c26bb4001c79a94010c`.
- 검증: 20개 테스트, [PR CI](https://github.com/krdn/gon-github-workflow/actions/runs/43238140032), [main CI](https://github.com/krdn/gon-github-workflow/actions/runs/43238247586) 통과.
- 외부 리뷰: `claude-opus-5-5` high의 독립 리뷰 및 수정분 재검토. [지적 처리](review.md).
- 실제 설치: 현재 PC의 Codex·Claude 시작 지침과 스킬, gon-workflow CLI 설치. 기존 지침은 사용자 로컬 backup에 보존.
- 실제 동작: 설치된 CLI로 시작 2회 연속 성공, 사용자 인수인계 보존, 미조사 ready 차단, 조사 기록 후 ready 통과, 재설치 시 전역 지침 해시 불변.
- 업데이트: [수동 실행](https://github.com/krdn/gon-github-workflow/actions/runs/43238304035)에서 원본 5개 변경 없음과 전체 검사 통과. 매일 06:17 KST 예약. 후보 생성·실패 재개는 테스트했고 실제 원본 새 버전 PR 생성은 아직 관찰하지 않았다.
- 의존성: Dependabot이 실제 [#6](https://github.com/krdn/gon-github-workflow/pull/6)·[#7](https://github.com/krdn/gon-github-workflow/pull/7)을 생성했다. #6·#7 모두 변경 검토와 해당 SHA의 CI 확인 후 merge. setup-python 7.1.0, checkout 7.0.1을 전체 SHA로 고정했다.
- 관리: [Project #20](https://github.com/users/krdn/projects/20), 하위 이슈 #2/#3, 첫 Milestone, [Discussions #4](https://github.com/krdn/gon-github-workflow/discussions/4), main PR·필수 test 규칙, Dependabot, Security 정책 적용.
- 실패 기록: 실제 GitHub API 503에서 시작 차단 후 재조회 성공. 구버전 gh에 update-branch가 없어 Dependabot 재정렬 경로를 사용했다.
- 미검증: 미래 정시 실행, 원본 새 버전의 실제 후보 PR. 서버/웹 배포와 원격 AI 엔진은 미실행이며 이 로컬 CLI 전달의 완료 조건에 포함하지 않는다.
- 다음 작업: 실제 프로젝트 요청 시 `gon-workflow start <경로> --repo OWNER/REPO` → `ready`. AI 작업을 별도로 요청받으면 도메인 조사 → `implementation-ready` → GitHub 이슈/PR로 구현. 재개는 이 문서와 최신 원격 기록을 대조한다.
