#!/usr/bin/env python
"""
algo-viz API 模式: MD 文件 → LLM 生成 Manim 代码 → 渲染 → 拼接

不依赖 Claude Code，直接调 OpenRouter / MindCraft / ablai API。
可被 VS Code 插件、Shell 脚本、或任何外部程序调用。

用法:
    python api_generate.py path/to/知识点.md
    python api_generate.py path/to/知识点.md -q m --model qwen/qwen3-235b-a22b
    python api_generate.py path/to/知识点.md --platform ablai --model gpt-4o

环境变量:
    OPENROUTER_API_KEY  — OpenRouter API key (放在 .env 或环境变量)
    MINDCRAFT_API_KEY   — MindCraft API key
    API_KEY_POOL        — ablai API key
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# ── 自动加载 .env ──
def load_dotenv():
    """简易 .env 加载 (不依赖 python-dotenv)"""
    for env_path in [Path(__file__).parent / ".env", Path.cwd() / ".env"]:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

load_dotenv()

# ── 代理自动检测 (全局规则) ──
def detect_proxy():
    """检测系统代理: 环境变量 → Windows 注册表"""
    for var in ["HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"]:
        if os.environ.get(var):
            print(f"[Proxy] Auto-detected: {os.environ[var]}")
            return os.environ[var]
    # Windows 注册表回退
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
        enabled, _ = winreg.QueryValueEx(key, "ProxyEnable")
        if enabled:
            server, _ = winreg.QueryValueEx(key, "ProxyServer")
            proxy = f"http://{server}" if not server.startswith("http") else server
            print(f"[Proxy] Auto-detected from registry: {proxy}")
            return proxy
    except Exception:
        pass
    return None


# ── API 调用 ──
def call_llm(messages, model="qwen/qwen3-235b-a22b", platform="openrouter",
             temperature=0.3, max_tokens=16000, max_retries=3):
    """调用 LLM API 生成文本"""
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    configs = {
        "openrouter": {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "key": os.environ.get("OPENROUTER_API_KEY", ""),
            "verify": True,
            "use_proxy": True,
        },
        "mindcraft": {
            "url": "https://api.mindcraft.com.cn/v1/chat/completions",
            "key": os.environ.get("MINDCRAFT_API_KEY", "MC-72C89F3896E04155B26DD4830FABFA96"),
            "verify": False,
            "use_proxy": False,
        },
        "ablai": {
            "url": "https://api.ablai.top/v1/chat/completions",
            "key": os.environ.get("API_KEY_POOL", "sk-crAH9xybefiwLzLypeuZNSwtJYonziKKIrmI9XIiXp6KlSlk"),
            "verify": True,
            "use_proxy": False,
        },
    }

    cfg = configs[platform]
    if not cfg["key"]:
        print(f"[algo-viz] ERROR: No API key for {platform}. Set env var or .env")
        return None

    headers = {
        "Authorization": f"Bearer {cfg['key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    proxies = None
    if cfg["use_proxy"]:
        proxy = detect_proxy()
        if proxy:
            proxies = {"http": proxy, "https": proxy}
    elif not cfg["use_proxy"]:
        proxies = {"http": None, "https": None}

    for retry in range(max_retries):
        try:
            print(f"[algo-viz] Calling {platform}/{model} (attempt {retry + 1})...")
            resp = requests.post(
                cfg["url"], headers=headers, json=payload,
                timeout=180, verify=cfg["verify"], proxies=proxies,
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                # 有些模型在 thinking 标签里输出思考过程，提取实际内容
                if "<think>" in content:
                    # 去掉 <think>...</think> 部分
                    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
                return content
            elif resp.status_code == 429:
                import time
                wait = 2 ** (retry + 1)
                print(f"[algo-viz] Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"[algo-viz] API error {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"[algo-viz] Request failed: {e}")
    return None


# ── Prompt 构建 ──
def load_system_prompt():
    """从 prompts/system.md 加载统一的系统提示词"""
    prompt_path = Path(__file__).parent / "prompts" / "system.md"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    # fallback
    return "你是一个 Manim Community Edition 动画专家。生成 3Blue1Brown 风格的教学动画 Python 脚本。只输出代码。"


SYSTEM_PROMPT = load_system_prompt()


def build_prompt(md_content: str, md_path: str) -> list:
    """构建消息列表"""
    user_msg = f"""请根据以下学习笔记生成 Manim 教学动画脚本。

