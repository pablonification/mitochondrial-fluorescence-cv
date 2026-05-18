from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from bioenergetics import (  # noqa: E402
    DATASET_CONFIG,
    analyze_image,
    analyze_records,
    compare_conditions,
    dataset_validation_summary,
    mask_to_image,
    overlay_mask,
    preprocessed_to_image,
    read_sample_manifest,
)


DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
FIGURE_DIR = OUTPUT_DIR / "figures"


def _ensure_output_dirs() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    FIGURE_DIR.mkdir(exist_ok=True)


def _remove_stale_outputs() -> None:
    """Remove generated outputs from the earlier OCR/ECAR prototype."""

    stale_names = [
        "tidy_seahorse_data.csv",
        "pre_post_summary.csv",
        "feature_table.csv",
        "treatment_delta.csv",
        "ecar_ocr_ratio.csv",
        "notebook_tidy_seahorse_data.csv",
        "notebook_feature_table.csv",
        "notebook_treatment_delta.csv",
    ]
    stale_figures = [
        "ocr_ecar_timeseries.png",
        "post_injection_delta.png",
        "ecar_ocr_ratio.png",
        "notebook_ocr_ecar_timeseries.png",
        "notebook_ecar_ocr_ratio.png",
        "streamlit_lps_final.png",
    ]
    for name in stale_names:
        path = OUTPUT_DIR / name
        if path.exists():
            path.unlink()
    for name in stale_figures:
        path = FIGURE_DIR / name
        if path.exists():
            path.unlink()


def save_visual_outputs(records, max_per_condition: int = 3) -> list[Path]:
    paths: list[Path] = []
    saved_by_condition: dict[str, int] = {}
    for record in records:
        count = saved_by_condition.get(record.condition, 0)
        if count >= max_per_condition:
            continue
        saved_by_condition[record.condition] = count + 1

        result = analyze_image(record.path, image_id=record.image_id, condition=record.condition)
        image = result["image"]
        segmentation = result["segmentation"]

        overlay_path = FIGURE_DIR / f"{record.image_id}_overlay.png"
        mask_path = FIGURE_DIR / f"{record.image_id}_mask.png"
        preprocessed_path = FIGURE_DIR / f"{record.image_id}_preprocessed.png"

        overlay_mask(image, segmentation).save(overlay_path)
        mask_to_image(segmentation).save(mask_path)
        preprocessed_to_image(segmentation).save(preprocessed_path)
        paths.extend([overlay_path, mask_path, preprocessed_path])
    return paths


def plot_metric_bars(metrics: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
    plot_specs = [
        ("mean_intensity", "Mean intensity"),
        ("integrated_density", "Integrated density"),
        ("area_pixels", "Foreground area (px)"),
    ]
    colors = {"DMSO": "#3b7a57", "FCCP": "#b6503c"}

    for ax, (column, title) in zip(axes, plot_specs):
        groups = [group[column].to_numpy() for _, group in metrics.groupby("condition", sort=True)]
        labels = [condition for condition, _ in metrics.groupby("condition", sort=True)]
        box = ax.boxplot(groups, tick_labels=labels, patch_artist=True)
        for patch, label in zip(box["boxes"], labels):
            patch.set_facecolor(colors.get(label, "#666666"))
            patch.set_alpha(0.55)
        for idx, values in enumerate(groups, start=1):
            x = [idx] * len(values)
            ax.scatter(x, values, s=18, color="#1f2933", alpha=0.55)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.25)
        ax.tick_params(axis="x", rotation=0)

    fig.suptitle("BBBC053 fluorescence metric distributions")
    fig.tight_layout()
    path = FIGURE_DIR / "sample_metric_bars.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def main() -> None:
    _ensure_output_dirs()
    _remove_stale_outputs()

    records = read_sample_manifest(DATA_DIR)
    metrics = analyze_records(records)
    condition_summary = compare_conditions(metrics)
    validation = dataset_validation_summary()
    visual_paths = save_visual_outputs(records)
    bar_path = plot_metric_bars(metrics)

    metrics.to_csv(OUTPUT_DIR / "image_metrics.csv", index=False)
    condition_summary.to_csv(OUTPUT_DIR / "condition_summary.csv", index=False)
    validation.to_csv(OUTPUT_DIR / "dataset_validation.csv", index=False)

    print("Dataset:", DATASET_CONFIG["BBBC053"]["name"])
    print("Loaded sample images:", len(records))
    print("\nMetric table:")
    print(metrics.round(4).to_string(index=False))
    print("\nCondition summary:")
    print(condition_summary.round(4).to_string(index=False))
    print("\nDataset validation:")
    print(validation.to_string(index=False))
    print("\nSaved visual outputs:")
    for path in [*visual_paths, bar_path]:
        print("-", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
