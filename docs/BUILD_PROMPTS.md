# 바이브코딩 단계별 프롬프트 (Claude Code 주력 · Codex 교차 리뷰)

공통 사용법:
- 각 Phase는 새 세션에서 시작한다. 첫 메시지에 아래 **공통 머리말 + 해당 Phase 프롬프트**를 붙인다.
- 끝나면 `repomix`로 묶어 Codex에 교차 리뷰를 맡긴다. 리뷰 기준은 `AGENTS.md` 셀프 리뷰 체크리스트다.
- superpowers 흐름(계획 → 테스트 먼저 → 구현 → 리뷰)을 따른다. Plan Mode로 계획을 먼저 승인받는다.

## 공통 머리말

```
이 레포의 AGENTS.md, docs/PLAN.md, docs/COMPLIANCE.md를 먼저 읽어라.
규칙 요약:
(1) sources.yml에서 ALLOWED_* + enabled인 출처만 호출한다.
(2) 모든 HTTP 요청은 hrwatch.net.client를 거친다.
(3) 차단 도메인에는 요청하지 않는다.
(4) 실패를 0건 성공으로 저장하지 않는다.
(5) 본문 전문·연락처·키를 저장하거나 출력하지 않는다.
(6) 테스트는 픽스처로만 하고 실제 사이트를 호출하지 않는다.
계획을 먼저 보여주고, 테스트부터 작성해라.
완료 기준은 AGENTS.md "완료 기준"의 명령이다.
```

---

## Phase 0 — 사전 확인 (사람 + Claude, 코드 없음)

사람이 할 일:
1. 레포 private 전환:
   `gh repo edit junthropic/HR-Recruitment-Notice-Track --visibility private --accept-visibility-change-consequences`
2. 사람인 API 신청: https://oapi.saramin.co.kr/join. 승인 메일의 이용조건(저장·표기·한도)을 `docs/COMPLIANCE.md`에 옮겨 적는다.
3. (사업자가 있으면) 고용24 기업회원 가입 후 Open API 신청.
4. 키를 GitHub Secrets에 등록: `gh secret set SARAMIN_ACCESS_KEY`

Claude에게:
```
docs/COMPLIANCE.md 1절에서 UNCHECKED 상태인 공식 채용사이트 4곳(삼성, LG, HD현대, KAI)을 하나씩 확인해라.
각 사이트에서 확인할 것:
- robots.txt 원문 중 공고 목록·상세 경로에 해당하는 줄
- 이용약관에서 자동수집·크롤링·복제 관련 조항(원문 인용 + URL)
- 로그인 없이 목록·상세가 보이는지
- 목록 데이터가 HTML인지 JSON(XHR)인지 → 브라우저 개발자도구 Network 탭 결과를 내가 붙여주면 판단
판정(ALLOWED_PUBLIC/EXCLUDED/보류)과 근거를 레지스트리 형식으로 제안하고, 내가 승인하면 반영해라.
접근은 WebFetch로 robots.txt와 약관 페이지만 연다. 공고 페이지를 대량으로 열지 않는다.
```

추가 확인(Actions에서 1회, 수동 실행 워크플로로):
```
.github/workflows/probe.yml(workflow_dispatch 전용)을 만들어라.
GitHub 러너에서 oapi.saramin.co.kr과 허용 후보 사이트 4곳의 robots.txt를 각각 1회만 GET한다.
기록할 것: 상태코드, 응답시간, 차단 페이지 여부(본문 키워드 검사).
결과는 Job Summary에만 출력하고 커밋하지 않는다. 해외 IP 차단 여부를 판단하기 위한 것이다.
```

**완료 기준:** 레지스트리 모든 행에 상태·확인일이 있다. 해외 IP 접속표가 있다. D-1~D-6 결정이 PLAN 12절에 기록돼 있다.

---

## Phase 1 — 골격과 감시 목록

