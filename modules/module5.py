"""Moduł 5: Widmo Messengera (GhostChat).

Analizuje usunięte wiadomości, foldery spamowe i ukryte ślady konwersacji.
"""

import tkinter as tk
from typing import Any, Dict, Optional

from .module_template import BaseModule


class Module(BaseModule):
    title = "Widmo Messengera"

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Przeszukujemy logi Messengera pod kątem usuniętych i ukrytych wiadomości.",
            "Wydobywamy statystyki dotyczące cofniętych wiadomości i folderów spam.",
            "Ujawnimy interakcje, które Facebook trzyma w ukryciu.",
            "Pokażemy, ile wiadomości mogłeś usunąć lub pominąć przez przypadek.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Widmo Messengera"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(GhostChat)"

    def panel_1(self) -> None:
        deleted_messages = self.data.get("deleted_messages") or [
            "Usunięta rozmowa z Karoliną", "Cofnięta wiadomość do Adama"
        ]
        self.add_list(0, deleted_messages, title="Usunięte/wygasłe wiadomości")

    def panel_2(self) -> None:
        hidden_senders = self.data.get("hidden_senders") or {
            "Nieznajomy 1": 12,
            "Spam Bot": 8,
            "Inny kontakt": 3,
        }
        self.add_sorted_list(1, hidden_senders, title="Ukryte wiadomości według nadawcy", reverse=True)

    def panel_3(self) -> None:
        folder_counts = self.data.get("folder_counts") or {
            "Spam": 14,
            "Inne": 6,
            "Usunięte": 9,
        }
        self.add_pie_chart(2, folder_counts, title="Rozkład ukrytych wiadomości")

    def panel_4(self) -> None:
        removal_trend = self.data.get("removal_trend") or {
            "2021": 5,
            "2022": 12,
            "2023": 8,
        }
        self.add_line_chart(3, removal_trend, title="Trend usuwania wiadomości")


if __name__ == "__main__":
    module = Module(tk.Tk())
    module.run_console()
