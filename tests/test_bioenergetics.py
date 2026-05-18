from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bioenergetics import (  # noqa: E402
    analyze_image,
    analyze_records,
    compare_conditions,
    connected_components,
    dataset_validation_summary,
    overlay_mask,
    read_sample_manifest,
    segment_fluorescence,
)


DATA_DIR = ROOT / "data"


def synthetic_mito_image() -> np.ndarray:
    image = np.zeros((80, 80), dtype=np.float32)
    image[18:35, 20:38] = 0.72
    image[42:58, 45:65] = 0.95
    image += 0.02
    return np.clip(image, 0.0, 1.0)


def test_sample_manifest_points_to_existing_images():
    records = read_sample_manifest(DATA_DIR)

    assert {record.condition for record in records} == {"DMSO", "FCCP"}
    assert len(records) == 58
    assert all(record.path.exists() for record in records)
    assert all(record.path.suffix.lower() == ".tif" for record in records)


def test_segmentation_and_components_on_synthetic_image():
    image = synthetic_mito_image()
    segmentation = segment_fluorescence(image, min_area=20)

    assert segmentation.mask.sum() > 0
    assert len(segmentation.components) == 2
    assert 0.0 <= segmentation.threshold <= 1.0

    labels, components = connected_components(segmentation.mask, min_area=20)
    assert labels.max() == 2
    assert all(component.area >= 100 for component in components)


def test_analyze_sample_images_produces_non_empty_finite_metrics():
    records = read_sample_manifest(DATA_DIR)[:4]
    table = analyze_records(records)

    required = {
        "mean_intensity",
        "total_fluorescence",
        "area_pixels",
        "integrated_density",
        "object_count",
        "coverage_fraction",
        "signal_to_background",
    }
    assert required.issubset(table.columns)
    assert len(table) == 4
    assert pd.notna(table[list(required)]).all().all()
    assert (table["area_pixels"] > 0).all()
    assert (table["object_count"] > 0).all()
    assert (table["integrated_density"] > 0).all()


def test_overlay_image_has_same_size_as_input_and_rgb_mode():
    record = read_sample_manifest(DATA_DIR)[0]
    result = analyze_image(record.path, image_id=record.image_id, condition=record.condition)
    overlay = overlay_mask(result["image"], result["segmentation"])

    assert overlay.mode == "RGB"
    assert overlay.size == result["image"].shape[::-1]


def test_condition_summary_and_dataset_validation_are_explicit():
    all_records = read_sample_manifest(DATA_DIR)
    records = [record for record in all_records if record.condition == "DMSO"][:3]
    records += [record for record in all_records if record.condition == "FCCP"][:3]
    table = analyze_records(records)
    summary = compare_conditions(table)
    validation = dataset_validation_summary()

    assert set(summary["condition"]) == {"DMSO", "FCCP"}
    assert "valid" in set(validation["status"])
    assert validation["evidence"].str.contains("BBBC053|fluoresensi|fluorescence|ATP", case=False).any()
