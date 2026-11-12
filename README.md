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

매번 중앙 저장소 main을 fast-forward하고 원본 5개의 버전과 README를 조회한다.
미반영 업데이트·통신 오류·사용자 파일 충돌이면 멈춘다. 캐시만으로 성공하지 않는다.
생성한 `docs/start-context.json`에 실제 조사 결과를 채운다. 예:

```json
{
  "checked_at": "실제 UTC ISO-8601 확인 시각",
  "objective": "누구의 어떤 문제를 해결할지",
  "sources": [{"url": "https://공식문서주소", "finding": "실제로 확인한 버전·제약"}],
  "decisions": "선택한 기술과 이유, 미확정 사항",
  "status": "reviewed"
}
```

```bash
gon-workflow ready /home/gon/dev/my-app
```

이후 Git 저장소·GitHub 비공개 저장소와 첫 이슈를 만들고 구현한다.
`start`는 로컬 준비 명령이며 원격 저장소를 자동 생성하지 않는다.
[생성된 작업 규칙](templates/docs/WORKFLOW.md), [GitHub 연결 절차](docs/operations.md)를 따른다.
프로젝트가 커지면 이슈를 나누고, 중간 결과는 `docs/STATE.md`에 압축한다.

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
