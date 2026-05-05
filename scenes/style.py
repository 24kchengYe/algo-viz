"""
3Blue1Brown / 漫士沉思录 风格 — 全局配置 + 布局工具 v3

核心升级:
1. MovingCameraScene 基类 — 支持 zoom in/out 引导注意力
2. 安全边距系统 — 所有元素 buff>=0.5 不溢出
3. auto_fit — 自动缩放相机适应内容
4. 透明度三层制 — 主 1.0 / 上下文 0.4 / 结构 0.15
5. 动画时间表 — 标题1.5s/公式2.0s/标注0.8s/aha moment 2.5s
6. 呼吸脉冲 — 静止元素可加 subtle_pulse
7. 中文适配 — Text 默认限宽，超长自动缩小
"""
from manim import *
import numpy as np


# ═══════════════════════════════════════════════════════
# 配色 — 3B1B Classic
# ═══════════════════════════════════════════════════════
BG_COLOR = "#1C1C1C"

ACCENT_BLUE = "#58C4DD"
ACCENT_YELLOW = "#FFFF00"
ACCENT_GREEN = "#83C167"
ACCENT_RED = "#FC6255"
ACCENT_PINK = "#E48080"
ACCENT_ORANGE = "#FF8C00"
ACCENT_PURPLE = "#9A72AC"
ACCENT_TEAL = "#5CD0B3"

TEXT_PRIMARY = "#EEEEEE"
TEXT_SECONDARY = "#888888"
TEXT_DIM = "#555555"
STROKE_LIGHT = "#AAAAAA"
STROKE_DIM = "#444444"

# 语义配色规则 (写场景时参考)
# BLUE   = 主要元素、默认、"这是什么"
# YELLOW = 高亮、强调、"注意看这里"
# GREEN  = 正确、完成、正面结论
# RED    = 关键、基准、需要注意
# PURPLE = Value/辅助概念
# TEAL   = 次要分组、"小于"
# ORANGE = 警告、"大于"

# ═══════════════════════════════════════════════════════
# 字号
# ═══════════════════════════════════════════════════════
TITLE_SIZE = 48
SUBTITLE_SIZE = 32
BODY_SIZE = 28
LABEL_SIZE = 24
SMALL_SIZE = 20
TINY_SIZE = 16

# ═══════════════════════════════════════════════════════
# 动画时间表 — 参考 3B1B + Hermes 规范
#
# 原则: "Breathing room" — 每个动画后必须 wait
# ═══════════════════════════════════════════════════════
T_LABEL = 0.5        # 小标注出现
T_NORMAL = 1.0       # 常规动画
T_KEY = 1.5          # 关键变换 (公式出现、重要转换)
T_TITLE = 1.8        # 标题 Write
T_AHA = 2.5          # "aha moment" 重要公式

W_BRIEF = 0.5        # 短暂停顿
W_STEP = 1.0         # 步骤间
W_THINK = 1.5        # 需要消化
W_AHA = 2.5          # 重要时刻后

# 兼容旧代码的别名
FAST = T_LABEL
NORMAL = T_NORMAL
SLOW = T_KEY
PAUSE = W_STEP


# ═══════════════════════════════════════════════════════
# 高级动画工具
#
# rate_func 选用指南:
#   smooth          — 大部分动画（默认，自然感）
#   linear          — 匀速运动（机械/精确）
#   ease_out_back   — 弹性出场（超调后回弹，元素出现时活泼）
#   ease_out_bounce — 弹跳落地（适合"掉下来"的效果）
#   rush_into       — 慢→快（加速离开）
#   rush_from       — 快→慢（减速到达）
#   there_and_back  — 去了又回来（临时强调）
#   double_smooth   — 更柔和的 smooth
# ═══════════════════════════════════════════════════════

def make_bezier_rate_func(p1x, p1y, p2x, p2y):
    """创建自定义贝塞尔缓动函数 (类似 CSS cubic-bezier)

    用法:
        my_ease = make_bezier_rate_func(0.34, 1.56, 0.64, 1)  # 弹性
        self.play(mob.animate.shift(RIGHT), rate_func=my_ease)
    """
    def bezier_rate(t):
        # 简化版三次贝塞尔 (Newton-Raphson 求 t 对应的 x)
        # B(t) = 3(1-t)^2*t*P1 + 3(1-t)*t^2*P2 + t^3
        u = t  # 初始猜测
        for _ in range(8):
            x = 3 * (1 - u) ** 2 * u * p1x + 3 * (1 - u) * u ** 2 * p2x + u ** 3
            dx = 3 * (1 - u) ** 2 * p1x + 6 * (1 - u) * u * (p2x - p1x) + 3 * u ** 2 * (1 - p2x)
            if abs(dx) < 1e-10:
                break
            u -= (x - t) / dx
            u = max(0, min(1, u))
        y = 3 * (1 - u) ** 2 * u * p1y + 3 * (1 - u) * u ** 2 * p2y + u ** 3
        return y
    return bezier_rate


