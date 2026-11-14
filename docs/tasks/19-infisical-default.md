# Infisical 기본 플랫폼

- 기준: [Issue #19](https://github.com/krdn/gon-github-workflow/issues/19)
- 목표: 소비 프로젝트의 앱·AI 비밀 키, 인증서, 권한 접근 기본 플랫폼을 Infisical로 통일한다.
- 범위: 생성 설정·가이드·AI 지침·설치 블록. 계정/서버 생성과 기존 소비 프로젝트 일괄 이전은 제외한다.
- 상태: 구현·로컬 검증 완료. 원격 CI·병합·설치 최종 결과는 [PR #20](https://github.com/krdn/gon-github-workflow/pull/20) 본문에서 확인한다.
- 작업 브랜치: `feat/infisical-default`; 기준 main `f36503dceb9fc1a38e26eca08932597b74cee38e`.

## 재개에 필요한 자료

`templates/docs/INFISICAL.md`, `scripts/workflow.py`의 `apply_templates`, 이 이슈와 PR만 먼저 읽는다.
공식 근거는 `docs/start-context.json`과 연결 안내에 있다.

## 변경과 검증

- 비밀값 없는 `.infisical.yaml`을 사용자 소유 seed로 생성한다. 기본 환경 dev, 운영 자동 매핑 없음.
- 기존 JSON 위에 YAML을 생성하지 않고 기존 YAML과 재실행 시 사용자 수정을 보존한다.
- AGENTS·WORKFLOW·스킬·설치 블록에 Infisical 정책과 실제 연결 검증 경계를 반영한다.
- 초기 테스트에서 설정 미생성·심볼릭 링크 검증 누락 3개 실패를 확인했다. 구현 후 전체 55개가 통과했다. 리뷰 후 JSON 심볼릭 링크 보존 회귀를 추가해 최종 56개가 통과했다.
- 중앙 저장소 ready는 기존 `.github/project-setup.json` 부재로 실패했다. 재개 작업이라 재초기화하지 않았다. 원격 main과 기존 CI 성공 및 implementation-ready는 확인했다.
- GitHub 커넥터 쓰기 403으로 인증된 gh를 사용했다. 요청한 type 라벨이 원격에 없어 이슈는 라벨 없이 생성했다.
- 최신 upstream 실조회와 임시 프로젝트 생성 통과. 생성 YAML 파싱·git check-ignore·Markdown 링크·validate --reviewed·diff 검사 통과.
- 로컬 CLI 0.45.7의 run 명령·옵션을 확인했다. 인증·비밀값 주입·PKI·PAM 실연결은 미검증이다.

## 독립 리뷰와 반영

- 실제 반환 모델 `claude-opus-5-5`, high. 중대 결함 없음, Medium 1개와 Low·설계 의견을 받았다. 수정 후 독립 재리뷰 PASS로 표현하지 않는다.
- Medium 반영: 읽기 전용 JSON 심볼릭 링크(깨진 링크 포함)는 보존하고 YAML 생성을 건너뛴다. 쓰기 대상 YAML 링크의 기존 차단은 유지한다.
- Low·설계 반영: 문서 원본을 templates로 통합하고 과거 STATE 링크 복구, YAML/JSON 우선순위·삭제 후 재생성·ignore 충돌 안내를 보강했다.
- 유지: US Cloud는 명시된 기본값이며 자체 호스팅은 주소 변경 후 로그인한다. 공식 설정 문서에서 domain 우선순위를 확인했다. ignore를 강제로 우회해 게시하지 않는다.
- 리뷰 후 수정분은 직접 코드 대조와 전체 56개 회귀 테스트로 확인했다. 실서비스 연결 검증 범위는 확대하지 않는다.

## 다음 행동

PR #20의 CI·병합·설치 결과를 확인하고 미완료인 전달 단계만 이어간다. 전달 완료 후에는 각 소비 프로젝트의 인스턴스·ID·권한을 확정하고 실제 Infisical 연결을 검증한다.
