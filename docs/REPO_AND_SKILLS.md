# 레포·스킬 선정 (vibe-repo-advisor 결과)

카탈로그: `vibe-repo-catalog-800.md`(2026-09-26 기준, Obsidian `리서치 - AI tool, agent, skills, etc/지식/claude/`)
레포 상태 확인: 2026-10-02 GitHub API(아카이브 여부·최근 push). 모두 활성 상태다.

## 상황 요약

- **목적:** 대기업 HR 채용공고를 매일 수집하고 HR 직무를 판별한다. 요구역량·자격을 추출해 트렌드를 집계한다. 결과는 Git과 Obsidian에 쌓는다.
- **현재 단계:** 기획 → 구현 직전.
- **가정**
  - 스택은 Python 3.12 + uv, 실행은 GitHub Actions로 한다. Windows에서는 `py`로 로컬 실행한다.
  - 개인·비상업 용도다. 그래도 라이선스는 MIT·Apache·BSD로 고른다. 나중에 상품화할 수 있기 때문이다.

## 추천 레포

| 레포 (Stars List) | 목적 · 사용 방향 | 기획·설계 | 구현·코딩 | 검토·검증 | 유지보수 | 보안·배포 | 주의 |
|---|---|:-:|:-:|:-:|:-:|:-:|---|
| apify/crawlee-python (Reliable Crawling) | 공식 채용사이트 수집 하네스. `respect_robots_txt_file=True`, 도메인별 동시성·재시도·요청 큐 내장. JS 렌더링이 필요한 사이트(HD현대)는 PlaywrightCrawler로 처리 |   | ● | ○ |   |   | Apache-2.0. `Crawl-delay` 지원은 이슈 #1396 상태 확인 필요 → 우리 코드에서 간격 강제 |
| adbar/trafilatura (Reliable Crawling) | 공고 상세 HTML에서 본문만 뽑아 담당업무·자격요건·우대사항 섹션으로 분리 |   | ● |   |   |   | Apache-2.0 |
| pydantic/pydantic (Data Quality) | `Position` 레코드, 출처 응답, (선택) LLM 출력 스키마 검증. 검증 실패 레코드는 저장하지 않고 review로 보냄 |   | ● | ● |   |   | MIT |
| duckdb/duckdb (Data Quality) | `data/postings/**/*.jsonl`에 바로 SQL을 실행. 주간 트렌드 집계, "이번 달 C&B 공고 몇 건?" 같은 질의 |   | ● |   | ● |   | MIT |
| google/langextract (Data Quality) | (선택, D-4) 자격요건 문장을 원문 위치(grounding)와 함께 구조화. 블루프린트의 "근거 저장" 원칙과 맞다 |   | ○ | ○ |   |   | Apache-2.0. LLM API 비용 발생. 규칙 분류로 먼저 시작 |
| gitleaks/gitleaks (AI Slop Elimination) | 사람인 키 등 시크릿 커밋 방지. pre-commit 훅 + Actions 단계 |   |   | ○ |   | ● | MIT |
| zizmorcore/zizmor *(카탈로그 외)* | GitHub Actions 워크플로 보안 린트: 액션 SHA 고정, 과한 `permissions`, 템플릿 인젝션 |   |   | ○ |   | ● | MIT. 카탈로그에 없지만 Actions 중심 설계라 추가 |
| binwiederhier/ntfy (Self-Verify & Report) | (선택, D-6) 휴대폰 푸시 보조. 기본 알림은 GitHub Issue |   |   |   | ○ |   | Apache-2.0. 공개 토픽은 이름만 알면 누구나 읽으므로 건수만 보냄 |
| santifer/career-ops (HR & People) | **참고만, 설치 안 함.** Claude Code 위 구직 파이프라인의 공고 평가·추적 구조를 개인 용도(관심·지원 상태) 설계에 참고 | ○ |   |   |   |   | 이 레포의 공고 수집 방식은 그대로 쓰지 않는다(출처 약관 별도) |

● 핵심 용도, ○ 보조 용도

## 고민 포인트

**이미 있는 것으로 충분하다(추가 안 함)**
- 기획→TDD: obra/superpowers
- PRD→태스크: eyaltoledano/claude-task-master
- 교차 리뷰용 패킹: yamadashy/repomix
- korean-law-mcp는 이 프로젝트에 필요 없다.
- 스펙 도구(spec-kit, OpenSpec)도 넣지 않는다. 이 문서 묶음과 superpowers로 충분하다.

**같은 역할 중 하나만 고른 것**
- **수집 하네스**: crawlee-python을 골랐다. 대안은 scrapy/scrapy(`ROBOTSTXT_OBEY`, AutoThrottle가 성숙함)다. 고른 이유는 세 가지다.
  - HTTP 크롤러와 Playwright 크롤러가 한 API에 있다.
  - robots 준수 옵션이 있다.
  - 출처가 몇 곳 안 돼 Scrapy 프로젝트 구조가 과하다.
  - 참고로 잡코리아 robots.txt는 Scrapy UA를 전면 차단한다. 잡코리아는 어차피 제외 대상이지만, 사이트들이 Scrapy를 경계한다는 신호로 읽을 수 있다.
