"""
自定义场景渲染器：接收 AI 生成的结构化脚本 JSON，动态渲染 Manim 动画。

JSON 脚本格式：
{
  "title": "主题标题",
  "scenes": [
    {"type": "title", "text": "...", "subtitle": "..."},
    {"type": "formula", "latex": "...", "explain": "..."},
    {"type": "step", "title": "Step N", "content": "...", "formula": "..."},
    {"type": "code", "language": "python", "code": "...", "highlight_lines": [1,3]},
    {"type": "diagram", "nodes": [...], "edges": [...], "labels": [...]},
    {"type": "comparison", "left": {...}, "right": {...}},
    {"type": "summary", "points": ["...", "..."]},
  ]
}
"""
from manim import *


class ScriptedScene(Scene):
    """根据 JSON 脚本动态生成动画"""

    def __init__(self, script=None, **kwargs):
        super().__init__(**kwargs)
        self.script = script or {"title": "Demo", "scenes": []}

    def construct(self):
        for scene_data in self.script.get("scenes", []):
            scene_type = scene_data.get("type", "")
            handler = getattr(self, f"_render_{scene_type}", None)
            if handler:
                handler(scene_data)
            else:
                self._render_text(scene_data)

    def _render_title(self, data):
        """渲染标题页"""
        title = Text(data["text"], font_size=42, color=BLUE)
        title.to_edge(UP, buff=1.5)
        self.play(Write(title))

        if data.get("subtitle"):
            sub = Text(data["subtitle"], font_size=24, color=GRAY)
            sub.next_to(title, DOWN, buff=0.5)
            self.play(FadeIn(sub, shift=UP * 0.3))

        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects])

    def _render_formula(self, data):
        """渲染公式 + 解释"""
        formula = MathTex(data["latex"], font_size=36)
        formula.move_to([0, 1, 0])
        self.play(Write(formula))

        if data.get("explain"):
            explain = Text(data["explain"], font_size=22, color=GRAY)
            explain.next_to(formula, DOWN, buff=0.5)
            self.play(FadeIn(explain))

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects])

    def _render_step(self, data):
        """渲染分步讲解"""
        step_title = Text(data.get("title", ""), font_size=30, color=YELLOW)
        step_title.to_edge(UP, buff=0.5)
        self.play(Write(step_title))

        content = Text(data.get("content", ""), font_size=22, color=WHITE)
        content.next_to(step_title, DOWN, buff=0.5)
        self.play(FadeIn(content))

        if data.get("formula"):
            formula = MathTex(data["formula"], font_size=30)
            formula.next_to(content, DOWN, buff=0.5)
            self.play(Write(formula))

        self.wait(1.5)
        self.play(*[FadeOut(mob) for mob in self.mobjects])

    def _render_code(self, data):
        """渲染代码块"""
        code_text = data.get("code", "")
        code = Code(
            code=code_text,
            language=data.get("language", "python"),
            font_size=18,
            background="window",
            insert_line_no=True,
        )
        code.move_to([0, 0, 0])
        self.play(FadeIn(code, shift=UP * 0.5), run_time=1)

        # 高亮指定行
        highlight_lines = data.get("highlight_lines", [])
        if highlight_lines:
            for line_no in highlight_lines:
                highlight = SurroundingRectangle(
                    code.code[line_no - 1],
                    color=YELLOW, buff=0.05,
                )
                self.play(Create(highlight), run_time=0.3)
                self.wait(0.5)
                self.play(FadeOut(highlight), run_time=0.2)

        self.wait(1)
        self.play(*[FadeOut(mob) for mob in self.mobjects])

    def _render_comparison(self, data):
        """渲染对比表"""
        left = data.get("left", {})
        right = data.get("right", {})

        # 左边
        left_title = Text(left.get("title", "A"), font_size=26, color=BLUE)
        left_title.move_to([-3, 2, 0])
        left_items = VGroup()
        for i, item in enumerate(left.get("items", [])):
            t = Text(f"• {item}", font_size=18, color=WHITE)
            t.move_to([-3, 1.2 - i * 0.5, 0])
            left_items.add(t)

        # 右边
        right_title = Text(right.get("title", "B"), font_size=26, color=GREEN)
        right_title.move_to([3, 2, 0])
        right_items = VGroup()
        for i, item in enumerate(right.get("items", [])):
            t = Text(f"• {item}", font_size=18, color=WHITE)
            t.move_to([3, 1.2 - i * 0.5, 0])
            right_items.add(t)

        # 分隔线
        divider = Line([0, 2.5, 0], [0, -2.5, 0], color=GRAY, stroke_width=1)

        vs = Text("VS", font_size=24, color=YELLOW)
        vs.move_to([0, 2, 0])

        self.play(
            Write(left_title), Write(right_title), Write(vs),
            Create(divider),
            run_time=0.8,
        )
        self.play(
            *[FadeIn(item, shift=RIGHT * 0.3) for item in left_items],
            *[FadeIn(item, shift=LEFT * 0.3) for item in right_items],
            run_time=1,
        )
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])

    def _render_summary(self, data):
        """渲染总结页"""
        title = Text("总结", font_size=34, color=GREEN)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        points = data.get("points", [])
        for i, point in enumerate(points):
            bullet = Text(f"✓ {point}", font_size=22, color=WHITE)
            bullet.move_to([0, 1.5 - i * 0.7, 0])
            self.play(FadeIn(bullet, shift=RIGHT * 0.5), run_time=0.4)

        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])

    def _render_text(self, data):
        """兜底：渲染纯文本"""
        text = data.get("text", data.get("content", str(data)))
        t = Text(str(text)[:100], font_size=24, color=WHITE)
        t.move_to([0, 0, 0])
        self.play(FadeIn(t))
        self.wait(1)
        self.play(FadeOut(t))
