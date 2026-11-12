# GitHub 기능 적용

저장소: https://github.com/{{REPO}}

| 기능 | 기준·적용 상태 |
| --- | --- |
| Code/docs | 설계·명세·ADR·압축된 인수인계 |
| Issues/sub-issues/dependencies | 작업 기준. 큰 작업에서 계층·차단 관계 연결 |
| Projects/Milestones/Labels | start가 첫 이슈·Milestone·Project를 연결. URL은 project-setup.json |
| Discussions | 탐색/협의. 비활성 시 이슈로 대체 |
| PR/Actions | 구성 파일 검사를 생성. 앱별 CI는 실제 스택으로 추가 |
| Releases/Deployments/Environments | 전달·운영 대상이 정해지면 구성. 미구성은 미배포 |
| Security/Dependabot | 스택별 취약점·의존성 갱신 정책 구성 |
| Rulesets/CODEOWNERS | 실제 권한·플랜 확인 후 적용 결과 기록 |
| Wiki | docs와 중복되지 않는 별도 용도가 있을 때만 사용 |
| Packages/Pages | 배포 제품이 해당할 때 사용 |
| Insights | 실제 이슈/PR/CI 결과 기반 현황 확인 |

설정 파일 존재와 기능 적용은 다르다. URL·검증 결과는 docs/STATE.md 또는 이슈에 기록한다.
