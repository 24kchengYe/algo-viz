"""数学概念可视化动画"""
from manim import *
import numpy as np


class MatrixMultiplyScene(Scene):
    """矩阵乘法可视化"""

    def construct(self):
        title = Text("矩阵乘法", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        # 公式
        formula = MathTex(
            r"C_{ij} = \sum_{k=1}^{n} A_{ik} \cdot B_{kj}",
            font_size=30,
        )
        formula.next_to(title, DOWN, buff=0.3)
        self.play(Write(formula))

        # 矩阵 A (2x3)
        A = Matrix(
            [[1, 2, 3], [4, 5, 6]],
            left_bracket="[", right_bracket="]",
        )
        A.scale(0.7)
        A.move_to([-4, -0.5, 0])
        A_label = MathTex("A", font_size=28, color=RED)
        A_label.next_to(A, UP, buff=0.15)

        # 矩阵 B (3x2)
        B = Matrix(
            [[7, 8], [9, 10], [11, 12]],
            left_bracket="[", right_bracket="]",
        )
        B.scale(0.7)
        B.move_to([-0.5, -0.5, 0])
        B_label = MathTex("B", font_size=28, color=GREEN)
        B_label.next_to(B, UP, buff=0.15)

        # 等号
        eq = MathTex("=", font_size=30)
        eq.move_to([1.8, -0.5, 0])

        # 结果矩阵 C (2x2)
        C_vals = [[58, 64], [139, 154]]
        C = Matrix(
            C_vals,
            left_bracket="[", right_bracket="]",
        )
        C.scale(0.7)
        C.move_to([3.5, -0.5, 0])
        C_label = MathTex("C", font_size=28, color=PURPLE)
        C_label.next_to(C, UP, buff=0.15)

        self.play(
            Write(A), Write(A_label),
            Write(B), Write(B_label),
            Write(eq),
            run_time=1.5,
        )

        # 逐步计算 C[0][0]
        step = MathTex(
            r"C_{11} = 1 \times 7 + 2 \times 9 + 3 \times 11 = 58",
            font_size=24, color=YELLOW,
        )
        step.to_edge(DOWN, buff=0.8)
        self.play(Write(step))

        # 高亮行和列
        row_highlight = SurroundingRectangle(A.get_rows()[0], color=RED, buff=0.05)
        col_highlight = SurroundingRectangle(
            VGroup(B.get_entries()[0], B.get_entries()[2], B.get_entries()[4]),
            color=GREEN, buff=0.05,
        )
        self.play(Create(row_highlight), Create(col_highlight), run_time=0.5)
        self.wait(0.8)

        self.play(FadeOut(row_highlight), FadeOut(col_highlight), FadeOut(step))

        # 显示结果
        self.play(Write(C), Write(C_label), run_time=0.8)

        # 维度提示
        dim = Text("(2×3) · (3×2) = (2×2)", font_size=22, color=GRAY)
        dim.to_edge(DOWN, buff=0.5)
        self.play(Write(dim))
        self.wait(1.5)


class GradientDescentScene(Scene):
    """梯度下降可视化"""

    def construct(self):
        title = Text("梯度下降 (Gradient Descent)", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        formula = MathTex(
            r"\theta_{t+1} = \theta_t - \eta \nabla_\theta \mathcal{L}(\theta_t)",
            font_size=30,
        )
        formula.next_to(title, DOWN, buff=0.3)
        self.play(Write(formula))

        # 画损失函数曲线
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 10, 2],
            x_length=8,
            y_length=4,
            axis_config={"color": GRAY},
        )
        axes.move_to([0, -1, 0])

        x_label = axes.get_x_axis_label(r"\theta", font_size=24)
        y_label = axes.get_y_axis_label(r"\mathcal{L}", font_size=24)

        # f(x) = x^2 + 1
        curve = axes.plot(lambda x: x ** 2 + 0.5, color=BLUE)

        self.play(Create(axes), Write(x_label), Write(y_label), run_time=0.8)
        self.play(Create(curve), run_time=0.8)

        # 梯度下降过程
        lr = 0.3  # 学习率
        theta = 2.5  # 起始点
        dot = Dot(axes.coords_to_point(theta, theta ** 2 + 0.5), color=RED, radius=0.1)
        self.play(FadeIn(dot))

        lr_label = Text(f"学习率 η = {lr}", font_size=20, color=YELLOW)
        lr_label.to_corner(UR, buff=0.5).shift(DOWN * 0.8)
        self.play(Write(lr_label))

        for step in range(8):
            grad = 2 * theta  # f'(x) = 2x
            new_theta = theta - lr * grad

            # 画梯度箭头
            grad_arrow = Arrow(
                axes.coords_to_point(theta, theta ** 2 + 0.5),
                axes.coords_to_point(theta, theta ** 2 + 0.5) + LEFT * grad * 0.3,
                color=YELLOW, stroke_width=2, buff=0,
                max_tip_length_to_length_ratio=0.3,
            )
            self.play(GrowArrow(grad_arrow), run_time=0.2)

            new_point = axes.coords_to_point(new_theta, new_theta ** 2 + 0.5)
            self.play(
                dot.animate.move_to(new_point),
                FadeOut(grad_arrow),
                run_time=0.4,
            )

            theta = new_theta

        # 到达最小值
        min_label = Text(f"收敛到 θ ≈ {theta:.2f}", font_size=22, color=GREEN)
        min_label.to_edge(DOWN, buff=0.5)
        self.play(Write(min_label))
        self.wait(1.5)


class CrossEntropyScene(Scene):
    """交叉熵损失函数可视化"""

    def construct(self):
        title = Text("交叉熵损失 (Cross-Entropy Loss)", font_size=34, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        formula = MathTex(
            r"\mathcal{L} = -\sum_{i} y_i \log(\hat{y}_i)",
            font_size=32,
        )
        formula.next_to(title, DOWN, buff=0.3)
        self.play(Write(formula))

        intuition = Text("真实标签和预测概率越接近，损失越小", font_size=22, color=GRAY)
        intuition.next_to(formula, DOWN, buff=0.2)
        self.play(Write(intuition))

        # -log(x) 曲线
        axes = Axes(
            x_range=[0.01, 1, 0.2],
            y_range=[0, 5, 1],
            x_length=6,
            y_length=3.5,
            axis_config={"color": GRAY},
        )
        axes.move_to([0, -1.2, 0])

        x_label = axes.get_x_axis_label(r"\hat{y}", font_size=22)
        y_label = axes.get_y_axis_label(r"-\log(\hat{y})", font_size=20)

        curve = axes.plot(lambda x: -np.log(x), x_range=[0.05, 1], color=RED)

        self.play(Create(axes), Write(x_label), Write(y_label), run_time=0.8)
        self.play(Create(curve), run_time=0.8)

        # 标注关键点
        good = Dot(axes.coords_to_point(0.9, -np.log(0.9)), color=GREEN, radius=0.1)
        bad = Dot(axes.coords_to_point(0.1, -np.log(0.1)), color=RED, radius=0.1)

        good_label = Text("预测正确 (0.9)\n损失小 ✓", font_size=16, color=GREEN)
        good_label.next_to(good, RIGHT, buff=0.2)

        bad_label = Text("预测错误 (0.1)\n损失大 ✗", font_size=16, color=RED)
        bad_label.next_to(bad, RIGHT, buff=0.2)

        self.play(FadeIn(good), Write(good_label), run_time=0.5)
        self.play(FadeIn(bad), Write(bad_label), run_time=0.5)
        self.wait(2)
