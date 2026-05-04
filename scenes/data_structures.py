"""数据结构可视化动画"""
from manim import *


class BSTScene(Scene):
    """二叉搜索树 (Binary Search Tree) 可视化"""

    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data or [5, 3, 7, 1, 4, 6, 8]
        self.node_radius = 0.35
        self.positions = {}  # val -> position
        self.node_circles = {}  # val -> circle
        self.node_labels = {}  # val -> text
        self.edges = {}  # (parent, child) -> line

    def construct(self):
        title = Text("二叉搜索树 (BST)", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        # BST性质
        prop = Text("性质：左子 < 根 < 右子", font_size=24, color=GRAY)
        prop.next_to(title, DOWN, buff=0.2)
        self.play(Write(prop))

        # 逐个插入
        root = None
        tree = {}  # val -> {'left': val|None, 'right': val|None}

        for val in self.data:
            step_text = Text(f"插入 {val}", font_size=24, color=YELLOW)
            step_text.to_edge(DOWN, buff=0.3)
            self.play(FadeIn(step_text), run_time=0.3)

            if root is None:
                root = val
                tree[val] = {'left': None, 'right': None}
                self._draw_node(val, [0, 2, 0])
            else:
                self._insert_and_animate(root, val, tree, [0, 2, 0], 0)

            self.play(FadeOut(step_text), run_time=0.2)

        self.wait(1)

        # 展示中序遍历
        inorder_title = Text("中序遍历 (得到有序序列):", font_size=24, color=GREEN)
        inorder_title.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(inorder_title))

        sorted_vals = sorted(self.data)
        result = Text(" → ".join(str(v) for v in sorted_vals), font_size=28, color=GREEN)
        result.next_to(inorder_title, DOWN, buff=0.2)
        self.play(Write(result))
        self.wait(1.5)

    def _draw_node(self, val, pos):
        """绘制一个节点"""
        circle = Circle(radius=self.node_radius, color=BLUE, fill_opacity=0.3)
        circle.move_to(pos)
        label = Text(str(val), font_size=22, color=WHITE)
        label.move_to(pos)

        self.positions[val] = pos
        self.node_circles[val] = circle
        self.node_labels[val] = label

        self.play(GrowFromCenter(circle), Write(label), run_time=0.4)

    def _insert_and_animate(self, current, val, tree, pos, depth):
        """递归插入并动画化路径"""
        # 高亮当前节点（比较过程）
        self.play(
            self.node_circles[current].animate.set_stroke(YELLOW, width=3),
            run_time=0.2,
        )

        h_offset = 2.5 / (depth + 1)  # 越深越窄
        v_offset = 1.2

        if val < current:
            # 去左子树
            if tree[current]['left'] is None:
                tree[current]['left'] = val
                tree[val] = {'left': None, 'right': None}
                new_pos = [pos[0] - h_offset, pos[1] - v_offset, 0]
                # 画边
                edge = Line(
                    self.positions[current] + DOWN * self.node_radius,
                    new_pos + UP * self.node_radius,
                    color=GRAY,
                )
                self.edges[(current, val)] = edge
                self.play(Create(edge), run_time=0.2)
                self._draw_node(val, new_pos)
            else:
                left_pos = self.positions[tree[current]['left']]
                self._insert_and_animate(tree[current]['left'], val, tree, left_pos, depth + 1)
        else:
            # 去右子树
            if tree[current]['right'] is None:
                tree[current]['right'] = val
                tree[val] = {'left': None, 'right': None}
                new_pos = [pos[0] + h_offset, pos[1] - v_offset, 0]
                edge = Line(
                    self.positions[current] + DOWN * self.node_radius,
                    new_pos + UP * self.node_radius,
                    color=GRAY,
                )
                self.edges[(current, val)] = edge
                self.play(Create(edge), run_time=0.2)
                self._draw_node(val, new_pos)
            else:
                right_pos = self.positions[tree[current]['right']]
                self._insert_and_animate(tree[current]['right'], val, tree, right_pos, depth + 1)

        # 恢复颜色
        self.play(
            self.node_circles[current].animate.set_stroke(BLUE, width=2),
            run_time=0.1,
        )