```
Phase 1을 해라.

0. setup/claude/README.md대로 .claude/settings.json과 .claude/hooks/block_domains.py를 설치하고 /hooks로 확인한다.

1. uv 패키지 hrwatch(Python 3.12)를 만든다.
   - 의존성: pydantic, httpx, pyyaml, duckdb
   - dev 의존성: pytest, ruff

2. src/hrwatch/models.py
   - Position, Company, SourceStatus(PENDING/OK/PARTIAL/FAILED/BLOCKED),
     Discovery(FOUND/NOT_FOUND_IN_CHECKED_SCOPE/UNDETERMINED/REVIEW), RunLog, AdapterResult
   - PLAN 5-1절 스키마를 따른다.
   - 모든 datetime은 Asia/Seoul aware.

3. src/hrwatch/net/client.py
   - UA, 도메인별 최소 간격, 일일 예산, 재시도 2회, 429 Retry-After, 403·429 시 도메인 중단
   - blocked_domains 거부(예외 대신 오류 결과 반환)
   - robots.py: 24시간 캐시, 가져오기 실패 시 해당 도메인 skip

4. data/watchlist/companies.json
   - 내가 줄 hr_watchlist_2025_275.json을 가져온다.
   - 없으면 korea_top100_revenue_2025_partial.xlsx에서 블루프린트 1절 규칙으로 생성한다.
   - 275개 중복 없음, 279 원본 소속 보존, 법인등록번호와 사업자등록번호 필드 분리.

5. cli.py
   - `hrwatch run --dry-run --fixtures --date YYYY-MM-DD`가 픽스처로 끝까지 돈다.
   - 결과는 data/·reports/에 쓴다(dry-run이면 임시 폴더).

6. store/
   - JSONL append + postings_index.json(posting_uid 기준 upsert, first_seen/last_seen)
   - runs/ 로그

테스트:
- 차단 도메인 요청 거부
- 예산 초과 시 PARTIAL
- 같은 날 2회 실행 시 중복 0
- 수집 창 = 마지막 성공 실행 이후(실패한 날 다음 실행에서 창이 늘어나는지)
```

**완료 기준:** AGENTS.md 자동 완료 기준 1~3 통과. 감시목록 검증 테스트 통과.

---

## Phase 2 — 사람인 어댑터와 역방향 매칭

```
Phase 2를 해라.

1. adapters/saramin_api.py
   - sources.yml의 queries를 순서대로 실행한다.
   - published_min = 수집 창 시작
   - count=110, start로 페이지 이동, total에 도달하면 종료
   - 예산을 넘으면 PARTIAL
   - 키는 SARAMIN_ACCESS_KEY 환경변수에서만 읽는다.
   - 응답의 company.detail.name, position.title, job-code, experience-level, required-education-level,
     job-type, location, posting/expiration-timestamp, close-type, keyword, url을 Position으로 정규화한다.
   - 본문 필드는 비운다(detail_body: false).

2. match/
   - 회사명 정규화: (주), 주식회사, ㈜, 공백, 영문 대소문자
   - companies.json의 name·aliases와 정확 일치하면 EXACT/ALIAS
   - 접두 일치 같은 부분 일치는 REVIEW로 보낸다.

3. 테스트 픽스처: tests/fixtures/saramin_api/
   - 실제 응답 형식을 본뜨되 회사·공고는 가상 데이터로 만든다.
   - 블루프린트 10절의 사례를 포함한다:
     · 삼성전자 vs 삼성전자서비스
     · HD현대마린솔루션 vs HD현대마린솔루션테크
     · 같은 출처 ID 재수집
     · 비슷한 제목, 다른 ID
     · 상시 공고
     · 시작 전 공고
```

**완료 기준:** 블루프린트 10절 사례 1·2·8·9·10·11·14 테스트 통과. 키 없이 실행하면 FAILED("키 없음")가 기록되고 0건 성공으로 저장되지 않는다.

---

## Phase 3 — HR 분류 + 골든셋 (hr-eval-harness 적용)

```
Phase 3을 해라.

1. classify/rules.py
   - config/job_families/hr.yml을 읽어(다른 직무군 파일도 같은 코드로 처리되게 일반화) INCLUDED/EXCLUDED/REVIEW, hr_field, hr_evidence(원문 200자 이하)를 반환한다.
   - 우선순위: 직무코드 > 제목 > 본문.
   - exclude_rules X1~X6을 적용한다.

2. tests/golden/hr_classification.jsonl — 40건
   - 각 행: id, input(title, job_codes, body_excerpt|null), expected(decision, field), why
   - 구성:
     · 10개 분야별 포함 사례 2건씩(20)
     · 근접 오답 12건: 교육상품 영업, 외부 강사, "인사담당자 문의"만 있는 영업, HR솔루션 영업, 헤드헌터, 총무만, 경영지원(인사 업무 있음), 경영지원(본문 없음→REVIEW), 이미지 본문, 종합공채(HR 1 + 비HR 2)…
     · 블루프린트 10절 3~6번 사례
   - 정답은 내가 검토·확정한다. 너는 초안만 만든다.

3. tests/eval/test_golden.py — CODE 채점
   - decision 일치, field 일치
   - 결과표: 케이스 / 기대 / 실제 / 근거
   - 회귀 게이트: 이전 실행보다 PASS 수가 줄면 실패

4. (D-4가 켜졌을 때만) classify/llm.py
   - REVIEW 건에만 쓴다.
   - 도구 없는 순수 함수다.
   - 출력 스키마는 {decision, field, evidence_quotes[], missing_reason}
   - evidence_quotes가 원문 부분 문자열이 아니면 버린다.
   - 같은 입력 3회 실행이 모두 같아야 PASS(pass^3).
```

