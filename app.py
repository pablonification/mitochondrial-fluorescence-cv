from __future__ import annotations

from io import BytesIO
from pathlib import Path
import sys

import pandas as pd
import streamlit as st


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


@st.cache_data
def load_manifest_records():
    return read_sample_manifest(DATA_DIR)


@st.cache_data
def load_sample_metrics() -> pd.DataFrame:
    metrics_path = ROOT / "outputs" / "image_metrics.csv"
    if metrics_path.exists():
        return pd.read_csv(metrics_path)
    return analyze_records(read_sample_manifest(DATA_DIR))


def metric_cards(metrics: dict[str, float | int | str]) -> None:
    cols = st.columns(5)
    cols[0].metric("Mean intensity", f"{float(metrics['mean_intensity']):.3f}")
    cols[1].metric("Total fluorescence", f"{float(metrics['total_fluorescence']):.1f}")
    cols[2].metric("Area", f"{int(metrics['area_pixels'])} px")
    cols[3].metric("Integrated density", f"{float(metrics['integrated_density']):.1f}")
    cols[4].metric("Components", f"{int(metrics['object_count'])}")


def main() -> None:
    st.set_page_config(page_title="Mitochondrial Fluorescence CV", layout="wide")
    st.title("Kuantifikasi Fluoresensi Mitokondria")
    st.caption(
        "Computer vision ringan untuk citra BBBC053 TOM20/AlexaFluor 568. "
        "Output dibatasi sebagai indikator citra tidak langsung, bukan pengukuran ATP absolut."
    )

    records = load_manifest_records()
    sample_metrics = load_sample_metrics()

    with st.sidebar:
        st.header("Input")
        mode = st.radio("Sumber citra", ["Sample BBBC053", "Upload citra"], horizontal=False)
        min_area = st.slider("Minimum area komponen", min_value=1, max_value=100, value=8, step=1)
        uploaded = None
        selected_record = records[0]
        if mode == "Sample BBBC053":
            selected_id = st.selectbox("Sample", [record.image_id for record in records])
            selected_record = next(record for record in records if record.image_id == selected_id)
        else:
            uploaded = st.file_uploader("File PNG/TIFF/JPEG", type=["png", "tif", "tiff", "jpg", "jpeg"])

        st.divider()
        st.markdown("**Dataset**")
        st.link_button("BBBC053", DATASET_CONFIG["BBBC053"]["source_url"])

    if mode == "Upload citra":
        if uploaded is None:
            st.info("Unggah citra fluoresensi grayscale atau RGB untuk dianalisis.")
            return
        image_bytes = uploaded.getvalue()
        result = analyze_image(BytesIO(image_bytes), image_id=uploaded.name, condition="uploaded", min_area=min_area)
        display_name = uploaded.name
    else:
        result = analyze_image(
            selected_record.path,
            image_id=selected_record.image_id,
            condition=selected_record.condition,
            min_area=min_area,
        )
        display_name = f"{selected_record.image_id} ({selected_record.condition})"

    image = result["image"]
    segmentation = result["segmentation"]
    metrics = result["metrics"]

    st.subheader(display_name)
    metric_cards(metrics)

    tabs = st.tabs(["Visualisasi", "Metrik sample", "Validasi dataset", "Interpretasi"])
    with tabs[0]:
        cols = st.columns(4)
        cols[0].image(image, caption="Original grayscale", width="stretch", clamp=True)
        cols[1].image(preprocessed_to_image(segmentation), caption="Preprocessed", width="stretch")
        cols[2].image(mask_to_image(segmentation), caption="Mask", width="stretch")
        cols[3].image(overlay_mask(image, segmentation), caption="Overlay + bounding region", width="stretch")

    with tabs[1]:
        st.dataframe(sample_metrics.round(4), width="stretch", hide_index=True)
        st.dataframe(compare_conditions(sample_metrics).round(4), width="stretch", hide_index=True)

    with tabs[2]:
        st.dataframe(dataset_validation_summary(), width="stretch", hide_index=True)

    with tabs[3]:
        st.write(result["interpretation"])
        st.write(
            "Fluoresensi TOM20/AlexaFluor 568 menandai struktur mitokondria. "
            "Mean intensity, total fluorescence, area, dan integrated density "
            "membantu membandingkan kekuatan sinyal serta luasan foreground antar citra. "
            "Hubungannya ke respirasi sel bersifat proksi: perubahan morfologi atau sinyal "
            "mitokondria dapat mendukung diskusi bioenergetik, tetapi tidak cukup untuk "
            "menghitung produksi ATP absolut."
        )


if __name__ == "__main__":
    main()
