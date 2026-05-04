"""图算法可视化动画"""
from manim import *
import heapq


class BFSScene(Scene):
    """广度优先搜索 (BFS) 可视化"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 图的邻接表
        self.graph_data = {
            0: [1, 2],
            1: [0, 3, 4],
            2: [0, 4],
            3: [1, 5],
            4: [1, 2, 5],
            5: [3, 4],
        }
        # 节点位置（手动布局）
        self.node_positions = {
            0: [-3, 1, 0],
            1: [-1, 2, 0],
            2: [-1, 0, 0],
            3: [1, 2, 0],
            4: [1, 0, 0],
            5: [3, 1, 0],
        }

    def construct(self):
        title = Text("广度优先搜索 (BFS)", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        idea = Text("策略：逐层探索，用队列 (Queue) 管理", font_size=22, color=GRAY)
        idea.next_to(title, DOWN, buff=0.2)
        self.play(Write(idea))

        complexity = MathTex(r"O(V + E)", font_size=28, color=YELLOW)
        complexity.to_corner(UR, buff=0.5)
        self.play(Write(complexity))

        # 画图
        nodes = {}
        node_labels = {}
        edges = {}

        for v, pos in self.node_positions.items():
            circle = Circle(radius=0.35, color=BLUE, fill_opacity=0.2)
            circle.move_to(pos)
            label = Text(str(v), font_size=22, color=WHITE).move_to(pos)
            nodes[v] = circle
            node_labels[v] = label

        for v, neighbors in self.graph_data.items():
            for u in neighbors:
                if (u, v) not in edges and (v, u) not in edges:
                    edge = Line(
                        self.node_positions[v], self.node_positions[u],
                        color=GRAY, stroke_width=2, stroke_opacity=0.5,
                    )
                    edges[(v, u)] = edge

        self.play(
            *[Create(e) for e in edges.values()],
            *[GrowFromCenter(n) for n in nodes.values()],
            *[Write(l) for l in node_labels.values()],
            run_time=1,
        )

        # BFS 动画
        start = 0
        visited = set()
        queue = [start]
        visited.add(start)
        order = []

        # 队列可视化
        queue_label = Text("Queue:", font_size=20, color=TEAL)
        queue_label.move_to([-5, -2.5, 0])
        self.play(Write(queue_label))

        queue_display = VGroup()
        queue_display.next_to(queue_label, RIGHT, buff=0.2)

        # 起点
        self.play(nodes[start].animate.set_fill(GREEN, opacity=0.8), run_time=0.3)

        while queue:
            current = queue.pop(0)
            order.append(current)

            # 高亮当前处理节点
            self.play(nodes[current].animate.set_fill(RED, opacity=0.8), run_time=0.3)

            for neighbor in self.graph_data[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    # 高亮发现的边和节点
                    edge_key = (current, neighbor) if (current, neighbor) in edges else (neighbor, current)
                    self.play(
                        edges[edge_key].animate.set_color(YELLOW).set_stroke(width=3),
                        nodes[neighbor].animate.set_fill(YELLOW, opacity=0.6),
                        run_time=0.3,
                    )

            # 标记为已完成
            self.play(nodes[current].animate.set_fill(GREEN, opacity=0.6), run_time=0.2)

        # 遍历顺序
        order_text = Text(f"遍历顺序: {' → '.join(str(v) for v in order)}",
                          font_size=24, color=GREEN)
        order_text.to_edge(DOWN, buff=0.3)
        self.play(Write(order_text))
        self.wait(1.5)


class DFSScene(Scene):
    """深度优先搜索 (DFS) 可视化"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.graph_data = {
            0: [1, 2],
            1: [0, 3, 4],
            2: [0, 4],
            3: [1, 5],
            4: [1, 2, 5],
            5: [3, 4],
        }
        self.node_positions = {
            0: [-3, 1, 0],
            1: [-1, 2, 0],
            2: [-1, 0, 0],
            3: [1, 2, 0],
            4: [1, 0, 0],
            5: [3, 1, 0],
        }

    def construct(self):
        title = Text("深度优先搜索 (DFS)", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        idea = Text("策略：一条路走到底，走不通再回溯，用栈 (Stack)", font_size=22, color=GRAY)
        idea.next_to(title, DOWN, buff=0.2)
        self.play(Write(idea))

        complexity = MathTex(r"O(V + E)", font_size=28, color=YELLOW)
        complexity.to_corner(UR, buff=0.5)
        self.play(Write(complexity))

        # 画图
        nodes = {}
        node_labels = {}
        edges = {}

        for v, pos in self.node_positions.items():
            circle = Circle(radius=0.35, color=BLUE, fill_opacity=0.2)
            circle.move_to(pos)
            label = Text(str(v), font_size=22, color=WHITE).move_to(pos)
            nodes[v] = circle
            node_labels[v] = label

        for v, neighbors in self.graph_data.items():
            for u in neighbors:
                if (u, v) not in edges and (v, u) not in edges:
                    edge = Line(
                        self.node_positions[v], self.node_positions[u],
                        color=GRAY, stroke_width=2, stroke_opacity=0.5,
                    )
                    edges[(v, u)] = edge

        self.play(
            *[Create(e) for e in edges.values()],
            *[GrowFromCenter(n) for n in nodes.values()],
            *[Write(l) for l in node_labels.values()],
            run_time=1,
        )

        # DFS 递归动画
        visited = set()
        order = []

        def dfs(v):
            visited.add(v)
            order.append(v)
            self.play(nodes[v].animate.set_fill(RED, opacity=0.8), run_time=0.3)

            for u in self.graph_data[v]:
                if u not in visited:
                    edge_key = (v, u) if (v, u) in edges else (u, v)
                    self.play(
                        edges[edge_key].animate.set_color(YELLOW).set_stroke(width=3),
                        run_time=0.2,
                    )
                    dfs(u)
                    # 回溯时颜色变化
                    self.play(nodes[v].animate.set_fill(ORANGE, opacity=0.6), run_time=0.15)

            self.play(nodes[v].animate.set_fill(GREEN, opacity=0.6), run_time=0.2)

        dfs(0)

        order_text = Text(f"遍历顺序: {' → '.join(str(v) for v in order)}",
                          font_size=24, color=GREEN)
        order_text.to_edge(DOWN, buff=0.3)
        self.play(Write(order_text))
        self.wait(1.5)


class DijkstraScene(Scene):
    """Dijkstra 最短路径算法可视化"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 带权图
        self.edges_data = [
            (0, 1, 4), (0, 2, 1),
            (1, 3, 1),
            (2, 1, 2), (2, 3, 5),
            (3, 4, 3),
        ]
        self.node_positions = {
            0: [-4, 0.5, 0],
            1: [-1, 2, 0],
            2: [-1, -1, 0],
            3: [2, 0.5, 0],
            4: [4, 0.5, 0],
        }

    def construct(self):
        title = Text("Dijkstra 最短路径", font_size=36, color=BLUE)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        idea = Text("贪心策略：每次取距离最小的未访问节点", font_size=22, color=GRAY)
        idea.next_to(title, DOWN, buff=0.2)
        self.play(Write(idea))

        complexity = MathTex(r"O((V+E) \log V)", font_size=28, color=YELLOW)
        complexity.to_corner(UR, buff=0.5)
        self.play(Write(complexity))

        # 画图
        nodes = {}
        node_labels = {}
        edge_lines = {}
        edge_weights = {}

        for v, pos in self.node_positions.items():
            circle = Circle(radius=0.35, color=BLUE, fill_opacity=0.2)
            circle.move_to(pos)
            label = Text(str(v), font_size=22, color=WHITE).move_to(pos)
            nodes[v] = circle
            node_labels[v] = label

        for u, v, w in self.edges_data:
            pos_u = np.array(self.node_positions[u])
            pos_v = np.array(self.node_positions[v])
            line = Arrow(pos_u, pos_v, buff=0.4, color=GRAY, stroke_width=2,
                          max_tip_length_to_length_ratio=0.15)
            edge_lines[(u, v)] = line
            weight = Text(str(w), font_size=16, color=YELLOW)
            mid = (pos_u + pos_v) / 2 + np.array([0, 0.25, 0])
            weight.move_to(mid)
            edge_weights[(u, v)] = weight

        self.play(
            *[Create(e) for e in edge_lines.values()],
            *[Write(w) for w in edge_weights.values()],
            *[GrowFromCenter(n) for n in nodes.values()],
            *[Write(l) for l in node_labels.values()],
            run_time=1.5,
        )

        # 距离表
        dist = {v: float('inf') for v in self.node_positions}
        dist[0] = 0
        dist_labels = {}

        for v, pos in self.node_positions.items():
            d = "0" if v == 0 else "∞"
            dl = Text(f"d={d}", font_size=16, color=TEAL)
            dl.next_to(nodes[v], DOWN, buff=0.15)
            dist_labels[v] = dl
            self.play(Write(dl), run_time=0.1)

        # Dijkstra
        visited = set()
        pq = [(0, 0)]  # (dist, node)

        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)

            self.play(nodes[u].animate.set_fill(RED, opacity=0.8), run_time=0.3)

            # 邻接节点
            for src, dst, w in self.edges_data:
                if src == u and dst not in visited:
                    new_dist = d + w
                    if new_dist < dist[dst]:
                        dist[dst] = new_dist
                        heapq.heappush(pq, (new_dist, dst))

                        # 更新距离标签
                        self.play(
                            edge_lines[(src, dst)].animate.set_color(YELLOW),
                            nodes[dst].animate.set_fill(YELLOW, opacity=0.5),
                            run_time=0.3,
                        )
                        new_label = Text(f"d={new_dist}", font_size=16, color=GREEN)
                        new_label.next_to(nodes[dst], DOWN, buff=0.15)
                        self.play(
                            Transform(dist_labels[dst], new_label),
                            run_time=0.2,
                        )

            self.play(nodes[u].animate.set_fill(GREEN, opacity=0.6), run_time=0.2)

        result = Text(f"从节点 0 出发的最短距离: {dict(sorted(dist.items()))}",
                       font_size=20, color=GREEN)
        result.to_edge(DOWN, buff=0.3)
        self.play(Write(result))
        self.wait(1.5)