文件: {md_path}

---
{md_content}
---

要求:
- 覆盖笔记中的所有核心概念
- 每个主要章节一个 Scene
- 包含直觉解释、公式推导、数值示例、对比总结
- 用 `self.add_subcaption()` 添加字幕
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]


def extract_code(response: str) -> str:
    """从 LLM 响应中提取 Python 代码"""
    # 尝试提取 ```python ... ``` 代码块
    match = re.search(r"```python\s*\n(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    # 如果没有代码块标记，检查是否整个响应就是代码
    if "from manim import" in response:
        return response.strip()
    return response


# ── 主流程 ──
def main():
    parser = argparse.ArgumentParser(description="algo-viz API 模式: MD → 动画视频")
    parser.add_argument("md_file", help="Markdown 文件路径")
    parser.add_argument("-q", "--quality", default="m", choices=["l", "m", "h"],
                        help="渲染质量 (默认 m=720p)")
    parser.add_argument("--model", default="qwen/qwen3-235b-a22b",
                        help="LLM 模型 (默认 qwen/qwen3-235b-a22b)")
    parser.add_argument("--platform", default="openrouter",
                        choices=["openrouter", "mindcraft", "ablai"],
                        help="API 平台 (默认 openrouter)")
    parser.add_argument("--output", "-o", help="输出目录 (默认: MD文件同级 _anim/)")
    parser.add_argument("--dry-run", action="store_true",
                        help="只生成代码不渲染")

    args = parser.parse_args()

    md_path = Path(args.md_file).resolve()
    if not md_path.exists():
        print(f"[algo-viz] File not found: {md_path}")
        sys.exit(1)

    # 输出目录
    if args.output:
        out_dir = Path(args.output)
    else:
        out_dir = md_path.parent / "_anim" / md_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[algo-viz] Input:    {md_path}")
    print(f"[algo-viz] Output:   {out_dir}")
    print(f"[algo-viz] Model:    {args.platform}/{args.model}")
    print()

    # 1. 读取 MD
    md_content = md_path.read_text(encoding="utf-8")
    print(f"[algo-viz] MD length: {len(md_content)} chars")

    # 2. 调 LLM 生成代码
    messages = build_prompt(md_content, str(md_path))
    response = call_llm(messages, model=args.model, platform=args.platform)

    if not response:
        print("[algo-viz] LLM call failed")
        sys.exit(1)

    code = extract_code(response)
    script_path = out_dir / "script.py"
    script_path.write_text(code, encoding="utf-8")
    print(f"[algo-viz] Generated: {script_path} ({len(code)} chars)")

    if args.dry_run:
        print("[algo-viz] Dry run — skipping render")
        return

    # 3. 渲染 + 拼接 (复用 generate.py 的 render_stitch)
    gen_script = Path(__file__).parent / "generate.py"
    cmd = [sys.executable, str(gen_script), "--stitch", str(script_path), "-q", args.quality]
    print(f"[algo-viz] Rendering: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(Path(__file__).parent))

    if result.returncode == 0:
        final = out_dir / "final.mp4"
        if final.exists():
            print(f"\n[algo-viz] Done! Video: {final}")
        else:
            print(f"\n[algo-viz] Render complete. Check {out_dir}")
    else:
        print(f"\n[algo-viz] Render failed. Check {script_path} for errors.")
        print(f"[algo-viz] You can manually fix and re-render:")
        print(f"  python generate.py --stitch {script_path} -q {args.quality}")


if __name__ == "__main__":
    main()
