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
기존 전역 지침은 로컬 백업 후 **새 프로젝트 시작 게이트만** 덧붙인다.
Codex는 `CODEX_HOME`을 존중한다. `~/.local/bin`을 PATH에 포함하고 새 세션에서 스킬을 확인한다.
Orca·원격 호스트·별도 CODEX_HOME은 해당 환경에서 별도 설치해야 한다.

## 새 프로젝트 시작

```bash
gon-workflow start /home/gon/dev/my-app --repo krdn/my-app
```

`start`는 최신 표준 확인 → 로컬 Git 초기화 → GitHub 저장소 → 첫 이슈·Milestone·Project → 구성 커밋·푸시까지 수행한다.
새 저장소는 기본 비공개이며 `--visibility public`으로 공개를 지정한다. 기존 공개 범위는 바꾸지 않는다.
원본 5개를 매번 조회하며, 미반영 업데이트·통신 오류·사용자 파일 충돌이면 중단한다.

```bash
gon-workflow ready /home/gon/dev/my-app
```

`ready`는 원격 커밋과 GitHub 연결을 재조회한다. 조사 결과가 비어 있어도 구성 확인은 통과한다.
구성 URL은 `.github/project-setup.json`에 저장한다. 같은 명령 재실행은 기존 자원을 재사용한다.
구성 Actions는 관리 파일을 검사한다. 앱 테스트·배포는 제품의 기술 스택이 정해진 후 추가한다.

**AI 조사·계획·구현은 구성 완료 후 해당 프로젝트에서 별도로 요청한다.**
예: 프로젝트 폴더를 열고 “이 프로젝트의 목표는 …이다. 공식 자료를 조사하고 계획부터 세워줘”라고 요청한다.
그때 `docs/start-context.json`에 실제 조사 결과를 기록하고 `gon-workflow implementation-ready <경로>`로 확인한다.
조사 결과를 자동 생성하거나 AI 실행 성공으로 표시하지 않는다.

[작업 규칙](templates/docs/WORKFLOW.md) · [실패 복구와 기존 저장소 적용](docs/operations.md)
프로젝트가 커지면 이슈를 나누고 중간 결과를 `docs/STATE.md`에 압축한다.

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

## 인수인계

```bash
# docs/STATE.md를 갱신하고 commit/push한 뒤 실행
gon-workflow handoff /path/to/my-app --issue https://github.com/krdn/my-app/issues/1
```

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