**완료 기준:** 골든 40건 정확도 95% 이상(규칙만). REVIEW 비율을 리포트한다. LLM을 켰다면 pass^3 기준으로 REVIEW 해소율을 리포트한다.

---

## Phase 4 — 자동화와 알림

```
Phase 4를 해라.

1. docs/drafts/daily.yml을 .github/workflows/daily.yml로 옮긴다.
   - <SHA>를 실제 릴리스 커밋 SHA로 채운다.

2. hrwatch run --summary-json 출력
   - new_positions, failed_sources, commit_message, issue_title

3. hrwatch report issue
   - 상단: "@junthropic 오늘 19:05 기준 신규 HR 직무 M건 (감시 275개 중 확인 완료 k개, 미완료 u개)"
   - 표: 회사 | 분야 | 직무 | 경력 | 마감(D-day) | 링크
   - 수집 미완료 출처가 있으면 ⚠ 섹션을 붙인다.
   - 키·연락처 출력 금지.

4. reports/daily/YYYY/MM/YYYY-MM-DD.md
   - 같은 표 + 출처별 수집상태 + "확인한 출처에서 미발견" 회사 수

5. zizmor, gitleaks를 CI에 추가한다(PR 대상 lint.yml).
```

**완료 기준:**
- workflow_dispatch 2회 연속 성공, 두 번째 실행의 신규 0건·중복 0
- Issue 알림이 GitHub 모바일 앱에 도착하는지 사람이 확인
- 일부 출처 실패를 시뮬레이션했을 때 ⚠ 표시가 나오는지 확인

---

## Phase 5 — Obsidian 동기화 (PC 실행)

```
Phase 5를 해라. tools/sync_obsidian.py, sync_obsidian.bat을 만든다.

1. 입력
   - 로컬 레포 경로(기본: 스크립트 위치). 시작할 때 `git pull --ff-only`
   - 볼트 폴더 기본값: C:\Obsidian (all)\Claude 프로젝트\HR 채용공고 모음

2. 출력
   - 공고/YYYY-MM/<YYYY-MM-DD 회사 - 직무>.md
   - 일일 리포트/YYYY-MM-DD.md
   - 트렌드/YYYY-Www.md
   - _시스템/sync_state.json

3. 노트 형식: PLAN 7절(frontmatter 키, 자동 블록 마커)

4. 기존 노트 처리
   - posting_uid로 찾는다(frontmatter 검색).
   - 자동 블록과 status·deadline·last_seen만 갱신한다.
   - my_status, '## 내 메모', 사용자가 추가한 다른 frontmatter 키는 보존한다.

5. 옵션
   - --since, --only-open, --field, --dry-run(변경 예정 목록만 출력)

6. 파일명
   - Windows 금지문자와 # ^ [ ] |를 제거하고, 120자에서 자른다.

7. 안전
   - 볼트 폴더 밖에는 쓰지 않는다.
   - 파일을 삭제하지 않는다. 마감 공고도 노트는 남기고 status만 CLOSED로 바꾼다.

테스트: 임시 볼트 폴더에서 2회 실행했을 때
- 중복 0
- 사용자가 수정한 메모 보존
- 금지문자 회사명 처리
```

**완료 기준:**
- 실제 볼트에서 `--dry-run` → 실제 실행
- Obsidian에서 `_채용공고.base` 표에 공고가 보이는지 사람이 확인

---

## Phase 6 — 공식 채용사이트 어댑터 (1곳씩)

```
Phase 6: <사이트 id>를 추가해라.

전제: COMPLIANCE 레지스트리 상태가 ALLOWED_PUBLIC이다. 아니면 멈추고 알려라.

1. AGENTS.md "새 수집 출처" 등록 지점 7곳을 순서대로 처리한다.

2. 수집기 구현(crawlee-python)
   - respect_robots_txt_file=True
   - max_concurrency=1
   - 요청 간 3초 이상
   - 렌더러: http면 BeautifulSoupCrawler/ParselCrawler, playwright면 PlaywrightCrawler(headless, stealth 금지)

3. 수집 범위
   - 목록 페이지에서 HR 후보 제목만 상세 페이지로 들어간다(예산 30 이하).

4. 본문 처리
   - trafilatura로 본문을 추출한다.
   - 담당업무/자격요건/우대사항 섹션을 항목으로 나눈다(항목당 150자 이하).
   - 연락처는 마스킹한다.

5. 차단 감지
   - 로그인 화면, CAPTCHA, 0건 목록에서 이전 실행 대비 급감이 보이면 BLOCKED 또는 PARTIAL로 기록한다.

6. 그룹 포털 처리
   - 계열사별로 배분한다.
   - 계열사 표기가 없으면 그룹 공고를 자회사 전체에 복제하지 말고 REVIEW로 보낸다.
```

