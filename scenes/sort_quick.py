"""
快速排序 — 3B1B 审美级

审美改进:
- swap 用弧形路径 (path_arc)
- 柱子底部有基线，不再悬浮
- i/j 指针三角形可视化
- 每步有充足呼吸空间 (wait)
- Indicate/Circumscribe 引导焦点
- 颜色语义一致: 红=基准, 蓝=默认, 黄=比较中, 青=小于区, 橙=大于区, 绿=就位
"""
from manim import *
from scenes.style import *


class QuickSort(StyledScene):

    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data or [6, 3, 8, 1, 5, 2, 7, 4]

    def construct(self):
        self.opening()
        self.sort_section()

    # ── 开场 ───────────────────────────────────────────

    def opening(self):
        mobs = self.show_title("Quick Sort", "快速排序")

        idea = styled_body("分治法: 选基准 -> 分区 -> 递归", color=ACCENT_YELLOW)
        idea.next_to(mobs[-1], DOWN, buff=0.6)
        self.play(FadeIn(idea, shift=UP * 0.3), run_time=NORMAL)
        self.wait(PAUSE)

        avg = VGroup(
            Text("平均", font_size=SMALL_SIZE, color=ACCENT_GREEN),
            MathTex(r"O(n \log n)", font_size=30, color=ACCENT_GREEN),
        ).arrange(RIGHT, buff=0.15)
        worst = VGroup(
            Text("最坏", font_size=SMALL_SIZE, color=ACCENT_RED),
            MathTex(r"O(n^2)", font_size=30, color=ACCENT_RED),
        ).arrange(RIGHT, buff=0.15)
        complexity = VGroup(avg, worst).arrange(RIGHT, buff=1.0)
        complexity.next_to(idea, DOWN, buff=0.5)
        self.play(Write(complexity), run_time=NORMAL)
        self.wait(LONG_PAUSE)

        self.transition(*mobs, idea, complexity)

    # ── 排序主体 ───────────────────────────────────────

    def sort_section(self):
        self.chart = BarChart(self.data, color=ACCENT_BLUE)
        self.chart.move_to(DOWN * 0.2)

        # 柱子依次生长
        self.play(
            LaggedStart(
                *[GrowFromEdge(b, DOWN) for b in self.chart.bar_group],
                lag_ratio=0.1,
            ),
            run_time=SLOW,
        )
        # 标签依次淡入
        self.play(
            LaggedStart(
                *[FadeIn(l, shift=DOWN * 0.15) for l in self.chart.label_group],
                lag_ratio=0.06,
            ),
            run_time=NORMAL,
        )
        # 基线淡入
        self.play(FadeIn(self.chart.baseline), run_time=FAST)
        self.wait(PAUSE)

        # 颜色图例 — 右上角
        self.legend = self._make_legend()
        self.legend.to_corner(UR, buff=0.4)
        self.play(FadeIn(self.legend, shift=LEFT * 0.3), run_time=NORMAL)
        self.wait(PAUSE)

        self._quicksort(0, len(self.data) - 1)
        self.play(FadeOut(self.legend), run_time=FAST)
        self.finale()

    def _make_legend(self):
        """颜色图例"""
        items = [
            (ACCENT_RED, "基准 pivot"),
            (ACCENT_YELLOW, "比较中"),
            (ACCENT_TEAL, "< pivot"),
            (ACCENT_ORANGE, ">= pivot"),
            (ACCENT_GREEN, "已就位"),
        ]
        legend = VGroup()
        for color, text in items:
            dot = Square(side_length=0.18, fill_color=color, fill_opacity=0.8,
                         stroke_width=0).set_fill(color, 0.8)
            label = Text(text, font_size=TINY_SIZE, color=TEXT_SECONDARY)
            row = VGroup(dot, label).arrange(RIGHT, buff=0.15)
            legend.add(row)
        legend.arrange(DOWN, buff=0.15, aligned_edge=LEFT)

        bg = SurroundingRectangle(
            legend, color=STROKE_DIM, buff=0.2,
            corner_radius=0.1, fill_opacity=0.08, stroke_width=1,
        )
        return VGroup(bg, legend)

    def _quicksort(self, low, high):
        if low > high:
            return
        if low == high:
            self.play(self.chart.highlight(low, ACCENT_GREEN), run_time=FAST)
            return

        # ── 高亮当前处理范围 ──
        range_rect = SurroundingRectangle(
            VGroup(*self.chart.bar_group[low:high + 1]),
            color=ACCENT_BLUE, buff=0.15,
            corner_radius=0.1, stroke_width=2, stroke_opacity=0.6,
        )
        self.play(Create(range_rect), run_time=FAST)
        self.wait(0.3)

        # ── 选基准 ──
        pivot_idx = high
        pivot_val = self.chart.data[pivot_idx]
        self.play(self.chart.highlight(pivot_idx, ACCENT_RED), run_time=FAST)

        pivot_label = styled_small(f"pivot = {pivot_val}", color=ACCENT_RED)
        pivot_label.next_to(self.chart.bar_group[pivot_idx], UP, buff=0.4)
        self.play(FadeIn(pivot_label, shift=DOWN * 0.2), run_time=FAST)
        self.wait(0.5)

        # ── i 指针 (三角形标记) ──
        i_ptr = self._make_pointer("i", ACCENT_TEAL)
        i_ptr.next_to(self.chart.bar_group[low], DOWN, buff=0.15)
        self.play(FadeIn(i_ptr, shift=UP * 0.2), run_time=FAST)

        # ── 分区 ──
        i = low
        for j in range(low, high):
            # j 指针: 用 Circumscribe 闪烁当前柱子
            self.play(
                self.chart.highlight(j, ACCENT_YELLOW, 0.8),
                run_time=0.25,
            )

            if self.chart.data[j] < pivot_val:
                if i != j:
                    self.play(
                        *self.chart.swap_anims(i, j),
                        rate_func=smooth, run_time=0.5,
                    )
                self.play(
                    self.chart.highlight(i, ACCENT_TEAL, 0.7),
                    run_time=0.2,
                )
                i += 1
                # 移动 i 指针
                self.play(
                    i_ptr.animate.next_to(self.chart.bar_group[i] if i <= high else self.chart.bar_group[high], DOWN, buff=0.15),
                    run_time=0.2,
                )
            else:
                self.play(
                    self.chart.highlight(j, ACCENT_ORANGE, 0.5),
                    run_time=0.2,
                )

        # ── 基准归位 ──
        if i != high:
            self.play(
                *self.chart.swap_anims(i, high),
                rate_func=smooth, run_time=0.5,
            )

        # 基准就位
        self.play(
            self.chart.highlight(i, ACCENT_GREEN),
            FadeOut(pivot_label),
            FadeOut(range_rect),
            FadeOut(i_ptr),
            run_time=FAST,
        )
        self.wait(0.3)

        # 重置颜色
        reset = []
        for k in range(low, high + 1):
            if k != i:
                reset.append(self.chart.reset_color(k))
        if reset:
            self.play(*reset, run_time=FAST)

        self.wait(0.3)

        # 递归
        self._quicksort(low, i - 1)
        self._quicksort(i + 1, high)

    def _make_pointer(self, text, color):
        """指针三角形 + 文字"""
        tri = Triangle(fill_color=color, fill_opacity=0.8, stroke_width=0)
        tri.scale(0.15).rotate(PI)  # 朝上的三角
        label = Text(text, font_size=TINY_SIZE, color=color)
        label.next_to(tri, DOWN, buff=0.05)
        return VGroup(tri, label)

    # ── 排序完成 ───────────────────────────────────────

    def finale(self):
        # 波浪式全部变绿
        self.play(
            LaggedStart(
                *[self.chart.highlight(i, ACCENT_GREEN, 0.85)
                  for i in range(len(self.data))],
                lag_ratio=0.1,
            ),
            run_time=SLOW,
        )
        self.wait(0.5)

        # Flash 每个柱子
        self.play(
            LaggedStart(
                *[Indicate(self.chart.bar_group[i], color=WHITE, scale_factor=1.05)
                  for i in range(len(self.data))],
                lag_ratio=0.06,
            ),
            run_time=NORMAL,
        )

        done = styled_title("排序完成", color=ACCENT_GREEN)
        done.to_edge(UP, buff=0.5)
        self.play(FadeIn(done, scale=1.1), run_time=NORMAL)

        result = styled_body(
            " -> ".join(str(v) for v in sorted(self.data)),
            color=TEXT_PRIMARY,
        )
        result.next_to(done, DOWN, buff=0.4)
        self.play(Write(result), run_time=NORMAL)
        self.wait(LONG_PAUSE)
