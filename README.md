# Gon GitHub Workflow

Claude·Codex의 계획, 디버깅, 검증, 인수인계와 도구 업데이트를 GitHub 기록으로 연결한다.
CCPM의 작업 분해, Spec Kit의 명세·검증, GSD의 상태 요약을 하나의 운영 계약으로 조합한다.
원본 실행기 5개를 중복 설치하는 제품은 아니다. [조합 분석](docs/analysis.md)을 참고한다.

## 설치

Python 3.10+, Git, 인증된 GitHub CLI가 필요하다. 별도 Python 패키지는 없다.

```bash
git clone git@github.com:krdn/gon-github-workflow.git
cd gon-github-workflow
python3 scripts/install.py
```

설치기는 `~/.local/bin/gon-workflow`, Codex와 Claude의 스킬 링크를 만든다.
기존 전역 지침은 로컬 백업 후 **GitHub 기준 작업·세션 운영 블록만** 덧붙인다.
Codex는 `CODEX_HOME`을 존중한다. `~/.local/bin`을 PATH에 포함하고 새 세션에서 스킬을 확인한다.
Orca·원격 호스트·별도 CODEX_HOME은 해당 환경에서 별도 설치해야 한다.

## 기본 보안 플랫폼

이 워크플로의 모든 소비 프로젝트는 **Infisical**을 비밀 키·인증서·권한 접근의 기본 플랫폼으로 사용한다.
`start`는 `.infisical.yaml`과 [연결 안내](templates/docs/INFISICAL.md)를 생성한다. 기본 환경은 `dev`이며 기존 YAML/JSON과 프로젝트별 수정은 보존한다.
프로젝트별로 인스턴스 주소·프로젝트 ID·접근 권한을 연결해야 한다. 계정/서버 생성, 비밀값 이전, 인증서 발급, PAM 연결은 자동 실행하지 않는다.
기존 소비 프로젝트는 명시적인 표준 갱신 시 적용하며 충돌 파일은 PR에서 통합한다.

## 새 프로젝트 시작

`start`는 워크플로 최초 적용 때 없는 권한 파일을 생성한다. 기존 워크플로 프로젝트에 재적용해도 권한 파일을 추가하지 않으며, 사용자 수정·삭제도 보존한다.

| 파일 | 기본값 | Git 게시 |
|---|---|---|
| `.claude/settings.local.json` | `permissions.defaultMode: bypassPermissions` | 제외 |
| `.codex/config.toml` | `approval_policy = "never"`, `sandbox_mode = "danger-full-access"` | 새로 생성한 파일만 seed로 등록; Git에서 무시하면 로컬 보존 |

