#!/usr/bin/env python
"""
algo-viz 主入口：生成算法/技术学习动画

用法:
    # 使用预制模板
    python generate.py --scene sorting --algo bubble --data "[5,3,8,1,9,2]"
    python generate.py --scene tree --data "[5,3,7,1,4,6,8]"
    python generate.py --scene attention
    python generate.py --scene bfs
    python generate.py --scene dijkstra
    python generate.py --scene gradient_descent
    python generate.py --scene matrix_multiply

    # 使用 AI 生成的 JSON 脚本
    python generate.py --script path/to/script.json

    # 列出所有可用场景
    python generate.py --list
"""
import argparse
import ast
import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

# 项目根目录
ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "output"
SCENES_DIR = ROOT / "scenes"

# 预制场景注册表
SCENE_REGISTRY = {
    # 排序
    "bubble_sort":     ("sorting", "BubbleSort"),
    "quick_sort":      ("sort_quick", "QuickSort"),
    "merge_sort":      ("sorting", "MergeSort"),
    # 数据结构
    "bst":             ("data_structures", "BSTScene"),
    "tree":            ("data_structures", "BSTScene"),
    "linked_list":     ("data_structures", "LinkedListScene"),
    "hash_table":      ("data_structures", "HashTableScene"),
    "stack_queue":     ("data_structures", "StackQueueScene"),
    # 图算法
    "bfs":             ("graph_algos", "BFSScene"),
    "dfs":             ("graph_algos", "DFSScene"),
    "dijkstra":        ("graph_algos", "DijkstraScene"),
    # 深度学习 (3B1B 风格 — 优先使用)
    "attention":       ("dl_attention", "SelfAttention"),
    "self_attention":  ("dl_attention", "SelfAttention"),
    "transformer":     ("deep_learning", "TransformerArchScene"),
    "softmax":         ("deep_learning", "SoftmaxScene"),
    "backprop":        ("deep_learning", "BackpropScene"),
    "positional_encoding": ("dl_positional_encoding", "PositionalEncoding"),
    "rope":            ("dl_positional_encoding", "PositionalEncoding"),
    "pe":              ("dl_positional_encoding", "PositionalEncoding"),
    # 数学
    "matrix_multiply": ("math_concepts", "MatrixMultiplyScene"),
    "gradient_descent":("math_concepts", "GradientDescentScene"),
    "cross_entropy":   ("math_concepts", "CrossEntropyScene"),
}

# 别名映射（中文 / 常用简称）
ALIASES = {
    "冒泡排序": "bubble_sort",
    "快速排序": "quick_sort",
    "归并排序": "merge_sort",
    "二叉搜索树": "bst",
    "链表": "linked_list",
    "哈希表": "hash_table",
    "栈和队列": "stack_queue",
    "广度优先": "bfs",
    "深度优先": "dfs",
    "最短路径": "dijkstra",
    "注意力机制": "attention",
    "self-attention": "attention",
    "transformer": "transformer",
    "反向传播": "backprop",
    "位置编码": "positional_encoding",
    "rope": "positional_encoding",
    "旋转位置编码": "positional_encoding",
    "矩阵乘法": "matrix_multiply",
    "梯度下降": "gradient_descent",
    "交叉熵": "cross_entropy",
    # 英文别名
    "bubble": "bubble_sort",
    "quick": "quick_sort",
    "merge": "merge_sort",
    "sorting": "bubble_sort",
}


def resolve_scene(name: str) -> str | None:
    """解析场景名（支持中文别名）"""
    name = name.lower().strip().replace(" ", "_").replace("-", "_")
    if name in SCENE_REGISTRY:
        return name
    if name in ALIASES:
        return ALIASES[name]
    # 模糊匹配
    for key in SCENE_REGISTRY:
        if name in key or key in name:
            return key
    return None


def render_preset(scene_key: str, data=None, quality="l"):
    """渲染预制场景"""
    module_name, class_name = SCENE_REGISTRY[scene_key]
    module_path = SCENES_DIR / f"{module_name}.py"

    OUTPUT_DIR.mkdir(exist_ok=True)

    # 构建 manim 命令
    quality_map = {"l": "-ql", "m": "-qm", "h": "-qh", "k": "-qk"}
    q_flag = quality_map.get(quality, "-ql")

    cmd = [
        sys.executable, "-m", "manim", "render",
        q_flag,
        "--media_dir", str(OUTPUT_DIR),
        str(module_path),
        class_name,
    ]

    print(f"[algo-viz] Rendering: {class_name} from {module_name}.py")
    print(f"[algo-viz] Command: {' '.join(cmd)}")
    print(f"[algo-viz] Output: {OUTPUT_DIR}")
    print()

    result = subprocess.run(cmd, cwd=str(ROOT))

    if result.returncode == 0:
        # 找到输出文件
        video_dir = OUTPUT_DIR / "videos" / f"{module_name}" / quality_to_dir(quality)
        mp4_files = list(video_dir.glob("*.mp4")) if video_dir.exists() else []
        if mp4_files:
            latest = max(mp4_files, key=lambda f: f.stat().st_mtime)
            print(f"\n[algo-viz] Done! Video: {latest}")
            return str(latest)
        else:
            print(f"\n[algo-viz] Done! Check output in {OUTPUT_DIR}")
            return str(OUTPUT_DIR)
    else:
        print(f"\n[algo-viz] Render failed with code {result.returncode}")
        return None


