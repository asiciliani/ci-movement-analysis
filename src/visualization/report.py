"""
HTML Report generator for Contact Improvisation movement analysis.
Compiles plots, tables, and interaction metrics into a clean, standalone HTML inspection report.
"""

from pathlib import Path
import base64
import pandas as pd
from typing import Optional, Dict, Any


def image_to_base64(img_path: str) -> str:
    """Encodes an image file to base64 string for standalone HTML embedding."""
    with open(img_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    ext = Path(img_path).suffix.lstrip(".").lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{b64}"


def generate_html_report(
    output_html_path: str,
    video_name: str,
    dashboard_img_path: str,
    trajectory_img_path: str,
    phase_summary_img_path: Optional[str] = None,
    df_phase_summary: Optional[pd.DataFrame] = None,
    global_xcorr_info: Optional[Dict[str, Any]] = None,
    video_annotated_relpath: Optional[str] = None
):
    """Generates a self-contained, clean HTML report for inspecting CI movement signals."""
    b64_dashboard = image_to_base64(dashboard_img_path)
    b64_traj = image_to_base64(trajectory_img_path)
    b64_phase = image_to_base64(phase_summary_img_path) if phase_summary_img_path else None

    # Format Phase Summary Table
    table_html = ""
    if df_phase_summary is not None and not df_phase_summary.empty:
        table_html = df_phase_summary.to_html(
            classes="table table-striped table-hover",
            index=False,
            float_format=lambda x: f"{x:.2f}"
        )

    peak_lag_str = ""
    if global_xcorr_info:
        peak_lag = global_xcorr_info.get("peak_lag", 0.0)
        peak_corr = global_xcorr_info.get("peak_corr", 0.0)
        interp = "Simultaneous Movement"
        if peak_lag > 0.05:
            interp = f"Dancer A tends to precede Dancer B by {peak_lag:.2f}s"
        elif peak_lag < -0.05:
            interp = f"Dancer B tends to precede Dancer A by {abs(peak_lag):.2f}s"
        peak_lag_str = f"""
        <div class="card p-3 mb-4 border-primary">
            <h5>Global Time-Lagged Coupling</h5>
            <p class="mb-1"><strong>Peak Lag (τ*):</strong> {peak_lag:+.2f} seconds | <strong>Peak Correlation (R):</strong> {peak_corr:.2f}</p>
            <p class="mb-0 text-muted"><strong>Interpretation:</strong> {interp}</p>
        </div>
        """

    video_tag = ""
    if video_annotated_relpath:
        video_tag = f"""
        <div class="card p-3 mb-4">
            <h5>Annotated Video Inspection</h5>
            <video controls width="100%" style="max-height: 480px; border-radius: 8px;">
                <source src="{video_annotated_relpath}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CI Movement Analysis - {video_name}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f8f9fa; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        .header-box {{ background: #2c3e50; color: white; padding: 25px; border-radius: 8px; margin-bottom: 25px; }}
        .figure-card {{ background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); padding: 20px; margin-bottom: 25px; }}
        img.responsive-img {{ max-width: 100%; height: auto; border-radius: 4px; }}
        table {{ font-size: 0.9rem; }}
    </style>
</head>
<body>
<div class="container py-4">
    <div class="header-box">
        <h2>Contact Improvisation: Movement & Coordination Analysis</h2>
        <p class="lead mb-0">Computational Proof-of-Concept | Video: <code>{video_name}</code></p>
    </div>

    {video_tag}
    {peak_lag_str}

    <div class="figure-card">
        <h4>1. Interpersonal Movement Dynamics Dashboard</h4>
        <p class="text-muted">Synchronized time series: inter-dancer distances, velocities, directional cosine similarity, contact proxies, and lagged cross-correlation.</p>
        <img src="{b64_dashboard}" class="responsive-img" alt="Movement Dynamics Dashboard">
    </div>

    <div class="row">
        <div class="col-md-6">
            <div class="figure-card">
                <h4>2. 2D Spatial Trajectories</h4>
                <p class="text-muted">Floor/camera plane paths of Dancer A (Teal) and Dancer B (Amber).</p>
                <img src="{b64_traj}" class="responsive-img" alt="Spatial Trajectories">
            </div>
        </div>
        {"<div class='col-md-6'><div class='figure-card'><h4>3. Phase-wise Metric Comparison</h4><p class='text-muted'>Comparing kinematics across manually annotated phases.</p><img src='" + b64_phase + "' class='responsive-img' alt='Phase Comparison'></div></div>" if b64_phase else ""}
    </div>

    {"<div class='figure-card'><h4>Manual Annotation Phase Summary</h4>" + table_html + "</div>" if table_html else ""}

    <div class="footer text-center text-muted py-4">
        <small>Contact Improvisation Movement Analysis PoC — Licenciatura Thesis Exploration</small>
    </div>
</div>
</body>
</html>
"""
    Path(output_html_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html)
