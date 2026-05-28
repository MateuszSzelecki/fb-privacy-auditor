"""Moduł 1: Cień Reklamowy (AdShadow).

Ten moduł analizuje dane reklamowe i wyświetla informacje o możliwych dopasowaniach
kontaktów przesłanych do Facebooka.
"""

import tkinter as tk
from typing import Any, Dict, Optional

from .module_template import BaseModule

class Module(BaseModule):
    title = "Cień Reklamowy"

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Sprawdzamy dopasowania pomiędzy danymi kontaktowymi a zewnętrznymi listami reklamodawców.",
            "Szacujemy liczbę firm, które mogły wykorzystać Twój e-mail lub numer telefonu.",
            "Analizujemy liczbę kliknięć reklam związanych z wykrytymi dopasowaniami.",
            "W Twoim przypadku ...",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Cień Reklamowy"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(AdShadow)"

    def panel_1(self) -> None:
        top_companies = self.data.get("top_companies") or [
            "Firma A",
            "Firma B",
            "Firma C",
        ]
        self.add_list(0, top_companies, title="Najbardziej prawdopodobne firmy")

    def panel_2(self) -> None:
        company_counts = self.data.get("company_counts") or {"Firma A": 5, "Firma B": 3, "Firma C": 1}
        self.add_sorted_list(1, company_counts, title="Liczba dopasowań (posortowane)", reverse=True)

    def panel_3(self) -> None:
        pie_data = {
            "Email": int(self.data.get("email_matches", self.data.get("external_matches", 5))),
            "Phone": int(self.data.get("phone_matches", 2)),
        }
        self.add_pie_chart(2, pie_data, title="Typy dopasowań")

    def panel_4(self) -> None:
        clicks_by_month = self.data.get("clicks_by_month") or {"Jan": 3, "Feb": 5, "Mar": 10}
        self.add_bar_chart(3, clicks_by_month, title="Kliknięcia reklam (przybliżone)")


if __name__ == "__main__":
    sample_data = {
        "external_matches": 5,
        "ad_clicks": 18,
        "company_count": 4,
    }
    module = Module(tk.Tk(), data=sample_data)
    module.run_console()
