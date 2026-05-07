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


# ── 图片提取 ──
def extract_images_from_md(md_content: str, md_dir: Path) -> list[tuple[str, str]]:
    """从 MD 内容中提取图片引用，返回 [(alt_text, base64_data_url), ...]

    支持:
    - 本地相对路径: ![alt](./images/arch.png)
    - 本地绝对路径: ![alt](D:/path/to/img.png)
    - 远程 URL: ![alt](https://example.com/img.png)
    """
    import base64
    import requests as req

    pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    images = []

    for alt, src in pattern.findall(md_content):
        src = src.strip()
        try:
            img_bytes = None
            mime = "image/png"

            # 处理 /assets/xxx.png 这种以 / 开头的站内路径
            if src.startswith("/") and not src.startswith("//"):
                src = "." + src  # 转成 ./assets/xxx.png

            # 判断类型
            if src.startswith(("http://", "https://")):
                # 远程图片
                print(f"[algo-viz] Downloading image: {src[:80]}...")
                resp = req.get(src, timeout=30, verify=False)
                if resp.status_code == 200:
                    img_bytes = resp.content
                    # 推断 MIME
                    ct = resp.headers.get("content-type", "")
                    if "jpeg" in ct or "jpg" in ct:
                        mime = "image/jpeg"
                    elif "gif" in ct:
                        mime = "image/gif"
                    elif "webp" in ct:
                        mime = "image/webp"
            else:
                # 本地图片
                img_path = Path(src) if Path(src).is_absolute() else md_dir / src
                img_path = img_path.resolve()
                if img_path.exists():
                    print(f"[algo-viz] Loading image: {img_path.name}")
                    img_bytes = img_path.read_bytes()
                    ext = img_path.suffix.lower()
                    mime = {
                        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                        ".png": "image/png", ".gif": "image/gif",
                        ".webp": "image/webp", ".bmp": "image/bmp",
                    }.get(ext, "image/png")
                else:
                    print(f"[algo-viz] Image not found: {img_path}")

            if img_bytes:
                b64 = base64.b64encode(img_bytes).decode("ascii")
                data_url = f"data:{mime};base64,{b64}"
                images.append((alt or f"image_{len(images)+1}", data_url))
                size_kb = len(img_bytes) / 1024
                print(f"[algo-viz]   → {alt or 'image'}: {size_kb:.0f}KB ({mime})")

        except Exception as e:
            print(f"[algo-viz] Failed to load image {src}: {e}")

    return images


def build_prompt(md_content: str, md_path: str) -> list:
    """构建消息列表（支持多模态：文字 + 图片）"""
    md_dir = Path(md_path).parent

    # 提取图片
    images = extract_images_from_md(md_content, md_dir)

    # 构建 user message content
    text_part = f"""请根据以下学习笔记生成 Manim 教学动画脚本。

文件: {md_path}
包含 {len(images)} 张图片（架构图/流程图等，请参考图片内容设计动画布局）。

---
{md_content}
---

要求:
- 覆盖笔记中的所有核心概念
- 每个主要章节一个 Scene
- 包含直觉解释、公式推导、数值示例、对比总结
- 参考笔记中的图片来设计动画的架构图和流程图布局
- 用 `self.add_subcaption()` 添加字幕
"""

    if images:
        # 多模态消息: text + images
        content_parts = [{"type": "text", "text": text_part}]
        for alt, data_url in images:
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": data_url, "detail": "low"},  # low detail 省 token
            })
        print(f"[algo-viz] Built multimodal prompt: text + {len(images)} images")
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content_parts},
        ]
    else:
        # 纯文字消息
        print(f"[algo-viz] Built text-only prompt (no images found)")
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text_part},
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