# 预制的高级缓动
EASE_SPRING = make_bezier_rate_func(0.34, 1.56, 0.64, 1)    # 弹簧感(超调回弹)
EASE_SNAP = make_bezier_rate_func(0.5, 0, 0.1, 1)           # 快速卡入(干脆利落)
EASE_GENTLE = make_bezier_rate_func(0.4, 0, 0.2, 1)         # 极柔和
LONG_PAUSE = W_THINK

# ═══════════════════════════════════════════════════════
# 安全边距
# ═══════════════════════════════════════════════════════
SAFE_MARGIN = 0.5     # 元素到屏幕边缘最小距离
SAFE_WIDTH = 12.5     # 安全区宽度 (14.2 - 2*0.5 - 余量)
SAFE_HEIGHT = 7.0     # 安全区高度 (8 - 2*0.5)

# ═══════════════════════════════════════════════════════
# 透明度分层
# ═══════════════════════════════════════════════════════
OP_PRIMARY = 0.9      # 主要元素
OP_CONTEXT = 0.4      # 上下文/已完成
OP_STRUCTURE = 0.15   # 网格线/辅助线/背景结构


# ═══════════════════════════════════════════════════════
# 文字工厂 — 带安全限宽
# ═══════════════════════════════════════════════════════

def _safe_text(text, font_size, color, weight=None, max_width=SAFE_WIDTH):
    """创建文字，如果超宽则自动缩小"""
    if weight:
        t = Text(text, font_size=font_size, color=color, weight=weight)
    else:
        t = Text(text, font_size=font_size, color=color)
    if t.get_width() > max_width:
        t.scale(max_width / t.get_width())
    return t


def styled_title(text, color=ACCENT_BLUE):
    return _safe_text(text, TITLE_SIZE, color, weight=BOLD)

def styled_subtitle(text, color=TEXT_SECONDARY):
    return _safe_text(text, SUBTITLE_SIZE, color)

def styled_body(text, color=TEXT_PRIMARY):
    return _safe_text(text, BODY_SIZE, color)

def styled_label(text, color=TEXT_SECONDARY):
    return _safe_text(text, LABEL_SIZE, color)

def styled_small(text, color=TEXT_DIM):
    return _safe_text(text, SMALL_SIZE, color)

def styled_formula(latex, font_size=38):
    f = MathTex(latex, font_size=font_size)
    if f.get_width() > SAFE_WIDTH:
        f.scale(SAFE_WIDTH / f.get_width())
    return f


# ═══════════════════════════════════════════════════════
# 视觉组件
# ═══════════════════════════════════════════════════════

def glow_rect(width, height, color, corner_radius=0.1, fill_opacity=0.2):
    """发光感圆角矩形"""
    return RoundedRectangle(
        width=width, height=height,
        corner_radius=corner_radius,
        fill_color=color, fill_opacity=fill_opacity,
        stroke_color=color, stroke_width=2.5, stroke_opacity=0.9,
    )

def dim_rect(width, height, color=STROKE_DIM, corner_radius=0.08):
    """结构层矩形 (opacity 0.15)"""
    return RoundedRectangle(
        width=width, height=height,
        corner_radius=corner_radius,
        fill_color=color, fill_opacity=0.06,
        stroke_color=color, stroke_width=1, stroke_opacity=0.25,
    )


# ═══════════════════════════════════════════════════════
# BarChart
# ═══════════════════════════════════════════════════════

