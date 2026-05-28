"""Moduł 2: Geotropy (GeoTracks).

Wyciąga geolokalizacje z historii logowań, powiadomień i zdjęć wysłanych przez Messengera.
"""

import tkinter as tk
from typing import Any, Dict, Optional

from .module_template import BaseModule


class Module(BaseModule):
    title = "Geotropy"

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Wyciągamy dane lokalizacyjne z plików logowania, powiadomień i zdjęć Messenger.",
            "Analizujemy częstotliwość występowania miejsc i sklejamy trasę Twoich aktywności.",
            "Budujemy mapę najczęściej odwiedzanych lokalizacji i sekwencję odwiedzin.",
            "Pokazujemy, jak dokładnie Facebook może odtwarzać Twoje ruchy w realnym świecie.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Geotropy"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(GeoTracks)"

    def panel_1(self) -> None:
        locations = self.data.get("top_locations") or [
            "Dom", "Praca", "Kawiarnia", "Siłownia"
        ]
        self.add_list(0, locations, title="Najczęstsze lokalizacje")

    def panel_2(self) -> None:
        location_counts = self.data.get("location_counts") or {
            "Dom": 135,
            "Praca": 98,
            "Kawiarnia": 42,
            "Siłownia": 28,
        }
        self.add_sorted_list(1, location_counts, title="Liczba wizyt w lokalizacjach", reverse=True)

    def panel_3(self) -> None:
        source_counts = self.data.get("source_counts") or {
            "Logowania": 16,
            "Powiadomienia": 9,
            "Zdjęcia Messenger": 11,
        }
        self.add_pie_chart(2, source_counts, title="Źródła danych lokalizacyjnych")

    def panel_4(self) -> None:
        visits_by_day = self.data.get("visits_by_day") or {
            "Pon": 18,
            "Wt": 14,
            "Śr": 22,
            "Czw": 16,
            "Pt": 20,
            "Sob": 10,
            "Niedz": 5,
        }
        self.add_line_chart(3, visits_by_day, title="Aktywność lokalizacyjna w tygodniu")


if __name__ == "__main__":
    sample_data = {
        "top_locations": ["Dom", "Praca", "Kawiarnia"],
        "location_counts": {"Dom": 25, "Praca": 18, "Kawiarnia": 10},
    }
    module = Module(tk.Tk(), data=sample_data)
    module.run_console()
