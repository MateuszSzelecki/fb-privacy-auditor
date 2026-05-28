"""Moduł 6: Archwium Emocji (MoodGraph).

Analizuje historię reakcji pod postami i tworzy profil behawioralno-emocjonalny.
"""

import tkinter as tk
from typing import Any, Dict, Optional

from .module_template import BaseModule


class Module(BaseModule):
    title = "Archwium Emocji"

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Analizujemy Twoje reakcje pod postami i komentarzami przez lata.",
            "Korelujemy je z porami dnia i dniami tygodnia.",
            "Budujemy profil emocjonalny, który Facebook może wykorzystać do targetowania.",
            "Ujawnimy, w jakich godzinach jesteś najbardziej skłonny do irytacji lub nostalgii.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Archwium Emocji"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(MoodGraph)"

    def panel_1(self) -> None:
        top_reactions = self.data.get("top_reactions") or [
            "Lubię to", "Super", "Przykro mi", "Wrrr"
        ]
        self.add_list(0, top_reactions, title="Najczęściej używane reakcje")

    def panel_2(self) -> None:
        emotion_by_day = self.data.get("emotion_by_day") or {
            "Pon": 14,
            "Wt": 18,
            "Śr": 12,
            "Czw": 20,
            "Pt": 22,
            "Sob": 10,
            "Niedz": 8,
        }
        self.add_bar_chart(1, emotion_by_day, title="Aktywność emocjonalna wg dnia tygodnia")

    def panel_3(self) -> None:
        reaction_trend = self.data.get("reaction_trend") or {
            "2023-03": 40,
            "2023-04": 55,
            "2023-05": 38,
        }
        self.add_line_chart(2, reaction_trend, title="Trendy reakcji w czasie")

    def panel_4(self) -> None:
        categories = self.data.get("categories") or {
            "Irytacja": 23,
            "Nostalgia": 17,
            "Radość": 12,
        }
        self.add_pie_chart(3, categories, title="Profil emocjonalny")


if __name__ == "__main__":
    module = Module(tk.Tk())
    module.run_console()
