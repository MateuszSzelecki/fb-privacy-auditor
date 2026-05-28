"""Moduł 3: Matryca Relacji (CoreCircle).

Analizuje historię Messengera, częstotliwość interakcji i kto zaczyna rozmowy.
"""

import tkinter as tk
from typing import Any, Dict, Optional

from .module_template import BaseModule


class Module(BaseModule):
    title = "Matryca Relacji"

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Analizujemy Twoje rozmowy w Messengerze: kto pisze pierwszy, jak długo piszecie i ile znaków wymieniacie.",
            "Budujemy algorytmiczny ranking bliskości Twoich kontaktów.",
            "Wykrywamy 'zombie-znajomych' – osoby, z którymi nie rozmawiasz od lat.",
            "Pokazujemy, kto jest dla Facebooka Twoim najważniejszym kontaktem, nawet jeśli Ty o tym nie wiesz.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Matryca Relacji"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(CoreCircle)"

    def panel_1(self) -> None:
        friend_rank = self.data.get("friend_rank") or [
            "Alicja - 98 pkt", "Bartek - 82 pkt", "Kasia - 74 pkt"
        ]
        self.add_list(0, friend_rank, title="Ranking najbliższych kontaktów")

    def panel_2(self) -> None:
        interaction_counts = self.data.get("interaction_counts") or {
            "Alicja": 1245,
            "Bartek": 932,
            "Kasia": 810,
            "Piotr": 24,
        }
        self.add_sorted_list(1, interaction_counts, title="Liczba interakcji", reverse=True)

    def panel_3(self) -> None:
        reaction_counts = self.data.get("reaction_counts") or {
            "Rozmowy rozpoczęte przez Ciebie": 120,
            "Rozmowy rozpoczęte przez drugą stronę": 76,
        }
        self.add_bar_chart(2, reaction_counts, title="Kto zaczyna rozmowy")

    def panel_4(self) -> None:
        zombie_contacts = self.data.get("zombie_contacts") or [
            "Tomek - ostatnia rozmowa 2019", "Magda - brak kontaktu 2 lata", "Paweł - brak odpowiedzi"
        ]
        self.add_list(3, zombie_contacts, title="Zombie-znajomi")


if __name__ == "__main__":
    sample_data = {"friend_rank": ["Alicja - 98 pkt", "Bartek - 82 pkt"]}
    module = Module(tk.Tk(), data=sample_data)
    module.run_console()
