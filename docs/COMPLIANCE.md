# 수집 정책 · 약관 · 보안 (COMPLIANCE)

기준일: 2026-10-02 KST. 약관·API 조건은 바뀐다. 출처를 켜기 전과 분기마다 원문을 다시 확인하고, 아래 레지스트리의 "확인일"을 갱신한다.
**법률 자문이 아니다.** 외부 공개, 팀 공유, 상업 이용 전에는 변호사 확인을 받는다.

---

## 1. 출처 레지스트리 (상태가 `ALLOWED_*`인 출처만 코드에서 켤 수 있다)

| 출처 | 상태 | 근거(요약) | 확인일 | 다음 행동 |
|---|---|---|---|---|
| 사람인 오픈API | `PENDING_KEY` | 이용신청 후 승인을 받아야 키가 나온다. 하루 최대 500(guide/info는 "500회", caution은 "500건"). 요청당 `count` 최대 110. `published`/`published_min`으로 당일 공고를 조회할 수 있다. 응답에 본문은 없다 | 2026-10-02 | 키 신청. 승인 메일의 이용조건을 이 표에 옮겨 적기 |
| 고용24 채용정보 API | `PENDING_ELIGIBILITY` | "고용 24 기업회원 전용". `regDate=D-0`(오늘), `busino`(사업자번호) 지원. 호출 한도는 공식 문서에서 미확인 | 2026-10-02 | 사업자가 있으면 신청 |
| 원티드 OpenAPI | `PENDING_ELIGIBILITY` | 신청서에 사업자번호·회사명·서비스 URL 필수. 한도·저장 조건 미확인 | 2026-10-02 | D-3 결정 후 |
| 삼성 채용 samsungcareers.com | `UNCHECKED` | robots·약관 미확인 | — | Phase 6 |
| LG 채용 careers.lg.com | `UNCHECKED` | 같음 | — | Phase 6 |
| HD현대 recruit.hd.com | `UNCHECKED` | 동적 렌더링. robots·약관 미확인 | — | Phase 6 |
| 한국항공우주산업 koreaaero.recruiter.co.kr | `UNCHECKED` | 채용 솔루션 호스팅. 솔루션사 약관도 함께 확인 | — | Phase 6 |
| 잡코리아 | `EXCLUDED` | 공식 API는 공공기관·학교 대상. 약관 제18조④ "얻은 정보를 회사의 사전동의 없이 복사, 복제…" 금지. 잡코리아 v. 사람인 판결(서울고법 2016나2019365, DB권 침해 인정). robots.txt가 Scrapy UA 전면 차단 | 2026-10-02 | — |
| 리멤버 / 리멤버 커리어 | `EXCLUDED` | 서비스 이용약관 제13조①24호: 사전 허락 없이 "자동화된 수단(매크로…봇, 스파이더, 스크래퍼 등)"으로 게시물 수집 금지. 일반 검색엔진 인덱싱만 예외. 제23조①: 경고·일시정지·계약해지 | 2026-10-02 | 수동 경로만(4절) |
| 블라인드 | `EXCLUDED` | 블라인드 하이어는 2025년에 신규 등록·지원 접수 기능 중단(2025-03-30 보도). 약관 원문과 robots.txt는 미확인(403·바이너리 응답) | 2026-10-02 | — |
| 원티드 웹 | `EXCLUDED` | 개인회원 약관 제19조 7호(2023-11-23본): 자동화 수단 수집, IP 변경·CAPTCHA 우회 금지. 웹이 아니라 OpenAPI만 검토 | 2026-10-02 | — |
| 사람인 웹 | `EXCLUDED` | API가 있으므로 웹은 쓰지 않음. robots.txt가 공고 상세 `/zf_user/recruit/view/` 등을 Disallow | 2026-10-02 | — |
| 구글·네이버 검색 결과 | `EXCLUDED` | 검색엔진 결과 자동 수집은 해당 약관 위반 | 2026-10-02 | 출처 URL 발굴은 사람이 수동으로 |
| 사용자 수동 URL | `MANUAL_ONLY` | 사람이 직접 입력한 값만 저장. 시스템이 그 URL을 자동으로 열지 않음 | — | — |

