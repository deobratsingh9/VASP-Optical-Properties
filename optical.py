#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import xml.etree.ElementTree as ET
from scipy.constants import c, hbar, epsilon_0
from matplotlib.ticker import ScalarFormatter

# =========================================================
# USER SETTINGS
# =========================================================
FILES = {
    "DFT": "vasprun.DIAG.xml",
    "RPA": "vasprun.NONE.xml",
    "BSE": "vasprun.BSE.xml",
}

ENERGY_MAX = 8.0          # eV
THICKNESS = 2.512e-10         # m
OUTFILE = "optical_full_pipeline_ALL_properties_FINAL.png"
SCIENTIFIC_THRESHOLD = 1e3   # ✅ auto switch threshold
# =========================================================

# =========================================================
# JOURNAL STYLE
# =========================================================
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 12,
    "legend.fontsize": 10,
    "axes.linewidth": 1.2,
})
# =========================================================


# =========================================================
# AUTO SCIENTIFIC Y‑AXIS FORMATTER
# =========================================================
def auto_scientific_yaxis(ax, data):
    maxval = np.nanmax(np.abs(data))
    if maxval >= SCIENTIFIC_THRESHOLD:
        fmt = ScalarFormatter(useMathText=True)
        fmt.set_powerlimits((0, 0))
        ax.yaxis.set_major_formatter(fmt)
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))


# =========================================================
# VISIBLE SPECTRUM BACKGROUND
# =========================================================
def add_visible_spectrum_background(ax):
    ax.axvspan(0.0, 1.65, color="lightgray", alpha=0.18)
    ax.axvspan(1.65, 1.98, color="#ff0000", alpha=0.18)
    ax.axvspan(1.98, 2.10, color="#ff7f00", alpha=0.18)
    ax.axvspan(2.10, 2.19, color="#ffff00", alpha=0.18)
    ax.axvspan(2.19, 2.48, color="#00ff00", alpha=0.18)
    ax.axvspan(2.48, 2.56, color="#00ffff", alpha=0.18)
    ax.axvspan(2.56, 2.75, color="#0000ff", alpha=0.18)
    ax.axvspan(2.75, 3.26, color="#7f00ff", alpha=0.18)
    ax.axvspan(3.26, ENERGY_MAX, color="#dcd6f7", alpha=0.18)


# =========================================================
# DIELECTRIC TENSOR READER
# =========================================================
def read_dielectric_tensor(xmlfile):
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    diel = next(e for e in root.iter() if e.tag.endswith("dielectricfunction"))

    def read_block(tag):
        blk = next(c for c in diel if c.tag.endswith(tag))
        arr = blk.find(".//array")
        return np.array([[float(x) for x in r.text.split()]
                         for r in arr.findall(".//r")])

    real = read_block("real")
    imag = read_block("imag")

    E = real[:, 0]
    exx, eyy, ezz = real[:, 1], real[:, 2], real[:, 3]
    eps1 = (exx + eyy + ezz) / 3
    eps2 = imag[:, 1:4].mean(axis=1)

    return E, eps1, eps2, exx, ezz


# =========================================================
# OPTICAL TRANSITIONS (BSE)
# =========================================================
def read_optical_transitions(xmlfile):
    tree = ET.parse(xmlfile)
    root = tree.getroot()

    varray = next(
        e for e in root.iter()
        if e.tag.endswith("varray") and e.attrib.get("name") == "opticaltransitions"
    )

    E, f = [], []
    for v in varray.findall(".//v"):
        e, s = map(float, v.text.split())
        E.append(e)
        f.append(s)

    return np.array(E), np.array(f)


# =========================================================
# OPTICAL PIPELINE
# =========================================================
def optical_pipeline(E, eps1, eps2, exx, ezz):
    mag = np.sqrt(eps1**2 + eps2**2)
    n = np.sqrt((mag + eps1) / 2)
    k = np.sqrt((mag - eps1) / 2)

    omega = E * 1.602176634e-19 / hbar
    alpha = 2 * omega * k / c * 1e-2

    delta = np.full_like(alpha, np.nan)
    mask = alpha > 0
    delta[mask] = 1e7 / alpha[mask]

    R = ((n - 1)**2 + k**2) / ((n + 1)**2 + k**2)
    T = (1 - R) * np.exp(-alpha * 1e2 * THICKNESS)

    sigma1 = epsilon_0 * omega * eps2
    sigma2 = epsilon_0 * omega * eps1
    ELF = eps2 / (eps1**2 + eps2**2)

    biref = (
        np.sqrt((np.sqrt(ezz**2 + eps2**2) + ezz) / 2) -
        np.sqrt((np.sqrt(exx**2 + eps2**2) + exx) / 2)
    )

    return dict(
        E=E, eps1=eps1, eps2=eps2,
        n=n, k=k,
        alpha=alpha, delta=delta,
        R=R, T=T,
        sigma1=sigma1, sigma2=sigma2,
        ELF=ELF, biref=biref
    )


