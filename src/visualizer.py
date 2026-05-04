import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class VisualizationError(Exception):
    pass

COLORS = {
    "foundation": "#4A90D9",
    "core":       "#F5A623",
    "advanced":   "#E74C3C",
    "accent":     "#2ECC71",
    "bg":         "#1C1C2E",
    "panel":      "#2A2A3E",
    "text":       "#ECEFF4",
}

TIER_COLORS = {
    "foundation": COLORS["foundation"],
    "core":       COLORS["core"],
    "advanced":   COLORS["advanced"],
}

def _apply_dark_style():
    plt.rcParams.update({
        "figure.facecolor": COLORS["bg"],
        "axes.facecolor":   COLORS["panel"],
        "axes.edgecolor":   "#444466",
        "axes.labelcolor":  COLORS["text"],
        "xtick.color":      COLORS["text"],
        "ytick.color":      COLORS["text"],
        "text.color":       COLORS["text"],
        "grid.color":       "#3A3A5A",
        "grid.linestyle":   "--",
        "grid.alpha":       0.5,
        "font.family":      "monospace",
    })

def plot_career_confidence(matches: list[dict]):
    try:
        _apply_dark_style()

        careers = [m["career"].replace("_", " ").title() for m in matches]
        scores  = [m["confidence_pct"] for m in matches]

        bar_colors = [
            COLORS["accent"], COLORS["foundation"], COLORS["core"]
        ][:len(careers)]

        fig, ax = plt.subplots(figsize=(9, 4))

        bars = ax.barh(
            careers, scores,
            color=bar_colors,
            edgecolor="#1C1C2E",
            height=0.5,
            zorder=3
        )

        for bar, score in zip(bars, scores):
            ax.text(
                bar.get_width() + 0.8,
                bar.get_y() + bar.get_height() / 2,
                f"{score}%",
                va="center",
                fontsize=12,
                fontweight="bold"
            )

        ax.set_xlim(0, 115)
        ax.set_xlabel("Confidence (%)")
        ax.set_title("Career Match Confidence", fontweight="bold")
        ax.grid(axis="x", zorder=0)
        ax.invert_yaxis()

        plt.tight_layout()
        return fig

    except Exception as e:
        raise VisualizationError(f"Confidence chart failed: {e}")

def plot_weekly_workload(roadmap: dict):
    try:
        _apply_dark_style()
        weekly = roadmap["weekly_plan"]

        weeks  = [f"Wk {w['week']}" for w in weekly]
        counts = [w["skill_count"] for w in weekly]
        colors = [TIER_COLORS.get(w["tier"], "#888") for w in weekly]

        fig, ax = plt.subplots(figsize=(10, 5))

        bars = ax.bar(
            weeks, counts,
            color=colors,
            edgecolor="#1C1C2E",
            zorder=3
        )

        for bar, count in zip(bars, counts):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.05,
                str(count),
                ha="center",
                va="bottom",
                fontweight="bold"
            )

        ax.set_title(f"Weekly Workload — {roadmap['meta']['career_display']}")
        ax.set_xlabel("Week")
        ax.set_ylabel("Skills")
        ax.set_ylim(0, max(counts) + 2)
        ax.grid(axis="y", zorder=0)

        legend = [
            mpatches.Patch(color=COLORS["foundation"], label="Foundation"),
            mpatches.Patch(color=COLORS["core"], label="Core"),
            mpatches.Patch(color=COLORS["advanced"], label="Advanced"),
        ]
        ax.legend(handles=legend)

        plt.tight_layout()
        return fig

    except Exception as e:
        raise VisualizationError(f"Workload chart failed: {e}")

def plot_skill_tier_distribution(roadmap: dict):
    try:
        _apply_dark_style()

        tier_counts = {"foundation": 0, "core": 0, "advanced": 0}

        for w in roadmap["weekly_plan"]:
            tier_counts[w["tier"]] += w["skill_count"]

        labels = [k.title() for k, v in tier_counts.items() if v > 0]
        sizes  = [v for v in tier_counts.values() if v > 0]
        colors = [TIER_COLORS[k] for k, v in tier_counts.items() if v > 0]

        fig, ax = plt.subplots(figsize=(6, 6))

        ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=140,
            wedgeprops={"edgecolor": COLORS["bg"], "linewidth": 2}
        )

        ax.set_title("Skill Tier Distribution")

        plt.tight_layout()
        return fig

    except Exception as e:
        raise VisualizationError(f"Tier chart failed: {e}")
