# CHANGELOG

## 2026-10-02 (2) — 확장 구조와 기업 지표
- 직무군 구조: `config/hr_taxonomy.yml` → `config/job_families/hr.yml`(사람인 검색어 포함) + `_template.yml`
- 사용자 추가 기업: `config/watchlist_custom.yml`(reverse_match / per_company, PR 승인 절차)
- 기업 지표 출처: 국민연금 가입 사업장 API, OpenDART 직원 현황 API(`sources.yml` kind: enrichment). PLAN 13·14절, BUILD_PROMPTS Phase 8·9
- COMPLIANCE: 잡플래닛 EXCLUDED, 사람인 과금 안내 없음·진행 중 공고만 조회 명시

## 2026-10-02 — 기획 패키지
- 기획서(PLAN), 수집 정책(COMPLIANCE), 레포·스킬 선정(REPO_AND_SKILLS), 단계별 프롬프트(BUILD_PROMPTS), AGENTS.md 추가
- config 초안: sources.yml, hr_taxonomy.yml, competency_lexicon.yml
- setup/claude/(설치 대기): settings.json + hooks/block_domains.py — 제외 도메인 자동 접근 차단. `.claude/`로 복사해 적용
- 워크플로 초안 docs/drafts/daily.yml(비활성)
