# 작업: GitHub 기준 세션 운영

기준 이슈: https://github.com/krdn/gon-github-workflow/issues/27

- 상태: 설계 기록, 구현 대기.
- 범위·완료 조건: [설계](../plans/github-session-resume.md), #27 체크리스트.
- 필수 자료: [조사](../research/github-session-2026-11.md), workflow.py handoff, install.py, tests/test_handoff.py. 이전 전체 대화는 읽지 않는다.
- 브랜치: feat/github-session-resume. 기준 de13110.
- 검증 경계: ready는 중앙 project-setup 기록 부재로 실패. 재초기화 없이 실제 main SHA·PR26·CI·이슈27 확인.
- 다음 행동: 원격에 설계 기록을 반영한 뒤 회귀 테스트와 resume을 구현한다.
- 리뷰: Fable5.2/high 우선, 사용량 소진 시에만 Opus5.5/high 사용. 반환 모델을 별도로 확인한다.