공식 채용사이트를 `ALLOWED_PUBLIC`으로 바꾸는 조건(모두 충족):
1. robots.txt가 수집할 목록·상세 경로를 허용한다(`User-agent: *` 기준, 우리 UA 기준 모두).
2. 사이트·채용 솔루션 약관에 자동 수집 금지 조항이 없다. 있으면 `EXCLUDED`로 둔다.
3. 로그인 없이 공고 목록과 상세가 보인다.
4. 확인한 날짜, 약관 URL, 판단 근거 문장을 위 표에 적는다.

---

## 2. 수집 행동 규칙 (코드에 강제)

| 규칙 | 값 | 강제 위치 |
|---|---|---|
| robots.txt | 실행마다 확인(24시간 캐시). 가져오기에 실패(5xx·타임아웃)하면 그 도메인은 건너뛴다. `Crawl-delay`가 있으면 따른다 | `hrwatch/net/robots.py` |
| User-Agent | `HRRecruitmentNoticeTrack/0.x (+https://github.com/junthropic/HR-Recruitment-Notice-Track; personal, non-commercial)`. 브라우저 위장 금지 | `hrwatch/net/client.py` |
| 간격·동시성 | 도메인당 동시 1, 요청 간 3초 이상(Crawl-delay가 더 크면 그 값) | 같음 |
| 예산 | 출처별 하루 요청 상한을 `sources.yml`에 둔다. 사람인 기본 50(공식 500의 10%). 공식 사이트는 30페이지 | 같음 |
| 재시도 | 최대 2회, 지수 백오프. 429는 `Retry-After`를 따르고 그날 해당 도메인 중단 | 같음 |
| 차단 감지 | 403·429, 로그인 화면, CAPTCHA, 빈 목록에 차단 문구가 보이면 `BLOCKED`로 기록하고 **우회하지 않는다** | 어댑터 공통 검사 |
| 금지 | 로그인·쿠키 재사용, 프록시·IP 회전, CAPTCHA 풀이, 헤드리스 탐지 회피(stealth) 플러그인, 비공개 API 역공학 | 리뷰 체크리스트 + semgrep 규칙(후속) |
| 실행 빈도 | 하루 1회(19:05 KST) + 수동 실행. 수동 실행도 같은 예산을 공유 | 워크플로 `concurrency` |
| 응답 200 오판 | 로그인·차단·파싱 실패 페이지를 "공고 0건 성공"으로 저장하지 않는다 | 어댑터 공통 검사 |

---

## 3. 저장 규칙 (데이터 최소화)

- **저장한다:** 공고 메타데이터(회사·제목·경력·고용형태·지역·게시일·마감·링크), HR 판별 근거 발췌(200자 이하), 담당업무·자격요건·우대사항 항목(항목당 150자 이하, 본문을 제공하는 허용 출처만), 키워드 집계.
- **저장하지 않는다:** 본문 전문, 원본 HTML, API 원본 응답, 채용담당자 이름·전화·이메일. 전화·이메일은 정규식으로 `[연락처 삭제]` 처리한다.
- **레포는 private.** 전환 전에는 `data/`, `reports/`를 커밋하지 않는다. 워크플로 첫 단계에서 레포 공개 여부를 확인하고, public이면 중단한다.
- **재배포 금지.** 레포 데이터를 다른 서비스·사람에게 제공하지 않는다. 사람인 API 조건에 따라 대가를 받거나 재판매하지 않는다.
- **출처 표기.** 리포트·노트의 각 공고에 출처명과 원문 링크를 단다. 출처를 사칭하지 않는다.

---

## 4. 블라인드·리멤버 계정 보호 설계

목표는 계정 정지 위험을 **구조적으로 0**으로 만드는 것이다.
1. 시스템 코드, 워크플로, Claude Code 세션 어디에서도 `teamblind.com`, `blindhub.net`, `rememberapp.co.kr`, `career.rememberapp.co.kr`에 요청하지 않는다.
   - **코드:** `hrwatch/net/client.py`에 차단 도메인 목록을 하드코딩하고, 이 도메인으로 요청하면 예외 대신 오류 문자열을 반환한다.
   - **에이전트:** `.claude/settings.json`의 `permissions.deny`에 `WebFetch(domain:teamblind.com)` 등을 넣는다. Bash에서 해당 도메인을 쓰면 PreToolUse 훅이 차단한다. `allowed-tools`는 제한 기능이 아니므로 쓰지 않는다.