class LinkedListScene(Scene):
    """链表操作可视化"""

    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data or [1, 3, 5, 7, 9]

    def construct(self):
        title = Text("单链表 (Singly Linked List)", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        nodes = VGroup()
        arrows = VGroup()
        node_rects = []
        node_labels = []

        # 创建链表
        start_x = -5
        for i, val in enumerate(self.data):
            # 节点框
            rect = RoundedRectangle(
                width=1.0, height=0.7, corner_radius=0.1,
                color=BLUE, fill_opacity=0.3,
            )
            rect.move_to([start_x + i * 1.8, 0.5, 0])
            label = Text(str(val), font_size=24, color=WHITE)
            label.move_to(rect.get_center())
            node_rects.append(rect)
            node_labels.append(label)
            nodes.add(VGroup(rect, label))

            # 箭头
            if i < len(self.data) - 1:
                arrow = Arrow(
                    rect.get_right(), rect.get_right() + RIGHT * 0.8,
                    buff=0, color=GRAY, stroke_width=2, max_tip_length_to_length_ratio=0.3,
                )
                arrows.add(arrow)

        # NULL 标记
        null_text = Text("NULL", font_size=18, color=RED)
        null_text.next_to(node_rects[-1], RIGHT, buff=0.5)

        # head 指针
        head_arrow = Arrow(UP * 0.8, DOWN * 0.1, color=GREEN, stroke_width=2)
        head_arrow.next_to(node_rects[0], UP, buff=0.05)
        head_label = Text("head", font_size=20, color=GREEN)
        head_label.next_to(head_arrow, UP, buff=0.05)

        self.play(
            *[GrowFromCenter(n) for n in nodes],
            *[GrowArrow(a) for a in arrows],
            FadeIn(null_text), GrowArrow(head_arrow), Write(head_label),
            run_time=1.5,
        )
        self.wait(0.5)

        # 演示：在位置 2 插入 4
        insert_text = Text("插入节点: 在位置 2 插入 4", font_size=24, color=YELLOW)
        insert_text.to_edge(DOWN, buff=0.8)
        self.play(Write(insert_text))

        # 新节点从上方出现
        new_rect = RoundedRectangle(
            width=1.0, height=0.7, corner_radius=0.1,
            color=YELLOW, fill_opacity=0.5,
        )
        new_rect.move_to([start_x + 2 * 1.8, 2, 0])
        new_label = Text("4", font_size=24, color=WHITE)
        new_label.move_to(new_rect.get_center())

        self.play(GrowFromCenter(new_rect), Write(new_label), run_time=0.5)

        # 指针遍历到位置 1
        for i in range(2):
            self.play(
                node_rects[i].animate.set_stroke(YELLOW, width=3),
                run_time=0.3,
            )
            self.play(
                node_rects[i].animate.set_stroke(BLUE, width=2),
                run_time=0.2,
            )

        # 新节点下移并连接
        target_pos = [start_x + 2 * 1.8, 0.5, 0]
        self.play(
            new_rect.animate.move_to(target_pos),
            new_label.animate.move_to(target_pos),
            run_time=0.5,
        )

        done_text = Text("插入完成! 链表: 1→3→4→5→7→9", font_size=24, color=GREEN)
        done_text.next_to(insert_text, DOWN, buff=0.3)
        self.play(Write(done_text))
        self.wait(1.5)


class HashTableScene(Scene):
    """哈希表可视化"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def construct(self):
        title = Text("哈希表 (Hash Table)", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        formula = MathTex(r"\text{index} = \text{hash}(\text{key}) \% \text{size}", font_size=30)
        formula.next_to(title, DOWN, buff=0.3)
        self.play(Write(formula))

        # 画表格（8个槽位）
        table_size = 8
        slots = VGroup()
        slot_labels = VGroup()
        start_y = 1.5

        for i in range(table_size):
            rect = Rectangle(width=2.5, height=0.6, color=BLUE_D, fill_opacity=0.1)
            rect.move_to([-1, start_y - i * 0.7, 0])
            idx = Text(f"[{i}]", font_size=18, color=GRAY)
            idx.next_to(rect, LEFT, buff=0.2)
            slots.add(rect)
            slot_labels.add(idx)

        self.play(*[Create(s) for s in slots], *[Write(l) for l in slot_labels], run_time=1)

        # 插入键值对
        pairs = [("name", "张业成"), ("age", "25"), ("city", "北京"), ("univ", "北大")]

        for key, val in pairs:
            # 计算哈希
            hash_val = hash(key) % table_size
            display_hash = abs(hash(key)) % table_size  # 保证正数

            step = Text(f'hash("{key}") % {table_size} = {display_hash}', font_size=22, color=YELLOW)
            step.to_edge(RIGHT, buff=0.5).shift(UP * 2)
            self.play(Write(step), run_time=0.4)

            # 高亮目标槽位
            self.play(slots[display_hash].animate.set_fill(YELLOW, opacity=0.3), run_time=0.3)

            # 写入值
            entry = Text(f'"{key}": "{val}"', font_size=16, color=WHITE)
            entry.move_to(slots[display_hash].get_center())
            self.play(Write(entry), run_time=0.3)

            self.play(
                slots[display_hash].animate.set_fill(GREEN, opacity=0.15),
                FadeOut(step),
                run_time=0.3,
            )

        # O(1) 查找演示
        lookup = Text('查找: table["city"] → O(1)', font_size=24, color=GREEN)
        lookup.to_edge(DOWN, buff=0.5)
        self.play(Write(lookup))
        self.wait(1.5)


class StackQueueScene(Scene):
    """栈和队列对比可视化"""

    def construct(self):
        title = Text("栈 vs 队列", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        # 左边：栈
        stack_title = Text("栈 (Stack) — LIFO", font_size=24, color=ORANGE)
        stack_title.move_to([-3.5, 2.2, 0])
        self.play(Write(stack_title))

        # 右边：队列
        queue_title = Text("队列 (Queue) — FIFO", font_size=24, color=TEAL)
        queue_title.move_to([3.5, 2.2, 0])
        self.play(Write(queue_title))

        # 栈：竖直叠放
        stack_items = []
        stack_base_y = -1.5
        for i, val in enumerate([3, 7, 1, 5]):
            rect = RoundedRectangle(width=2, height=0.55, corner_radius=0.08,
                                     color=ORANGE, fill_opacity=0.3)
            rect.move_to([-3.5, stack_base_y + i * 0.65, 0])
            label = Text(str(val), font_size=22, color=WHITE).move_to(rect)
            group = VGroup(rect, label)
            stack_items.append(group)
            self.play(FadeIn(group, shift=UP * 0.3), run_time=0.3)

        # 栈 push/pop 演示
        top_arrow = Arrow(LEFT * 0.3, RIGHT * 0.3, color=RED, stroke_width=2)
        top_arrow.next_to(stack_items[-1], LEFT, buff=0.2)
        top_label = Text("top", font_size=18, color=RED).next_to(top_arrow, LEFT, buff=0.1)
        self.play(GrowArrow(top_arrow), Write(top_label))

        pop_text = Text("pop() → 5", font_size=20, color=YELLOW)
        pop_text.move_to([-3.5, -2.5, 0])
        self.play(Write(pop_text), FadeOut(stack_items[-1], shift=UP), run_time=0.5)
        self.play(
            top_arrow.animate.next_to(stack_items[-2], LEFT, buff=0.2),
            top_label.animate.next_to(top_arrow, LEFT, buff=0.1),
            run_time=0.3,
        )

        # 队列：水平排列
        queue_items = []
        queue_base_x = 2
        for i, val in enumerate([3, 7, 1, 5]):
            rect = RoundedRectangle(width=0.8, height=1.5, corner_radius=0.08,
                                     color=TEAL, fill_opacity=0.3)
            rect.move_to([queue_base_x + i * 1.0, 0, 0])
            label = Text(str(val), font_size=22, color=WHITE).move_to(rect)
            group = VGroup(rect, label)
            queue_items.append(group)
            self.play(FadeIn(group, shift=LEFT * 0.3), run_time=0.3)

        # 队列 dequeue
        deq_text = Text("dequeue() → 3", font_size=20, color=YELLOW)
        deq_text.move_to([3.5, -2.5, 0])
        self.play(Write(deq_text), FadeOut(queue_items[0], shift=LEFT), run_time=0.5)

        self.wait(1.5)
