# HR-Recruitment-Notice-Track

2025년 매출 1,000억원 이상 기업(초기 275개)이 **오늘** 올린 HR 채용공고를 매일 19:05 KST에 자동 수집합니다. 수집한 공고는 HR 직무 여부를 판별해 이 레포에 쌓고, GitHub 알림으로 알려줍니다.
Obsidian `HR 채용공고 모음` 폴더로 내려받으면 채용 트렌드(워딩·요구역량·필수자격)를 볼 수 있습니다.

> 상태: **기획 완료, 구현 전(Phase 0)** · 개인·비상업 용도 · 레포는 private 운영 전제

| 문서 | 내용 |
|---|---|
| [docs/PLAN.md](docs/PLAN.md) | 기획서: 목적, 구조, 데이터, 자동화, Obsidian, 단계, 결정사항 |
| [docs/COMPLIANCE.md](docs/COMPLIANCE.md) | 출처별 약관·robots·API 조건, 수집 규칙, 계정 보호, 법적 배경 |
| [docs/REPO_AND_SKILLS.md](docs/REPO_AND_SKILLS.md) | 사용할 오픈소스 레포와 스킬 적용 맵 |
| [docs/BUILD_PROMPTS.md](docs/BUILD_PROMPTS.md) | Claude Code·Codex용 단계별 구현 프롬프트 |
| [AGENTS.md](AGENTS.md) | 코딩 에이전트 규칙(등록 지점·완료 기준·함정·현실 점검) |
| `config/` | 출처 레지스트리, HR 분류 체계, 역량·자격 사전(초안) |
| `docs/drafts/daily.yml` | GitHub Actions 워크플로 초안(Phase 4에서 활성화) |

수집 원칙:
- 공식 API와 기업 공식 채용사이트만 사용합니다.
- 블라인드·리멤버 등 약관상 자동 수집이 금지된 서비스에는 접속하지 않습니다.
- 로그인, 우회, 본문 전문 저장은 하지 않습니다.
