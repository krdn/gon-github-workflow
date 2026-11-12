# 작업 인수인계

- 목표: 신규 프로젝트 시작·업데이트·인수인계를 GitHub 기준으로 통합한다.
- 기준 이슈: https://github.com/krdn/gon-github-workflow/issues/1
- 하위 작업: https://github.com/krdn/gon-github-workflow/issues/2 · https://github.com/krdn/gon-github-workflow/issues/3
- Project: https://github.com/users/krdn/projects/20
- 확정 결정: 원본 전체 설치 대신 역할·상태 계약을 조합한다. 원본 5개 버전/README를 추적한다. 공개 저장소 유지(사용자 답변).
- 완료: CLI·템플릿·스킬·업데이트 workflow 작성, 본 저장소 시작/조사 게이트 통과, 20개 테스트 통과.
- 실패한 시도: 첫 실제 시작 조회에서 GitHub API 503으로 적용 중단. 재시도 성공. 공개 범위 재조회 후 사용자 확인 완료.
- 검증 근거: `python3 -m unittest discover -s tests -v`, `python3 scripts/workflow.py validate`, 스킬 quick_validate 통과.
- 미완료: PR CI·merge, 전역 설치와 신규 생성 실제 확인. Claude 독립 리뷰와 수정분 재검토 완료; 지적 처리: docs/review.md.
- 다음 행동: 검증된 SHA를 PR로 전달하고 CI·merge·실제 설치를 확인한다.
- 운영 배포: 로컬 CLI 설치 예정. 서버/웹 배포·유료 원격 AI 엔진은 해당 없음/미실행.

- 운영 협의: https://github.com/krdn/gon-github-workflow/discussions/4
