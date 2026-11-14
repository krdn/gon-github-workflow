# 원본 업데이트 검토

2026-11-14. `gon-stock03` 시작을 막은 Claude Code Action 변경을 [PR #18](https://github.com/krdn/gon-github-workflow/pull/18)에서 반영한다.
중앙 main `b0989d6`과 비교했다. 기존 최신 확인·미검토 변경 차단 정책은 유지한다.

| 원본 | 이전 | 반영 후보 |
| --- | --- | --- |
| Claude Code Action | `v1` / `4d75e5f390ee76b2e09c1980ecc99ff3a2e088c8` | `v1` / `f3b070c88125d33dbae5653df5f143101d4ea9dc` |

## 변경과 영향

[공식 변경 범위](https://github.com/anthropics/claude-code-action/compare/4d75e5f390ee76b2e09c1980ecc99ff3a2e088c8...f3b070c88125d33dbae5653df5f143101d4ea9dc)는 1개 커밋, 6개 파일이다.
Claude Code 설치 버전은 `2.1.323`에서 `2.1.325`로 바뀐다.
Agent SDK 의존성과 두 Bun lock은 `0.3.323`에서 `0.3.325`로 바뀐다.
해당 diff에는 Action 입력·권한·트리거 변경이 없다. Claude Code·SDK 내부 동작의 동일성을 뜻하지는 않는다.

현재 [원격 엔진 계약](engines.md)은 Claude Code Action을 선택 항목으로 둔다.
`scripts`, `templates`, `.github/workflows`를 검색하면 원본 추적 선언 외에 이 Action이나 SDK의 실행·설치 경로가 없다.
따라서 공통 규칙·템플릿·입력 어댑터의 수정 없이 lock과 검토 기록을 갱신한다.
이 판단은 현재 구성에 한정한다. 엔진을 활성화할 때는 잠긴 SHA로 실제 요청·응답과 권한을 검증한다.
[이전 보안 영향 검토](https://github.com/krdn/gon-github-workflow/blob/691fcace852bd64aeb96dda0f5a33a59f65c6205/docs/upstream-update.md)의 외부 PR 실행 제한·권한 모드·push 인증 확인도 유지한다.

## 문서 조회와 검증 범위

원본 5개의 README 본문 해시는 이전 main과 같다.
GSD Core·gh-aw·Claude Code Action의 README 커밋·URL 변경은 동일 본문의 참조 위치 갱신이다.
[Action README 조회 커밋](https://github.com/anthropics/claude-code-action/blob/9fa68854da5fadef4ed3dce240325a0dfe251880/README.md)은 실행 SHA보다 뒤에 있다.
그 커밋의 실행 코드까지 채택한 것은 아니며, 실행 변경 판단에는 위의 고정된 compare를 사용했다.

`upgrade`로 최신 후보와의 일치를 확인하고 기존 테스트·lock 검증·문서 링크 검사를 수행한다.
실제 결과와 독립 리뷰는 [검토 기록](review.md)에 남겨 `upstream-review.json`으로 lock과 연결한다.
Action·SDK 자체 실행과 주식 프로젝트 기능은 이번 중앙 갱신의 검증 범위에 포함하지 않는다.
중앙 PR CI·병합을 확인한 뒤 설치된 main을 갱신하고 `gon-stock03`의 `start`와 `ready`를 실행한다.
