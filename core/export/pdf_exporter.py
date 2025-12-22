from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
from pathlib import Path
import re
import pandas as pd
import tempfile

from core.export.chart_images import render_chart_to_image


# -------------------------
# Helpers
# -------------------------

def safe_filename(name: str, max_len: int = 40) -> str:
    name = name.strip()
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r"\s+", "_", name)
    return name[:max_len] or "chat"


def dataframe_to_table(df: pd.DataFrame):
    data = [list(df.columns)] + df.astype(str).values.tolist()

    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ]
        )
    )
    return table


# -------------------------
# Main exporter
# -------------------------

def export_chat_to_pdf(chat: dict, output_path: Path):
    styles = getSampleStyleSheet()
    story = []

    # ---- Header ----
    story.append(Paragraph(chat["name"], styles["Title"]))
    story.append(
        Paragraph(
            f"Exported on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.4 * inch))

    # ---- Questions ----
    for idx, entry in enumerate(chat["history"], start=1):
        story.append(
            Paragraph(f"Q{idx}: {entry['question']}", styles["Heading2"])
        )
        story.append(Spacer(1, 0.2 * inch))

        result = entry.get("result") or {}

        # ---- Executive summary ----
        summary = result.get("summary")
        if summary:
            story.append(Paragraph("<b>Executive summary</b>", styles["Heading4"]))
            story.append(Paragraph(summary, styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))

        # ---- Chart snapshot (NEW) ----
        df = result.get("data")
        chart_type = result.get("chart_type")

        if isinstance(df, pd.DataFrame) and chart_type in {"line", "bar"}:
            with tempfile.NamedTemporaryFile(
                suffix=".png", delete=False
            ) as tmp:
                img_path = Path(tmp.name)

            img = render_chart_to_image(
                df=df,
                chart_type=chart_type,
                output_path=img_path,
            )

            if img and img.exists():
                story.append(Paragraph("<b>Visualization</b>", styles["Heading4"]))
                story.append(Spacer(1, 0.1 * inch))
                story.append(
                    Image(
                        str(img),
                        width=5.5 * inch,
                        height=3.5 * inch,
                        kind="proportional",
                    )
                )
                story.append(Spacer(1, 0.25 * inch))

        # ---- Data table ----
        if isinstance(df, pd.DataFrame) and not df.empty:
            story.append(Paragraph("<b>Results</b>", styles["Heading4"]))
            story.append(Spacer(1, 0.1 * inch))
            story.append(dataframe_to_table(df))
            story.append(Spacer(1, 0.25 * inch))

        # ---- SQL ----
        sql = result.get("sql")
        if sql:
            story.append(Paragraph("<b>SQL</b>", styles["Heading4"]))
            story.append(
                Paragraph(f"<font size=8>{sql}</font>", styles["Code"])
            )
            story.append(Spacer(1, 0.15 * inch))

        # ---- Duration ----
        duration = entry.get("duration")
        if duration is not None:
            story.append(
                Paragraph(
                    f"<i>Processed in {duration} seconds</i>",
                    styles["Italic"],
                )
            )

        story.append(PageBreak())

    # ---- Build ----
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    doc.build(story)