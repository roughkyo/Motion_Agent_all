"""스토리보드 미리보기 서버 설정을 세션 루트의 .claude/launch.json에 합친다.

preview_start는 '세션 작업 폴더'의 .claude/launch.json만 읽는다.
하위 폴더에서 작업하면 거기에 launch.json을 만들어도 인식되지 않으므로,
루트 launch.json에 --directory <작업 폴더> 설정을 추가(같은 이름이면 교체)한다.

사용(세션 루트에서): python preview.py <작업 폴더> [--port 8767] [--name storyboard]
"""
import argparse
import json
import sys
from pathlib import Path

# Windows 콘솔(cp949)에서도 한글 안내문이 깨지지 않게 한다
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workdir", nargs="?", default=".")
    ap.add_argument("--port", type=int, default=8767)
    ap.add_argument("--name", default="storyboard")
    args = ap.parse_args()

    path = Path(".claude/launch.json")
    data = {"version": "0.0.1", "configurations": []}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))

    # 같은 이름의 기존 설정은 빼고 새 설정을 넣는다 (다른 설정은 보존)
    configs = []
    for c in data.get("configurations", []):
        if c.get("name") != args.name:
            configs.append(c)
    configs.append({
        "name": args.name,
        "runtimeExecutable": "python",
        "runtimeArgs": ["-m", "http.server", str(args.port), "--directory", args.workdir],
        "port": args.port,
    })
    data["configurations"] = configs

    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"→ {path} : '{args.name}' = {args.workdir} (포트 {args.port}) → preview_start 후 /storyboard/")


if __name__ == "__main__":
    main()
