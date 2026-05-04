"""
Self-Attention — 3B1B 审美级

审美改进:
- token 用 glow_rect 发光框
- 热力图更高对比度
- 公式出现后 Circumscribe 强调关键部分
- 流程图用 glow_rect
- 充足的 wait 呼吸空间
- Indicate 引导视觉焦点
"""
from manim import *
import numpy as np
from scenes.style import *


class SelfAttention(StyledScene):

    def construct(self):
        self.opening()
        self.intuition()
        self.qkv_transform()
        self.attention_scores()
        self.weighted_sum()
        self.full_picture()

    # ── 1. 开场 ─────────────────────────────────────────

    def opening(self):
        title = styled_title("Self-Attention", color=ACCENT_BLUE)
        subtitle = styled_subtitle("注意力机制的核心", color=TEXT_SECONDARY)
        group = VGroup(title, subtitle).arrange(DOWN, buff=0.5)
        group.move_to(UP * 0.5)

        self.play(Write(title), run_time=SLOW)
        self.wait(0.5)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=NORMAL)
        self.wait(LONG_PAUSE)

        question = styled_body(
            "一个词如何知道该关注序列中的哪些词?",
            color=ACCENT_YELLOW,
        )
        question.next_to(group, DOWN, buff=1.0)
        self.play(FadeIn(question, shift=UP * 0.3), run_time=NORMAL)
        self.wait(LONG_PAUSE)

        self.transition(title, subtitle, question)

    # ── 2. 直觉 ─────────────────────────────────────────

    def intuition(self):
        step = self.show_step("直觉理解")

        tokens = ["The", "cat", "sat", "on", "the", "mat"]
        token_mobs = VGroup()
        for i, t in enumerate(tokens):
            is_focus = (i == 1)
            box = glow_rect(1.1, 0.6, ACCENT_YELLOW if is_focus else ACCENT_BLUE)
            if not is_focus:
                box.set_fill(opacity=0.12).set_stroke(opacity=0.5)
            label = Text(t, font_size=LABEL_SIZE, color=TEXT_PRIMARY)
            label.move_to(box)
            token_mobs.add(VGroup(box, label))

        token_mobs.arrange(RIGHT, buff=0.25)
        token_mobs.move_to(UP * 1.5)

        self.staggered_fadein(token_mobs, shift=UP * 0.3, lag=0.12)
        self.wait(PAUSE)

        # "cat" 脉冲强调
        self.play(Indicate(token_mobs[1], color=ACCENT_YELLOW, scale_factor=1.15), run_time=NORMAL)

        query_label = styled_small(
            '"cat" 想知道: 谁和我最相关?', color=ACCENT_YELLOW
        )
        query_label.next_to(token_mobs, DOWN, buff=0.6)
        self.play(FadeIn(query_label, shift=UP * 0.2), run_time=NORMAL)
        self.wait(PAUSE)

        # 注意力弧线 — 线粗 = 权重
        weights = [0.05, 1.0, 0.3, 0.1, 0.05, 0.5]
        lines = VGroup()
        cat_bottom = token_mobs[1].get_bottom()

        for i, w in enumerate(weights):
            if i == 1:
                continue
            target = token_mobs[i].get_bottom()
            angle = -0.5 if i < 1 else 0.5
            arc = CurvedArrow(
                cat_bottom + DOWN * 0.15,
                target + DOWN * 0.15,
                color=interpolate_color(ManimColor(STROKE_DIM), ManimColor(ACCENT_YELLOW), w),
                stroke_width=1.5 + w * 5,
                angle=angle,
            )
            lines.add(arc)

        self.staggered_create(lines, lag=0.15)
        self.wait(PAUSE)

        insight = styled_label(
            '每个 token 都会计算对其他 token 的 "注意力权重"',
            color=TEXT_SECONDARY,
        )
        insight.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(insight, shift=UP * 0.2), run_time=NORMAL)
        self.wait(LONG_PAUSE)

        self.clear_step(step)
        self.transition(token_mobs, lines, query_label, insight)

    # ── 3. Q, K, V ──────────────────────────────────────

    def qkv_transform(self):
        step = self.show_step("Step 1: 生成 Q, K, V")

        # 输入
        x_group = VGroup(
            styled_body("输入", color=TEXT_SECONDARY),
            MathTex(r"\vec{x}", font_size=40, color=ACCENT_BLUE),
        ).arrange(DOWN, buff=0.2)
        x_group.move_to(LEFT * 4.5)

        self.play(FadeIn(x_group), run_time=NORMAL)
        self.wait(PAUSE)

        # 三条分支
        branches_data = [
            ("Q", ACCENT_RED, r"W^Q"),
            ("K", ACCENT_GREEN, r"W^K"),
            ("V", ACCENT_PURPLE, r"W^V"),
        ]

        branches = VGroup()
        for name, color, w_tex in branches_data:
            arrow = Arrow(ORIGIN, RIGHT * 2.2, color=color, stroke_width=2.5, buff=0)
            w_label = MathTex(w_tex, font_size=LABEL_SIZE, color=color)
            w_label.next_to(arrow, UP, buff=0.1)
            # 结果用 glow_rect 框住
            result_box = glow_rect(0.8, 0.6, color)
            result_text = Text(name, font_size=30, color=color, weight=BOLD)
            result_text.move_to(result_box)
            result = VGroup(result_box, result_text)
            result.next_to(arrow, RIGHT, buff=0.3)
            branches.add(VGroup(arrow, w_label, result))

        branches.arrange(DOWN, buff=0.6)
        branches.next_to(x_group, RIGHT, buff=1.2)

        # 依次出现
        for b in branches:
            self.play(
                GrowArrow(b[0]), Write(b[1]),
                run_time=NORMAL,
            )
            self.play(FadeIn(b[2], shift=RIGHT * 0.3), run_time=FAST)
        self.wait(PAUSE)

        # 公式
        formula = MathTex(
            r"Q = xW^Q ,\quad K = xW^K ,\quad V = xW^V",
            font_size=30,
        )
        formula.to_edge(DOWN, buff=0.6)
        self.play(Write(formula), run_time=NORMAL)
        self.wait(LONG_PAUSE)

        self.clear_step(step)
        self.transition(x_group, branches, formula)

    # ── 4. 注意力分数 ────────────────────────────────────

    def attention_scores(self):
        step = self.show_step("Step 2: 计算注意力分数")

        # 公式
        formula = MathTex(
            r"\text{score} = \frac{Q \cdot K^T}{\sqrt{d_k}}",
            font_size=38,
        )
        formula.to_edge(UP, buff=0.8)
        self.play(Write(formula), run_time=SLOW)
        self.wait(PAUSE)

        # 解释
        explain = styled_small(
            "除以 sqrt(d_k) 防止点积过大导致 softmax 饱和",
            color=TEXT_SECONDARY,
        )
        explain.next_to(formula, DOWN, buff=0.3)
        self.play(FadeIn(explain, shift=UP * 0.2), run_time=NORMAL)
        self.wait(PAUSE)

        # 热��图
        tokens = ["I", "love", "ML"]
        attn_vals = [
            [0.70, 0.15, 0.15],
            [0.10, 0.55, 0.35],
            [0.15, 0.30, 0.55],
        ]

        heatmap = HeatMap(
            values=attn_vals,
            row_labels=tokens,
            col_labels=tokens,
        )
        heatmap.move_to(DOWN * 0.7)

        # 角标
        q_tag = styled_small("Query", color=ACCENT_RED)
        q_tag.next_to(heatmap.row_labels, UP, buff=0.35)
        q_tag.align_to(heatmap.row_labels, LEFT)
        k_tag = styled_small("Key", color=ACCENT_GREEN)
        k_tag.next_to(heatmap.col_labels, LEFT, buff=0.35)
        k_tag.align_to(heatmap.col_labels, UP)

        self.play(FadeIn(heatmap), run_time=SLOW)
        self.play(FadeIn(q_tag), FadeIn(k_tag), run_time=FAST)
        self.wait(PAUSE)

        # 高亮对角线 + Indicate 强调
        diag = heatmap.get_diagonal_cells()
        diag_rects = VGroup(*[
            SurroundingRectangle(c, color=ACCENT_YELLOW, buff=0.04, stroke_width=2.5)
            for c in diag
        ])

        self.play(
            LaggedStart(*[Create(r) for r in diag_rects], lag_ratio=0.2),
            run_time=NORMAL,
        )
        diag_note = styled_small("对角线较大 -> 每个词都关注自身", color=ACCENT_YELLOW)
        diag_note.next_to(heatmap, RIGHT, buff=0.5)
        self.play(FadeIn(diag_note, shift=LEFT * 0.3), run_time=NORMAL)
        self.wait(LONG_PAUSE)

        self.clear_step(step)
        self.transition(formula, explain, heatmap, q_tag, k_tag, diag_rects, diag_note)

    # ── 5. Softmax + 加权求和 ────────────────────────────

    def weighted_sum(self):
        step = self.show_step("Step 3: Softmax 归一化")

        softmax_f = MathTex(
            r"\alpha_i = \frac{e^{\text{score}_i}}{\sum_j e^{\text{score}_j}}",
            font_size=36,
        )
        softmax_f.move_to(UP * 2.5)
        self.play(Write(softmax_f), run_time=SLOW)
        self.wait(PAUSE)

        # 数值演示
        scores = [2.0, 0.5, 0.5]
        exp_scores = [np.exp(s) for s in scores]
        total = sum(exp_scores)
        sm_vals = [e / total for e in exp_scores]
        tokens = ["I", "love", "ML"]

        # 左: score 柱状图
        score_chart = BarChart(
            scores, labels=tokens,
            bar_width=0.5, max_height=2.0, color=ACCENT_BLUE,
        )
        score_title = styled_label("score", color=TEXT_SECONDARY)
        score_col = VGroup(score_title, score_chart).arrange(DOWN, buff=0.3)
        score_col.move_to(LEFT * 3.5 + DOWN * 0.3)

        self.play(FadeIn(score_col), run_time=NORMAL)
        self.wait(PAUSE)

        # ��: 箭头
        arrow = Arrow(LEFT * 0.8, RIGHT * 0.8, color=ACCENT_YELLOW, stroke_width=3)
        arrow.move_to(DOWN * 0.3)
        arrow_label = styled_label("softmax", color=ACCENT_YELLOW)
        arrow_label.next_to(arrow, UP, buff=0.15)
        self.play(GrowArrow(arrow), FadeIn(arrow_label), run_time=NORMAL)

        # 右: 结果 — 用 glow_rect 框住
        sm_rows = VGroup()
        for token, val in zip(tokens, sm_vals):
            val_box = glow_rect(1.0, 0.4, ACCENT_YELLOW)
            val_text = Text(f"{val:.3f}", font_size=LABEL_SIZE, color=ACCENT_YELLOW)
            val_text.move_to(val_box)
            tk = Text(f"{token}:", font_size=LABEL_SIZE, color=TEXT_SECONDARY)
            row = VGroup(tk, VGroup(val_box, val_text)).arrange(RIGHT, buff=0.2)
            sm_rows.add(row)

        sm_rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        sm_rows.next_to(arrow, RIGHT, buff=1.2)

        self.staggered_fadein(sm_rows, shift=LEFT * 0.3, lag=0.15)
        self.wait(PAUSE)

        # 和为 1
        sum_text = MathTex(r"\sum \alpha_i = 1", font_size=26, color=ACCENT_GREEN)
        sum_text.next_to(sm_rows, DOWN, buff=0.5)
        self.play(Write(sum_text), run_time=NORMAL)
        # Circumscribe 强调
        self.play(Circumscribe(sum_text, color=ACCENT_GREEN, run_time=NORMAL))
        self.wait(LONG_PAUSE)

        self.clear_step(step)
        self.transition(softmax_f, score_col, arrow, arrow_label, sm_rows, sum_text)

    # ── 6. 完整公式 ──────────────────────────────────────

    def full_picture(self):
        step = self.show_step("完整公式")

        full = MathTex(
            r"\text{Attention}(Q,K,V) = \text{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right) V",
            font_size=40,
        )
        full.move_to(UP * 2)
        box = SurroundingRectangle(
            full, color=ACCENT_BLUE, buff=0.3,
            corner_radius=0.12, stroke_width=2.5, fill_opacity=0.06,
        )
        self.play(Write(full), run_time=2.5)
        self.play(Create(box), run_time=NORMAL)
        self.wait(LONG_PAUSE)

        # 流程图
        flow = FlowDiagram([
            ("Input\nEmbed", TEXT_SECONDARY),
            ("Linear\nQ, K, V", ACCENT_BLUE),
            ("Score\nQK/sqrt", ACCENT_YELLOW),
            ("Softmax", ACCENT_YELLOW),
            ("Weighted\nSum V", ACCENT_PURPLE),
            ("Output", ACCENT_GREEN),
        ], box_width=1.4, box_height=0.65)
        flow.move_to(DOWN * 0.3)

        self.staggered_fadein(flow.boxes, shift=UP * 0.2, lag=0.12)
        self.play(
            LaggedStart(*[GrowArrow(a) for a in flow.arrows], lag_ratio=0.12),
            run_time=NORMAL,
        )
        self.wait(PAUSE)

        # 总结
        summary = VGroup(
            styled_label("Q: 我在找什么    K: 我是什么    V: 我能给什��", color=TEXT_SECONDARY),
            styled_label("输出 = softmax(Q . K^T / sqrt(d_k)) x V", color=TEXT_SECONDARY),
        )
        summary.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        summary.next_to(flow, DOWN, buff=0.6)

        self.staggered_fadein(summary, shift=RIGHT * 0.3, lag=0.3)
        self.wait(LONG_PAUSE)

        self.clear_step(step)
