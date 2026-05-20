# Bulanik kontrol - toprak nemi, sicaklik, isik -> sulama suresi (dk)

from dataclasses import dataclass
from typing import Any

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# Evrenler
NEM_UNIVERSE = np.arange(0, 101, 1)
SICAKLIK_UNIVERSE = np.arange(10, 41, 1)
ISIK_UNIVERSE = np.arange(0, 101, 1)
SULAMA_UNIVERSE = np.arange(0, 15.1, 0.1)


def _build_antecedents_consequent():
    nem = ctrl.Antecedent(NEM_UNIVERSE, "nem")
    sicaklik = ctrl.Antecedent(SICAKLIK_UNIVERSE, "sicaklik")
    isik = ctrl.Antecedent(ISIK_UNIVERSE, "isik")
    sulama = ctrl.Consequent(SULAMA_UNIVERSE, "sulama")

    nem["kuru"] = fuzz.trimf(nem.universe, [0, 0, 40])
    nem["orta"] = fuzz.trimf(nem.universe, [25, 50, 75])
    nem["nemli"] = fuzz.trimf(nem.universe, [60, 100, 100])

    sicaklik["soguk"] = fuzz.trimf(sicaklik.universe, [10, 10, 22])
    sicaklik["ilik"] = fuzz.trimf(sicaklik.universe, [18, 25, 32])
    sicaklik["sicak"] = fuzz.trimf(sicaklik.universe, [28, 40, 40])

    isik["az"] = fuzz.trimf(isik.universe, [0, 0, 40])
    isik["orta"] = fuzz.trimf(isik.universe, [25, 50, 75])
    isik["cok"] = fuzz.trimf(isik.universe, [60, 100, 100])

    sulama["kisa"] = fuzz.trimf(sulama.universe, [0, 0, 5])
    sulama["orta"] = fuzz.trimf(sulama.universe, [3, 7.5, 12])
    sulama["uzun"] = fuzz.trimf(sulama.universe, [10, 15, 15])

    return nem, sicaklik, isik, sulama


def _build_rules(nem, sicaklik, isik, sulama):
    rules = [
        ctrl.Rule(nem["kuru"] & sicaklik["sicak"] & isik["cok"], sulama["uzun"]),
        ctrl.Rule(nem["kuru"] & sicaklik["ilik"] & isik["orta"], sulama["uzun"]),
        ctrl.Rule(nem["kuru"] & sicaklik["soguk"] & isik["az"], sulama["orta"]),
        ctrl.Rule(nem["kuru"] & sicaklik["ilik"] & isik["az"], sulama["uzun"]),
        ctrl.Rule(nem["kuru"] & sicaklik["sicak"] & isik["az"], sulama["uzun"]),
        ctrl.Rule(nem["orta"] & sicaklik["sicak"] & isik["cok"], sulama["orta"]),
        ctrl.Rule(nem["orta"] & sicaklik["ilik"] & isik["orta"], sulama["orta"]),
        ctrl.Rule(nem["orta"] & sicaklik["soguk"] & isik["az"], sulama["kisa"]),
        ctrl.Rule(nem["orta"] & sicaklik["ilik"] & isik["cok"], sulama["orta"]),
        ctrl.Rule(nem["nemli"] & sicaklik["soguk"] & isik["az"], sulama["kisa"]),
        ctrl.Rule(nem["nemli"] & sicaklik["ilik"] & isik["orta"], sulama["kisa"]),
        ctrl.Rule(nem["nemli"] & sicaklik["sicak"] & isik["cok"], sulama["kisa"]),
        ctrl.Rule(nem["nemli"] & sicaklik["sicak"] & isik["orta"], sulama["kisa"]),
        ctrl.Rule(nem["kuru"] & sicaklik["soguk"] & isik["orta"], sulama["orta"]),
        ctrl.Rule(nem["nemli"] & sicaklik["ilik"] & isik["cok"], sulama["kisa"]),
        ctrl.Rule(nem["orta"] & sicaklik["sicak"] & isik["az"], sulama["orta"]),
        ctrl.Rule(nem["kuru"] & sicaklik["sicak"] & isik["orta"], sulama["uzun"]),
        ctrl.Rule(nem["nemli"] & sicaklik["soguk"] & isik["cok"], sulama["kisa"]),
    ]
    return rules