- **본문 추출**: trafilatura를 골랐다. 대안은 kepano/defuddle(JS, Obsidian Web Clipper 엔진)이다. 파이프라인이 Python이라 trafilatura로 정했다.
- **알림**: GitHub Issue를 기본으로 쓴다. ntfy와 apprise 중에서는 ntfy를 골랐다. 하나면 충분하다.

**기업 지표(Phase 8)용**
- OpenDART 호출은 httpx(`hrwatch.net.client`)로 직접 한다. 엔드포인트가 2개뿐이라 라이브러리가 필요 없다.
- 대화 중에 회사 공시를 물어볼 때는 chrisryugj/korean-dart-mcp(카탈로그 Korean Picks)를 Claude에 연결하면 편하다. 수집 파이프라인에는 넣지 않는다.

**넣지 않는 것과 이유**
- RSSHub(⚠AGPL): 잡사이트 경로가 결국 해당 사이트를 스크래핑한다. 약관 회피 경로가 된다.
- EasySpider, Skyvern, browser-use, Firecrawl, Apify Actor: 약관 확인 없이 쓰기 쉬운 범용 스크래퍼다. 이 규모에는 과하다.
- changedetection.io: 셀프호스팅 서버가 필요하다. Actions 1회 실행 구조와 맞지 않는다.
- huginn, TrendRadar(⚠GPL): 상시 서버형이다.
- claude-code-action, gh-aw: 일일 수집에 LLM 에이전트가 필요 없다. 주간 리포트를 LLM으로 다듬고 싶어지면 그때 검토한다(API 비용 발생).

**도입 순서 의존성**
pydantic 스키마 → 사람인 어댑터(httpx만으로 충분하고 crawlee 불필요) → duckdb 집계 → gitleaks·zizmor → crawlee + trafilatura(Phase 6, 공식 사이트) → langextract(선택)

**비용·위험**
- crawlee의 Playwright를 Actions에서 쓰면 Chromium 설치에 1~2분이 더 든다. 동적 사이트에만 쓴다.
- langextract는 LLM 호출 비용이 든다. D-4를 켜기 전에는 의존성에 넣지 않는다.

## 바로 할 일

1. 레포 private 전환(PowerShell, gh 로그인 상태):
   ```powershell
   gh repo edit junthropic/HR-Recruitment-Notice-Track --visibility private --accept-visibility-change-consequences
   ```
2. 사람인 API 이용신청: https://oapi.saramin.co.kr/join (이용 목적 예: "개인 HR 직무 채용동향 모니터링, 비상업, 결과 비공개 저장")
3. 로컬 골격(Phase 1, Claude Code에서 `docs/BUILD_PROMPTS.md` Phase 1 프롬프트 사용):
   ```powershell
   py -m pip install uv
   uv init --package --name hrwatch; uv add pydantic httpx pyyaml duckdb
   uv add --dev pytest ruff
   ```

---

# 스킬 적용 맵

| 스킬 | 이 프로젝트에서 한 일 / 할 일 | 문서 위치 |
|---|---|---|
| vibe-repo-advisor | 위 레포 선정 | 이 문서 |
| agent-platform-playbook | 하네스 1개 원칙, LLM 단계 무도구화(trifecta 차단), 호출 상한·재시도 2회, 3단 triage, `allowed-tools`가 아니라 deny 규칙·훅으로 금지 도메인 차단, 스킬 수 10개 이하 유지 | PLAN 4절, AGENTS.md 규칙, COMPLIANCE 4절 |
| agent-ready-project-docs | AGENTS.md 골격: 등록 지점, 완료 기준 3층, 함정, 현실 점검, 셀프 리뷰 | AGENTS.md |
| desktop-commander:obsidian-vault | 볼트 폴더·MOC(`_홈.md`)·Bases(`_채용공고.base`)·frontmatter 통일·고아 노트 방지(모든 공고 노트가 일일 리포트에서 링크됨) | PLAN 7절 |
| obsidian-vault-sync | 볼트 루트 `C:\Obsidian (all)\Claude 프로젝트\` 규칙, 세션 결과물을 `사업 운영 - HR` 폴더에 저장 | PLAN 7절 |
| hr-periodic-watch (추가) | 회차 창(마지막 성공 이후), 출처 장애를 "없음"으로 처리 금지, append-only, 0건 2회 연속 시 "출처 점검 필요" | PLAN 3·4절 |
| hr-eval-harness (추가) | HR 직무 판별 골든셋 40건(블루프린트 10절 사례 포함), CODE 채점, LLM을 켜면 pass^3, 회귀 게이트 | BUILD_PROMPTS Phase 3 |
| hr-recruit-obsidian-sync (신규 제안) | "채용공고 옵시디언에 넣어줘" → 동기화 스크립트 실행 → 결과 보고 | 별도 스킬 제안 |

프로젝트 전용 Claude Code 스킬(레포 `.claude/skills/`, 구현 단계에서 생성, 최대 3개):
- `hrwatch-run`: 수동 실행·dry-run·특정 출처만 재실행
- `hrwatch-ask`: 3단 triage로 질문에 답함(리포트 → DuckDB → API)
- `hrwatch-add-source`: 새 출처 추가 시 AGENTS.md 등록 지점 7개를 순서대로 처리
