"""Forest plot generation using matplotlib."""

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for server
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Optional
import io
import base64
import logging

logger = logging.getLogger(__name__)


class Visualizer:
    """Generates forest plots for meta-analysis results."""

    def create_forest_plot(
        self,
        studies: List[Dict],
        pooled_effect: float,
        ci_lower: float,
        ci_upper: float,
        title: str = "Forest Plot of Study Effect Sizes",
        figsize: tuple = (10, 8),
        dpi: int = 100,
    ) -> str:
        """
        Generate a forest plot and return as base64-encoded PNG.

        Args:
            studies: List of study dictionaries with:
                - effect_size: Individual study effect size
                - ci_lower: Lower CI bound
                - ci_upper: Upper CI bound
                - study_label: Label for the study
            pooled_effect: Pooled effect size from meta-analysis
            ci_lower: Lower CI bound for pooled effect
            ci_upper: Upper CI bound for pooled effect
            title: Plot title
            figsize: Figure size (width, height) in inches
            dpi: Resolution in dots per inch

        Returns:
            Base64-encoded PNG image string
        """
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

        n_studies = len(studies)
        y_positions = np.arange(n_studies + 1)  # +1 for pooled effect row

        # Plot individual studies
        for i, study in enumerate(studies):
            y_pos = y_positions[i]
            effect = study["effect_size"]
            ci_low = study["ci_lower"]
            ci_high = study["ci_upper"]

            # Plot point estimate
            ax.plot(effect, y_pos, "o", markersize=8, color="steelblue")

            # Plot confidence interval
            ax.plot([ci_low, ci_high], [y_pos, y_pos], "b-", linewidth=2)

            # Add study label
            label = study.get("study_label", f"Study {i+1}")
            ax.text(-0.5, y_pos, label, va="center", ha="right", fontsize=9)

        # Plot pooled effect (diamond shape)
        pooled_y = y_positions[-1]
        ax.plot(pooled_effect, pooled_y, "D", markersize=12, color="red", label="Pooled Effect")
        ax.plot([ci_lower, ci_upper], [pooled_y, pooled_y], "r-", linewidth=3)

        # Add vertical line at effect = 0
        ax.axvline(x=0, color="black", linestyle="--", linewidth=1, alpha=0.5)

        # Add vertical line at pooled effect
        ax.axvline(x=pooled_effect, color="red", linestyle=":", linewidth=1, alpha=0.5)

        # Labels and formatting
        ax.set_xlabel("Effect Size (Cohen's d)", fontsize=11)
        ax.set_ylabel("Study", fontsize=11)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_yticks(y_positions)
        ax.set_yticklabels(
            [s.get("study_label", f"Study {i+1}") for i, s in enumerate(studies)]
            + ["Pooled Effect"]
        )
        ax.grid(True, alpha=0.3, axis="x")
        ax.legend(loc="best")

        # Add text annotation for pooled effect
        ax.text(
            pooled_effect + 0.1,
            pooled_y,
            f"d = {pooled_effect:.3f} [{ci_lower:.3f}, {ci_upper:.3f}]",
            va="center",
            fontsize=9,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        plt.tight_layout()

        # Convert to base64
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=dpi)
        plt.close(fig)
        buf.seek(0)

        image_base64 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()

        return image_base64

