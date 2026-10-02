"""PreToolUse 훅: 약관상 자동 수집이 금지되었거나 제외한 도메인으로의 요청을 차단한다.

settings.json의 deny 규칙은 WebFetch만 막는다. Bash(curl, python -c ...)나 MCP 브라우저 도구로
같은 도메인에 접근하는 경로를 여기서 막는다. 근거: docs/COMPLIANCE.md 1절·4절.
종료 코드 2 = 차단(stderr가 에이전트에게 전달됨). 그 외 0.
"""
import json
import re
import sys

BLOCKED = re.compile(
    r"(teamblind\.com|blindhub\.net|rememberapp\.co\.kr|jobkorea\.co\.kr|"
    r"wanted\.co\.kr|(?<!oapi\.)saramin\.co\.kr)",
    re.IGNORECASE,
)

def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # 입력을 못 읽으면 막지 않는다(훅 오류로 작업 전체가 멈추지 않게)
    text = json.dumps(payload.get("tool_input", {}), ensure_ascii=False)
    hit = BLOCKED.search(text)
    if hit:
        sys.stderr.write(
            f"차단: '{hit.group(0)}'는 이 프로젝트에서 자동 접근 금지 도메인입니다 "
            "(docs/COMPLIANCE.md). 사람인은 oapi.saramin.co.kr API만 사용하세요.\n"
        )
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
