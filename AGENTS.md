# 지금 진행 중인 작업 — 먼저 읽기

- 진행 중인 계획: `docs/PLAN.md` → 현재 **Phase 0(사전 확인)**. 다음은 Phase 1(골격). 단계별 지시는 `docs/BUILD_PROMPTS.md`에 있다.
- 출처를 켜거나 바꾸기 전에 반드시 `docs/COMPLIANCE.md`를 읽는다.

# 역할

너는 이 레포에서 **개인용 HR 채용공고 수집·분석 파이프라인(`hrwatch`)**을 만들고 유지하는 엔지니어다.
목표는 두 가지다.
1. 매출 1,000억 이상 감시 기업의 당일 HR 공고를 빠짐없이, 약관을 지키며 수집한다.
2. 수집 실패를 "공고 없음"으로 오인하지 않는다.

# 구조

```
config/            출처·직무군(job_families/)·사전·회사연결·사용자 추가 기업 설정 (사람이 승인하는 데이터)
data/              수집 결과. append-only, 사람 손으로 수정 금지(검토 결정은 review 경유)
reports/           생성물. 직접 수정 금지, 생성 명령: uv run hrwatch report
src/hrwatch/
  cli.py           진입점: run / report / review / export
  models.py        pydantic 스키마 (Position, RunLog, SourceStatus …)
  net/             client.py(UA·간격·예산·차단도메인), robots.py
  adapters/        출처별 어댑터. 공통 프로토콜 Adapter.fetch(window) -> AdapterResult
  match/           회사 정규화·매칭 (EXACT/ALIAS/REVIEW)
  classify/        HR 분류 규칙 → (선택) LLM 판별
  extract/         요구역량·자격·우대 추출, PII 마스킹
  store/           JSONL append, index, run log
  enrich/          기업 지표(국민연금·DART), 월·분기 실행
  report/          일일·주간 리포트, Issue 본문
tools/sync_obsidian.py  PC 전용. 레포 읽기 → 볼트 쓰기
.github/workflows/daily.yml
```

의존 방향은 `cli → adapters/match/classify/extract → store → models`. `models`는 아무것도 import하지 않는다. 어댑터끼리 서로 import하지 않는다.
외부 경계는 사람인 API, 공식 채용사이트(허용된 것만), GitHub(커밋·Issue), 로컬 Obsidian 볼트(sync 스크립트만)다.

# 규칙

## 수집·약관 (위반 시 PR 거절)
- `config/sources.yml`에서 `status`가 `ALLOWED_API` 또는 `ALLOWED_PUBLIC`이 아닌 출처는 호출하지 않는다. 새 출처를 켜려면 `docs/COMPLIANCE.md` 레지스트리에 확인일과 근거를 먼저 적는다. 이유: 약관 위반은 되돌릴 수 없다.
- 차단 도메인(`teamblind.com`, `blindhub.net`, `rememberapp.co.kr`, `jobkorea.co.kr`, `wanted.co.kr`, `saramin.co.kr` 웹)에 HTTP 요청을 보내지 않는다. 사람인은 API 도메인 `oapi.saramin.co.kr`만 쓴다. 테스트에서도 실제 요청 대신 픽스처를 쓴다.
- 로그인, 쿠키 재사용, 프록시·IP 회전, CAPTCHA 처리, stealth 플러그인, UA 위장 코드를 쓰지 않는다. 차단되면 `BLOCKED`로 기록하고 끝낸다.
- 모든 HTTP 요청은 `hrwatch.net.client`를 거친다. `requests`·`httpx`를 직접 호출하지 않는다. 이유: 간격·예산·robots·차단 도메인을 한 곳에서 강제하기 위해서다.
- 도메인당 동시성 1, 간격 3초 이상, 재시도 최대 2회, 429면 그날 그 도메인을 중단한다.

## 데이터
- 레코드는 `models.Position`을 통과한 것만 저장한다. 검증에 실패하면 `data/review/`로 보낸다.
- 같은 `posting_uid`는 새 줄로 추가하지 않는다. index를 갱신하고, 바뀐 필드만 `job_events`에 남긴다.
- 본문 전문·원본 HTML·API 원본 응답·담당자 연락처를 저장하지 않는다. 대신 항목 150자 이하, 근거 200자 이하로 저장한다.
- 마감일이 없으면 `deadline_type`을 `ROLLING`/`UNTIL_FILLED`/`UNKNOWN`으로 둔다. 날짜를 지어내지 않는다.
- 목록에서 사라진 공고를 `CLOSED`로 바꾸지 않는다. 명시적 마감 표시나 지난 마감일만 근거로 쓴다.
- 회사 매칭은 전체 이름·별칭·공식 도메인으로만 한다. 부분 문자열(예: "현대")로 자동 연결하지 않는다. 애매하면 `REVIEW`로 둔다.
- 출처 하나라도 실패하면 그 출처에 연결된 회사는 `UNDETERMINED`가 된다. "미발견"으로 쓰지 않는다.