# =========================================================
# LOAD DATA
# =========================================================
data = {}
for lbl, f in FILES.items():
    E, e1, e2, exx, ezz = read_dielectric_tensor(f)
    data[lbl] = optical_pipeline(E, e1, e2, exx, ezz)

tE, tf = read_optical_transitions("vasprun.BSE.xml")


# =========================================================
# PLOTTING
# =========================================================
fig, ax = plt.subplots(6, 2, figsize=(7.2, 15.5), constrained_layout=True)
ax = ax.flatten()

STYLES = {
    "DFT": dict(color="#1f77b4", linewidth=2.4),
    "RPA": dict(color="#2ca02c", linewidth=2.8),
    "BSE": dict(color="black", linewidth=3.2),
}

def panel(i, key, title, ylabel, spectrum=False, logy=False, ylim=None):
    allY = []
    for lbl, st in STYLES.items():
        y = data[lbl][key]
        allY.append(y)
        ax[i].plot(data[lbl]["E"], y, label=lbl, **st)

    ax[i].set_xlim(0, ENERGY_MAX)
    ax[i].set_title(title)
    ax[i].set_ylabel(ylabel)
    ax[i].set_xlabel("Photon energy (eV)")

    if spectrum:
        add_visible_spectrum_background(ax[i])

    if logy:
        ax[i].set_yscale("log")
        if ylim:
            ax[i].set_ylim(*ylim)
    else:
        auto_scientific_yaxis(ax[i], np.hstack(allY))

    ax[i].legend(frameon=False)


def panel_eps2_transitions(i):
    E = data["BSE"]["E"]
    eps2 = data["BSE"]["eps2"]

    ax[i].plot(E, eps2, color="black", linewidth=3.2,
               label=r"$\varepsilon_2(\omega)$ (BSE)")
    ax[i].axhline(0, color="black", linewidth=2.0, alpha=0.6)

    mask = (tE <= ENERGY_MAX) & (tf > 0)
    f_norm = tf[mask] / tf[mask].max()

    ax[i].vlines(
        tE[mask], 0,
        0.9 * f_norm * eps2[E <= ENERGY_MAX].max(),
        color="red", linewidth=1.0, alpha=0.6
    )

    add_visible_spectrum_background(ax[i])
    ax[i].set_xlim(0, ENERGY_MAX)
    ax[i].set_ylabel(r"$\varepsilon_2(\omega)$")
    ax[i].set_xlabel("Photon energy (eV)")
    ax[i].legend(frameon=False)


# =========================================================
# PANEL LAYOUT
# =========================================================
panel(0, "eps1", r"$\varepsilon_1(\omega)$", r"$\varepsilon_1$")
panel_eps2_transitions(1)
panel(2, "n", "Refractive index", r"$n$")
panel(3, "k", "Extinction coefficient", r"$k$")
panel(4, "alpha", "Absorption coefficient", r"$\alpha$ (cm$^{-1}$)", spectrum=True)
panel(5, "delta", "Penetration depth", r"$\delta$ (nm)",
      spectrum=True, logy=True, ylim=(1, 1e6))
panel(6, "R", "Reflectivity", r"$R$", spectrum=True)
panel(7, "T", "Transmittance", r"$T$", spectrum=True)
panel(8, "sigma1", "Optical conductivity (real)", r"$\sigma_1$ (S/m)")
ax[8].set_ylim(0, 500000)
panel(9, "sigma2", "Optical conductivity (imag)", r"$\sigma_2$ (S/m)")
panel(10, "ELF", "Energy loss function", r"Im$[-1/\varepsilon(\omega)]$")
ax[10].set_ylim(0, 0.65)
panel(11, "biref", "Birefringence", r"$\Delta n$")

plt.savefig(OUTFILE, dpi=600)
print(f"✅ Final figure written: {OUTFILE}")