새 `.gitignore`에는 Claude 로컬 설정 제외 규칙을 넣는다. 기존 `.gitignore`는 보존하므로 규칙이 없으면 `.claude/settings.local.json`을 직접 추가한다. 제외하지 않으면 이 파일이 미추적 상태로 남아 clean 상태를 요구하는 `handoff`가 중단된다.
Claude Code v2.1.257부터 프로젝트 파일의 `bypassPermissions`는 적용되지 않는다. 실제 실행에는 `claude --permission-mode bypassPermissions` 또는 사용자 설정이 필요하다([공식 설정](https://code.claude.com/docs/en/settings-reference#permissions-defaultmode)).
Codex는 [신뢰한 프로젝트의 설정](https://learn.chatgpt.com/docs/config-file/config-basic)을 읽는다. 생성기는 전역 설정·프로젝트 신뢰·실행 인자를 바꾸지 않으며, 파일 생성이 런타임 적용을 증명하지는 않는다.

```bash
gon-workflow start /home/gon/dev/my-app --repo krdn/my-app
```

`start`는 최신 표준 확인 → 로컬 Git 초기화 → GitHub 저장소 → 첫 이슈·Milestone·Project → 구성 커밋·푸시까지 수행한다.
새 저장소는 기본 **public**이며 비공개가 필요할 때만 `--visibility private`을 지정한다. 기존 공개 범위는 바꾸지 않는다.
원본 5개를 매번 조회하며, 미반영 업데이트·통신 오류·사용자 파일 충돌이면 중단한다.

```bash
gon-workflow ready /home/gon/dev/my-app
```

`ready`는 원격 커밋과 GitHub 연결을 재조회한다. 조사 결과가 비어 있어도 구성 확인은 통과한다.
구성 URL은 `.github/project-setup.json`에 저장한다. 같은 명령 재실행은 기존 자원을 재사용한다.
구성 Actions는 관리 파일을 검사한다. 앱 테스트·배포는 제품의 기술 스택이 정해진 후 추가한다.
새 공개 저장소는 main 변경에 PR·구성 CI·리뷰 대화 해결을 요구하고 강제 푸시·main 삭제를 차단한다.
개인 작업이 막히지 않도록 필수 승인 인원은 0명이다. 토론과 병합 후 작업 브랜치 자동 삭제도 켠다.

라벨은 [labels.json](labels.json)의 9개로 구성한다. 작업 종류는 feature·bug·docs·research·maintenance,
추가 표시는 priority:high·status:blocked·needs:input·workflow:ai다(type 접두사는 종류에 붙는다).
이번 버전으로 새로 만든 저장소의 미사용 기본 라벨을 최초 한 번만 정리하고, 기존 이슈·PR에 사용 중이거나 정리 목록에 없는 라벨은 보존한다.
[라벨과 보호 설정 운영](docs/operations.md#라벨과-공개-저장소-설정)에서 적용 범위를 확인한다.

**AI 조사·계획·구현은 구성 완료 후 해당 프로젝트에서 별도로 요청한다.**
예: 프로젝트 폴더를 열고 “이 프로젝트의 목표는 …이다. 공식 자료를 조사하고 계획부터 세워줘”라고 요청한다.
그때 `docs/start-context.json`에 실제 조사 결과를 기록하고 `gon-workflow implementation-ready <경로>`로 확인한다.
조사 결과를 자동 생성하거나 AI 실행 성공으로 표시하지 않는다.

[작업 규칙](templates/docs/WORKFLOW.md) · [실패 복구와 기존 저장소 적용](docs/operations.md)
큰 요청은 작업별 이슈와 `docs/tasks/<이슈번호>-<짧은이름>.md`로 나눈다.
`docs/STATE.md`는 현재 작업을 가리키는 짧은 목차이며, 새 세션은 그 작업 파일의 필수 자료만 먼저 읽는다.

## 업데이트

```bash
cd /path/to/gon-github-workflow
git switch -c chore/review-upstreams
python3 scripts/workflow.py upgrade
# docs/upstream-update.md의 변경 링크를 읽고 조합 규칙/템플릿을 수정
# 독립 리뷰와 지적 처리를 docs/review.md에 기록
python3 -m unittest discover -s tests -v
python3 scripts/workflow.py record-review --notes docs/review.md --reviewer "실제 리뷰어/모델"
python3 scripts/workflow.py validate --reviewed
# 독립 리뷰 → commit → push → PR → CI 확인 → merge
```

매일 06:17 KST에 Actions가 같은 후보를 draft PR로 준비한다. 자동 merge는 하지 않는다.
원본 SHA·문서 해시 변경은 **검토 대상 감지**다. 실제 호환성 판단은 영향 검토와 관련 검사로 남긴다.
검토·merge 후 중앙 checkout을 main으로 돌린다. 전역 지침 갱신은 `python3 scripts/install.py`로 다시 적용한다. 다음 `start`가 새 표준을 적용한다.
기존 프로젝트의 상태 요약·조사 기록은 보존하며, 수정된 관리 파일은 자동 덮어쓰지 않는다.

## GitHub 기록과 세션 시작

모든 계획된 설계·구현은 GitHub 이슈에 범위·완료 조건을 먼저 기록하고, 설계·작업 파일을 커밋·푸시해 원격 링크로 연결한다. 대화나 로컬 파일만을 작업 기준으로 삼지 않는다.
새 세션은 `gon-workflow resume <경로> --issue URL --task docs/tasks/N-task.md`로 원격 기록을 확인한다. 별도 설계는 `--plan`, 관련 PR은 `--pr`로 모두 지정한다. 같은 세션에서 계속할 때도 이슈·문서·검증 기록을 갱신한다.
필요한 추가 개선은 현재 목표와의 관계·완료 조건을 먼저 기록하고 범위 안에서 구현한다. 독립 기능은 후속 이슈로 분리한다. 이슈 등록은 거래·배포·삭제 등 별도 실행 승인을 뜻하지 않는다.

단순 질의에는 이슈를 만들지 않는다. 작은 변경은 기존 이슈의 체크리스트와 짧은 작업 기록을 재사용한다. 설계 PR은 후속 구현 이슈를 자동 종료하지 않는다.

```bash
gon-workflow resume . --issue https://github.com/OWNER/REPO/issues/N \
  --task docs/tasks/N-task.md --plan docs/plans/feature.md \
  --pr https://github.com/OWNER/REPO/pull/P
```

`--plan`·`--pr`은 반복 가능하다. 별도 설계가 없으면 작업 파일에 계획을 기록한다. 이슈와 작업 파일의 정확한 이슈 URL, STATE·작업·지정 설계의 로컬/커밋/원격 일치, native 선행 관계, 지정 PR/CI를 확인한다. 새 세션을 실제 생성하지 않는다. JSON의 미지정·빈 CI·실패를 성공으로 해석하지 않는다.

명령 성공은 기록 확인이다. 선행 이슈의 not_planned 종료·열린 상태, PR 미통합·head 불일치, CI 실패/대기, 사용자 승인·소유권을 판단한 뒤 해당 범위의 다음 행동을 정한다. CI 실패 수정은 같은 이슈로 진행할 수 있다. 문서의 충분성이나 지정하지 않은 PR까지 검사하지 않는다.

미커밋·미푸시·원격 불일치·조회 실패이면 자동 stash/삭제/재초기화하지 않는다. 소유권을 확인하고 변경을 보존한 뒤 기록을 갱신한다. clean 체크아웃에서 확인하는 경우 작업 중인 다른 worktree의 미커밋 변경은 별도로 보고한다. 검증 시각 이후의 변경도 착수 전에 확인한다.

## 인수인계

생성된 저장소에는 [작업 파일 양식](templates/docs/tasks/TEMPLATE.md)이 포함된다.
작업 파일에 목표·범위·완료 조건·필수 자료·브랜치/SHA·검증/미검증·실패·다음 행동을 저장한다.
STATE에는 현재 작업 링크를 남긴다. 완료 이력은 링크로 보존하고 원문 대화·로그는 반복 복사하지 않는다.
기존 프로젝트는 적용 중인 기록을 재사용한다. 새 양식 도입 때문에 기존 STATE·작업 파일을 덮어쓰지 않는다.

새 세션 시작 문구:

> docs/STATE.md의 현재 작업 파일과 필수 읽기 목록, 관련 이슈·PR·CI만 먼저 확인하고 다음 행동부터 이어가줘.


```bash
# docs/STATE.md를 갱신하고 commit/push한 뒤 실행
gon-workflow handoff /path/to/my-app --issue https://github.com/krdn/my-app/issues/1 \
  --task docs/tasks/1-feature.md --dry-run
# 위 명령에서 --dry-run을 빼면 게시 후 원격 내용을 확인한다.
```

`--task`는 선택 항목이다. 현재 브랜치가 origin에 같은 SHA로 푸시되고 작업 트리가 clean이어야 한다.
STATE·선택 작업 파일의 로컬/커밋/원격 blob을 비교하고, SHA 고정 링크와 시작 문구를 이슈에 남긴다.
본문 복사 대신 링크를 사용하므로 문서 안의 상대 링크도 해당 커밋에서 열린다.
같은 전달의 순차 재실행은 댓글을 재사용하며, 게시 후 확인 실패는 성공으로 표시하지 않는다.
네트워크 오류 뒤 재시도할 때도 먼저 기존 댓글을 조회한다. 동시에 실행한 게시의 exactly-once 보장은 하지 않는다.
미커밋 작업은 자동으로 커밋하거나 버리지 않는다. 다른 환경에서 재개할 수 있다고 표시하기 전에 별도로 보존한다.

이 명령은 **기록 전달만 수행**한다. CI·사용자 수용·배포·제품 동작과 새 세션 실행은 별도다.
작업 경계에서는 새 대화에 필요한 기록만 전달하고, 디버깅이 이어질 때는 같은 세션을 사용할 수 있다.
새 탭에서 기존 세션을 resume하거나 대화를 fork하는 것은 독립된 새 대화 시작과 다르다.
AI에 새 세션 실행을 요청했다면 실제 세션 ID·프로젝트 경로·첫 작업과 요청한 탭 가시성을 확인한다.

명세·결정은 docs, 실행은 Issues, 진척 보기는 Projects, 변경·검증은 PR/Actions,
출시는 Releases, 실제 운영 배포는 Environments/Deployments를 사용한다.
원격 AI 실행은 [선택적 엔진 안내](docs/engines.md)를 따른다. 유료 엔진은 기본 활성화하지 않는다.

## 이 프로젝트의 근거

- [구현 이슈](https://github.com/krdn/gon-github-workflow/issues/1)
- [Project](https://github.com/users/krdn/projects/20)
- [CI](https://github.com/krdn/gon-github-workflow/actions/workflows/ci.yml)
- [업데이트 점검](https://github.com/krdn/gon-github-workflow/actions/workflows/upstreams.yml)
- [원본 버전 잠금](upstreams.lock.json) · [현재 상태](docs/STATE.md)

검증: `python3 -m unittest discover -s tests -v` 및 `python3 scripts/workflow.py validate --reviewed`.
시작/조사 게이트는 CLI에서 강제하며 AI가 임의의 다른 경로로 작업하는 것까지 차단하지는 않는다.