**완료 기준:** 픽스처 4케이스(정상·빈 결과·차단·부분) 통과. 실제 1회 수동 실행 결과를 사람이 확인한 뒤에만 `enabled: true`로 바꾼다.

---

## Phase 7 — 주간 트렌드 리포트

```
Phase 7을 해라. hrwatch report weekly --week 2026-W41

1. DuckDB로 data/postings/**/*.jsonl을 읽어 PLAN 5-2절 1~5를 계산한다.

2. 용어 매칭
   - competency_lexicon.yml로 정규화한다.
   - 사전에 없는 2~4어절 n-gram 중 최근 4주에 처음 등장하고 2개 이상 회사에서 나온 표현을 "새 워딩 후보"로 낸다.

3. 리포트 표기
   - 숫자 표와 원문 인용(출처 링크 포함)만 싣는다. 해석·전망 문장은 쓰지 않는다.
   - 출처별 표본 수를 표기한다.
   - 사람인 출처는 본문이 없다는 사실을 각주로 적는다.

4. 실행 시점: 월요일 실행분에서 자동 생성한다.

테스트: 고정 픽스처 4주 데이터에 대해 수치가 재현되는지(스냅샷) 확인한다.
```

**완료 기준:** 4주 실데이터로 리포트를 생성한다. Top 20 항목 5개를 원문과 대조해 사람이 확인한다.

---

## Phase 8 — 기업 지표(국민연금·DART)

```
Phase 8을 해라. 전제: COMPLIANCE 레지스트리에서 nps_workplace_api, dart_api가 ALLOWED_API다.

1. src/hrwatch/enrich/nps.py
   - 공공데이터포털 국민연금 가입 사업장 API를 호출한다.
   - 회사별로 사업장명·사업자번호를 매칭한다.
   - 복수 사업장은 합산하고, 사업장 목록을 남긴다.
   - 매칭이 애매하면 REVIEW로 보낸다.

2. src/hrwatch/enrich/dart.py
   - corpCode.xml로 고유번호를 매칭한다.
   - empSttus(사업보고서 11011, 반기 11012)를 호출한다.
   - 정기보고서가 없으면 "공시 없음"으로 기록한다.

3. 저장: data/company_metrics/{nps,dart}/
   - 기준월·기준연도, 출처 URL, 수집 시각을 함께 저장한다.

4. 파생 지표(코드 계산): 6개월 순증, 월평균 퇴사율, 평균 근속, 1인 평균 급여.

5. 표시
   - 일일 Issue와 공고 노트에 지표 한 줄을 붙인다.
   - Obsidian 기업/<회사>.md를 만든다.
   - 해석 문장은 금지한다.

6. 워크플로: .github/workflows/enrich-monthly.yml
   - cron '35 10 3 * *' = 매월 3일 19:35 KST
   - DART는 분기 첫 달에만 실행한다.

테스트: 동명 법인, 사업자번호 일부 마스킹, 공시 없음, API 실패(UNDETERMINED).
```

**완료 기준:**
- 275개 중 매칭 성공·REVIEW·실패 수와 사유 표를 만든다.
- 사람이 5개 회사의 수치를 원 데이터와 대조한다.

## Phase 9 — 직무군·기업 확장 (필요할 때)

```
<직무군 추가> config/job_families/_template.yml을 복사해 <family_id>.yml을 만들어라.
- 하위 분야·검색어 초안과 골든셋 초안(하위 분야마다 포함 2 + 근접 오답 2)을 만든다.
- 사람인 예산 합계를 계산해 보여준다.
- 내가 골든셋을 확정하면 테스트하고, 통과하면 enabled: true로 바꾼다.

<기업 추가> "<회사명>"을 감시 기업에 추가해라.
- 정식 법인명·별칭·공식 도메인·DART 고유번호를 확인한다. 동명 법인은 후보를 보여준다.
- watchlist_custom.yml 변경을 PR로 올린다.
- scan_mode는 내가 말하지 않으면 reverse_match로 둔다.
```
