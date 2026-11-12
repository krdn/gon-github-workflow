# GitHub 연결·업그레이드 운영

## 새 저장소 연결

```bash
gon-workflow start /path/to/my-app --repo krdn/my-app
gon-workflow ready /path/to/my-app
```

start가 저장소 생성·Git 연결·첫 이슈·Milestone·Project·구성 푸시를 수행한다.
[저장소 생성](https://cli.github.com/manual/gh_repo_create)과 [Project 생성](https://cli.github.com/manual/gh_project_create)은 인증된 gh를 사용한다.
repo·workflow·project 권한이 필요하다. 권한 오류는 구성 성공이 아니며, 인증을 해결한 뒤 같은 명령을 다시 실행한다.
AI 실행 요청은 구성 이후 프로젝트에서 별도로 한다. 조사·구현·배포 결과는 아직 존재하지 않는다.

기존 원격에 코드가 있으면 먼저 clone한 기본 브랜치에서 실행한다. 원격 불일치·커밋되지 않은 변경은 먼저 정리한다.
기존 파일을 덮어쓰지 않으며, 관리 파일 충돌은 diff를 확인해 수동 통합한다.
기존 기본 브랜치의 구성 변경은 별도 PR로 전달한다. 해당 PR을 검증·merge·pull한 뒤 재실행한다.
구성 중 실패하면 이미 생성한 저장소·첫 이슈·Milestone·Project를 재조회해 재사용한다.
PR 단계에서 중단돼도 같은 start 명령이 기존 브랜치·PR을 재사용한다. 닫힌 PR은 다시 열어 재개한다.
커밋 hook·서명 실패 시 이번 실행의 stage만 해제한다. 원인을 해결한 뒤 재실행한다.
이때 생성 파일의 내용이 기록된 해시와 달라지면 사용자 변경으로 간주해 중단한다.

`.env`와 무관한 미추적 파일은 초기 커밋에 포함하지 않는다. 생성한 구성 파일만 명시적으로 추가한다. 기존 미추적 인수인계·조사 파일도 자동 공개하지 않는다.
기존 Dependabot 설정은 보존하고, 파일이 없을 때만 기본 설정을 만든다.
구성 Actions는 파일 형식과 저장소 연결값을 검사한다. 앱 테스트·배포·비밀값·유료 AI 엔진은 별도 작업이다.
`.github/project-management.md`의 기능별 적용 범위와 실제 URL을 함께 확인한다.

## 라벨과 공개 저장소 설정

새 public 원격의 첫 푸시에는 기존 로컬 Git 커밋 이력도 포함된다.
새 저장소 기본값은 public이다. 명시적인 `--visibility private`과 기존 저장소의 공개 범위는 존중한다.
공개 저장소에서는 [GitHub Free의 브랜치 보호](https://docs.github.com/en/rest/branches/branch-protection)를 사용할 수 있다.

표준 라벨의 이름·색·한국어 설명과 정리 대상은 중앙 [labels.json](../labels.json)에서 관리한다.
start는 표준 라벨을 생성·갱신한다. 이번 버전으로 새로 만든 저장소에만 미사용 기본 라벨 정리를 최초 한 번 적용한다.
정리 완료 후 사용자가 같은 이름의 라벨을 다시 만들어도 삭제하지 않는다. 이전 버전의 생성 기록만 있으면 정리·저장소 옵션·보호 설정을 소급 적용하지 않는다.
닫힌 이슈·PR까지 포함해 사용 여부를 조회하고, 조회 실패 시 해당 라벨을 삭제하지 않는다.
[GitHub Issues API](https://docs.github.com/en/rest/issues/issues#list-repository-issues)는 PR도 반환하므로 과거 분류를 보존할 수 있다.
일반 기존 저장소에 표준을 도입할 때는 기존 라벨을 삭제하지 않는다. 표준 9개와 같은 이름의 색·설명은 중앙 정책을 따른다.

새로 만든 공개 저장소는 main에 PR, configuration CI 통과, 리뷰 대화 해결을 요구한다.
관리자도 적용 대상이며 강제 푸시와 main 삭제를 막는다. 개인 저장소라 필수 승인 인원은 0명이다.
토론과 병합 후 head 브랜치 자동 삭제를 켠다. 기존 보호 규칙이나 적용 이후의 사용자 변경은 덮어쓰지 않는다.
GitHub 설정을 재조회해 적용을 확인한 뒤에만 성공으로 표시한다. 오류가 나면 같은 start로 재개한다.
비공개를 명시한 경우 유료 플랜이 필요한 보호 설정은 자동 적용하지 않는다.

기존 이슈·Project·Milestone, Dependabot, 구성 CI는 계속 사용한다.
Pages·Packages·배포·코드 스캔은 앱의 언어와 배포 대상이 정해진 뒤 구성한다. 공개가 모든 유료 기능을 활성화한다는 뜻은 아니다.

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
