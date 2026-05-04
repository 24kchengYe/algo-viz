"""排序算法可视化动画"""
from manim import *
import copy


class SortingBase(Scene):
    """排序动画基类"""

    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data or [5, 3, 8, 1, 9, 2, 7, 4]
        self.bar_width = 0.6
        self.bar_gap = 0.15
        self.colors = [BLUE, GREEN, YELLOW, RED, PURPLE, ORANGE, TEAL, PINK]

    def create_bars(self, data, label=None):
        """创建柱状图"""
        bars = VGroup()
        labels = VGroup()
        max_val = max(data) if data else 1
        total_width = len(data) * (self.bar_width + self.bar_gap) - self.bar_gap
        start_x = -total_width / 2

        for i, val in enumerate(data):
            height = (val / max_val) * 4
            bar = Rectangle(
                width=self.bar_width,
                height=height,
                fill_color=self.colors[i % len(self.colors)],
                fill_opacity=0.8,
                stroke_color=WHITE,
                stroke_width=1,
            )
            bar.move_to(
                [start_x + i * (self.bar_width + self.bar_gap) + self.bar_width / 2,
                 -2 + height / 2, 0]
            )
            bars.add(bar)

            num_label = Text(str(val), font_size=20, color=WHITE)
            num_label.next_to(bar, DOWN, buff=0.1)
            labels.add(num_label)

        group = VGroup(bars, labels)
        if label:
            title = Text(label, font_size=28, color=WHITE)
            title.to_edge(UP, buff=0.5)
            group.add(title)
        return bars, labels

    def highlight_bars(self, bars, indices, color=YELLOW):
        """高亮指定柱子"""
        anims = []
        for i in indices:
            anims.append(bars[i].animate.set_fill(color, opacity=1))
        return anims

    def swap_bars(self, bars, labels, i, j, data):
        """交换两个柱子的动画"""
        bar_i, bar_j = bars[i], bars[j]
        label_i, label_j = labels[i], labels[j]

        pos_i = bar_i.get_center()
        pos_j = bar_j.get_center()

        # 交换数据
        data[i], data[j] = data[j], data[i]

        # 重新计算高度位置
        max_val = max(data) if data else 1
        h_i = (data[i] / max_val) * 4
        h_j = (data[j] / max_val) * 4

        target_i = [pos_i[0], -2 + h_i / 2, 0]
        target_j = [pos_j[0], -2 + h_j / 2, 0]

        # 动画：先上移 → 水平移动 → 下移（弧形路径）
        self.play(
            bar_i.animate.move_to(target_j).set_height(h_i),
            bar_j.animate.move_to(target_i).set_height(h_j),
            label_i.animate.move_to([pos_j[0], -2.3, 0]),
            label_j.animate.move_to([pos_i[0], -2.3, 0]),
            run_time=0.5,
        )

        # 交换列表中的引用
        bars[i], bars[j] = bars[j], bars[i]
        labels[i], labels[j] = labels[j], labels[i]


class BubbleSort(SortingBase):
    """冒泡排序可视化"""

    def construct(self):
        title = Text("冒泡排序 (Bubble Sort)", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        data = list(self.data)
        bars, labels = self.create_bars(data)
        self.play(*[FadeIn(b, shift=UP * 0.5) for b in bars],
                  *[FadeIn(l) for l in labels], run_time=1)
        self.wait(0.5)

        n = len(data)
        # 复杂度标注
        complexity = MathTex(r"O(n^2)", font_size=32, color=YELLOW)
        complexity.to_corner(UR, buff=0.5)
        self.play(Write(complexity))

        for i in range(n):
            for j in range(0, n - i - 1):
                # 高亮比较的两个
                self.play(*self.highlight_bars(bars, [j, j + 1], RED_B), run_time=0.2)

                if data[j] > data[j + 1]:
                    self.swap_bars(bars, labels, j, j + 1, data)

                # 恢复颜色
                self.play(
                    bars[j].animate.set_fill(BLUE, opacity=0.8),
                    bars[j + 1].animate.set_fill(BLUE, opacity=0.8),
                    run_time=0.15,
                )

            # 标记已排好的
            self.play(bars[n - i - 1].animate.set_fill(GREEN, opacity=0.9), run_time=0.2)

        self.play(*[b.animate.set_fill(GREEN, opacity=0.9) for b in bars], run_time=0.5)

        done = Text("排序完成!", font_size=36, color=GREEN)
        done.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(done, scale=1.2))
        self.wait(1)


