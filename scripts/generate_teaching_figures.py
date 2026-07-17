#!/usr/bin/env python3
"""Generate BioEZ-owned teaching SVGs that replace legacy remote images."""

from __future__ import annotations

import argparse
import math
import random
import sys
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIRECTORY = ROOT / "assets/generated"
SEED = 20260717
LICENSE = "CC BY-SA 4.0"
FONT = "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"


def text(x: float, y: float, value: str, size: int = 18, anchor: str = "middle", weight: int = 400, fill: str = "#172033") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}">{escape(value)}</text>'


def line(x1: float, y1: float, x2: float, y2: float, color: str = "#34435e", width: float = 2, dash: str | None = None) -> str:
    dashed = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}"{dashed}/>'


def rect(x: float, y: float, width: float, height: float, fill: str, stroke: str = "none", radius: float = 0, stroke_width: float = 1) -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" rx="{radius:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'


def circle(x: float, y: float, radius: float, fill: str, stroke: str = "none", stroke_width: float = 1) -> str:
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'


def polyline(points: list[tuple[float, float]], color: str, width: float = 2, fill: str = "none") -> str:
    coordinates = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{coordinates}" fill="{fill}" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>'


def arrow(x1: float, y1: float, x2: float, y2: float, color: str = "#385a8c") -> str:
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 10
    left = (x2 - size * math.cos(angle - 0.55), y2 - size * math.sin(angle - 0.55))
    right = (x2 - size * math.cos(angle + 0.55), y2 - size * math.sin(angle + 0.55))
    return line(x1, y1, x2, y2, color, 2.4) + polyline([left, (x2, y2), right], color, 2.4)


def document(title: str, body: str, width: int = 960, height: int = 600) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
  <title id="title">{escape(title)}</title>
  <desc id="description">BioEZ 可复现教学图，由 scripts/generate_teaching_figures.py 生成。</desc>
  <metadata>Copyright BioEZ contributors; licensed under {LICENSE}; generator seed {SEED}.</metadata>
  <rect width="100%" height="100%" fill="#fbfcff"/>
  <g font-family="{FONT}">
{body}
  </g>
</svg>
'''


def axes(x: float, y: float, width: float, height: float, xlabel: str, ylabel: str) -> str:
    body = line(x, y + height, x + width, y + height, "#26354d", 1.6)
    body += line(x, y, x, y + height, "#26354d", 1.6)
    body += text(x + width / 2, y + height + 42, xlabel, 16)
    body += f'<text x="{x - 50:.1f}" y="{y + height / 2:.1f}" font-size="16" text-anchor="middle" fill="#172033" transform="rotate(-90 {x - 50:.1f} {y + height / 2:.1f})">{escape(ylabel)}</text>'
    return body


def heat_color(value: float) -> str:
    value = max(-1.0, min(1.0, value))
    if value < 0:
        factor = value + 1
        red = int(45 + 210 * factor)
        green = int(98 + 157 * factor)
        blue = int(175 + 80 * factor)
    else:
        red = 255
        green = int(255 - 160 * value)
        blue = int(255 - 120 * value)
    return f"#{red:02x}{green:02x}{blue:02x}"


def amino_acid_structure(_: random.Random) -> str:
    parts = [text(480, 48, "α-氨基酸的通式", 28, weight=650)]
    parts += [circle(480, 300, 42, "#eaf2ff", "#28568c", 3), text(480, 310, "Cα", 25, weight=700)]
    groups = [(480, 130, "H", "氢"), (480, 470, "R", "侧链"), (250, 300, "H₃N⁺", "氨基"), (710, 300, "COO⁻", "羧基")]
    for x, y, symbol, label in groups:
        end_x = 480 + (x - 480) * 0.72
        end_y = 300 + (y - 300) * 0.72
        parts.append(line(480, 300, end_x, end_y, "#34435e", 4))
        parts.append(rect(x - 72, y - 35, 144, 70, "#ffffff", "#7891b5", 12, 2))
        parts.append(text(x, y + 5, symbol, 25, weight=650))
        parts.append(text(x, y + 62, label, 17, fill="#52647f"))
    parts.append(text(480, 562, "R 基决定氨基酸的极性、电荷和反应特性", 19, weight=550))
    return document("α-氨基酸通式", "\n".join(parts))


def carbohydrate_catabolism(_: random.Random) -> str:
    parts = [text(480, 42, "糖代谢的主要分流与汇合", 28, weight=650)]
    nodes = {
        "葡萄糖": (110, 250, "#e8f2ff"), "G6P": (300, 250, "#e8f2ff"), "丙酮酸": (500, 250, "#fff0d9"),
        "乙酰 CoA": (690, 250, "#fff0d9"), "TCA 循环": (850, 250, "#ffe3e3"), "糖原": (300, 90, "#e6f7ec"),
        "磷酸戊糖途径": (300, 440, "#efe8ff"), "乳酸": (500, 440, "#e6f7ec"), "ATP / NADH": (850, 440, "#fff7cc"),
    }
    for label, (x, y, fill) in nodes.items():
        width = 158 if len(label) > 5 else 120
        parts.append(rect(x - width / 2, y - 30, width, 60, fill, "#5f7391", 14, 1.8))
        parts.append(text(x, y + 6, label, 18, weight=600))
    connections = [((170, 250), (240, 250)), ((360, 250), (438, 250)), ((560, 250), (620, 250)), ((760, 250), (782, 250)),
                   ((300, 220), (300, 123)), ((300, 280), (300, 407)), ((500, 280), (500, 407)), ((850, 283), (850, 407))]
    for start, end in connections:
        parts.append(arrow(*start, *end))
    parts.append(text(402, 222, "糖酵解", 15, fill="#52647f"))
    parts.append(text(618, 222, "氧化脱羧", 15, fill="#52647f"))
    parts.append(text(480, 558, "关键思路：碳骨架在不同途径间分流，最终与能量代谢耦联", 18, weight=550))
    return document("糖代谢途径概览", "\n".join(parts))


def boxplot_anatomy(_: random.Random) -> str:
    parts = [text(480, 48, "箱形图的结构", 28, weight=650)]
    y = 285
    parts += [line(120, y, 840, y, "#8290a6", 2), line(210, y - 40, 210, y + 40, "#40506b", 3), line(750, y - 40, 750, y + 40, "#40506b", 3)]
    parts += [line(210, y, 330, y, "#40506b", 3), line(650, y, 750, y, "#40506b", 3)]
    parts += [rect(330, y - 92, 320, 184, "#dfeeff", "#28568c", 4, 3), line(480, y - 92, 480, y + 92, "#d64848", 4)]
    parts += [circle(100, y, 7, "#d64848"), circle(865, y, 7, "#d64848")]
    labels = [(210, 165, "下须"), (330, 420, "Q1"), (480, 165, "中位数"), (650, 420, "Q3"), (750, 165, "上须"), (100, 420, "离群点")]
    for x, label_y, label in labels:
        parts.append(line(x, y + (-55 if label_y < y else 55), x, label_y + (-20 if label_y > y else 20), "#8a96aa", 1.5, "5 4"))
        parts.append(text(x, label_y, label, 18, weight=550))
    parts.append(text(490, 520, "IQR = Q3 − Q1；须通常延伸到 1.5 × IQR 范围内的最远观测值", 18))
    return document("箱形图结构", "\n".join(parts))


def boxplot_examples(rng: random.Random) -> str:
    parts = [text(480, 42, "四组数据的箱形图比较", 28, weight=650), axes(100, 90, 760, 390, "处理组", "观测值")]
    values = [(18, 23, 28, 34, 40), (22, 28, 30, 35, 39), (10, 20, 31, 40, 52), (29, 37, 42, 47, 55)]
    colors = ["#9ec5fe", "#b6e2c1", "#ffd59e", "#d6bbfb"]
    scale = lambda value: 480 - value * 6.4
    for index, (minimum, q1, median, q3, maximum) in enumerate(values):
        x = 210 + index * 170
        parts += [line(x, scale(minimum), x, scale(maximum), "#485b78", 2), line(x - 25, scale(minimum), x + 25, scale(minimum), "#485b78", 2), line(x - 25, scale(maximum), x + 25, scale(maximum), "#485b78", 2)]
        parts += [rect(x - 45, scale(q3), 90, scale(q1) - scale(q3), colors[index], "#485b78", 5, 2), line(x - 45, scale(median), x + 45, scale(median), "#b53535", 3)]
        for _ in range(9):
            value = rng.uniform(minimum, maximum)
            parts.append(circle(x + rng.uniform(-28, 28), scale(value), 3, "#52647f", "#ffffff", .5))
        parts.append(text(x, 520, f"组 {chr(65 + index)}", 17, weight=550))
    return document("多组箱形图", "\n".join(parts))


def histogram_example(rng: random.Random) -> str:
    samples_a = [rng.gauss(42, 7) for _ in range(240)]
    samples_b = [rng.gauss(56, 9) for _ in range(240)]
    bins = list(range(15, 86, 5))
    counts = []
    for samples in (samples_a, samples_b):
        counts.append([sum(low <= value < low + 5 for value in samples) for low in bins])
    parts = [text(480, 42, "用直方图比较两组分布", 28, weight=650), axes(100, 90, 760, 390, "表达量", "频数")]
    max_count = max(max(group) for group in counts)
    for index, low in enumerate(bins):
        x = 105 + index * 51
        for group, (color, offset) in enumerate((("#3478c7", 0), ("#e05b4e", 18))):
            height = counts[group][index] / max_count * 330
            parts.append(rect(x + offset, 480 - height, 24, height, color, "none", 1))
    parts += [rect(620, 105, 18, 18, "#3478c7"), text(648, 120, "对照组", 15, "start"), rect(730, 105, 18, 18, "#e05b4e"), text(758, 120, "处理组", 15, "start")]
    return document("两组数据的直方图", "\n".join(parts))


def scatterplot_example(rng: random.Random) -> str:
    parts = [text(480, 42, "散点图：变量关系与波动", 28, weight=650), axes(110, 80, 730, 410, "变量 X", "变量 Y")]
    points = []
    for index in range(55):
        x_value = 4 + index * 1.6
        y_value = 18 + 0.66 * x_value + rng.gauss(0, 7)
        x = 120 + x_value * 7.6
        y = 480 - y_value * 4.6
        points.append((x, y))
        parts.append(circle(x, y, 4.5, "#3478c7", "#ffffff", .8))
    parts.append(line(150, 408, 820, 140, "#d64848", 3))
    parts.append(text(610, 105, "趋势线只描述线性关系，不证明因果", 17, weight=550, fill="#8b2f2f"))
    return document("散点图与线性趋势", "\n".join(parts))


def scatterplot_matrix(rng: random.Random) -> str:
    variables = ["Gene A", "Gene B", "Clinical"]
    samples = [(rng.gauss(0, 1), 0, 0) for _ in range(36)]
    samples = [(a, 0.72 * a + rng.gauss(0, .65), -0.35 * a + rng.gauss(0, .8)) for a, _, _ in samples]
    parts = [text(480, 36, "散点图矩阵：两两关系", 26, weight=650)]
    size, start_x, start_y = 155, 210, 75
    for row in range(3):
        for column in range(3):
            x0, y0 = start_x + column * size, start_y + row * size
            parts.append(rect(x0, y0, size, size, "#ffffff", "#c6cfdd", 0, 1))
            if row == column:
                parts.append(text(x0 + size / 2, y0 + 68, variables[row], 17, weight=650))
                parts.append(text(x0 + size / 2, y0 + 100, "分布", 14, fill="#61708a"))
            elif row < column:
                means = {(0, 1): "r = 0.73", (0, 2): "r = -0.31", (1, 2): "r = -0.18"}
                parts.append(text(x0 + size / 2, y0 + 86, means[(row, column)], 18, weight=650, fill="#385a8c"))
            else:
                for sample in samples:
                    x = x0 + 76 + sample[column] * 28
                    y = y0 + 76 - sample[row] * 28
                    if x0 + 5 < x < x0 + size - 5 and y0 + 5 < y < y0 + size - 5:
                        parts.append(circle(x, y, 2.7, "#3478c7", "none"))
    parts.append(text(480, 575, "对角线是单变量分布，下三角是散点，上三角是相关系数", 17))
    return document("散点图矩阵", "\n".join(parts))


def heatmap(title: str, rows: int, columns: int, value_function, row_prefix: str = "Cluster") -> str:
    parts = [text(480, 38, title, 26, weight=650)]
    x0, y0, cell_w, cell_h = 190, 75, 27, min(38, 410 / rows)
    for row in range(rows):
        parts.append(text(x0 - 16, y0 + row * cell_h + cell_h * .7, f"{row_prefix} {row + 1}", 12, "end", fill="#52647f"))
        for column in range(columns):
            value = value_function(row, column)
            parts.append(rect(x0 + column * cell_w, y0 + row * cell_h, cell_w + .2, cell_h + .2, heat_color(value)))
    for column in range(columns):
        if column % 3 == 0:
            parts.append(text(x0 + column * cell_w + 5, y0 + rows * cell_h + 22, f"G{column + 1}", 10, anchor="start", fill="#52647f"))
    for index, value in enumerate((-1, -.5, 0, .5, 1)):
        parts.append(rect(760 + index * 30, 510, 30, 18, heat_color(value)))
    parts.append(text(755, 552, "低表达", 13, "start", fill="#52647f"))
    parts.append(text(910, 552, "高表达", 13, "end", fill="#52647f"))
    return document(title, "\n".join(parts))


def cluster_marker_heatmap(rng: random.Random) -> str:
    noise = [[rng.uniform(-.25, .25) for _ in range(24)] for _ in range(10)]
    return heatmap("细胞簇 Marker 基因热图", 10, 24, lambda row, column: .85 if column // 3 == row % 8 else -.25 + noise[row][column])


def multi_group_heatmap(rng: random.Random) -> str:
    noise = [[rng.uniform(-.35, .35) for _ in range(24)] for _ in range(9)]
    return heatmap("多组表达模式热图", 9, 24, lambda row, column: .72 * math.sin((row + 1) * (column + 2) / 7) + noise[row][column], "Group")


def clinical_expression_heatmap(rng: random.Random) -> str:
    parts = [text(480, 34, "临床特征与基因表达复合热图", 25, weight=650)]
    x0, y0, cell_w, cell_h = 220, 145, 25, 29
    annotations = [("Sex", ["#7bb7e8", "#ef9aaa"]), ("Stage", ["#9bd3ae", "#f3c77b", "#d99bdd"]), ("Group", ["#8ecbd0", "#e59a87"])]
    for index, (label, colors) in enumerate(annotations):
        y = 60 + index * 25
        parts.append(text(x0 - 12, y + 16, label, 12, "end", fill="#52647f"))
        for column in range(24):
            parts.append(rect(x0 + column * cell_w, y, cell_w, 20, colors[(column // (3 + index)) % len(colors)]))
    for row in range(11):
        parts.append(text(x0 - 12, y0 + row * cell_h + 20, f"Gene {row + 1}", 11, "end", fill="#52647f"))
        for column in range(24):
            block = .6 if (row < 4 and column > 13) or (row > 7 and column < 9) else -.15
            parts.append(rect(x0 + column * cell_w, y0 + row * cell_h, cell_w, cell_h, heat_color(block + rng.uniform(-.45, .45))))
    parts.append(text(520, 510, "每列为一个样本；顶部色条为临床注释", 16, weight=550))
    return document("临床注释复合热图", "\n".join(parts))


def volcano_plot_anatomy(rng: random.Random) -> str:
    parts = [text(480, 42, "火山图：差异倍数与显著性", 28, weight=650), axes(110, 80, 730, 410, "log₂ fold change", "−log₁₀ adjusted p-value")]
    for _ in range(260):
        x_value = max(-4.5, min(4.5, rng.gauss(0, 1.65)))
        y_value = min(6.8, rng.expovariate(.8) + abs(x_value) * .42)
        x = 475 + x_value * 78
        y = 480 - y_value * 52
        significant = y_value >= 2 and abs(x_value) >= 1
        color = "#d84949" if significant and x_value > 0 else "#3478c7" if significant else "#9da8b8"
        parts.append(circle(x, y, 3.2, color, "none"))
    parts += [line(110, 376, 840, 376, "#7556a3", 2, "7 5"), line(397, 80, 397, 490, "#7556a3", 2, "7 5"), line(553, 80, 553, 490, "#7556a3", 2, "7 5")]
    parts += [text(230, 105, "显著下调", 16, weight=600, fill="#2867a8"), text(720, 105, "显著上调", 16, weight=600, fill="#a93434")]
    return document("火山图阈值解读", "\n".join(parts))


GENERATORS = {
    "amino-acid-structure.svg": amino_acid_structure,
    "carbohydrate-catabolism.svg": carbohydrate_catabolism,
    "boxplot-anatomy.svg": boxplot_anatomy,
    "boxplot-examples.svg": boxplot_examples,
    "histogram-example.svg": histogram_example,
    "scatterplot-example.svg": scatterplot_example,
    "scatterplot-matrix.svg": scatterplot_matrix,
    "cluster-marker-heatmap.svg": cluster_marker_heatmap,
    "multi-group-heatmap.svg": multi_group_heatmap,
    "clinical-expression-heatmap.svg": clinical_expression_heatmap,
    "volcano-plot-anatomy.svg": volcano_plot_anatomy,
}


def generate_all() -> dict[str, str]:
    return {name: generator(random.Random(SEED + index)) for index, (name, generator) in enumerate(GENERATORS.items())}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIRECTORY)
    parser.add_argument("--check", action="store_true", help="检查已提交 SVG 是否可由脚本完全复现")
    args = parser.parse_args(argv)
    generated = generate_all()
    if args.check:
        mismatches = [name for name, content in generated.items() if not (args.output_dir / name).is_file() or (args.output_dir / name).read_text(encoding="utf-8") != content]
        if mismatches:
            for name in mismatches:
                print(f"ERROR: generated asset differs: {name}")
            return 1
        print(f"可复现图像检查通过：{len(generated)} 个 SVG。")
        return 0
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in generated.items():
        (args.output_dir / name).write_text(content, encoding="utf-8")
    print(f"已生成 {len(generated)} 个 SVG 到 {args.output_dir}。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
