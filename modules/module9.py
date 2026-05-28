"""Moduł 9: Cyfrowy Zegar (LifeTime).

Bada znaczniki czasu aktywności, aby określić Twój cyfrowy rytm dobowy.
"""

import tkinter as tk
from typing import Any, Dict, Optional

from .module_template import BaseModule


class Module(BaseModule):
    title = "Cyfrowy Zegar"

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Analizujemy znaczniki czasu każdej aktywności Facebookowej.",
            "Wyznaczamy Twój cyfrowy rytm dnia i nocny cykl aktywności.",
            "Pokazujemy godziny, w których najczęściej korzystasz z Facebooka.",
            "Ujawnimy, kiedy Twoje konto jest najbardziej aktywne i kiedy najczęściej śpisz.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Cyfrowy Zegar"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(LifeTime)"

    def panel_1(self) -> None:
        active_windows = self.data.get("active_windows") or [
            "21:00-23:00", "08:00-09:00", "14:00-15:00"
        ]
        self.add_list(0, active_windows, title="Najczęstsze okna aktywności")

    def panel_2(self) -> None:
        hour_distribution = self.data.get("hour_distribution") or {
            "0": 2,
            "6": 5,
            "12": 14,
            "18": 28,
            "22": 22,
        }
        self.add_bar_chart(1, hour_distribution, title="Aktywność wg godzin")

    def panel_3(self) -> None:
        timeline = self.data.get("timeline") or {
            "2023-06-01": 13,
            "2023-06-02": 17,
            "2023-06-03": 9,
        }
        self.add_line_chart(2, timeline, title="Aktywność w wybranym okresie")

    def panel_4(self) -> None:
        weekday_activity = self.data.get("weekday_activity") or {
            "Pon": 18,
            "Wt": 15,
            "Śr": 20,
            "Czw": 19,
            "Pt": 22,
            "Sob": 11,
            "Niedz": 9,
        }
        self.add_sorted_list(3, weekday_activity, title="Najaktywniejsze dni tygodnia", reverse=True)


if __name__ == "__main__":
    module = Module(tk.Tk())
    module.run_console()