2. 두 서비스의 아이디·비밀번호·쿠키·세션 토큰을 레포, Secrets, 설정 파일에 두지 않는다.
3. 사용자가 두 서비스에서 본 공고를 기록하고 싶으면, **본인이 브라우저로 직접** Obsidian Web Clipper 등으로 `HR 채용공고 모음/수동 스크랩/`에 저장한다. 이 폴더는 레포로 올리지 않는다(개인 열람용). 레포에는 원하면 회사명·직무·URL만 수동으로 기록한다.
4. 리멤버 robots.txt가 `/job/`을 `Allow`하는 것은 일반 검색엔진 인덱싱을 위한 것이다. 약관 제13조①24호가 개인 수집기를 예외로 두지 않으므로 robots 허용을 근거로 수집하지 않는다.

---

## 5. 법적 배경 (요약, 법률 자문 아님)

| 쟁점 | 요지 | 이 설계의 대응 |
|---|---|---|
| 데이터베이스제작자 권리(저작권법 제93조) | 상당한 부분이 아니어도 "반복적이거나 특정한 목적을 위하여 체계적으로" 복제해 DB의 통상 이용과 충돌하면 침해로 본다. 잡코리아 v. 사람인(서울고법 2016나2019365, 확정)에서 채용공고 반복 복제가 침해로 인정됐다 | 스크래핑 대신 공식 API 사용. 본문 미저장. 비공개 개인 이용 |
| 야놀자 v. 여기어때(대법원 2021도1533, 2022-05-12) | 형사는 무죄. 접근권한 판단에 robots.txt 등 보호조치와 약관을 종합 고려했다. 같은 사안의 민사(서울중앙지법 2021-08-23)는 부정경쟁 행위를 인정해 10억 원 배상 | robots·약관을 지키고, 상업적 경쟁 목적이 없음 |
| 부정경쟁방지법 데이터 부정사용 조항(2022-04-20 시행) | 접근권한 없는 취득, 기술적 보호조치 무력화 등을 금지 | 로그인·우회 금지 |
| 사적이용 복제(저작권법 제30조) | 개인·가정 범위만 인정된다. 공개 게시는 벗어난다 | private 레포, 재배포 금지 |
| 개인정보 | 공고 속 담당자 연락처는 개인정보다 | 마스킹 후 저장 |

출처:
- 서울고법 2016나2019365: https://www.legaltimes.co.kr/news/articleView.html?idxno=32614
- 대법원 2021도1533: https://file.scourt.go.kr/dcboard/1727143941701_111221.pdf
- 민사 1심 보도: https://www.news1.kr/society/court-prosecution/4410402
- 부정경쟁방지법 데이터 조항 해설: https://www.kimchang.com/ko/insights/detail.kc?sch_section=4&idx=24264
- 사적이용 복제 안내: https://easylaw.go.kr/CSP/CnpClsMain.laf?popMenu=ov&csmSeq=695&ccfNo=3&cciNo=2&cnpClsNo=3

---

## 6. 1차 자료 링크 (2026-10-02 확인)

- 사람인 API 안내: https://oapi.saramin.co.kr/guide/1
- 사람인 API 정보: https://oapi.saramin.co.kr/guide/info
- 사람인 API 주의사항: https://oapi.saramin.co.kr/caution
- 사람인 공고 검색 API: https://oapi.saramin.co.kr/guide/job-search
- 사람인 robots.txt: https://www.saramin.co.kr/robots.txt
- 고용24 Open API 소개: https://www.work24.go.kr/cm/e/a/0110/selectOpenApiIntro.do
- 원티드 OpenAPI: https://openapi.wanted.jobs/
- 원티드 약관: https://help.wanted.co.kr/hc/ko/articles/25148621341337
- 잡코리아 API: https://www.jobkorea.co.kr/service/api
- 잡코리아 약관: https://www.jobkorea.co.kr/service/ProvisionGG
- 잡코리아 robots.txt: https://www.jobkorea.co.kr/robots.txt
- 리멤버 서비스 약관: https://page.rememberapp.co.kr/terms/service?locale=kr
- 리멤버 커리어 robots.txt: https://career.rememberapp.co.kr/robots.txt
- 블라인드 하이어 종료 보도: https://v.daum.net/v/20250330070042099
- GitHub 예약 워크플로 지연: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- GitHub 60일 비활성화: https://docs.github.com/actions/managing-workflow-runs/disabling-and-enabling-a-workflow
- GitHub Actions 과금: https://docs.github.com/en/billing/concepts/product-billing/github-actions
- Crawlee robots.txt 준수 예제: https://crawlee.dev/python/docs/examples/respect-robots-txt-file
