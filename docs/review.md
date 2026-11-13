# 최초 조합 검토

2026-11-12. 구현: Codex. 독립 리뷰 실제 반환 모델: `claude-opus-5-5`, effort high.
원본별 채택/제외는 [조합 분석](analysis.md)에 기록했다. 초기 버전 lock과 이 문서의 해시는 upstream-review.json으로 연결한다.

## 원본 영향

- CCPM: PRD/epic/issue 추적을 채택. 별도 `.claude/epics` 할 일 목록은 만들지 않는다.
- Spec Kit: 명세·검증·버그 단계 분리를 채택. 기존 도구의 전체 커맨드 설치는 제외한다.
- GSD Core: 새 저장소 경로와 STATE/CONTEXT의 지속적 맥락 개념을 채택. 문서 경로를 통합한다.
- gh-aw: AI 추론 작업과 결정적 CI/CD 분리를 채택. 원격 엔진은 인증/비용 조건이 있는 선택 항목이다.
- Claude Code Action: 이슈/PR 상호작용을 선택적 엔진 경로로 유지. gh-aw와 중복 트리거하지 않는다.

## 독립 리뷰 처리

- 수용: orphan 업데이트 브랜치에서 PR 생성 재개. 원격 lock 내용이 다르면 차단한다.
- 수용: 미검토 lock이 CI/start를 통과하지 못하도록 lock·검토 문서 해시를 연결한다.
- 수용: 업데이트 후보는 한 번에 하나만 열어 중복 PR 누적을 막는다.
- 수용: 최신 정식 릴리스는 GitHub latest API를 사용한다. 404만 기본 브랜치로 대체한다.
- 수용: README는 커밋에 고정해 가져오고 별도 문서 compare 근거를 남긴다.
- 수용: 전역 지침은 경계 블록만 갱신하며 이전 내용을 백업한다. UTF-8·임시 파일 교체를 사용한다.
- 수용: UTC Z 표기 지원, 입력 타입 오류 처리, 직접 실행 테스트 누락을 보완한다.
- 조건부 지적 해소: `.local/`와 `__pycache__/`는 이미 ignore 대상이다. 설치 후 wrapper 연속 실행으로 확인한다.
- 기각: GITHUB_TOKEN 생성 PR의 CI가 전혀 생성되지 않는다는 주장은 [현재 공식 정책](https://docs.github.com/en/actions/concepts/security/github_token)과 다르다. opened/synchronize/reopened는 승인 대기 실행을 생성한다. 승인 대기는 통과가 아니다.
- 의도적 제약: 최신 문서 변경·원본 갱신 시 시작을 차단한다. 빈번한 upstream 변경의 운영 비용을 운영 문서에 명시했다.
- 의도적 제약: 심볼릭 링크 대상과 템플릿 은퇴는 수동 마이그레이션으로 처리한다. handoff는 명시적 게시 명령이며 commit/push 확인은 실행 절차로 남긴다.

20개 테스트 통과. 외부 리뷰 후 수정분 검토와 실제 GitHub CI·설치 검증 근거는 이슈/PR에 이어 기록한다.

## 수정분 재검토

동일 `claude-opus-5-5` high가 수정분을 한 번 더 검토했다. 새로 지적한 후보 해시 문제를 수정했다.
README 본문과 무관한 커밋이 생겨도 의미가 같은 후보는 같은 브랜치로 재개한다. 회귀 테스트를 추가했다.
branch 모드는 동일 SHA로 README를 조회해 두 번 조회 사이의 시점 차이를 없앴다.
미검토 자동 보고서를 record-review의 근거로 사용하는 경로도 거부한다.
이전 END_MARKER 없는 설치 버전은 실제 배포한 적이 없으므로 마이그레이션 대상이 없다.
검토 파일 누락은 CLI 최상위 OSError/KeyError 처리로 실패 종료한다. CI에는 검토 파일·문서를 함께 커밋한다.
checkout SHA는 GitHub API의 actions/checkout v4 commit 조회 결과와 일치한다.
검토 기록은 사람·모델 판단의 추적 장치이며 그 판단의 진실성을 자동 증명하지 않는다.

## 2026-11-13 원본 갱신

[PR #14](https://github.com/krdn/gon-github-workflow/pull/14): Claude Code Action `v1`의 커밋 이동과 GSD Core `v1.21.0`을 반영한다.
[영향 검토](upstream-update.md)는 실행기 미설치 계약을 유지하며 템플릿·스크립트 수정이 필요 없다고 판단했다.

- 독립 리뷰 실제 반환 모델: `claude-opus-5-5`, effort high. 결과: PASS, 병합 차단 지적 없음.
- 기존 테스트: `python3 -B -m unittest discover -s tests -v`로 49개 통과.
- 최신 조회: `python3 -B scripts/workflow.py check` 결과 `changed: []`, 종료코드 0.
- lock 형식·문서 상대 링크·`git diff --check` 통과. 원본 5개의 README 본문 해시 불변을 직접 비교했다.
- 문서 스타일 검사: `evolve docs ste-lint --strict --changed refs/remotes/origin/main --added`는 기준 파일 부재로 실행 불가. 수동 문장 검토와 링크 검사를 수행했다.

리뷰의 낮은 우선순위 관찰은 다음과 같이 처리한다.
검토 게이트는 기존 계약대로 `docs/review.md` 한 파일의 해시를 묶는다. 영향 문서의 현재 해시는 아래에 별도로 기록한다.
Action의 명령 제한과 auto 검토는 샌드박스를 보장하지 않는다. 엔진 활성화 시 classifier 비용·모델 접근 권한도 확인한다.
이동하는 태그 때문에 시작 차단이 반복될 수 있는 정책은 이번 갱신에서 변경하지 않는다.

외부 리뷰는 제공된 자료를 검토했으며 원격 상태·테스트 실행을 독립 재실행하지 않았다.
GSD 판단은 공식 릴리스 설명과 변경 범위를 기준으로 하며 전체 원본 구현의 보안 감사를 뜻하지 않는다.
새 lock의 검토 기록을 갱신한 뒤 `validate --reviewed`가 통과했다.
실네트워크 `prepare_project`는 임시 폴더에 구성 파일을 생성했고, 시작 상태와 복사된 lock의 일치를 확인했다.
해당 PR 커밋의 CI는 [PR #14](https://github.com/krdn/gon-github-workflow/pull/14)의 검사 결과로 확인한다.
원본 엔진 실행과 `gon-stock02`의 실제 GitHub 생성은 이번 갱신의 검증 범위에 포함하지 않는다.

- 영향 문서 SHA-256: `03fb3582cd46e4b08e5041ab66d7b618360f36b9fad4b83bc59f8adc9f739926`
- 외부 리뷰 입력 SHA-256: `6c6153b77f23b4da5ec667b4aff2870d85839df6328c4b72a54cc638e24a6a57`
