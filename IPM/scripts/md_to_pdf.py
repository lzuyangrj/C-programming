#!/usr/bin/env python3
"""Render a CSNS IPM markdown report to PDF with figures (fpdf2)."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

MATH = [
    (r"\^{12}", "¹²"),
    (r"\^\{12\}", "¹²"),
    (r"\^12", "¹²"),
    (r"\^\{-\}", "⁻"),
    (r"\^\{+\}", "⁺"),
    (r"\^\+", "⁺"),
    (r"_\{x,y\}", "ₓ,ᵧ"),
    (r"_\{x\}", "ₓ"),
    (r"_x", "ₓ"),
    (r"_y", "ᵧ"),
    (r"_\{y\}", "ᵧ"),
    (r"_\{2\}", "₂"),
    (r"_2(?=\^)", "₂"),
    (r"_t", "ₜ"),
    (r"_\{b\}", "b"),
    (r"_\{min\}", "ₘᵢₙ"),
    (r"_min", "ₘᵢₙ"),
    (r"\\lesssim", "≲"),
    (r"\\gtrsim", "≳"),
    (r"\\pm", "±"),
    (r"\\propto", "∝"),
    (r"\\ldots", "…"),
    (r"\\dots", "…"),
    (r"\\sim", "∼"),
    (r"\\approx", "≈"),
    (r"\\times", "×"),
    (r"\\in", "∈"),
    (r"\\Delta", "Δ"),
    (r"\\sigma", "σ"),
    (r"\\mathrm\{mm\}", "mm"),
    (r"\\mathrm\{kW\}", "kW"),
    (r"\\mathrm\{kV\}", "kV"),
    (r"\\mathrm\{G\}", "G"),
    (r"\\mathrm\{T\}", "T"),
    (r"\\mathrm\{MeV\}", "MeV"),
    (r"\\mathrm\{GeV\}", "GeV"),
    (r"\\mathrm\{sc\}", "sc"),
    (r"\\min", "min"),
    (r"\\%", "%"),
    (r"\\,", " "),
    (r"\\;", " "),
    (r"\\quad", " "),
    (r"\\!", ""),
    (r"\\left", ""),
    (r"\\right", ""),
    (r"\\int", "∫"),
    (r"\\text\{([^}]*)\}", r"\1"),
    (r"\\mathrm\{([^}]*)\}", r"\1"),
]


def subst_math(text: str) -> str:
    def inner(expr: str) -> str:
        for pat, repl in MATH:
            expr = re.sub(pat, repl, expr)
        expr = expr.replace("{", "").replace("}", "").replace("\\", "")
        return re.sub(r"\s+", " ", expr).strip()

    text = re.sub(r"\\\((.+?)\\\)", lambda m: inner(m.group(1)), text)
    text = re.sub(r"\$(.+?)\$", lambda m: inner(m.group(1)), text)
    text = re.sub(r"(?<!!)\[`?([^\]`]+)`?\]\([^)]+\)", r"\1", text)
    return text


def drop_appendix(md: str) -> str:
    i = md.find("## Appendix")
    return md[:i].rstrip() + "\n" if i >= 0 else md


def split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_sep(line: str) -> bool:
    cells = split_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells)


def parse_blocks(md: str) -> list[tuple[str, object]]:
    lines = md.splitlines()
    blocks: list[tuple[str, object]] = []
    i = 0
    para: list[str] = []

    def flush() -> None:
        nonlocal para
        if para:
            blocks.append(("p", " ".join(para)))
            para = []

    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip() == "---":
            flush()
            i += 1
            continue
        if line.startswith("# "):
            flush()
            blocks.append(("h1", line[2:].strip()))
        elif line.startswith("## "):
            flush()
            blocks.append(("h2", line[3:].strip()))
        elif line.startswith("### "):
            flush()
            blocks.append(("h3", line[4:].strip()))
        elif line.startswith("!["):
            flush()
            m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
            if m:
                blocks.append(("img", (m.group(1), m.group(2))))
        elif line.startswith("|"):
            flush()
            table = [[c.replace("**", "") for c in split_row(line)]]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not is_sep(lines[i]):
                    table.append([c.replace("**", "") for c in split_row(lines[i])])
                i += 1
            blocks.append(("table", table))
            continue
        elif re.match(r"\d+\. ", line.strip()):
            flush()
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
                while i < len(lines) and lines[i].startswith("   "):
                    items[-1] += " " + lines[i].strip()
                    i += 1
            blocks.append(("ol", items))
            continue
        elif re.match(r"[-*] ", line.strip()):
            flush()
            items = []
            while i < len(lines) and re.match(r"[-*] ", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
                while i < len(lines) and lines[i].startswith("   "):
                    items[-1] += " " + lines[i].strip()
                    i += 1
            blocks.append(("ul", items))
            continue
        else:
            para.append(line.strip())
        i += 1
    flush()
    return blocks


class ReportPDF(FPDF):
    footer_label = "CSNS RCS IPM"

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 8, f"{self.footer_label}  ·  {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)


def write_rich(pdf: ReportPDF, text: str, size: float = 10.5) -> None:
    parts = re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            pdf.set_font("DejaVu", "B", size)
            pdf.write(5.2, part[2:-2])
            pdf.set_font("DejaVu", "", size)
        elif part.startswith("`") and part.endswith("`"):
            pdf.set_font("DejaVu", "", size - 0.5)
            pdf.write(5.2, part[1:-1])
            pdf.set_font("DejaVu", "", size)
        else:
            pdf.set_font("DejaVu", "", size)
            pdf.write(5.2, part)
    pdf.ln(6)


def render(pdf: ReportPDF, blocks: list[tuple[str, object]], root: Path) -> None:
    usable = pdf.w - pdf.l_margin - pdf.r_margin
    for kind, payload in blocks:
        if kind == "h1":
            pdf.set_font("DejaVu", "B", 16)
            pdf.multi_cell(0, 8, str(payload))
            pdf.ln(2)
        elif kind == "h2":
            pdf.ln(3)
            pdf.set_font("DejaVu", "B", 12.5)
            pdf.multi_cell(0, 7, str(payload))
            y = pdf.get_y()
            pdf.set_draw_color(80, 80, 80)
            pdf.line(pdf.l_margin, y, pdf.l_margin + usable, y)
            pdf.ln(3)
        elif kind == "h3":
            pdf.set_font("DejaVu", "B", 11)
            pdf.ln(2)
            pdf.multi_cell(0, 6, str(payload))
            pdf.ln(1)
        elif kind == "p":
            write_rich(pdf, str(payload))
        elif kind == "ol":
            for n, item in enumerate(payload, 1):
                pdf.set_font("DejaVu", "B", 10.5)
                x, y = pdf.get_x(), pdf.get_y()
                pdf.cell(8, 5.2, f"{n}.")
                pdf.set_xy(x + 8, y)
                write_rich(pdf, item)
        elif kind == "ul":
            for item in payload:
                pdf.set_font("DejaVu", "B", 10.5)
                x, y = pdf.get_x(), pdf.get_y()
                pdf.cell(8, 5.2, "•")
                pdf.set_xy(x + 8, y)
                write_rich(pdf, item)
        elif kind == "img":
            _alt, rel = payload
            path = root / rel
            if not path.is_file():
                continue
            if pdf.get_y() > 175:
                pdf.add_page()
            # Keep a caption-sized figure on one page; very tall panels get a new page.
            pdf.image(str(path), w=usable)
            pdf.ln(2)
        elif kind == "table":
            rows: list[list[str]] = payload  # type: ignore[assignment]
            ncols = max(len(r) for r in rows)
            rows = [r + [""] * (ncols - len(r)) for r in rows]
            col_w = usable / ncols
            pdf.set_font("DejaVu", "", 7.4)
            line_h = 4.4
            for ri, row in enumerate(rows):
                # wrap estimate
                max_lines = 1
                wrapped = []
                for cell in row:
                    lines = pdf.multi_cell(col_w, line_h, cell, dry_run=True, output="LINES")
                    wrapped.append(cell)
                    max_lines = max(max_lines, len(lines))
                need = max_lines * line_h + 1.2
                if pdf.get_y() + need > pdf.h - 16:
                    pdf.add_page()
                y0 = pdf.get_y()
                x0 = pdf.l_margin
                for ci, cell in enumerate(row):
                    x = x0 + ci * col_w
                    pdf.set_xy(x, y0)
                    if ri == 0:
                        pdf.set_fill_color(235, 235, 235)
                        pdf.set_font("DejaVu", "B", 7.4)
                        fill = True
                    else:
                        pdf.set_fill_color(255, 255, 255)
                        pdf.set_font("DejaVu", "", 7.4)
                        fill = False
                    pdf.rect(x, y0, col_w, need, style="DF" if fill else "D")
                    pdf.set_xy(x + 0.6, y0 + 0.5)
                    pdf.multi_cell(col_w - 1.2, line_h, cell)
                pdf.set_y(y0 + need)
            pdf.ln(3)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--md", type=Path, default=ROOT / "CSNS_IPM_REPORT.md")
    parser.add_argument("--pdf", type=Path, default=ROOT / "CSNS_IPM_REPORT.pdf")
    parser.add_argument(
        "--footer",
        default="CSNS RCS IPM — e-mode and ion-mode",
        help="Footer label printed with the page number.",
    )
    args = parser.parse_args()

    md = subst_math(drop_appendix(args.md.read_text()))
    blocks = parse_blocks(md)

    pdf = ReportPDF(format="A4", unit="mm")
    pdf.footer_label = args.footer
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_margins(14, 14, 14)
    pdf.add_font("DejaVu", "", FONT)
    pdf.add_font("DejaVu", "B", FONT_B)
    pdf.add_page()
    render(pdf, blocks, args.md.parent)
    args.pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(args.pdf))
    print(f"Wrote {args.pdf} ({args.pdf.stat().st_size} bytes, {pdf.pages_count} pages)")


if __name__ == "__main__":
    main()
