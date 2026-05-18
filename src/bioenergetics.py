"""Computer vision utilities for mitochondrial fluorescence images.

The project analyzes fluorescence intensity and morphology proxies from
mitochondria-stained microscopy images. The measurements are interpretable as
indirect image-derived indicators only; they are not ATP concentration or ATP
production estimates.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Iterable

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFilter, ImageOps


DATASET_CONFIG = {
    "BBBC053": {
        "name": "Murine Cath.a differentiated cells - mitochondria",
        "source_url": "https://bbbc.broadinstitute.org/BBBC053",
        "collection_url": "https://bbbc.broadinstitute.org/bbbc",
        "full_image_format": "2048 x 2048 pixel, 16-bit TIFF",
        "sample_format": "58 full-resolution 2048 x 2048 16-bit TIFF images: 29 DMSO and 29 FCCP",
        "biology": (
            "Mitochondria visualized with TOM20 antibody and AlexaFluor 568. "
            "The public dataset contains DMSO and FCCP/CCCP-like perturbation "
            "classes for mitochondrial morphology analysis."
        ),
        "citation": (
            "Edwards, P. et al. BBBC053, Broad Bioimage Benchmark Collection; "
            "Ljosa et al., Nature Methods 2012."
        ),
        "license": "CC BY-NC-SA 3.0 as stated on the BBBC053 page.",
    }
}


@dataclass(frozen=True)
class ImageRecord:
    """Metadata for one local microscopy sample image."""

    image_id: str
    condition: str
    path: Path
    source_url: str
    dataset: str = "BBBC053"
    description: str = ""


@dataclass(frozen=True)
class Component:
    """One connected foreground component in the fluorescence mask."""

    component_id: int
    area: int
    bbox_x: int
    bbox_y: int
    bbox_width: int
    bbox_height: int
    centroid_x: float
    centroid_y: float


@dataclass(frozen=True)
class SegmentationResult:
    """Segmentation output used by analysis, tests, and Streamlit."""

    preprocessed: np.ndarray
    threshold: float
    mask: np.ndarray
    labels: np.ndarray
    components: list[Component]


def read_sample_manifest(data_dir: str | Path) -> list[ImageRecord]:
    """Read the small local sample manifest."""

    data_dir = Path(data_dir)
    manifest_path = data_dir / "sample_manifest.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Sample manifest not found: {manifest_path}")

    manifest = pd.read_csv(manifest_path)
    required = {"image_id", "condition", "filename", "source_url", "description"}
    missing = required.difference(manifest.columns)
    if missing:
        raise ValueError(f"Sample manifest is missing columns: {sorted(missing)}")

    records = []
    for row in manifest.itertuples(index=False):
        filename = Path(str(row.filename))
        path = data_dir / filename
        if not path.exists():
            path = data_dir / "sample_images" / filename
        if not path.exists():
            raise FileNotFoundError(f"Sample image listed in manifest is missing: {path}")
        records.append(
            ImageRecord(
                image_id=str(row.image_id),
                condition=str(row.condition),
                path=path,
                source_url=str(row.source_url),
                description=str(row.description),
            )
        )
    return records


def load_grayscale_image(path_or_file: str | Path | BinaryIO | BytesIO) -> np.ndarray:
    """Load a fluorescence image as a normalized 2D float array in [0, 1]."""

    with Image.open(path_or_file) as image:
        if image.mode not in {"L", "I", "I;16", "F"}:
            image = ImageOps.grayscale(image)
        arr = np.asarray(image)

    arr = arr.astype(np.float32)
    if arr.ndim != 2:
        raise ValueError(f"Expected a 2D grayscale image, got shape {arr.shape}")

    finite = np.isfinite(arr)
    if not finite.all():
        arr = np.where(finite, arr, 0.0)

    if arr.size == 0:
        raise ValueError("Image is empty")

    min_value = float(arr.min())
    max_value = float(arr.max())
    if max_value <= min_value:
        return np.zeros_like(arr, dtype=np.float32)

    if max_value > 1.0:
        arr = (arr - min_value) / (max_value - min_value)
    return np.clip(arr, 0.0, 1.0).astype(np.float32)


def preprocess_image(
    image: np.ndarray,
    gaussian_radius: float = 1.0,
    background_percentile: float = 2.0,
) -> np.ndarray:
    """Apply conservative background subtraction and Gaussian denoising."""

    if image.ndim != 2:
        raise ValueError("preprocess_image expects a 2D grayscale array")

    background = float(np.percentile(image, background_percentile))
    corrected = np.clip(image - background, 0.0, None)
    max_value = float(corrected.max())
    if max_value > 0:
        corrected = corrected / max_value

    pil = Image.fromarray((corrected * 255).astype(np.uint8))
    if gaussian_radius > 0:
        pil = pil.filter(ImageFilter.GaussianBlur(radius=gaussian_radius))
    return (np.asarray(pil).astype(np.float32) / 255.0).clip(0.0, 1.0)


def otsu_threshold(image: np.ndarray, bins: int = 256) -> float:
    """Compute an Otsu threshold for a normalized grayscale image."""

    values = image[np.isfinite(image)].ravel()
    if values.size == 0:
        raise ValueError("Cannot threshold an empty image")
    if float(values.max()) <= float(values.min()):
        return float(values.max())

    hist, edges = np.histogram(values, bins=bins, range=(0.0, 1.0))
    centers = (edges[:-1] + edges[1:]) / 2.0
    hist = hist.astype(np.float64)

    weight_background = np.cumsum(hist)
    weight_foreground = hist.sum() - weight_background
    mean_background = np.cumsum(hist * centers) / np.maximum(weight_background, 1e-12)
    reverse_cumsum = np.cumsum((hist * centers)[::-1])[::-1]
    mean_foreground = reverse_cumsum / np.maximum(weight_foreground, 1e-12)

    between_variance = weight_background * weight_foreground * (mean_background - mean_foreground) ** 2
    idx = int(np.nanargmax(between_variance))
    return float(centers[idx])


def _connected_components_cv2(mask: np.ndarray, min_area: int) -> tuple[np.ndarray, list[Component]] | None:
    try:
        import cv2  # type: ignore
    except Exception:
        return None

    count, raw_labels, stats, centroids = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    labels = np.zeros_like(raw_labels, dtype=np.int32)
    components: list[Component] = []
    next_id = 1
    for raw_id in range(1, count):
        area = int(stats[raw_id, cv2.CC_STAT_AREA])
        if area < min_area:
            continue
        x = int(stats[raw_id, cv2.CC_STAT_LEFT])
        y = int(stats[raw_id, cv2.CC_STAT_TOP])
        width = int(stats[raw_id, cv2.CC_STAT_WIDTH])
        height = int(stats[raw_id, cv2.CC_STAT_HEIGHT])
        labels[raw_labels == raw_id] = next_id
        components.append(
            Component(
                component_id=next_id,
                area=area,
                bbox_x=x,
                bbox_y=y,
                bbox_width=width,
                bbox_height=height,
                centroid_x=float(centroids[raw_id][0]),
                centroid_y=float(centroids[raw_id][1]),
            )
        )
        next_id += 1
    return labels, components


def _connected_components_fallback(mask: np.ndarray, min_area: int) -> tuple[np.ndarray, list[Component]]:
    height, width = mask.shape
    labels = np.zeros((height, width), dtype=np.int32)
    visited = np.zeros((height, width), dtype=bool)
    components: list[Component] = []
    next_id = 1

    for start_y, start_x in np.argwhere(mask):
        if visited[start_y, start_x]:
            continue

        stack = [(int(start_y), int(start_x))]
        pixels: list[tuple[int, int]] = []
        visited[start_y, start_x] = True

        while stack:
            y, x = stack.pop()
            pixels.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    ny = y + dy
                    nx = x + dx
                    if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((ny, nx))

        if len(pixels) < min_area:
            continue

        ys = np.array([p[0] for p in pixels], dtype=np.int32)
        xs = np.array([p[1] for p in pixels], dtype=np.int32)
        labels[ys, xs] = next_id
        components.append(
            Component(
                component_id=next_id,
                area=int(len(pixels)),
                bbox_x=int(xs.min()),
                bbox_y=int(ys.min()),
                bbox_width=int(xs.max() - xs.min() + 1),
                bbox_height=int(ys.max() - ys.min() + 1),
                centroid_x=float(xs.mean()),
                centroid_y=float(ys.mean()),
            )
        )
        next_id += 1

    return labels, components


def connected_components(mask: np.ndarray, min_area: int = 8) -> tuple[np.ndarray, list[Component]]:
    """Label connected foreground regions and remove tiny noise components."""

    if mask.ndim != 2:
        raise ValueError("connected_components expects a 2D mask")
    if min_area < 1:
        raise ValueError("min_area must be at least 1")

    cv2_result = _connected_components_cv2(mask.astype(bool), min_area)
    if cv2_result is not None:
        return cv2_result
    return _connected_components_fallback(mask.astype(bool), min_area)


def segment_fluorescence(
    image: np.ndarray,
    threshold: float | None = None,
    min_area: int = 8,
) -> SegmentationResult:
    """Segment bright mitochondrial fluorescence regions."""

    preprocessed = preprocess_image(image)
    threshold_value = otsu_threshold(preprocessed) if threshold is None else float(threshold)
    raw_mask = preprocessed >= threshold_value
    labels, components = connected_components(raw_mask, min_area=min_area)
    mask = labels > 0
    return SegmentationResult(
        preprocessed=preprocessed,
        threshold=threshold_value,
        mask=mask,
        labels=labels,
        components=components,
    )


def quantify_fluorescence(image: np.ndarray, segmentation: SegmentationResult) -> dict[str, float | int | str]:
    """Extract quantitative fluorescence and simple quality metrics."""

    mask = segmentation.mask
    foreground = image[mask]
    background = image[~mask]
    image_area = int(image.size)
    foreground_area = int(mask.sum())
    object_count = int(len(segmentation.components))

    if foreground_area == 0:
        mean_intensity = 0.0
        total_fluorescence = 0.0
    else:
        mean_intensity = float(foreground.mean())
        total_fluorescence = float(foreground.sum())

    background_mean = float(background.mean()) if background.size else 0.0
    background_std = float(background.std()) if background.size else 0.0
    signal_to_background = float((mean_intensity - background_mean) / (background_std + 1e-6))
    coverage_fraction = float(foreground_area / image_area) if image_area else 0.0

    if foreground_area == 0:
        quality_flag = "no foreground detected"
    elif coverage_fraction < 0.005:
        quality_flag = "very sparse foreground; inspect threshold"
    elif coverage_fraction > 0.70:
        quality_flag = "large foreground fraction; possible over-segmentation"
    elif signal_to_background < 1.0:
        quality_flag = "low contrast; inspect image quality"
    else:
        quality_flag = "usable"

    return {
        "mean_intensity": mean_intensity,
        "total_fluorescence": total_fluorescence,
        "area_pixels": foreground_area,
        "integrated_density": float(mean_intensity * foreground_area),
        "object_count": object_count,
        "coverage_fraction": coverage_fraction,
        "threshold": float(segmentation.threshold),
        "background_mean": background_mean,
        "background_std": background_std,
        "signal_to_background": signal_to_background,
        "quality_flag": quality_flag,
    }


def analyze_image(
    path_or_file: str | Path | BinaryIO | BytesIO,
    image_id: str = "uploaded",
    condition: str = "unknown",
    min_area: int = 8,
) -> dict[str, object]:
    """Run the full image analysis pipeline."""

    image = load_grayscale_image(path_or_file)
    segmentation = segment_fluorescence(image, min_area=min_area)
    metrics = quantify_fluorescence(image, segmentation)
    return {
        "image_id": image_id,
        "condition": condition,
        "image": image,
        "segmentation": segmentation,
        "metrics": metrics,
        "interpretation": interpret_metrics(metrics),
    }


def analyze_records(records: Iterable[ImageRecord], min_area: int = 8) -> pd.DataFrame:
    """Analyze manifest records into a tidy feature table."""

    rows = []
    for record in records:
        result = analyze_image(record.path, image_id=record.image_id, condition=record.condition, min_area=min_area)
        row = {
            "dataset": record.dataset,
            "image_id": record.image_id,
            "condition": record.condition,
            "filename": record.path.name,
            "source_url": record.source_url,
        }
        row.update(result["metrics"])
        rows.append(row)

    table = pd.DataFrame(rows)
    numeric_cols = table.select_dtypes(include=[np.number]).columns
    if table.empty or table[numeric_cols].isna().any().any():
        raise ValueError("Analysis produced empty or NaN metric output")
    return table


def overlay_mask(image: np.ndarray, segmentation: SegmentationResult, alpha: float = 0.45) -> Image.Image:
    """Create an RGB overlay with red mask and yellow component boxes."""

    base = Image.fromarray((np.clip(image, 0.0, 1.0) * 255).astype(np.uint8)).convert("RGB")
    overlay = Image.new("RGB", base.size, (0, 0, 0))
    mask_img = Image.fromarray((segmentation.mask.astype(np.uint8) * 255))
    red = Image.new("RGB", base.size, (255, 40, 40))
    overlay.paste(red, mask=mask_img)
    blended = Image.blend(base, overlay, alpha=alpha)

    draw = ImageDraw.Draw(blended)
    for component in segmentation.components:
        x0 = component.bbox_x
        y0 = component.bbox_y
        x1 = x0 + component.bbox_width - 1
        y1 = y0 + component.bbox_height - 1
        draw.rectangle([x0, y0, x1, y1], outline=(255, 220, 20), width=1)
    return blended


def mask_to_image(segmentation: SegmentationResult) -> Image.Image:
    """Convert a boolean mask to a displayable PIL image."""

    return Image.fromarray((segmentation.mask.astype(np.uint8) * 255))


def preprocessed_to_image(segmentation: SegmentationResult) -> Image.Image:
    """Convert preprocessed grayscale output to a displayable PIL image."""

    arr = (np.clip(segmentation.preprocessed, 0.0, 1.0) * 255).astype(np.uint8)
    return Image.fromarray(arr)


def compare_conditions(metrics_table: pd.DataFrame) -> pd.DataFrame:
    """Build a compact condition-level summary from image metrics."""

    metric_cols = [
        "mean_intensity",
        "total_fluorescence",
        "area_pixels",
        "integrated_density",
        "object_count",
        "coverage_fraction",
        "signal_to_background",
    ]
    return (
        metrics_table.groupby("condition", as_index=False)[metric_cols]
        .mean(numeric_only=True)
        .sort_values("condition")
        .reset_index(drop=True)
    )


def interpret_metrics(metrics: dict[str, float | int | str]) -> str:
    """Return a restrained biological interpretation for one image."""

    area = int(metrics["area_pixels"])
    mean_intensity = float(metrics["mean_intensity"])
    integrated_density = float(metrics["integrated_density"])
    object_count = int(metrics["object_count"])
    quality_flag = str(metrics["quality_flag"])

    if area == 0:
        return (
            "Tidak ada area fluoresensi yang lolos segmentasi. Citra perlu dicek "
            "ulang sebelum ditafsirkan secara biologis."
        )

    return (
        f"Area fluoresensi terdeteksi seluas {area} piksel pada {object_count} komponen. "
        f"Mean intensity {mean_intensity:.3f} dan integrated density {integrated_density:.1f} "
        "dapat digunakan sebagai indikator tidak langsung sinyal/luas struktur mitokondria "
        f"pada citra ini. Status kualitas: {quality_flag}. Hasil ini bukan pengukuran ATP absolut."
    )


def dataset_validation_summary() -> pd.DataFrame:
    """Document why the selected public dataset is feasible for this project."""

    config = DATASET_CONFIG["BBBC053"]
    return pd.DataFrame(
        [
            {
                "criterion": "Sumber publik",
                "evidence": config["source_url"],
                "status": "valid",
            },
            {
                "criterion": "Pemilihan sumber",
                "evidence": (
                    "BBBC dipilih karena langsung menyediakan dataset mitokondria fluoresensi. "
                    "Sumber lain seperti Cell Image Library tidak diperlukan untuk demo setelah "
                    "BBBC053 memenuhi kebutuhan biologis, format, dan sitasi."
                ),
                "status": "valid",
            },
            {
                "criterion": "Relevansi biologis",
                "evidence": config["biology"],
                "status": "valid",
            },
            {
                "criterion": "Format data",
                "evidence": f"Dataset penuh: {config['full_image_format']}; demo lokal: {config['sample_format']}",
                "status": "valid with subset",
            },
            {
                "criterion": "Kelayakan komputasi",
                "evidence": "58 TIFF full-resolution diproses lokal; metode classical CV tidak membutuhkan GPU.",
                "status": "valid",
            },
            {
                "criterion": "Batasan klaim",
                "evidence": "Intensitas fluoresensi diperlakukan sebagai indikator tidak langsung, bukan ATP absolut.",
                "status": "valid",
            },
        ]
    )
