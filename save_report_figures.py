# Rapor grafikleri (PNG)

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from fuzzy_controller import SulamaFuzzyController

FIG_DIR = Path(__file__).resolve().parent / "rapor_gorselleri"


def save_membership_plots(ctrl: SulamaFuzzyController):
    data = ctrl.membership_plot_data()
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    titles = {
        "nem": "Toprak nemi (%)",
        "sicaklik": "Sicaklik (C)",
        "isik": "Isik seviyesi",
        "sulama": "Sulama suresi (dk)",
    }
    for ax, (key, (x, terms)) in zip(axes.flatten(), data.items()):
        for term, mf in terms.items():
            ax.plot(x, mf, label=term, linewidth=2)
        ax.set_title(titles[key])
        ax.set_xlabel("Deger")
        ax.set_ylabel("Uyelik")
        ax.set_ylim(-0.05, 1.1)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "uyelik_fonksiyonlari.png", dpi=150)
    plt.close(fig)


def save_defuzz_example(ctrl: SulamaFuzzyController):
    nem, sic, isik = 15, 32, 90
    r = ctrl.compute(nem, sic, isik)
    x, mf = ctrl.aggregated_output_mf(nem, sic, isik)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.fill_between(x, mf, alpha=0.4, color="steelblue")
    ax.plot(x, mf, color="steelblue", linewidth=2, label="Birlesik cikis")
    ax.axvline(r.sulama_dakika, color="red", linewidth=2, label=f"y* = {r.sulama_dakika:.2f} dk")
    ax.set_xlabel("Sulama suresi (dakika)")
    ax.set_ylabel("Uyelik")
    ax.set_title("Durulastirma (centroid) - Yaz oglen senaryosu")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.savefig(FIG_DIR / "durulastirma_ornek.png", dpi=150)
    plt.close(fig)


def save_test_chart(ctrl: SulamaFuzzyController):
    cases = [
        ("Yaz", 15, 32, 90),
        ("Ilkbahar", 50, 22, 55),
        ("Kis", 85, 14, 20),
        ("Aksam", 20, 18, 30),
    ]
    labels, values = [], []
    for ad, n, s, i in cases:
        r = ctrl.compute(n, s, i)
        labels.append(ad)
        values.append(r.sulama_dakika)

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, values, color=["#e74c3c", "#2ecc71", "#3498db", "#f39c12"])
    ax.set_ylabel("Sulama suresi (dk)")
    ax.set_title("Test senaryolarina gore cikis")
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.2, f"{v:.2f}", ha="center", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    fig.savefig(FIG_DIR / "test_sonuclari.png", dpi=150)
    plt.close(fig)


def main():
    FIG_DIR.mkdir(exist_ok=True)
    ctrl = SulamaFuzzyController()
    save_membership_plots(ctrl)
    save_defuzz_example(ctrl)
    save_test_chart(ctrl)
    print(f"Gorseller kaydedildi: {FIG_DIR}")


if __name__ == "__main__":
    main()
