"""Moduł 8: Słowa Klucze (TagCloud).

Analizuje teksty postów, komentarzy i wiadomości, aby stworzyć profil zainteresowań.
"""

import tkinter as tk
from typing import Any, Dict, Optional

from .module_template import BaseModule


class Module(BaseModule):
    title = "Słowa Klucze"

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Analizujemy teksty Twoich postów, komentarzy i wiadomości pod kątem najczęściej używanych słów.",
            "Pomijamy stop-words i skupiamy się na rzeczownikach oraz przymiotnikach.",
            "Budujemy chmurę tagów oraz kategorie semantyczne zainteresowań.",
            "Pokażemy, w jakie 'szufladki' tematyczne algorytm mógł Cię wrzucić.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Słowa Klucze"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(TagCloud)"

    def panel_1(self) -> None:
        nouns = self.data.get("top_nouns") or [
            "muzyka", "polityka", "podróże", "sport"
        ]
        self.add_list(0, nouns, title="Najpopularniejsze rzeczowniki")

    def panel_2(self) -> None:
        adjectives = self.data.get("top_adjectives") or [
            "ważny", "nowy", "ciekawy", "śmieszny"
        ]
        self.add_list(1, adjectives, title="Najpopularniejsze przymiotniki")

    def panel_3(self) -> None:
        categories = self.data.get("topic_categories") or {
            "Polityka": 18,
            "Technologia": 12,
            "Sport": 9,
            "Finanse": 7,
        }
        self.add_bar_chart(2, categories, title="Kategorie tematyczne")

    def panel_4(self) -> None:
        tag_scores = self.data.get("tag_scores") or {
            "muzyka": 24,
            "kryptowaluty": 16,
            "film": 11,
            "podróże": 14,
        }
        self.add_sorted_list(3, tag_scores, title="Waga tagów", reverse=True)


if __name__ == "__main__":
    module = Module(tk.Tk())
    module.run_console()