@dataclass
class FuzzyResult:
    sulama_dakika: float
    nem_dereceleri: dict[str, float]
    sicaklik_dereceleri: dict[str, float]
    isik_dereceleri: dict[str, float]
    sulama_dereceleri: dict[str, float]
    aktif_kurallar: list[str]


class SulamaFuzzyController:
    def __init__(self):
        self.nem, self.sicaklik, self.isik, self.sulama = _build_antecedents_consequent()
        rules = _build_rules(self.nem, self.sicaklik, self.isik, self.sulama)
        self.system = ctrl.ControlSystem(rules)
        self.sim = ctrl.ControlSystemSimulation(self.system)
        self._rule_labels = self._rule_text_list()

    def _rule_text_list(self) -> list[str]:
        return [
            "R1: IF nem=kuru AND sicaklik=sicak AND isik=cok THEN sulama=uzun",
            "R2: IF nem=kuru AND sicaklik=ilik AND isik=orta THEN sulama=uzun",
            "R3: IF nem=kuru AND sicaklik=soguk AND isik=az THEN sulama=orta",
            "R4: IF nem=kuru AND sicaklik=ilik AND isik=az THEN sulama=uzun",
            "R5: IF nem=kuru AND sicaklik=sicak AND isik=az THEN sulama=uzun",
            "R6: IF nem=orta AND sicaklik=sicak AND isik=cok THEN sulama=orta",
            "R7: IF nem=orta AND sicaklik=ilik AND isik=orta THEN sulama=orta",
            "R8: IF nem=orta AND sicaklik=soguk AND isik=az THEN sulama=kisa",
            "R9: IF nem=orta AND sicaklik=ilik AND isik=cok THEN sulama=orta",
            "R10: IF nem=nemli AND sicaklik=soguk AND isik=az THEN sulama=kisa",
            "R11: IF nem=nemli AND sicaklik=ilik AND isik=orta THEN sulama=kisa",
            "R12: IF nem=nemli AND sicaklik=sicak AND isik=cok THEN sulama=kisa",
            "R13: IF nem=nemli AND sicaklik=sicak AND isik=orta THEN sulama=kisa",
            "R14: IF nem=kuru AND sicaklik=soguk AND isik=orta THEN sulama=orta",
            "R15: IF nem=nemli AND sicaklik=ilik AND isik=cok THEN sulama=kisa",
            "R16: IF nem=orta AND sicaklik=sicak AND isik=az THEN sulama=orta",
            "R17: IF nem=kuru AND sicaklik=sicak AND isik=orta THEN sulama=uzun",
            "R18: IF nem=nemli AND sicaklik=soguk AND isik=cok THEN sulama=kisa",
        ]

    def compute(self, nem_pct: float, sicaklik_c: float, isik_lvl: float) -> FuzzyResult:
        self.sim.input["nem"] = float(np.clip(nem_pct, 0, 100))
        self.sim.input["sicaklik"] = float(np.clip(sicaklik_c, 10, 40))
        self.sim.input["isik"] = float(np.clip(isik_lvl, 0, 100))
        self.sim.compute()

        sulama_out = float(self.sim.output["sulama"])

        nem_deg = self._membership_at(self.nem, nem_pct)
        sic_deg = self._membership_at(self.sicaklik, sicaklik_c)
        isik_deg = self._membership_at(self.isik, isik_lvl)
        sulama_deg = self._membership_at(self.sulama, sulama_out)

        aktif = self._active_rules(nem_deg, sic_deg, isik_deg)

        return FuzzyResult(
            sulama_dakika=sulama_out,
            nem_dereceleri=nem_deg,
            sicaklik_dereceleri=sic_deg,
            isik_dereceleri=isik_deg,
            sulama_dereceleri=sulama_deg,
            aktif_kurallar=aktif,
        )

    def _membership_at(self, antecedent_or_consequent, value: float) -> dict[str, float]:
        out = {}
        for label in antecedent_or_consequent.terms:
            mf = antecedent_or_consequent[label].mf
            idx = int(np.argmin(np.abs(antecedent_or_consequent.universe - value)))
            out[label] = float(mf[idx])
        return out

    def _active_rules(
        self,
        nem_deg: dict[str, float],
        sic_deg: dict[str, float],
        isik_deg: dict[str, float],
        threshold: float = 0.05,
    ) -> list[str]:
        conditions = [
            (0, ("kuru", "sicak", "cok")),
            (1, ("kuru", "ilik", "orta")),
            (2, ("kuru", "soguk", "az")),
            (3, ("kuru", "ilik", "az")),
            (4, ("kuru", "sicak", "az")),
            (5, ("orta", "sicak", "cok")),
            (6, ("orta", "ilik", "orta")),
            (7, ("orta", "soguk", "az")),
            (8, ("orta", "ilik", "cok")),
            (9, ("nemli", "soguk", "az")),
            (10, ("nemli", "ilik", "orta")),
            (11, ("nemli", "sicak", "cok")),
            (12, ("nemli", "sicak", "orta")),
            (13, ("kuru", "soguk", "orta")),
            (14, ("nemli", "ilik", "cok")),
            (15, ("orta", "sicak", "az")),
            (16, ("kuru", "sicak", "orta")),
            (17, ("nemli", "soguk", "cok")),
        ]
        aktif = []
        for idx, (n, s, i) in conditions:
            strength = min(nem_deg.get(n, 0), sic_deg.get(s, 0), isik_deg.get(i, 0))
            if strength >= threshold:
                label = self._rule_labels[idx]
                aktif.append(f"{label} (aktivasyon: {strength:.2f})")
        return aktif

    def membership_plot_data(self) -> dict[str, Any]:
        return {
            "nem": (self.nem.universe, {t: self.nem[t].mf for t in self.nem.terms}),
            "sicaklik": (self.sicaklik.universe, {t: self.sicaklik[t].mf for t in self.sicaklik.terms}),
            "isik": (self.isik.universe, {t: self.isik[t].mf for t in self.isik.terms}),
            "sulama": (self.sulama.universe, {t: self.sulama[t].mf for t in self.sulama.terms}),
        }

    def aggregated_output_mf(
        self, nem_pct: float, sicaklik_c: float, isik_lvl: float
    ) -> tuple[np.ndarray, np.ndarray]:
        universe = np.array(self.sulama.universe, dtype=float)
        aggregated = np.zeros_like(universe)

        nem_deg = self._membership_at(self.nem, nem_pct)
        sic_deg = self._membership_at(self.sicaklik, sicaklik_c)
        isik_deg = self._membership_at(self.isik, isik_lvl)

        rule_map = [
            (("kuru", "sicak", "cok"), "uzun"),
            (("kuru", "ilik", "orta"), "uzun"),
            (("kuru", "soguk", "az"), "orta"),
            (("kuru", "ilik", "az"), "uzun"),
            (("kuru", "sicak", "az"), "uzun"),
            (("orta", "sicak", "cok"), "orta"),
            (("orta", "ilik", "orta"), "orta"),
            (("orta", "soguk", "az"), "kisa"),
            (("orta", "ilik", "cok"), "orta"),
            (("nemli", "soguk", "az"), "kisa"),
            (("nemli", "ilik", "orta"), "kisa"),
            (("nemli", "sicak", "cok"), "kisa"),
            (("nemli", "sicak", "orta"), "kisa"),
            (("kuru", "soguk", "orta"), "orta"),
            (("nemli", "ilik", "cok"), "kisa"),
            (("orta", "sicak", "az"), "orta"),
            (("kuru", "sicak", "orta"), "uzun"),
            (("nemli", "soguk", "cok"), "kisa"),
        ]

        for (n, s, i), out_label in rule_map:
            firing = min(nem_deg[n], sic_deg[s], isik_deg[i])
            if firing <= 0:
                continue
            clipped = np.fmin(firing, self.sulama[out_label].mf)
            aggregated = np.fmax(aggregated, clipped)

        return universe, aggregated


def test_scenarios():
    ctrl_obj = SulamaFuzzyController()
    cases = [
        ("Yaz oglen, kuru toprak", 15, 32, 90),
        ("Ilkbahar, orta nem", 50, 22, 55),
        ("Kis, nemli toprak", 85, 14, 20),
        ("Serin aksam, kuru", 20, 18, 30),
    ]
    for name, n, s, i in cases:
        r = ctrl_obj.compute(n, s, i)
        print(f"{name}: nem={n}, sicaklik={s}, isik={i} -> {r.sulama_dakika:.2f} dk")


if __name__ == "__main__":
    test_scenarios()