def render_script(script_path: str, quality="l"):
    """渲染 AI 生成的 JSON 脚本"""
    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # 生成临时渲染文件
    render_code = textwrap.dedent(f"""\
    import json
    import sys
    sys.path.insert(0, r"{ROOT}")
    from scenes.custom import ScriptedScene

    script = json.loads(r'''{json.dumps(script, ensure_ascii=False)}''')

    class GeneratedScene(ScriptedScene):
        def __init__(self, **kwargs):
            super().__init__(script=script, **kwargs)
    """)

    tmp_file = ROOT / "_generated_scene.py"
    tmp_file.write_text(render_code, encoding="utf-8")

    quality_map = {"l": "-ql", "m": "-qm", "h": "-qh", "k": "-qk"}
    q_flag = quality_map.get(quality, "-ql")

    cmd = [
        sys.executable, "-m", "manim", "render",
        q_flag,
        "--media_dir", str(OUTPUT_DIR),
        str(tmp_file),
        "GeneratedScene",
    ]

    print(f"[algo-viz] Rendering AI-generated script: {script.get('title', 'Untitled')}")
    result = subprocess.run(cmd, cwd=str(ROOT))

    # 清理临时文件
    tmp_file.unlink(missing_ok=True)

    if result.returncode == 0:
        video_dir = OUTPUT_DIR / "videos" / "_generated_scene" / quality_to_dir(quality)
        mp4_files = list(video_dir.glob("*.mp4")) if video_dir.exists() else []
        if mp4_files:
            latest = max(mp4_files, key=lambda f: f.stat().st_mtime)
            print(f"\n[algo-viz] Done! Video: {latest}")
            return str(latest)
    else:
        print(f"\n[algo-viz] Render failed with code {result.returncode}")

    return None


def quality_to_dir(quality: str) -> str:
    """质量标记转输出目录名"""
    return {
        "l": "480p15",
        "m": "720p30",
        "h": "1080p60",
        "k": "2160p60",
    }.get(quality, "480p15")


def list_scenes():
    """列出所有可用场景"""
    print("\n[algo-viz] 可用场景列表:\n")

    categories = {}
    for key, (module, cls) in SCENE_REGISTRY.items():
        categories.setdefault(module, []).append((key, cls))

    category_names = {
        "sorting": "排序算法",
        "data_structures": "数据结构",
        "graph_algos": "图算法",
        "deep_learning": "深度学习",
        "math_concepts": "数学概念",
    }

    for module, scenes in categories.items():
        name = category_names.get(module, module)
        print(f"  [{name}]")
        for key, cls in scenes:
            # 找中文别名
            cn_aliases = [k for k, v in ALIASES.items() if v == key and not k.isascii()]
            alias_str = f" ({', '.join(cn_aliases)})" if cn_aliases else ""
            print(f"    {key:<20s} → {cls}{alias_str}")
        print()


def main():
    parser = argparse.ArgumentParser(description="algo-viz: 算法学习动画生成器")
    parser.add_argument("topic", nargs="?", help="主题名称（中文或英文）")
    parser.add_argument("--scene", "-s", help="场景名称")
    parser.add_argument("--algo", "-a", help="具体算法（用于排序等）")
    parser.add_argument("--data", "-d", help="输入数据，如 '[5,3,8,1,9,2]'")
    parser.add_argument("--script", help="AI 生成的 JSON 脚本文件路径")
    parser.add_argument("--quality", "-q", default="l",
                        choices=["l", "m", "h", "k"],
                        help="渲染质量: l=480p, m=720p, h=1080p, k=4K")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有可用场景")
    parser.add_argument("--output", "-o", help="输出目录（默认 ./output）")

    args = parser.parse_args()

    if args.output:
        global OUTPUT_DIR
        OUTPUT_DIR = Path(args.output)

    if args.list:
        list_scenes()
        return

    if args.script:
        result = render_script(args.script, args.quality)
        return

    # 确定场景
    scene_name = args.scene or args.topic
    if args.algo:
        scene_name = args.algo

    if not scene_name:
        parser.print_help()
        print("\n示例:")
        print('  python generate.py "快速排序"')
        print('  python generate.py --scene attention')
        print('  python generate.py --list')
        return

    scene_key = resolve_scene(scene_name)
    if not scene_key:
        print(f"[algo-viz] 未找到场景: {scene_name}")
        print(f"[algo-viz] 使用 --list 查看所有可用场景")
        # 尝试模糊推荐
        suggestions = [k for k in SCENE_REGISTRY if any(c in k for c in scene_name.lower())]
        if suggestions:
            print(f"[algo-viz] 你是否在找: {', '.join(suggestions)}")
        return

    render_preset(scene_key, data=args.data, quality=args.quality)


if __name__ == "__main__":
    main()
