# Infisical 연결과 운영

이 프로젝트의 비밀 키·인증서·권한 접근 기본 플랫폼은 **Infisical**이다.
클라우드·온프레미스·AI 인프라에 같은 원칙을 적용한다. 생성된 설정은 연결 전 상태다.
`gon-workflow ready`는 GitHub 구성만 확인하며 Infisical 인증·접근 성공을 뜻하지 않는다.

## 프로젝트 연결

1. 사용할 Infisical Cloud 또는 자체 호스팅 인스턴스와 프로젝트를 정한다.
2. [공식 설치 안내](https://infisical.com/docs/cli/overview)로 CLI 0.44.8 이상을 설치한다.
3. `.infisical.yaml`의 `project-id`를 실제 프로젝트 ID로 바꾼다.
   `general.domain`은 US Cloud 기본 주소이며 EU Cloud 또는 자체 호스팅이면 해당 HTTPS 주소로 바꾼다.
4. 해당 인스턴스에 `infisical login --domain https://YOUR_INFISICAL_HOST`로 로그인한다.
   로그인은 사용자가 안전한 인증 화면에서 수행한다. 토큰·비밀번호를 대화나 명령 인수에 입력하지 않는다.

프로젝트 ID와 주소는 비밀값이 아니므로 설정 파일을 커밋할 수 있다.
설정 파일에는 비밀값을 넣지 않는다. 기존 `.infisical.json`은 계속 사용하며 YAML을 덧씌우지 않는다.
JSON에서는 `workspaceId`·`domain`·`defaultEnvironment`를 지정한다. 두 파일이 있으면 YAML이 우선하므로 사용할 파일을 확인한다.
`start` 재실행은 사용자 설정을 보존한다. 이미 설정이 있으면 `infisical init`으로 초기화하지 않는다.
두 설정 파일이 모두 없으면 다음 `start`가 기본 YAML을 다시 생성한다.
기존 Git ignore 규칙이 YAML을 제외하면 게시가 중단된다. 비밀값이 없는 설정인지 검토한 뒤 예외를 추가한다.
YAML의 환경·경로 키와 파일 우선순위는 [공식 설정 문서](https://infisical.com/docs/cli/project-config)를 따른다.

## 앱과 AI 실행

API 키·DB 비밀번호·모델 제공자 키는 Secrets Management에 저장한다.
`dev`·`staging`·`prod`를 분리하고 사람·CI·앱·AI 작업마다 필요한 프로젝트·환경·경로만 허용한다.
기본 환경은 `dev`다. 브랜치 이름으로 운영 비밀값을 자동 선택하지 않는다.

앱 실행 명령 앞에 CLI를 붙여 환경변수를 주입한다. 아래는 Node 앱의 예다.

```bash
infisical secrets-manager run --env dev --path / -- npm run dev
```

서버·컨테이너·Kubernetes에서는 지원되는 workload identity/OIDC와 Agent·SDK·Operator 중 해당 배포 방식을 사용한다.
머신 인증은 설정 파일의 프로젝트 선택에 의존하지 않고 `INFISICAL_PROJECT_ID` 또는 `--projectId`를 지정한다.
장기 공유 토큰 대신 짧은 수명의 인증과 최소 권한을 사용한다.
비밀값을 AI 프롬프트·이슈·로그·이미지 빌드 인수에 복사하지 않는다. `.env.example`에는 이름과 빈 값만 쓴다.
인증 실패는 실패로 처리하며 운영 비밀값이나 로컬 평문 파일로 자동 대체하지 않는다.

## GitHub Actions

배포 작업은 [Infisical OIDC 연결 절차](https://infisical.com/docs/integrations/cicd/githubactions)를 따른다.
Infisical에 전용 machine identity를 만들고 필요한 환경·경로의 읽기 권한만 부여한다.
신뢰 조건은 실제 저장소의 subject와 audience 및 브랜치 또는 보호된 GitHub Environment로 제한한다.
저장소 생성 시점에 따라 subject 형식이 다르므로 이름만으로 추측하지 않는다. 전체 저장소 wildcard를 기본으로 사용하지 않는다.

앱의 배포 workflow에 다음 값을 지정한다. 기본 구성 CI에는 비밀값을 주입하지 않는다.

| 항목 | 설정 |
| --- | --- |
| job permissions | `contents: read`, `id-token: write` |
| action | `Infisical/secrets-action`의 검토한 전체 commit SHA |
| `method` | `oidc` |
| `identity-id`, `project-slug` | 해당 identity ID와 프로젝트 slug; GitHub Variables에 저장 가능 |
| `domain` | 연결한 Infisical HTTPS 주소 |
| `env-slug`, `secret-path` | 해당 job에 허용한 환경과 경로 |

비밀값이 필요한 신뢰된 job에만 주입한다. 외부 PR 코드와 `pull_request_target`에서 비밀값을 사용하지 않는다.
OIDC를 쓸 수 없는 환경의 대체 인증은 별도로 결정하고 자격증명 보관·회전 방법을 기록한다.

## 인증서와 권한 접근

| 대상 | 기본 기능과 프로젝트별 설정 |
| --- | --- |
| TLS/mTLS 인증서 | [Certificate Management](https://infisical.com/docs/documentation/platform/pki/overview): CA·발급 정책·유효기간·갱신과 배포 대상 |
| 서버·DB·클러스터·클라우드 접근 | [PAM](https://infisical.com/docs/documentation/platform/pam/overview): Gateway·대상 계정·접근 역할·승인·세션 기록 |
| AI 에이전트 | 작업별 identity와 필요한 PAM 대상만 허용하고 작업 종료 시 접근 회수 |

이 CLI 설정 파일은 인증서 발급이나 PAM 구성을 자동 활성화하지 않는다.
기능별 인프라·플랜 가용성을 확인하고 필요한 대상만 연결한다.
인증서 개인키와 자격증명은 저장소에 넣지 않는다. 불가피한 로컬 파일은 `.secrets/`에 제한된 권한으로 보관한다.
기존 `.gitignore`는 자동 수정하지 않으므로 `.env*`·개인키·`.secrets/` 제외 여부를 확인한다.
이미 추적 중인 파일은 ignore로 보호되지 않는다. 유출된 값은 회전하고 이력을 별도로 정리한다.

## 연결 검증

대상 인스턴스·프로젝트·환경·권한을 확정한 후 실제 주입과 앱 요청 성공을 확인한다.
값을 출력하지 않고 필수 환경변수의 존재와 앱 동작만 검사한다. 허용하지 않은 환경의 접근 거부도 확인한다.
인증서는 발급·갱신·적용 결과, PAM은 실제 접속·권한 제한·세션 기록을 각각 확인한다.
이슈와 작업 파일에 검증 대상·시각·결과만 남기며 비밀값과 토큰은 남기지 않는다.