class BarChart(VGroup):
    """自适应柱状图"""

    def __init__(
        self, data, labels=None,
        bar_width=0.6, max_height=3.8, gap=0.15,
        color=ACCENT_BLUE, fill_opacity=0.7,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.data = list(data)
        self.bar_width = bar_width
        self.max_height = max_height
        self.gap = gap
        self.default_color = color
        self.default_opacity = fill_opacity
        self.max_val = max(self.data) if self.data else 1

        self.bar_group = VGroup()
        self.label_group = VGroup()

        for i, val in enumerate(self.data):
            h = max((val / self.max_val) * self.max_height, 0.2)
            bar = RoundedRectangle(
                width=self.bar_width, height=h, corner_radius=0.07,
                fill_color=color, fill_opacity=fill_opacity,
                stroke_color=color, stroke_width=2, stroke_opacity=0.9,
            )
            self.bar_group.add(bar)

            lbl_text = str(val) if labels is None else str(labels[i])
            label = Text(lbl_text, font_size=LABEL_SIZE, color=TEXT_PRIMARY, weight=BOLD)
            self.label_group.add(label)

        self.bar_group.arrange(RIGHT, buff=self.gap, aligned_edge=DOWN)
        for bar, label in zip(self.bar_group, self.label_group):
            label.next_to(bar, UP, buff=0.12)

        total_w = self.bar_group.get_width() + 0.6
        base_y = self.bar_group.get_bottom()[1]
        self.baseline = Line(
            LEFT * total_w / 2, RIGHT * total_w / 2,
            color=STROKE_DIM, stroke_width=2, stroke_opacity=0.4,
        )
        self.baseline.move_to([self.bar_group.get_center()[0], base_y, 0])
        self.add(self.baseline, self.bar_group, self.label_group)

        # 超宽则自动缩放
        if self.get_width() > SAFE_WIDTH:
            self.scale(SAFE_WIDTH / self.get_width())

    def highlight(self, i, color, opacity=0.85):
        return self.bar_group[i].animate.set_fill(color, opacity=opacity).set_stroke(color)

    def reset_color(self, i):
        return self.bar_group[i].animate.set_fill(
            self.default_color, opacity=self.default_opacity
        ).set_stroke(self.default_color)

    def swap_anims(self, i, j):
        bar_i, bar_j = self.bar_group[i], self.bar_group[j]
        lbl_i, lbl_j = self.label_group[i], self.label_group[j]
        x_i, x_j = bar_i.get_center()[0], bar_j.get_center()[0]
        bot = bar_i.get_bottom()[1]
        h_i, h_j = bar_i.get_height(), bar_j.get_height()
        self.data[i], self.data[j] = self.data[j], self.data[i]
        anims = [
            bar_i.animate(path_arc=PI / 3).move_to([x_j, bot + h_i / 2, 0]),
            bar_j.animate(path_arc=PI / 3).move_to([x_i, bot + h_j / 2, 0]),
            lbl_i.animate(path_arc=PI / 3).move_to([x_j, bot + h_i + 0.12, 0]),
            lbl_j.animate(path_arc=PI / 3).move_to([x_i, bot + h_j + 0.12, 0]),
        ]
        self.bar_group[i], self.bar_group[j] = self.bar_group[j], self.bar_group[i]
        self.label_group[i], self.label_group[j] = self.label_group[j], self.label_group[i]
        return anims


# ═══════════════════════════════════════════════════════
# HeatMap
# ═══════════════════════════════════════════════════════

class HeatMap(VGroup):
    """热力图"""

    def __init__(
        self, values, row_labels=None, col_labels=None,
        cell_size=0.85, low_color=BG_COLOR, high_color=ACCENT_BLUE,
        font_size=SMALL_SIZE, label_font_size=LABEL_SIZE,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.values = np.array(values)
        rows, cols = self.values.shape

        self.cells = VGroup()
        for i in range(rows):
            for j in range(cols):
                val = self.values[i][j]
                cell = Square(side_length=cell_size * 0.92)
                intensity = min(val * 1.3, 1.0)
                cell.set_fill(
                    interpolate_color(ManimColor(low_color), ManimColor(high_color), intensity),
                    opacity=0.85,
                )
                cell.set_stroke(STROKE_LIGHT, width=0.8, opacity=0.25)
                num = Text(f"{val:.2f}", font_size=font_size, color=TEXT_PRIMARY)
                num.move_to(cell)
                self.cells.add(VGroup(cell, num))

        self.cells.arrange_in_grid(rows=rows, cols=cols, buff=cell_size * 0.08)
        self.add(self.cells)

        if col_labels:
            self.col_labels = VGroup()
            for j, text in enumerate(col_labels):
                lbl = Text(text, font_size=label_font_size, color=ACCENT_GREEN)
                lbl.next_to(self.cells[j], UP, buff=0.18)
                self.col_labels.add(lbl)
            self.add(self.col_labels)

        if row_labels:
            self.row_labels = VGroup()
            for i, text in enumerate(row_labels):
                lbl = Text(text, font_size=label_font_size, color=ACCENT_RED)
                lbl.next_to(self.cells[i * cols], LEFT, buff=0.18)
                self.row_labels.add(lbl)
            self.add(self.row_labels)

        # 超宽超高则缩放
        if self.get_width() > SAFE_WIDTH * 0.7:
            self.scale(SAFE_WIDTH * 0.7 / self.get_width())

    def get_cell(self, row, col):
        cols = self.values.shape[1]
        return self.cells[row * cols + col]

    def get_diagonal_cells(self):
        n = min(self.values.shape)
        cols = self.values.shape[1]
        return VGroup(*[self.cells[i * cols + i] for i in range(n)])


# ═══════════════════════════════════════════════════════
# FlowDiagram
# ═══════════════════════════════════════════════════════

class FlowDiagram(VGroup):
    """流程图"""

    def __init__(self, items, box_width=1.5, box_height=0.7, buff=0.35, **kwargs):
        super().__init__(**kwargs)
        self.boxes = VGroup()
        self.arrows = VGroup()

        for text, color in items:
            box = glow_rect(box_width, box_height, color)
            label = Text(text, font_size=TINY_SIZE + 2, color=color)
            if label.get_width() > box_width - 0.2:
                label.scale((box_width - 0.2) / label.get_width())
            label.move_to(box)
            self.boxes.add(VGroup(box, label))

        self.boxes.arrange(RIGHT, buff=buff)

        # 超宽自动缩放
        if self.boxes.get_width() > SAFE_WIDTH:
            self.boxes.scale(SAFE_WIDTH / self.boxes.get_width())

        for i in range(len(self.boxes) - 1):
            arrow = Arrow(
                self.boxes[i].get_right(), self.boxes[i + 1].get_left(),
                color=STROKE_LIGHT, stroke_width=1.5, buff=0.05,
                max_tip_length_to_length_ratio=0.3,
            )
            self.arrows.add(arrow)

        self.add(self.boxes, self.arrows)


# ═══════════════════════════════════════════════════════
# 基础场景类 — MovingCameraScene
# ═══════════════════════════════════════════════════════

class StyledScene(MovingCameraScene):
    """
    3B1B 风格基础场景

    新增能力:
    - self.zoom_in(mob, scale=0.5)  聚焦到某个元素
    - self.zoom_out()               恢复全局视角
    - self.auto_fit(group)          自动缩放相机适应一组元素
    - self.subtle_pulse(mob)        微妙脉冲（静止元素的呼吸感）
    - self.flash_highlight(mob)     闪光强调
    """

    def setup(self):
        super().setup()
        self.camera.background_color = BG_COLOR
        self.camera.frame.save_state()

    # ── 相机运动 ──────────────────────────────────────

    def zoom_in(self, mob, scale=0.5, run_time=T_KEY):
        """聚焦到某个元素"""
        self.play(
            self.camera.frame.animate.scale(scale).move_to(mob),
            rate_func=smooth,
            run_time=run_time,
        )

    def zoom_out(self, run_time=T_NORMAL):
        """恢复全局视角"""
        self.play(Restore(self.camera.frame), rate_func=smooth, run_time=run_time)

    def auto_fit(self, group, margin=0.8, run_time=T_NORMAL):
        """自动缩放相机适应一组元素"""
        target_w = group.get_width() + margin * 2
        target_h = group.get_height() + margin * 2
        frame_w = self.camera.frame.get_width()
        frame_h = self.camera.frame.get_height()
        scale = max(target_w / frame_w, target_h / frame_h, 1.0)
        self.play(
            self.camera.frame.animate.scale(scale).move_to(group),
            rate_func=smooth,
            run_time=run_time,
        )

    # ── 视觉强调 ──────────────────────────────────────

    def subtle_pulse(self, mob, scale=1.05, color=None):
        """微妙脉冲 — 静止元素的呼吸感"""
        if color:
            self.play(
                mob.animate.scale(scale).set_color(color),
                rate_func=there_and_back,
                run_time=0.8,
            )
        else:
            self.play(
                mob.animate.scale(scale),
                rate_func=there_and_back,
                run_time=0.8,
            )

    def flash_highlight(self, mob, color=ACCENT_YELLOW):
        """闪光强调 — 画圈 + Indicate"""
        self.play(
            Circumscribe(mob, color=color, buff=0.08, run_time=T_NORMAL),
        )

    def indicate(self, mob, color=ACCENT_YELLOW, scale=1.15):
        """脉冲强调"""
        self.play(Indicate(mob, color=color, scale_factor=scale), run_time=T_NORMAL)

    # ── 字幕 ──────────────────────────────────────────

    def caption(self, text, duration=2):
        """添加字幕 (渲染后生成 .srt 文件)"""
        self.add_subcaption(text, duration=duration)

    # ── 叙事工具 ──────────────────────────────────────

    def show_title(self, title_text, subtitle_text=None):
        title = styled_title(title_text)
        title.to_edge(UP, buff=SAFE_MARGIN + 0.3)
        self.play(Write(title), run_time=T_TITLE)

        subtitle = None
        if subtitle_text:
            subtitle = styled_subtitle(subtitle_text)
            subtitle.next_to(title, DOWN, buff=0.4)
            self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=T_NORMAL)

        self.wait(W_STEP)
        return (title, subtitle) if subtitle else (title,)

    def show_step(self, step_text):
        step = styled_body(step_text, color=ACCENT_YELLOW)
        step.to_corner(UL, buff=SAFE_MARGIN)
        self.play(FadeIn(step, shift=RIGHT * 0.3), run_time=T_LABEL)
        return step

    def clear_step(self, step_mob):
        self.play(FadeOut(step_mob, shift=LEFT * 0.3), run_time=T_LABEL)

    def show_formula(self, latex, position=ORIGIN, explain=None):
        formula = styled_formula(latex)
        formula.move_to(position)
        bg = SurroundingRectangle(
            formula, color=ACCENT_BLUE, buff=0.3,
            corner_radius=0.12, stroke_width=1.5, fill_opacity=0.05,
        )
        group = VGroup(bg, formula)
        self.play(FadeIn(bg, run_time=T_LABEL), Write(formula, run_time=T_AHA))
        self.wait(W_THINK)
        if explain:
            exp = styled_small(explain, color=TEXT_SECONDARY)
            exp.next_to(group, DOWN, buff=0.35)
            self.play(FadeIn(exp, shift=UP * 0.2), run_time=T_NORMAL)
            group.add(exp)
        return group

    # ── 批量动画 ──────────────────────────────────────

    def transition(self, *mobs):
        targets = mobs if mobs else self.mobjects
        anims = [FadeOut(m, shift=DOWN * 0.3) for m in targets if m is not None]
        if anims:
            self.play(*anims, run_time=T_NORMAL)

    def staggered_fadein(self, group, shift=UP * 0.3, lag=0.12):
        self.play(
            LaggedStart(*[FadeIn(m, shift=shift) for m in group], lag_ratio=lag),
            run_time=T_KEY,
        )

    def staggered_create(self, group, lag=0.1):
        self.play(
            LaggedStart(*[Create(m) for m in group], lag_ratio=lag),
            run_time=T_KEY,
        )

    def staggered_write(self, group, lag=0.15):
        self.play(
            LaggedStart(*[Write(m) for m in group], lag_ratio=lag),
            run_time=T_KEY,
        )

    # ── 高级动画 ──────────────────────────────────────

    def bounce_in(self, mob, shift_from=UP * 1.5):
        """弹性入场 — ease_out_back (超调后回弹)"""
        mob.shift(shift_from)
        self.play(
            mob.animate.shift(-shift_from),
            rate_func=ease_out_back,
            run_time=T_KEY,
        )

    def snap_in(self, mob):
        """干脆利落入场 — 从 0.3x 放大到 1x"""
        mob.scale(0.3).set_opacity(0)
        self.play(
            mob.animate.scale(1 / 0.3).set_opacity(1),
            rate_func=EASE_SNAP,
            run_time=T_NORMAL,
        )

    def arc_move(self, mob, target_pos, arc_angle=PI / 3, run_time=T_KEY):
        """弧形移动 — 比直线移动更有动感"""
        self.play(
            mob.animate(path_arc=arc_angle).move_to(target_pos),
            rate_func=smooth,
            run_time=run_time,
        )

    def morph(self, source, target, run_time=T_KEY):
        """平滑变形 — ReplacementTransform + 弧线"""
        self.play(
            ReplacementTransform(source, target, path_arc=PI / 4),
            run_time=run_time,
        )

    def wave_highlight(self, group, color=ACCENT_YELLOW):
        """波浪式高亮 — 逐个 Indicate"""
        self.play(
            LaggedStart(
                *[Indicate(m, color=color, scale_factor=1.1) for m in group],
                lag_ratio=0.08,
            ),
            run_time=T_KEY,
        )

    def typewriter(self, text_mob, run_time=None):
        """打字机效果 — 仅限 Text 对象"""
        rt = run_time or max(0.5, len(text_mob.text) * 0.05)
        self.play(AddTextLetterByLetter(text_mob, time_per_char=0.05), run_time=rt)

    def focus_then_restore(self, mob, scale=0.5, hold=W_THINK):
        """聚焦 → 停留 → 恢复 (三段式)"""
        self.zoom_in(mob, scale=scale)
        self.wait(hold)
        self.zoom_out()

    def sequence(self, *anim_funcs):
        """顺序执行多个动画函数 (每个之间有 W_BRIEF 间隔)"""
        for fn in anim_funcs:
            fn()
            self.wait(W_BRIEF)
