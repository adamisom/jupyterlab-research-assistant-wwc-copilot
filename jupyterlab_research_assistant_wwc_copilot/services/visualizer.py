"""Forest plot generation using matplotlib."""

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for server
import base64
import io
import logging

import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


class Visualizer:
    """Generates forest plots for meta-analysis results."""

    def create_forest_plot(
        self,
        studies: list[dict],
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
            bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5},
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

    def create_funnel_plot(
        self,
        effect_sizes: list[float],
        std_errors: list[float],
        labels: list[str],
        title: str = "Funnel Plot",
        figsize: tuple = (8, 8),
        dpi: int = 100
    ) -> str:
        """
        Generate a funnel plot for publication bias assessment.

        Args:
            effect_sizes: List of effect sizes
            std_errors: List of standard errors
            labels: List of study labels
            title: Plot title
            figsize: Figure size (width, height) in inches
            dpi: Resolution in dots per inch

        Returns:
            Base64-encoded PNG image string
        """
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

        # Plot effect sizes vs precision (1/SE)
        precision = [1.0 / se for se in std_errors]

        ax.scatter(effect_sizes, precision, alpha=0.6, s=50, color='steelblue')

        # Add labels for outliers
        for _i, (es, prec, label) in enumerate(zip(effect_sizes, precision, labels)):
            # Label studies with extreme values
            if abs(es) > 2 or prec > max(precision) * 0.8:
                ax.annotate(
                    label[:20] if len(label) > 20 else label,
                    (es, prec),
                    fontsize=8,
                    alpha=0.7,
                    xytext=(5, 5),
                    textcoords='offset points'
                )

        ax.set_xlabel('Effect Size', fontsize=11)
        ax.set_ylabel('Precision (1/SE)', fontsize=11)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axvline(x=0, color='black', linestyle='--', linewidth=1, alpha=0.5)

        plt.tight_layout()

        # Convert to base64
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
        plt.close(fig)
        buf.seek(0)

        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        return image_base64

