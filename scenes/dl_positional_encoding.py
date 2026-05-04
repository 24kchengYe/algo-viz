"""
位置编码 (Positional Encoding) — 3B1B 审美级 v2

升级:
- MovingCameraScene: Part 3 RoPE 旋转时 zoom in 到平面
- 安全边距: 所有 buff >= SAFE_MARGIN
- 自动限宽: styled_*() + FlowDiagram 自动缩放
- 透明度分层: 结构线 0.15, 上下文 0.4, 主元素 0.9
- 动画节奏: T_TITLE/T_KEY/T_AHA + W_STEP/W_THINK/W_AHA
"""
from manim import *
import numpy as np
from scenes.style import *


class PositionalEncoding(StyledScene):

    def construct(self):
        self.why_need_pe()
        self.sinusoidal_pe()
        self.rope_intuition()
        self.rope_relative()
        self.comparison()

    # ═══════════════════════════════════════════════════
    # Part 1: 为什么需要位置编码
    # ═══════════════════════════════════════════════════

    def why_need_pe(self):
        mobs = self.show_title("Positional Encoding", "位置编码")
        self.wait(W_STEP)

        question = styled_body(
            "Transformer 如何知道词的先后顺序?",
            color=ACCENT_YELLOW,
        )
        question.next_to(mobs[-1], DOWN, buff=0.8)
        self.play(FadeIn(question, shift=UP * 0.3), run_time=T_NORMAL)
        self.wait(W_THINK)
        self.transition(*mobs, question)

        # ── "猫追狗" vs "狗追猫" ──
        step = self.show_step("Self-Attention 不区分顺序")

        def make_sent(words, colors):
            boxes = VGroup()
            for w, c in zip(words, colors):
                box = glow_rect(1.2, 0.65, c)
                label = Text(w, font_size=BODY_SIZE, color=TEXT_PRIMARY)
                label.move_to(box)
                boxes.add(VGroup(box, label))
            boxes.arrange(RIGHT, buff=0.25)
            return boxes

        sent_a = make_sent(["猫", "追", "狗"], [ACCENT_RED, TEXT_SECONDARY, ACCENT_BLUE])
        sent_b = make_sent(["狗", "追", "猫"], [ACCENT_BLUE, TEXT_SECONDARY, ACCENT_RED])

        label_a = styled_label("A:", color=ACCENT_GREEN)
        label_b = styled_label("B:", color=ACCENT_ORANGE)

        row_a = VGroup(label_a, sent_a).arrange(RIGHT, buff=0.4)
        row_b = VGroup(label_b, sent_b).arrange(RIGHT, buff=0.4)
        rows = VGroup(row_a, row_b).arrange(DOWN, buff=0.8)
        rows.move_to(UP * 0.3)

        self.staggered_fadein(row_a, lag=0.15)
        self.wait(W_STEP)
        self.staggered_fadein(row_b, lag=0.15)
        self.wait(W_STEP)

        diff = styled_body("含义完全不同!", color=ACCENT_RED)
        diff.next_to(rows, DOWN, buff=0.6)
        self.play(FadeIn(diff, shift=UP * 0.3), run_time=T_NORMAL)
        self.flash_highlight(diff, color=ACCENT_RED)
        self.wait(W_STEP)

        problem = styled_small(
            'Attention 只看 Embedding, 不看顺序 -> 两句 "一样"',
            color=TEXT_SECONDARY,
        )
        problem.next_to(diff, DOWN, buff=0.4)
        self.play(FadeIn(problem, shift=UP * 0.2), run_time=T_NORMAL)
        self.wait(W_THINK)

        self.clear_step(step)
        self.transition(rows, diff, problem)

        # ── 解决方案 ──
        step = self.show_step("解决: E(word) + PE(pos)")

        def make_pe_row(word, pos):
            embed = VGroup(
                glow_rect(1.3, 0.55, ACCENT_BLUE),
                styled_small(f'E("{word}")', color=ACCENT_BLUE),
            )
            embed[1].move_to(embed[0])
            plus = MathTex("+", font_size=28, color=TEXT_SECONDARY)
            pe = VGroup(
                glow_rect(1.4, 0.55, ACCENT_YELLOW),
                styled_small(f"PE(pos={pos})", color=ACCENT_YELLOW),
            )
            pe[1].move_to(pe[0])
            return VGroup(embed, plus, pe).arrange(RIGHT, buff=0.2)

        pe_rows = VGroup(
            make_pe_row("猫", 0),
            make_pe_row("追", 1),
            make_pe_row("狗", 2),
        ).arrange(DOWN, buff=0.35)
        pe_rows.move_to(ORIGIN)

        self.staggered_fadein(pe_rows, shift=RIGHT * 0.3, lag=0.2)
        self.wait(W_STEP)

        result = styled_label("无序集合 -> 有序序列", color=ACCENT_GREEN)
        result.next_to(pe_rows, DOWN, buff=0.6)
        self.play(FadeIn(result, shift=UP * 0.2), run_time=T_NORMAL)
        self.flash_highlight(result, color=ACCENT_GREEN)
        self.wait(W_THINK)

        self.clear_step(step)
        self.transition(pe_rows, result)

    # ═══════════════════════════════════════════════════
    # Part 2: 正弦 PE
    # ═══════════════════════════════════════════════════

    def sinusoidal_pe(self):
        step = self.show_step("正弦位置编码 (Sinusoidal PE)")

        # 时钟类比
        analogy = styled_label("类比: 时钟的秒针/分针/时针", color=ACCENT_BLUE)
        analogy.to_edge(UP, buff=SAFE_MARGIN + 0.3)
        self.play(Write(analogy), run_time=T_NORMAL)

        clock_items = VGroup(
            styled_small("秒针: 高频, 区分相邻位置", color=ACCENT_RED),
            styled_small("分针: 中频, 区分较远位置", color=ACCENT_YELLOW),
            styled_small("时针: 低频, 区分很远位置", color=ACCENT_GREEN),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        clock_items.next_to(analogy, DOWN, buff=0.4)

        self.staggered_fadein(clock_items, shift=RIGHT * 0.3, lag=0.2)
        self.wait(W_THINK)
        self.transition(analogy, clock_items)

        # 波形图
        axes = Axes(
            x_range=[0, 20, 5], y_range=[-1.2, 1.2, 0.5],
            x_length=10, y_length=3.2,
            axis_config={
                "color": STROKE_DIM,
                "stroke_width": 1.5,
                "stroke_opacity": OP_STRUCTURE,
                "include_tip": False,
            },
            x_axis_config={"include_numbers": True, "font_size": TINY_SIZE},
        )
        axes.move_to(DOWN * 0.2)

        x_label = styled_small("position", color=TEXT_SECONDARY)
        x_label.next_to(axes.x_axis, RIGHT, buff=0.2)
        y_label = styled_small("PE", color=TEXT_SECONDARY)
        y_label.next_to(axes.y_axis, UP, buff=0.2)

        self.play(Create(axes), Write(x_label), Write(y_label), run_time=T_NORMAL)
        self.wait(W_BRIEF)

        freqs = [
            (1.0, ACCENT_RED, "高频 (dim 0-1)"),
            (0.25, ACCENT_YELLOW, "中频 (dim 4-5)"),
            (0.04, ACCENT_GREEN, "低频 (dim 10-11)"),
        ]

        legend = VGroup()
        for freq, color, name in freqs:
            curve = axes.plot(
                lambda x, f=freq: np.sin(f * x),
                x_range=[0, 20], color=color, stroke_width=2.5,
            )
            label = styled_small(name, color=color)
            legend.add(label)
            self.play(Create(curve), run_time=T_NORMAL)
            self.wait(W_BRIEF)

        legend.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        legend.to_corner(UR, buff=SAFE_MARGIN)
        self.play(FadeIn(legend), run_time=T_LABEL)
        self.wait(W_STEP)

        insight = styled_small(
            "不同频率组合 -> 每个位置有唯一编码",
            color=TEXT_SECONDARY,
        )
        insight.to_edge(DOWN, buff=SAFE_MARGIN)
        self.play(FadeIn(insight, shift=UP * 0.2), run_time=T_NORMAL)
        self.wait(W_THINK)

        self.clear_step(step)
        # 手动收集要清除的对象
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=T_NORMAL)

    # ═══════════════════════════════════════════════════
    # Part 3: RoPE 旋转直觉 — 带 zoom in
    # ═══════════════════════════════════════════════════

    def rope_intuition(self):
        step = self.show_step("RoPE: 旋转位置编码")

        subtitle = styled_label("核心思想: 用旋转角度编码位置", color=ACCENT_BLUE)
        subtitle.to_edge(UP, buff=SAFE_MARGIN + 0.3)
        self.play(Write(subtitle), run_time=T_NORMAL)
        self.wait(W_STEP)

        # 2D 平面
        plane = NumberPlane(
            x_range=[-2.5, 2.5, 1], y_range=[-2.5, 2.5, 1],
            x_length=5, y_length=5,
            background_line_style={
                "stroke_color": STROKE_DIM,
                "stroke_width": 0.8,
                "stroke_opacity": OP_STRUCTURE,
            },
            axis_config={
                "stroke_color": STROKE_DIM,
                "stroke_width": 1.5,
                "stroke_opacity": 0.3,
            },
        )
        plane.move_to(LEFT * 1.5 + DOWN * 0.3)
        self.play(FadeIn(plane, run_time=T_NORMAL))
        self.wait(W_BRIEF)

        # ── zoom in 到平面 ──
        self.zoom_in(plane, scale=0.75, run_time=T_KEY)
        self.wait(W_BRIEF)

        # pos=0 向量
        vec_0 = Arrow(
            plane.c2p(0, 0), plane.c2p(1.8, 0),
            color=ACCENT_BLUE, stroke_width=3.5, buff=0,
            max_tip_length_to_length_ratio=0.12,
        )
        lbl_0 = styled_small("pos=0", color=ACCENT_BLUE)
        lbl_0.next_to(vec_0.get_end(), UR, buff=0.1)
        self.play(GrowArrow(vec_0), FadeIn(lbl_0), run_time=T_NORMAL)
        self.wait(W_STEP)

        # 旋转到 pos=1,2,3,4
        theta = 30 * DEGREES
        colors = [ACCENT_GREEN, ACCENT_YELLOW, ACCENT_RED, ACCENT_PURPLE]
        all_vecs = [vec_0]
        all_lbls = [lbl_0]

        # 右侧说明面板
        info_rows = VGroup()

        for pos in range(1, 5):
            angle = pos * theta
            end = plane.c2p(1.8 * np.cos(angle), 1.8 * np.sin(angle))
            direction = normalize(np.array(end) - np.array(plane.c2p(0, 0)))
            color = colors[pos - 1]

            vec = Arrow(
                plane.c2p(0, 0), end,
                color=color, stroke_width=3, buff=0,
                max_tip_length_to_length_ratio=0.12,
            )
            lbl = styled_small(f"pos={pos}", color=color)
            lbl.next_to(end, direction=direction, buff=0.12)

            arc = Arc(
                radius=0.5, start_angle=0, angle=angle,
                arc_center=plane.c2p(0, 0),
                color=color, stroke_width=1.5, stroke_opacity=0.5,
            )

            self.play(GrowArrow(vec), Create(arc), FadeIn(lbl), run_time=0.8)
            self.wait(W_BRIEF)

            all_vecs.append(vec)
            all_lbls.append(lbl)

            row = styled_small(
                f"pos={pos}  rotate {pos * int(theta / DEGREES)}deg",
                color=color,
            )
            info_rows.add(row)

        # zoom out 看全局
        self.zoom_out(run_time=T_KEY)
        self.wait(W_BRIEF)

        # 右侧面板
        info_rows.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        info_rows.to_edge(RIGHT, buff=SAFE_MARGIN)
        self.play(FadeIn(info_rows), run_time=T_LABEL)
        self.wait(W_STEP)

        key_insight = styled_body(
            "每个位置旋转固定角度 -> 位置不同, 方向不同",
            color=ACCENT_YELLOW,
        )
        key_insight.to_edge(DOWN, buff=SAFE_MARGIN)
        self.play(FadeIn(key_insight, shift=UP * 0.2), run_time=T_NORMAL)
        self.flash_highlight(key_insight, color=ACCENT_YELLOW)
        self.wait(W_THINK)

        self.clear_step(step)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=T_NORMAL)

    # ═══════════════════════════════════════════════════
    # Part 4: RoPE 相对位置
    # ═══════════════════════════════════════════════════

    def rope_relative(self):
        step = self.show_step("RoPE 关键: 点积只取决于相对位置")

        # 公式
        formula = styled_formula(r"q_m^T k_n \propto f(m - n)")
        formula.to_edge(UP, buff=SAFE_MARGIN + 0.3)
        self.play(Write(formula), run_time=T_KEY)
        self.wait(W_STEP)

        # 两组对比
        def make_pair_row(pos_q, pos_k):
            q_box = glow_rect(1.3, 0.5, ACCENT_RED)
            q_text = styled_small(f"Q(pos={pos_q})", color=ACCENT_RED)
            q_text.move_to(q_box)

            dot = MathTex(r"\cdot", font_size=28, color=TEXT_SECONDARY)

            k_box = glow_rect(1.3, 0.5, ACCENT_BLUE)
            k_text = styled_small(f"K(pos={pos_k})", color=ACCENT_BLUE)
            k_text.move_to(k_box)

            dist = styled_label(f"距离={pos_q - pos_k}", color=ACCENT_GREEN)

            return VGroup(
                VGroup(q_box, q_text), dot, VGroup(k_box, k_text), dist,
            ).arrange(RIGHT, buff=0.25)

        pair1 = make_pair_row(3, 1)
        pair2 = make_pair_row(103, 101)
        pairs = VGroup(pair1, pair2).arrange(DOWN, buff=0.8)
        pairs.move_to(DOWN * 0.2)

        self.staggered_fadein(VGroup(pair1), shift=RIGHT * 0.3, lag=0.1)
        self.wait(W_STEP)
        self.staggered_fadein(VGroup(pair2), shift=RIGHT * 0.3, lag=0.1)
        self.wait(W_STEP)

        # 等号
        eq_sign = styled_title("=", color=ACCENT_GREEN)
        eq_sign.move_to(pairs)
        same = styled_body("注意力分数完全相同!", color=ACCENT_GREEN)
        same.next_to(pairs, DOWN, buff=0.6)

        self.play(FadeIn(eq_sign, scale=1.5), run_time=T_NORMAL)
        self.play(FadeIn(same, shift=UP * 0.2), run_time=T_NORMAL)
        self.indicate(same, color=ACCENT_GREEN)
        self.wait(W_THINK)

        explain = styled_small(
            "旋转差 = 相对位置 x 频率 -> 绝对旋转自动变成相对位置",
            color=TEXT_SECONDARY,
        )
        explain.next_to(same, DOWN, buff=0.35)
        self.play(FadeIn(explain, shift=UP * 0.2), run_time=T_NORMAL)
        self.wait(W_THINK)

        self.clear_step(step)
        self.transition(formula, pairs, eq_sign, same, explain)

    # ═══════════════════════════════════════════════════
    # Part 5: 对比总结
    # ═══════════════════════════════════════════════════

    def comparison(self):
        step = self.show_step("位置编码方法对比")

        headers = ["方法", "类型", "可学习", "外推", "代表模型"]
        header_cells = VGroup()
        for h in headers:
            cell = VGroup(
                dim_rect(2.0, 0.5, ACCENT_BLUE),
                styled_small(h, color=ACCENT_BLUE),
            )
            cell[1].move_to(cell[0])
            header_cells.add(cell)
        header_cells.arrange(RIGHT, buff=0.06)

        rows_data = [
            (["Sinusoidal", "绝对", "No", "较差", "Transformer"], False),
            (["Learned PE", "绝对", "Yes", "不支持", "BERT, GPT-2"], False),
            (["RoPE", "相对", "No", "较好", "LLaMA, Qwen"], True),
        ]

        data_rows = VGroup()
        for row_vals, is_highlight in rows_data:
            row_cells = VGroup()
            for val in row_vals:
                txt_color = ACCENT_GREEN if is_highlight else TEXT_PRIMARY
                cell = VGroup(
                    dim_rect(2.0, 0.45),
                    styled_small(val, color=txt_color),
                )
                cell[1].move_to(cell[0])
                row_cells.add(cell)
            row_cells.arrange(RIGHT, buff=0.06)
            data_rows.add(row_cells)
        data_rows.arrange(DOWN, buff=0.06)

        table = VGroup(header_cells, data_rows).arrange(DOWN, buff=0.06)
        table.move_to(UP * 0.3)

        # 如果表太宽, 自动缩放
        if table.get_width() > SAFE_WIDTH:
            table.scale(SAFE_WIDTH / table.get_width())

        self.play(FadeIn(header_cells), run_time=T_NORMAL)
        self.wait(W_BRIEF)
        self.staggered_fadein(data_rows, shift=RIGHT * 0.2, lag=0.2)
        self.wait(W_STEP)

        # 高亮 RoPE 行
        rope_rect = SurroundingRectangle(
            data_rows[2], color=ACCENT_GREEN, buff=0.06,
            corner_radius=0.08, stroke_width=2.5,
        )
        self.play(Create(rope_rect), run_time=T_NORMAL)
        self.wait(W_BRIEF)

        conclusion = styled_body("RoPE = 当前大模型主流", color=ACCENT_GREEN)
        conclusion.next_to(table, DOWN, buff=0.6)
        self.play(FadeIn(conclusion, shift=UP * 0.3), run_time=T_NORMAL)
        self.flash_highlight(conclusion, color=ACCENT_GREEN)
        self.wait(W_AHA)

        self.clear_step(step)
