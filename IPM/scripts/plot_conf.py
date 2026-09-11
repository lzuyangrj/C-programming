#!/usr/bin/env python3
"""Shared matplotlib style for CSNS IPM plots (Helvetica / TeX / inward ticks)."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
from matplotlib.figure import Figure
from matplotlib.legend import Legend

# Unicode compounds must be replaced before their shorter pieces (σ_x before σ).
_UNICODE_TO_TEX = (
    ("H₂O⁺", r"H$_2$O$^+$"),
    ("H₂⁺", r"H$_2^+$"),
    ("N₂⁺", r"N$_2^+$"),
    ("e−", r"e$^{-}$"),
    ("e⁻", r"e$^{-}$"),
    ("Δy", r"$\Delta y$"),
    ("Δx", r"$\Delta x$"),
    ("Δσ", r"$\Delta\sigma$"),
    ("σ_off", r"$\sigma_{\mathrm{off}}$"),
    ("σ_on", r"$\sigma_{\mathrm{on}}$"),
    ("σ_init", r"$\sigma_{\mathrm{init}}$"),
    ("σ_x", r"$\sigma_x$"),
    ("σ_y", r"$\sigma_y$"),
    ("×", r"$\times$"),
    ("±", r"$\pm$"),
    ("−", r"$-$"),
    ("σ", r"$\sigma$"),
    ("Δ", r"$\Delta$"),
)

_INT_KEYS = {
    "b_gs",
    "power_kw",
    "sigma_x_mm",
    "voltage_kv",
    "dx_mm",
    "dy_mm",
    "n_sc_on",
    "n_sc_off",
    "n_all_on",
    "n_all_off",
}
_SKIP_KEYS = {"family", "beam", "species", "species_label", "slug", "case"}

_WRAP_INSTALLED = False


def texify(s: str) -> str:
    """Make a label safe for matplotlib text.usetex=True. Idempotent."""
    if not s or not mpl.rcParams.get("text.usetex"):
        return s
    for src, dst in _UNICODE_TO_TEX:
        s = s.replace(src, dst)
    parts = s.split("$")
    for i in range(0, len(parts), 2):
        seg = parts[i]
        out: list[str] = []
        for j, ch in enumerate(seg):
            if ch in "_&#" and (j == 0 or seg[j - 1] != "\\"):
                out.append("\\" + ch)
            elif ch == "%" and (j == 0 or seg[j - 1] != "\\"):
                out.append(r"\%")
            else:
                out.append(ch)
        parts[i] = "".join(out)
    return "$".join(parts)


def _maybe_texify(value):
    if isinstance(value, str):
        return texify(value)
    return value


def _install_texify_wrappers() -> None:
    """Route axis / legend / colorbar strings through texify when usetex is on."""
    global _WRAP_INSTALLED
    if _WRAP_INSTALLED:
        return
    _WRAP_INSTALLED = True

    _set_title = Axes.set_title
    _set_xlabel = Axes.set_xlabel
    _set_ylabel = Axes.set_ylabel
    _legend = Axes.legend
    _suptitle = Figure.suptitle
    _cb_label = Colorbar.set_label
    _leg_set_title = Legend.set_title

    def set_title(self, label, *args, **kwargs):
        return _set_title(self, _maybe_texify(label), *args, **kwargs)

    def set_xlabel(self, xlabel, *args, **kwargs):
        return _set_xlabel(self, _maybe_texify(xlabel), *args, **kwargs)

    def set_ylabel(self, ylabel, *args, **kwargs):
        return _set_ylabel(self, _maybe_texify(ylabel), *args, **kwargs)

    def legend(self, *args, **kwargs):
        for container in (self.lines, self.patches, self.collections, self.containers):
            for artist in container:
                lab = artist.get_label()
                if lab and not str(lab).startswith("_"):
                    artist.set_label(texify(str(lab)))
        if args:
            args = list(args)
            if len(args) >= 2 and args[1] is not None:
                args[1] = [texify(str(x)) for x in args[1]]
            args = tuple(args)
        if "title" in kwargs:
            kwargs["title"] = _maybe_texify(kwargs["title"])
        if "labels" in kwargs and kwargs["labels"] is not None:
            kwargs["labels"] = [texify(str(x)) for x in kwargs["labels"]]
        return _legend(self, *args, **kwargs)

    def suptitle(self, t, *args, **kwargs):
        return _suptitle(self, _maybe_texify(t), *args, **kwargs)

    def cb_set_label(self, label, *args, **kwargs):
        return _cb_label(self, _maybe_texify(label), *args, **kwargs)

    def legend_set_title(self, title, *args, **kwargs):
        return _leg_set_title(self, _maybe_texify(title), *args, **kwargs)

    Axes.set_title = set_title
    Axes.set_xlabel = set_xlabel
    Axes.set_ylabel = set_ylabel
    Axes.legend = legend
    Figure.suptitle = suptitle
    Colorbar.set_label = cb_set_label
    Legend.set_title = legend_set_title


def plot_conf() -> None:
    """Apply the paper matplotlib rc (Helvetica, usetex, inward ticks, cycles)."""
    mpl.rcParams["font.family"] = "sans-serif"
    mpl.rcParams["font.size"] = 16
    mpl.rcParams["xtick.direction"] = "in"
    mpl.rcParams["ytick.direction"] = "in"
    mpl.rcParams["text.usetex"] = True
    mpl.rcParams["xtick.top"] = True
    mpl.rcParams["ytick.right"] = True

    font = {"size": 16, "family": "sans-serif", "sans-serif": ["Helvetica"]}
    color_cycle = ["b", "r", "g", "k", "m", "y", "c"]
    linestyle_cycle = [
        "-",
        "--",
        "-.",
        ":",
        (0, (5, 2, 5, 2)),
        (0, (10, 2, 5, 2, 2, 2)),
        (0, (12, 2, 2, 2)),
    ]
    # helvet + sfdefault so usetex text matches the requested Helvetica sans.
    text = {
        "usetex": True,
        "latex.preamble": "\n".join(
            [
                r"\usepackage[T1]{fontenc}",
                r"\usepackage{helvet}",
                r"\renewcommand{\familydefault}{\sfdefault}",
                r"\usepackage{siunitx}",
                r"\usepackage{sfmath}",
                r"\sisetup{detect-family = true}",
                r"\usepackage{amsmath}",
            ]
        ),
    }
    tick = {
        "labelsize": 16,
        "major.width": 1,
        "major.size": 8,
        "minor.width": 1,
        "minor.size": 4,
        "minor.visible": True,
        "direction": "in",
    }
    mpl.rc("text", **text)
    mpl.rc("font", **font)
    mpl.rc(("xtick", "ytick"), **tick)
    mpl.rc("lines", linewidth=1.5, color="r")
    mpl.rc(
        "axes",
        prop_cycle=(cycler("color", color_cycle) + cycler("linestyle", linestyle_cycle)),
    )
    mpl.rc(
        "legend",
        fontsize=16,
        labelspacing=0.1,
        frameon=True,
        fancybox=False,
        edgecolor="k",
        facecolor="None",
    )
    mpl.rc("figure", figsize=(6, 4.5))
    mpl.rc("figure.subplot", bottom=0.12)
    mpl.rc("figure.subplot", top=0.88)
    mpl.rc("figure.subplot", left=0.14)
    mpl.rc("figure.subplot", right=0.90)
    mpl.rc("axes", labelpad=1)
    plt.rcParams["xtick.top"] = True
    plt.rcParams["ytick.right"] = True
    _install_texify_wrappers()


def load_summary(path: str | Path) -> list[dict]:
    """Load a summary CSV and coerce numeric columns used by the plotters."""
    path = Path(path)
    if not path.is_file():
        return []
    with path.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        for key, val in list(row.items()):
            if val is None or val == "" or key in _SKIP_KEYS:
                continue
            if key in _INT_KEYS:
                row[key] = int(float(val))
                continue
            try:
                row[key] = float(val)
            except ValueError:
                continue
    return rows
