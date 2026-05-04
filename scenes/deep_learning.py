"""深度学习概念可视化动画"""
from manim import *
import numpy as np


class SelfAttentionScene(Scene):
    """Self-Attention 机制可视化"""

    def construct(self):
        title = Text("Self-Attention 机制", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        # === Step 1: 输入 tokens ===
        step1 = Text("Step 1: 输入嵌入", font_size=24, color=YELLOW)
        step1.to_corner(UL, buff=0.5).shift(DOWN * 0.8)
        self.play(Write(step1))

        tokens = ["I", "love", "ML"]
        token_boxes = VGroup()
        for i, t in enumerate(tokens):
            box = RoundedRectangle(width=1.2, height=0.6, corner_radius=0.1,
                                    color=BLUE, fill_opacity=0.3)
            box.move_to([-3 + i * 2, 1.5, 0])
            label = Text(t, font_size=22, color=WHITE).move_to(box)
            token_boxes.add(VGroup(box, label))

        self.play(*[FadeIn(t, shift=DOWN * 0.3) for t in token_boxes], run_time=0.8)
        self.wait(0.5)

        # === Step 2: 生成 Q, K, V ===
        self.play(FadeOut(step1))
        step2 = Text("Step 2: 线性变换得到 Q, K, V", font_size=24, color=YELLOW)
        step2.to_corner(UL, buff=0.5).shift(DOWN * 0.8)
        self.play(Write(step2))

        formula_qkv = MathTex(
            r"Q = XW^Q, \quad K = XW^K, \quad V = XW^V",
            font_size=28,
        )
        formula_qkv.move_to([0, 0.3, 0])
        self.play(Write(formula_qkv))
        self.wait(0.5)

        # Q K V 矩阵可视化
        colors = {"Q": RED, "K": GREEN, "V": PURPLE}
        qkv_groups = VGroup()
        for i, (name, color) in enumerate(colors.items()):
            mat = Rectangle(width=1.8, height=1.2, color=color, fill_opacity=0.2)
            mat.move_to([-3 + i * 3, -1.2, 0])
            label = Text(name, font_size=28, color=color, weight=BOLD)
            label.move_to(mat)

            # 矩阵数值（示意）
            vals = Text("3×2", font_size=16, color=GRAY)
            vals.next_to(mat, DOWN, buff=0.1)

            qkv_groups.add(VGroup(mat, label, vals))

        self.play(*[FadeIn(g, shift=DOWN * 0.3) for g in qkv_groups], run_time=0.8)
        self.wait(0.5)

        # === Step 3: 计算注意力分数 ===
        self.play(FadeOut(step2), FadeOut(formula_qkv), FadeOut(qkv_groups))
        step3 = Text("Step 3: 计算注意力分数", font_size=24, color=YELLOW)
        step3.to_corner(UL, buff=0.5).shift(DOWN * 0.8)
        self.play(Write(step3))

        formula_attn = MathTex(
            r"\text{score} = \frac{Q \cdot K^T}{\sqrt{d_k}}",
            font_size=34,
        )
        formula_attn.move_to([0, 1, 0])
        self.play(Write(formula_attn))

        # 注意力矩阵热力图
        attn_vals = np.array([[0.7, 0.2, 0.1],
                               [0.1, 0.6, 0.3],
                               [0.2, 0.3, 0.5]])

        heatmap = VGroup()
        cell_size = 0.9
        labels_top = VGroup()
        labels_left = VGroup()

        for i in range(3):
            lt = Text(tokens[i], font_size=16, color=GRAY)
            lt.move_to([-1 + i * cell_size, -0.2, 0])
            labels_top.add(lt)

            ll = Text(tokens[i], font_size=16, color=GRAY)
            ll.move_to([-2.0, -0.8 - i * cell_size, 0])
            labels_left.add(ll)

            for j in range(3):
                val = attn_vals[i][j]
                cell = Square(side_length=cell_size * 0.9)
                cell.move_to([-1 + j * cell_size, -0.8 - i * cell_size, 0])
                # 颜色深度映射
                cell.set_fill(
                    interpolate_color(BLACK, RED, val),
                    opacity=0.8,
                )
                cell.set_stroke(WHITE, width=0.5)
                num = Text(f"{val:.1f}", font_size=14, color=WHITE)
                num.move_to(cell)
                heatmap.add(VGroup(cell, num))

        self.play(
            *[FadeIn(c) for c in heatmap],
            *[Write(l) for l in labels_top],
            *[Write(l) for l in labels_left],
            run_time=1,
        )

        explain = Text('"I" 最关注自己 (0.7)，"love" 也关注 "ML" (0.3)',
                        font_size=20, color=GRAY)
        explain.to_edge(DOWN, buff=0.5)
        self.play(Write(explain))
        self.wait(1)

        # === Step 4: Softmax + 加权求和 ===
        self.play(FadeOut(step3), FadeOut(heatmap), FadeOut(labels_top),
                  FadeOut(labels_left), FadeOut(formula_attn), FadeOut(explain))
        step4 = Text("Step 4: Softmax → 加权求和 Value", font_size=24, color=YELLOW)
        step4.to_corner(UL, buff=0.5).shift(DOWN * 0.8)
        self.play(Write(step4))

        full_formula = MathTex(
            r"\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right) V",
            font_size=34,
        )
        full_formula.move_to([0, 0.5, 0])
        self.play(Write(full_formula))

        # 流程总结图
        flow_items = ["Input\nEmbed", "Q,K,V\n线性变换", "QK^T\n计算分数",
                       "Softmax\n归一化", "×V\n加权求和", "Output"]
        flow = VGroup()
        for i, item in enumerate(flow_items):
            box = RoundedRectangle(width=1.3, height=0.8, corner_radius=0.1,
                                    color=BLUE if i < 5 else GREEN, fill_opacity=0.3)
            box.move_to([-4.5 + i * 1.8, -1.5, 0])
            label = Text(item, font_size=13, color=WHITE).move_to(box)
            flow.add(VGroup(box, label))
            if i > 0:
                arrow = Arrow(flow[i - 1][0].get_right(), box.get_left(),
                              buff=0.05, color=GRAY, stroke_width=2,
                              max_tip_length_to_length_ratio=0.2)
                flow.add(arrow)

        self.play(*[FadeIn(f) for f in flow], run_time=1)
        self.wait(2)


class TransformerArchScene(Scene):
    """Transformer 整体架构可视化"""

    def construct(self):
        title = Text("Transformer 架构", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.2)
        self.play(Write(title))

        # Encoder 侧
        enc_title = Text("Encoder", font_size=22, color=BLUE_B)
        enc_title.move_to([-3, 2.5, 0])
        self.play(Write(enc_title))

        enc_components = [
            ("Input\nEmbedding", GRAY, [-3, 1.8, 0]),
            ("Positional\nEncoding", GRAY, [-3, 0.9, 0]),
            ("Multi-Head\nAttention", RED, [-3, 0, 0]),
            ("Add & Norm", YELLOW_D, [-3, -0.8, 0]),
            ("Feed\nForward", PURPLE, [-3, -1.6, 0]),
            ("Add & Norm", YELLOW_D, [-3, -2.4, 0]),
        ]

        enc_boxes = VGroup()
        for text, color, pos in enc_components:
            box = RoundedRectangle(width=2.2, height=0.65, corner_radius=0.08,
                                    color=color, fill_opacity=0.25)
            box.move_to(pos)
            label = Text(text, font_size=13, color=WHITE).move_to(box)
            group = VGroup(box, label)
            enc_boxes.add(group)
            self.play(FadeIn(group, shift=UP * 0.2), run_time=0.25)

        # Encoder 之间的箭头
        for i in range(len(enc_boxes) - 1):
            arrow = Arrow(enc_boxes[i][0].get_bottom(), enc_boxes[i + 1][0].get_top(),
                          buff=0.03, color=GRAY, stroke_width=1.5,
                          max_tip_length_to_length_ratio=0.3)
            self.play(GrowArrow(arrow), run_time=0.1)

        # N× 标注
        nx = Text("×N", font_size=20, color=YELLOW)
        nx.next_to(enc_boxes[2], RIGHT, buff=0.3)
        brace = Brace(VGroup(enc_boxes[2], enc_boxes[5]), RIGHT, buff=0.1, color=YELLOW)
        self.play(GrowFromCenter(brace), Write(nx))

        # Decoder 侧
        dec_title = Text("Decoder", font_size=22, color=GREEN_B)
        dec_title.move_to([3, 2.5, 0])
        self.play(Write(dec_title))

        dec_components = [
            ("Output\nEmbedding", GRAY, [3, 1.8, 0]),
            ("Positional\nEncoding", GRAY, [3, 0.9, 0]),
            ("Masked\nMulti-Head Attn", RED_B, [3, 0, 0]),
            ("Add & Norm", YELLOW_D, [3, -0.5, 0]),
            ("Cross\nAttention", ORANGE, [3, -1.2, 0]),
            ("Add & Norm", YELLOW_D, [3, -1.7, 0]),
            ("Feed\nForward", PURPLE, [3, -2.2, 0]),
            ("Linear\n+ Softmax", GREEN, [3, -2.9, 0]),
        ]

        dec_boxes = VGroup()
        for text, color, pos in dec_components:
            box = RoundedRectangle(width=2.2, height=0.5, corner_radius=0.08,
                                    color=color, fill_opacity=0.25)
            box.move_to(pos)
            label = Text(text, font_size=12, color=WHITE).move_to(box)
            group = VGroup(box, label)
            dec_boxes.add(group)
            self.play(FadeIn(group, shift=UP * 0.2), run_time=0.2)

        # Cross-attention 连接线
        cross_arrow = CurvedArrow(
            enc_boxes[-1][0].get_right(),
            dec_boxes[4][0].get_left(),
            color=ORANGE,
            angle=-0.3,
        )
        self.play(Create(cross_arrow), run_time=0.5)

        cross_label = Text("K, V from\nEncoder", font_size=14, color=ORANGE)
        cross_label.move_to([0, -1.2, 0])
        self.play(Write(cross_label))

        self.wait(2)


class SoftmaxScene(Scene):
    """Softmax 函数可视化"""

    def construct(self):
        title = Text("Softmax 函数", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        # 公式
        formula = MathTex(
            r"\text{softmax}(z_i) = \frac{e^{z_i}}{\sum_{j=1}^{K} e^{z_j}}",
            font_size=34,
        )
        formula.next_to(title, DOWN, buff=0.4)
        self.play(Write(formula))

        # 直觉解释
        intuition = Text("把任意实数向量 → 概率分布 (和为1, 全部>0)", font_size=22, color=GRAY)
        intuition.next_to(formula, DOWN, buff=0.3)
        self.play(Write(intuition))

        # 数值示例
        input_vals = [2.0, 1.0, 0.1]
        exp_vals = [np.exp(v) for v in input_vals]
        exp_sum = sum(exp_vals)
        softmax_vals = [v / exp_sum for v in exp_vals]

        # 输入
        input_label = Text("输入 z:", font_size=22, color=YELLOW)
        input_label.move_to([-4, -0.5, 0])
        self.play(Write(input_label))

        input_bars = VGroup()
        for i, val in enumerate(input_vals):
            bar = Rectangle(width=val * 0.8, height=0.5,
                             color=BLUE, fill_opacity=0.6)
            bar.move_to([-2 + val * 0.4, -0.5 - i * 0.7, 0])
            num = Text(f"{val}", font_size=18, color=WHITE)
            num.next_to(bar, RIGHT, buff=0.1)
            input_bars.add(VGroup(bar, num))

        self.play(*[FadeIn(b) for b in input_bars], run_time=0.8)

        # 箭头
        arrow = Arrow(LEFT * 0.2, RIGHT * 1.2, color=YELLOW)
        arrow.move_to([1.5, -1, 0])
        arrow_label = Text("softmax", font_size=18, color=YELLOW)
        arrow_label.next_to(arrow, UP, buff=0.1)
        self.play(GrowArrow(arrow), Write(arrow_label))

        # 输出
        output_label = Text("输出 p:", font_size=22, color=GREEN)
        output_label.move_to([3, -0.5, 0])

        output_bars = VGroup()
        for i, val in enumerate(softmax_vals):
            bar = Rectangle(width=val * 5, height=0.5,
                             color=GREEN, fill_opacity=0.6)
            bar.move_to([4.5 + val * 2.5, -0.5 - i * 0.7, 0])
            num = Text(f"{val:.3f}", font_size=18, color=WHITE)
            num.next_to(bar, RIGHT, buff=0.1)
            output_bars.add(VGroup(bar, num))

        self.play(Write(output_label), *[FadeIn(b) for b in output_bars], run_time=0.8)

        # 验证和为 1
        sum_text = MathTex(
            f"{softmax_vals[0]:.3f} + {softmax_vals[1]:.3f} + {softmax_vals[2]:.3f} = 1.000",
            font_size=24, color=GREEN,
        )
        sum_text.to_edge(DOWN, buff=0.5)
        self.play(Write(sum_text))
        self.wait(2)


class BackpropScene(Scene):
    """反向传播可视化"""

    def construct(self):
        title = Text("反向传播 (Backpropagation)", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        core = Text("核心：链式法则从输出向输入传播梯度", font_size=22, color=GRAY)
        core.next_to(title, DOWN, buff=0.3)
        self.play(Write(core))

        # 简单神经网络：3层
        layers = [3, 4, 2]  # 输入3，隐藏4，输出2
        layer_names = ["Input", "Hidden", "Output"]
        all_nodes = []
        all_labels = []

        for l, (n, name) in enumerate(zip(layers, layer_names)):
            x = -3 + l * 3
            nodes = []
            for i in range(n):
                y = (n - 1) / 2 * 0.8 - i * 0.8
                circle = Circle(radius=0.25, color=BLUE, fill_opacity=0.3)
                circle.move_to([x, y, 0])
                nodes.append(circle)

            all_nodes.append(nodes)

            label = Text(name, font_size=18, color=GRAY)
            label.move_to([x, -2.5, 0])
            all_labels.append(label)

        # 画所有节点
        self.play(
            *[GrowFromCenter(n) for layer in all_nodes for n in layer],
            *[Write(l) for l in all_labels],
            run_time=1,
        )

        # 画连接线
        edges = VGroup()
        for l in range(len(layers) - 1):
            for n1 in all_nodes[l]:
                for n2 in all_nodes[l + 1]:
                    edge = Line(n1.get_right(), n2.get_left(),
                                color=GRAY, stroke_width=1, stroke_opacity=0.4)
                    edges.add(edge)
        self.play(Create(edges), run_time=0.8)

        # Forward pass（蓝色波浪从左到右）
        fwd_label = Text("Forward Pass →", font_size=22, color=BLUE)
        fwd_label.to_edge(DOWN, buff=1.2)
        self.play(Write(fwd_label))

        for l in range(len(layers)):
            anims = [n.animate.set_fill(BLUE, opacity=0.8) for n in all_nodes[l]]
            self.play(*anims, run_time=0.4)
            self.play(*[n.animate.set_fill(BLUE, opacity=0.3) for n in all_nodes[l]], run_time=0.2)

        # Loss 计算
        loss = MathTex(r"\mathcal{L} = \text{CrossEntropy}(y, \hat{y})",
                        font_size=26, color=RED)
        loss.move_to([3, -1.5, 0])
        self.play(Write(loss))

        # Backward pass（红色波浪从右到左）
        self.play(FadeOut(fwd_label))
        bwd_label = Text("← Backward Pass (梯度回传)", font_size=22, color=RED)
        bwd_label.to_edge(DOWN, buff=1.2)
        self.play(Write(bwd_label))

        for l in range(len(layers) - 1, -1, -1):
            anims = [n.animate.set_fill(RED, opacity=0.8) for n in all_nodes[l]]
            self.play(*anims, run_time=0.4)

        # 梯度更新公式
        update = MathTex(
            r"w \leftarrow w - \eta \frac{\partial \mathcal{L}}{\partial w}",
            font_size=28, color=YELLOW,
        )
        update.next_to(bwd_label, UP, buff=0.3)
        self.play(Write(update))
        self.wait(2)
