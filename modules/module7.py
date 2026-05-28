"""Moduł 7: Poza Systemem (OffFacebook).

Analizuje aktywność Off-Facebook i zewnętrzne źródła danych przesyłane do Facebooka.
"""

import tkinter as tk
from typing import Any, Dict, Optional

from .module_template import BaseModule


class Module(BaseModule):
    title = "Poza Systemem"

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Przetwarzamy dane z Off-Facebook Activity, czyli wszystko, co Facebook wie o Tobie poza platformą.",
            "Pokazujemy aplikacje i strony, które doniosły Facebookowi o Twoich działaniach.",
            "Ujawnimy zakres szpiegowania z użyciem Facebook Pixel i zewnętrznych skryptów.",
            "Pokażemy, jak duży ruch poza Facebookiem trafia do Meta na Twój temat.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Poza Systemem"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(OffFacebook)"

    def panel_1(self) -> None:
        apps = self.data.get("apps") or [
            "Spotify", "Tinder", "Aplikacja bankowa", "Serwis informacyjny"
        ]
        self.add_list(0, apps, title="Zewnętrzne aplikacje przesyłające dane")

    def panel_2(self) -> None:
        app_counts = self.data.get("app_counts") or {
            "Spotify": 22,
            "Tinder": 15,
            "Bank": 9,
            "News": 18,
        }
        self.add_sorted_list(1, app_counts, title="Liczba zdarzeń z aplikacji", reverse=True)

    def panel_3(self) -> None:
        category_counts = self.data.get("category_counts") or {
            "Zakupy": 12,
            "Rozrywka": 11,
            "Finanse": 7,
            "Informacje": 9,
        }
        self.add_bar_chart(2, category_counts, title="Kategorie aplikacji")

    def panel_4(self) -> None:
        self.add_pie_chart(3, self.data.get("app_type_share") or {
            "Mobile": 55,
            "Desktop": 30,
            "Inne": 15,
        }, title="Udział typów źródeł")


if __name__ == "__main__":
    module = Module(tk.Tk())
    module.run_console()
