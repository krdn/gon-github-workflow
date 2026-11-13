# 원본 업데이트 검토

2026-11-13. 신규 프로젝트 시작을 막은 두 원본 변경을 [PR #14](https://github.com/krdn/gon-github-workflow/pull/14)에서 함께 반영한다.
기준은 중앙 main `55dbf7b`이며, 원본 실행기 설치 범위는 [조합 분석](analysis.md)을 따른다.

| 원본 | 이전 | 반영 후보 |
| --- | --- | --- |
| Claude Code Action | `v1` / `4fa93a88de49bbef68b10eb15aabedf28ca0e1ed` | `v1` / `4d75e5f390ee76b2e09c1980ecc99ff3a2e088c8` |
| GSD Core | `v1.20.1` / `9385f4618b52ef68ed8a5e8bdd93cfb25bd87765` | `v1.21.0` / `357508df233ccca0dcf4332b385d6bee9b113da9` |

## Claude Code Action

[변경 12개 커밋](https://github.com/anthropics/claude-code-action/compare/4fa93a88de49bbef68b10eb15aabedf28ca0e1ed...4d75e5f390ee76b2e09c1980ecc99ff3a2e088c8)과 action 입력·사용 문서를 검토했다.
쓰기 권한이 없는 작성자의 PR에서 코드 실행 제한이 기본으로 켜지고, 조건에 따라 기본 권한 모드가 auto로 바뀐다.
Git 래퍼·인증정보·후속 단계 보호, fork 브랜치 처리와 구조화 출력 전달도 변경됐다.
세부 조건은 고정된 [사용 문서](https://github.com/anthropics/claude-code-action/blob/4d75e5f390ee76b2e09c1980ecc99ff3a2e088c8/docs/usage.md)와 [보안 문서](https://github.com/anthropics/claude-code-action/blob/4d75e5f390ee76b2e09c1980ecc99ff3a2e088c8/docs/security.md)를 따른다.

영향 검토: 현재 중앙·생성 템플릿에는 이 Action을 실행하는 job이나 입력 어댑터가 없다.
선택적 엔진이라는 기존 계약을 유지하며 lock만 갱신한다.
향후 엔진을 켤 때는 외부 PR 실행 제한, 권한 모드, 후속 push 인증을 해당 workflow에서 검증한다.

## GSD Core

[v1.21.0 릴리스](https://github.com/open-gsd/gsd-core/releases/tag/v1.21.0)와 [변경 범위](https://github.com/open-gsd/gsd-core/compare/9385f4618b52ef68ed8a5e8bdd93cfb25bd87765...357508df233ccca0dcf4332b385d6bee9b113da9)를 검토했다.
CLI 인수 검증과 worktree 밖 커밋 차단이 강화됐다.
상태 기록·재개·보관과 설정 파일 읽기 오류를 수정하고, Claude Workflow 사용 가능 여부의 판정도 변경했다.

영향 검토: 이 조합은 GSD 실행기·CLI·설정 형식을 설치하거나 호출하지 않는다.
`docs/STATE.md`에 결정·검증·다음 행동을 남기는 계약은 유지된다.
따라서 템플릿·스크립트 수정 없이 lock을 갱신한다. GSD 실행기의 동작 검증은 이번 범위에 포함하지 않는다.

## 문서와 검증 범위

원본 5개의 README 본문 해시는 중앙 main과 같다.
Spec Kit·gh-aw의 README 커밋·URL 변경은 동일 본문의 조회 시점 갱신이다.
README가 같아도 실행 코드와 하위 문서는 바뀔 수 있으므로 위의 별도 변경 근거를 사용했다.
독립 리뷰·검증 결과는 [검토 기록](review.md)에 남기고 `upstream-review.json`으로 lock과 연결한다.
기존의 최신 확인·미검토 변경 차단 정책은 유지한다.
