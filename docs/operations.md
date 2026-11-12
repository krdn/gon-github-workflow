# GitHub 연결·업그레이드 운영

## 새 저장소 연결

`start`와 도메인 조사·`ready` 후 아래 순서를 적용한다. 기존 저장소는 remote부터 확인한다.

```bash
cd /path/to/my-app
git init -b main
git add .
git commit -m 'chore: initialize project workflow'
gh repo create krdn/my-app --private --source . --remote origin --push
gh issue create --repo krdn/my-app --title '첫 구현 목표' --body-file /path/to/task.md
gh project create --owner krdn --title 'ggw-my-app' --format json
# 반환된 Project 번호를 사용한다.
gh project link NUMBER --owner krdn --repo krdn/my-app
gh project item-add NUMBER --owner krdn --url ISSUE_URL
```

항상 생성 전에 같은 저장소·작업 키·Project가 있는지 조회한다. timeout 후 POST를 곧바로 재시도하지 않는다.
`.github/project-management.md`의 기능별 상태와 실제 URL을 `docs/STATE.md`에 연결한다.
새 기술 스택의 package/lockfile에 맞춰 CI를 추가한다. 이 표준의 테스트는 소비 앱의 테스트가 아니다.

## 업데이트 판정

`check`는 변경 없으면 0, 변경 발견이면 2, 네트워크·입력 실패이면 1로 종료한다.
`upgrade`는 후보 lock과 보고서를 생성하고 0으로 종료한다. 종료코드 0이 호환성 승인이라는 뜻은 아니다.

1. docs/upstream-update.md의 각 원본 compare와 현재 문서를 읽는다.
2. 기존 계약에 영향이 없으면 이유를 기록한다. 영향이 있으면 templates/skills/scripts를 함께 수정한다.
3. 테스트·독립 리뷰 후 docs/review.md에 결과를 쓴다. `record-review --notes docs/review.md --reviewer "실제 리뷰어"`로 해당 lock과 근거 해시를 묶는다. `validate --reviewed`와 CI는 미검토 lock 변경을 거부한다.
4. PR에서 해당 SHA의 CI를 확인하고 merge한다. 문제가 있으면 변경 PR을 revert한다.
5. 소비 프로젝트 start에서 수정되지 않은 관리 파일을 갱신한다. 충돌은 diff를 보며 수동 통합한다.

매일 자동 점검은 중앙 저장소에서만 수행한다. 후보 PR을 만들려면 Actions의 PR 생성 권한이 필요하다.
[GITHUB_TOKEN으로 만든 PR의 CI](https://docs.github.com/en/actions/concepts/security/github_token)는 실행 승인 대기 상태가 될 수 있다.
승인 대기를 통과로 간주하지 않는다. 자동화는 자체 테스트도 실행하지만 대상 PR SHA의 검증을 대신하지 않는다.

## 설치 복구

설치 전 지침은 `~/.local/state/gon-github-workflow/backups/<시각>/`에 보존한다.
제거할 때 전역 AGENTS.md/CLAUDE.md의 `<!-- gon-github-workflow -->` 블록만 제거하고
설치된 CLI·스킬 심볼릭 링크만 제거한다. 다른 도구의 원본 디렉터리는 삭제하지 않는다.
백업 전체 복원은 설치 이후 다른 편집이 없는지 먼저 비교한다.

## 현재 저장소 기능 적용

실제 운영 증거는 docs/STATE.md와 이슈 #1에 기록한다.
Projects는 `ggw-gon-github-workflow`, 이슈는 작업 기준이다. 초기 Milestone은 첫 표준 전달이다.
Discussions는 도입·운영 협의에 사용하고 확정 결정은 docs에 둔다.
Actions CI와 일일 upstream 후보, Dependabot Actions 갱신을 사용한다.
Wiki는 docs와 중복되어 사용하지 않는다. 이 제품은 로컬 CLI이므로 웹 Deployments·Pages·Packages는 현재 해당하지 않는다.
Secrets·유료 엔진·클라우드 배포는 필요해질 때 해당 실행 경로를 별도로 구성한다.

업데이트 후보는 한 번에 하나만 연다. 원격 브랜치만 남았으면 내용 해시를 확인해 PR 생성부터 재개한다.
README도 최신 정보 확인 대상으로 삼으므로 릴리스가 같아도 문서 변경은 검토가 필요하다. 활동이 잦은 원본은 시작 차단 빈도가 높을 수 있다.
템플릿 은퇴 시 관리 파일을 별도 PR에서 보존/이동/제거하고 workflow-state.json의 해당 항목을 함께 제거한다. 소유권 해제 이유를 이슈에 남긴다.
