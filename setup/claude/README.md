# Claude Code 프로젝트 설정 (설치 대기)

이 폴더의 파일은 **`.claude/`로 복사해야 적용**된다. 원격 도구로는 `.claude/` 폴더에 직접 쓸 수 없어 여기에 두었다.

PowerShell(레포 루트에서):
```powershell
New-Item -ItemType Directory -Force .claude\hooks | Out-Null
Copy-Item setup\claude\settings.json .claude\settings.json
Copy-Item setup\claude\hooks\block_domains.py .claude\hooks\block_domains.py
```

- `settings.json`: 제외 도메인 WebFetch deny + Bash·WebFetch·MCP 도구용 PreToolUse 훅 등록
- `hooks/block_domains.py`: 블라인드·리멤버·잡코리아·원티드 웹·사람인 웹 도메인을 Bash 명령, MCP 도구 입력에서 차단한다(종료 코드 2)
- 복사 후 Claude Code에서 `/hooks`로 등록됐는지 확인한다.