## LLM (D-4가 켜졌을 때만)
- LLM 호출 함수는 텍스트 입력 → JSON 출력의 순수 함수다. 도구·네트워크·파일 접근 권한을 주지 않는다. 이유: 공고 텍스트는 신뢰할 수 없는 입력이다(prompt injection).
- 출력은 pydantic으로 검증한다. 원문에 없는 문장(부분 문자열 불일치)은 버린다.
- LLM은 규칙 분류가 `REVIEW`로 남긴 공고에만 쓴다. 이미 판정한 공고는 본문 해시가 바뀔 때만 다시 판정한다.

## 비밀값·워크플로
- API 키는 환경변수(`SARAMIN_ACCESS_KEY`)로만 읽는다. 로그·예외 메시지·Issue·커밋에 키를 출력하지 않는다.
- 워크플로 액션은 커밋 SHA로 고정한다. `permissions`는 `contents: write`와 `issues: write`만 준다.
- 워크플로 첫 단계에서 레포가 public이면 실패 처리한다(`gh repo view --json visibility`).

## 코드 스타일
- Python 3.12, uv, ruff(기본 + `I`, `B`, `UP`). 함수가 60줄을 넘으면 분리한다.
- 시각은 모두 KST(`Asia/Seoul`) aware datetime으로 다룬다. naive datetime은 금지한다.
- 오류는 어댑터 밖으로 예외를 던지지 않고 `AdapterResult(status=FAILED, error=...)`로 반환한다.

# 새 단위를 추가할 때 건드릴 파일

## 새 수집 출처(어댑터) — 7곳
1. `docs/COMPLIANCE.md` 1절 레지스트리: 상태·근거·확인일
2. `config/sources.yml`: id, status, base_url, 일일 예산, robots 확인일, `enabled: false`로 시작
3. `src/hrwatch/adapters/<id>.py`: `Adapter` 프로토콜 구현
4. `src/hrwatch/adapters/__init__.py`: `REGISTRY`에 등록
5. `config/company_bindings.yml`: 이 출처로 확인하는 회사와 provider id
6. `tests/fixtures/<id>/`: 녹화 응답(키·PII 제거) + `tests/adapters/test_<id>.py`(정상·빈 결과·차단 화면·부분 실패 4케이스)
7. `docs/CHANGELOG.md`
(선택) 새 출처가 제외 대상이면 `.claude/settings.json` deny 목록과 `.claude/hooks/block_domains.py`에 도메인 추가

## 새 직무군(HR 외 직무) — 5곳
1. `config/job_families/<family_id>.yml`: `_template.yml`을 복사하고 `enabled: false`로 시작한다
2. `config/sources.yml` saramin_api 예산 합계를 확인한다(켜진 직무군 예상 호출 합 ≤ `daily_request_budget`, 한도의 30% 이하)
3. `tests/golden/<family_id>_classification.jsonl`: 하위 분야마다 포함 2건 + 근접 오답 2건 이상
4. 골든셋을 통과하면 `enabled: true`로 바꾼다. 분류 코드는 직무군 파일을 읽으므로 수정하지 않는다
5. `docs/CHANGELOG.md`

## 기존 직무군의 하위 분야·분류 규칙 변경 — 3곳
1. `config/job_families/<family_id>.yml`의 `fields`·`exclude_rules`
2. `tests/golden/<family_id>_classification.jsonl`: 포함 2건 + 근접 오답 2건 이상
3. `src/hrwatch/report/weekly.py`의 분야 순서(설정에서 읽도록 구현했다면 생략)

## 감시 기업 추가·삭제 — 3곳 (반드시 PR, 사람 승인)
1. `config/watchlist_custom.yml`: 정식 법인명, 별칭, 공식 도메인, families, scan_mode, reason, added_at. 삭제는 `active: false`로만
2. `per_company`를 쓰면 30곳 이하인지, 사람인 예산 합계가 넘지 않는지 확인한다
3. (선택) 공식 채용사이트를 수집하려면 "새 수집 출처" 7곳 절차를 따른다

## 새 기업 지표 출처 — 4곳
1. `docs/COMPLIANCE.md` 레지스트리
2. `config/sources.yml`: `kind: enrichment`, `schedule`
3. `src/hrwatch/enrich/<id>.py` + 회사 매칭 테스트(사업자번호·법인명·동명 법인)
4. 결과 표시: Issue 지표 한 줄, Obsidian `기업/` 노트 템플릿

## 새 역량·자격 용어 — 2곳
1. `config/competency_lexicon.yml`(정규형 + 동의어)
2. `tests/extract/test_lexicon.py`

# 완료 기준

