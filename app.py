# Streamlit arayuzu - donem projesi
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from fuzzy_controller import SulamaFuzzyController

st.set_page_config(page_title="Bitki Sulama Bulanik Kontrol", layout="wide")

st.title("Ev Bitkisi Sulama Kontrolu")
st.caption("Bulanik mantik - scikit-fuzzy")


@st.cache_resource
def get_controller():
    return SulamaFuzzyController()


controller = get_controller()

with st.sidebar:
    st.header("Giris Degerleri")
    nem = st.slider("Toprak nemi (%)", 0, 100, 35)
    sicaklik = st.slider("Ortam sicakligi (C)", 10, 40, 24)
    isik = st.slider("Isik seviyesi (0-100)", 0, 100, 50)
    hesapla = st.button("Hesapla", type="primary", use_container_width=True)

st.subheader("Manuel giris (metin kutusu)")
col1, col2, col3 = st.columns(3)
with col1:
    nem_txt = st.number_input("Nem (%)", 0.0, 100.0, float(nem), key="nem_num")
with col2:
    sic_txt = st.number_input("Sicaklik (C)", 10.0, 40.0, float(sicaklik), key="sic_num")
with col3:
    isik_txt = st.number_input("Isik", 0.0, 100.0, float(isik), key="isik_num")

if hesapla:
    nem_in, sic_in, isik_in = nem, sicaklik, isik
else:
    nem_in, sic_in, isik_in = nem_txt, sic_txt, isik_txt

result = controller.compute(nem_in, sic_in, isik_in)

st.divider()
st.metric("Onerilen sulama suresi (y*)", f"{result.sulama_dakika:.2f} dakika")

st.subheader("Aktif kurallar")
if result.aktif_kurallar:
    for k in result.aktif_kurallar:
        st.write(f"- {k}")
else:
    st.info("Bu giris icin esik uzerinde aktif kural bulunamadi.")

plot_data = controller.membership_plot_data()

fig_inputs, axes = plt.subplots(2, 2, figsize=(10, 7))
axes = axes.flatten()
labels_tr = {
    "nem": ("Toprak nemi (%)", nem_in, result.nem_dereceleri),
    "sicaklik": ("Sicaklik (C)", sic_in, result.sicaklik_dereceleri),
    "isik": ("Isik seviyesi", isik_in, result.isik_dereceleri),
    "sulama": ("Sulama suresi (dk)", result.sulama_dakika, result.sulama_dereceleri),
}
colors = {"kuru": "brown", "orta": "green", "nemli": "blue", "soguk": "cyan", "ilik": "orange",
          "sicak": "red", "az": "gray", "cok": "gold", "kisa": "navy", "uzun": "crimson"}

for ax, (key, (title, val, degrees)) in zip(axes, labels_tr.items()):
    x, terms = plot_data[key]
    for term, mf in terms.items():
        c = colors.get(term, None)
        ax.plot(x, mf, label=term, linewidth=2, color=c)
    ax.axvline(val, color="black", linestyle="--", linewidth=1.5, label=f"giris={val:.1f}")
    ax.set_title(title)
    ax.set_xlabel("Deger")
    ax.set_ylabel("Uyelik derecesi")
    ax.set_ylim(-0.05, 1.1)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig_inputs)
plt.close(fig_inputs)

st.subheader("Durulastirma (centroid)")
try:
    x_out, mf_agg = controller.aggregated_output_mf(nem_in, sic_in, isik_in)
    fig_def, ax_def = plt.subplots(figsize=(8, 4))
    ax_def.fill_between(x_out, mf_agg, alpha=0.4, color="steelblue", label="Birlesik cikis MF")
    ax_def.plot(x_out, mf_agg, color="steelblue", linewidth=2)
    y_star = result.sulama_dakika
    ax_def.axvline(y_star, color="red", linestyle="-", linewidth=2, label=f"y* = {y_star:.2f} dk")
    if mf_agg.sum() > 0:
        cx = np.sum(x_out * mf_agg) / np.sum(mf_agg)
        ax_def.scatter([cx], [0], color="red", s=80, zorder=5)
    ax_def.set_xlabel("Sulama suresi (dakika)")
    ax_def.set_ylabel("Uyelik")
    ax_def.set_title("Agirlik merkezi (centroid)")
    ax_def.legend()
    ax_def.grid(True, alpha=0.3)
    st.pyplot(fig_def)
    plt.close(fig_def)
except Exception:
    st.warning("Birlesik cikis grafigi bu oturumda gosterilemedi; sayisal sonuc gecerlidir.")

st.subheader("Giris uyelik dereceleri (bulaniklastirma)")
c1, c2, c3 = st.columns(3)
with c1:
    st.write("**Nem**")
    for k, v in result.nem_dereceleri.items():
        st.progress(min(1.0, v), text=f"{k}: {v:.2f}")
with c2:
    st.write("**Sicaklik**")
    for k, v in result.sicaklik_dereceleri.items():
        st.progress(min(1.0, v), text=f"{k}: {v:.2f}")
with c3:
    st.write("**Isik**")
    for k, v in result.isik_dereceleri.items():
        st.progress(min(1.0, v), text=f"{k}: {v:.2f}")

st.subheader("Test senaryolari (hizli)")
scenarios = [
    ("Yaz oglen - kuru toprak", 15, 32, 90),
    ("Ilkbahar - orta nem", 50, 22, 55),
    ("Kis - nemli toprak", 85, 14, 20),
    ("Serin aksam - kuru", 20, 18, 30),
]
rows = []
for ad, n, s, i in scenarios:
    r = controller.compute(n, s, i)
    rows.append({"Senaryo": ad, "Nem": n, "Sicaklik": s, "Isik": i, "Sulama (dk)": round(r.sulama_dakika, 2)})
st.table(rows)