class QuickSort(SortingBase):
    """快速排序可视化"""

    def construct(self):
        title = Text("快速排序 (Quick Sort)", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        complexity = MathTex(r"O(n \log n)", font_size=32, color=YELLOW)
        complexity.to_corner(UR, buff=0.5)
        self.play(Write(complexity))

        data = list(self.data)
        bars, labels = self.create_bars(data)
        self.play(*[FadeIn(b, shift=UP * 0.5) for b in bars],
                  *[FadeIn(l) for l in labels], run_time=1)
        self.wait(0.5)

        # 添加分治思想说明
        idea = Text("核心思想：选基准 → 分区 → 递归", font_size=24, color=GRAY)
        idea.to_edge(DOWN, buff=0.3)
        self.play(Write(idea))

        self._quicksort(bars, labels, data, 0, len(data) - 1)

        self.play(*[b.animate.set_fill(GREEN, opacity=0.9) for b in bars], run_time=0.5)
        self.play(FadeOut(idea))

        done = Text("排序完成!", font_size=36, color=GREEN)
        done.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(done, scale=1.2))
        self.wait(1)

    def _quicksort(self, bars, labels, data, low, high):
        if low >= high:
            if low == high:
                self.play(bars[low].animate.set_fill(GREEN, opacity=0.9), run_time=0.2)
            return

        # 高亮当前范围
        range_anims = []
        for i in range(low, high + 1):
            range_anims.append(bars[i].animate.set_fill(BLUE_B, opacity=0.9))
        self.play(*range_anims, run_time=0.3)

        pivot_idx = high
        pivot_val = data[pivot_idx]

        # 高亮基准
        self.play(bars[pivot_idx].animate.set_fill(RED, opacity=1), run_time=0.3)

        # 显示基准值
        pivot_label = Text(f"基准={pivot_val}", font_size=22, color=RED)
        pivot_label.next_to(bars[pivot_idx], UP, buff=0.2)
        self.play(FadeIn(pivot_label), run_time=0.3)

        i = low
        for j in range(low, high):
            self.play(bars[j].animate.set_fill(YELLOW, opacity=0.9), run_time=0.15)
            if data[j] < pivot_val:
                if i != j:
                    self.swap_bars(bars, labels, i, j, data)
                i += 1
            self.play(bars[j].animate.set_fill(BLUE_B, opacity=0.8), run_time=0.1)

        if i != high:
            self.swap_bars(bars, labels, i, high, data)

        self.play(FadeOut(pivot_label), run_time=0.2)
        self.play(bars[i].animate.set_fill(GREEN, opacity=0.9), run_time=0.3)

        self._quicksort(bars, labels, data, low, i - 1)
        self._quicksort(bars, labels, data, i + 1, high)


class MergeSort(SortingBase):
    """归并排序可视化"""

    def construct(self):
        title = Text("归并排序 (Merge Sort)", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        complexity = MathTex(r"O(n \log n)", font_size=32, color=YELLOW)
        complexity.to_corner(UR, buff=0.5)
        self.play(Write(complexity))

        data = list(self.data)
        bars, labels = self.create_bars(data)
        self.play(*[FadeIn(b, shift=UP * 0.5) for b in bars],
                  *[FadeIn(l) for l in labels], run_time=1)

        idea = Text("核心思想：拆分到最小 → 有序合并", font_size=24, color=GRAY)
        idea.to_edge(DOWN, buff=0.3)
        self.play(Write(idea))
        self.wait(0.5)

        self._mergesort_visual(bars, labels, data, 0, len(data) - 1)

        self.play(*[b.animate.set_fill(GREEN, opacity=0.9) for b in bars], run_time=0.5)
        self.play(FadeOut(idea))

        done = Text("排序完成!", font_size=36, color=GREEN)
        done.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(done, scale=1.2))
        self.wait(1)

    def _mergesort_visual(self, bars, labels, data, left, right):
        if left >= right:
            return

        mid = (left + right) // 2

        # 高亮左右两半
        left_anims = [bars[i].animate.set_fill(BLUE_C, opacity=0.9) for i in range(left, mid + 1)]
        right_anims = [bars[i].animate.set_fill(ORANGE, opacity=0.9) for i in range(mid + 1, right + 1)]
        self.play(*left_anims, *right_anims, run_time=0.4)

        self._mergesort_visual(bars, labels, data, left, mid)
        self._mergesort_visual(bars, labels, data, mid + 1, right)

        # 合并阶段：简化为冒泡式排序该区间
        for i in range(left, right + 1):
            for j in range(i + 1, right + 1):
                if data[i] > data[j]:
                    self.swap_bars(bars, labels, i, j, data)

        merge_anims = [bars[i].animate.set_fill(TEAL, opacity=0.9) for i in range(left, right + 1)]
        self.play(*merge_anims, run_time=0.3)