1. **자동(순서대로):**
   ```
   uv run ruff format --check . && uv run ruff check .
   uv run pytest -q
   uv run hrwatch run --dry-run --fixtures --date 2026-10-02
   gitleaks detect --no-banner
   zizmor .github/workflows/
   ```
   `reports/`는 손으로 고치지 않는다. 생성 명령으로 다시 만든다.
2. **수동(5분):**
   - dry-run 일일 리포트를 열어 회사·분야·마감·링크가 맞는지 3건 확인한다.
   - 출처 하나를 실패로 만든 픽스처에서 "수집 미완료" 표시가 나오는지 확인한다.
   - 같은 날짜로 2회 실행해 중복 줄이 0인지 확인한다.
3. **문서 갱신:**
   - CHANGELOG
   - 출처를 바꿨다면 COMPLIANCE 레지스트리
   - 등록 지점 목록(이 파일)
   - 새로 겪은 함정

# 고생해서 배운 함정

(사전 조사로 알려진 것. 실제로 겪으면 날짜를 갱신한다.)
- **사람인 한도 표기 불일치**: guide/info는 "1일 500회", caution은 "일 공고 호출 수 500건"이다. 문서마다 단위가 다르다. 그래서 일일 예산을 50회로 잡고, 응답 건수 합도 500 미만으로 제한한다. (발견 2026-10-02)
- **사람인 API에는 본문이 없음**: 요구역량 분석을 사람인 데이터로 하면 제목·키워드 편향이 생긴다. 리포트에 출처별 표본 수를 표시한다. (발견 2026-10-02)
- **cron 정시 지연**: GitHub 예약 실행은 매시 정각 부하로 늦어지거나 누락될 수 있다. 그래서 `:05`에 걸고, 실제 시작 시각을 기록한다. (발견 2026-10-02)
- **해외 IP**: Actions 러너는 해외에 있다. 국내 사이트가 해외 IP를 막으면 응답 200에 차단 페이지가 올 수 있다. 차단 문구 검사를 둔다. (발견 2026-10-02)
- **도메인 차단 훅의 부작용**: `.claude/hooks/block_domains.py`는 Bash 명령 문자열에 제외 도메인이 들어 있으면 막는다. 문서에 URL을 쓸 때는 Bash(sed·heredoc) 대신 Edit/Write 도구를 쓴다. (발견 2026-10-02)
- **사람인 API는 진행 중 공고만**: 마감된 공고는 조회되지 않는다(FAQ). 과거 공고를 다시 받으려고 하지 말고, 처음 본 시점의 레코드를 보존한다. (발견 2026-10-02)
- **robots 허용 ≠ 약관 허용**: 리멤버는 robots가 `/job/`을 허용하지만 약관이 자동 수집을 금지한다. 출처를 켤 때는 둘 다 확인한다. (발견 2026-10-02)

# 현실 점검

- 레포는 2026-10-02 기준 **비어 있다**. 코드, 테스트, 픽스처, 워크플로, `uv` 프로젝트가 모두 없다. 위 완료 기준 명령은 목표이며, Phase 1에서 만든다.
- `data/watchlist/companies.json`(275개)은 아직 레포에 없다. 블루프린트 패키지의 `hr_watchlist_2025_275.json`을 가져오거나, `korea_top100_revenue_2025_partial.xlsx`에서 다시 생성해야 한다.
- 사람인 API 키가 없다. 키가 나오기 전에는 픽스처로만 개발한다.
- 레포는 현재 **public**이다. private로 바꾸기 전에는 `data/`와 `reports/`를 커밋하지 않는다.
- gitleaks·zizmor·pre-commit은 아직 설치되지 않았다.
- `.claude/settings.json`과 차단 훅은 아직 `setup/claude/`에만 있다. **Phase 1 첫 단계에서 `setup/claude/README.md`대로 `.claude/`로 복사한다.** 복사 전에는 에이전트 차원의 도메인 차단이 적용되지 않는다.

# 셀프 리뷰 체크리스트

- [ ] 새 HTTP 요청이 모두 `hrwatch.net.client`를 거치는가
- [ ] 차단 도메인·미허용 출처를 호출하는 경로가 없는가(테스트 포함)
- [ ] 로그·예외·Issue 본문에 키나 개인 연락처가 나가지 않는가
- [ ] 실패·차단·부분 수집이 "0건 성공"으로 저장되지 않는가
- [ ] 같은 공고를 두 번 실행해도 중복 줄이 생기지 않는가
- [ ] 마감일·경력 조건을 지어내지 않았는가
- [ ] Obsidian 동기화가 `my_status`와 `## 내 메모`를 덮어쓰지 않는가
- [ ] 기업 지표에 해석 문장("이직이 잦다" 등) 없이 수치·기준월·출처만 실었는가
- [ ] 등록 지점 목록의 해당 항목(출처 7곳 / 직무군 5곳 / 분야 3곳 / 기업 3곳 / 지표 4곳 / 용어 2곳)을 모두 수정했는가
