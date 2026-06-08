"""Moduł 5: Widmo Messengera (GhostChat).

Analizuje usunięte wiadomości, foldery spamowe i ukryte ślady konwersacji.
"""

import tkinter as tk
import os
import json
from typing import Any, Dict, Optional

from .module_template import BaseModule


class Module(BaseModule):

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

    # archived threads - statistics
    def panel_1(self) -> None:
        archived_count = self.data.get("archived_count")
        self.add_kpi_card(
            0,
            value=str(archived_count),
            title="Liczba zarchiwizowanych konwersacji",
            subtitle="Są to konwersacje i grupy, które nie wyświetlają się już w aplikacji, ale ich wiadomości dalej widnieją w bazie danych",
        )

    # autofill information
    def panel_2(self) -> None:
        autofill: dict = self.data.get("autofill_info") or {}
        table_rows: list = []
        for key, value in autofill.items():
            table_rows.append((key, value))

        self.add_table(
            rows = table_rows,
            title = "Automatyczne wypełnianie formularzy",
            columns = ["Typ danej", "Wartość"],
            col_widths = [ 140, 800]
        )

    # your messenger structure: Inbox vs Archive vs E2EE (quantity)
    def panel_3(self) -> None:
        folder_counts = self.data.get("folder_counts") or {
            "Spam": 14,
            "Inne": 6,
            "Usunięte": 9,
        }
        self.add_pie_chart(folder_counts, title="Rozkład ukrytych wiadomości")

    # devices from your_end-to-end_encryption_enabled_messenger_device.json
    def panel_4(self) -> None:
        removal_trend = self.data.get("removal_trend") or {
            "2021": 5,
            "2022": 12,
            "2023": 8,
        }
        self.add_line_chart(removal_trend, title="Trend usuwania wiadomości")

    def _get_conversation_count(self, dirpath: str) -> int:
        if not os.path.exists(dirpath): return 0
        return len(os.listdir(dirpath))

    def _get_autofill_info(self, filepath: str) -> dict:
        if not os.path.exists(filepath): return {}
        with open(filepath, "r", encoding = "utf-8") as f:
            data: dict = json.load(f)

        autofill: dict = data.get("autofill_information_v2") or {}
        return autofill

    def _get_threads_count(self, messages_path: str) -> dict:
        archived_dir: str = os.path.join(messages_path, "archived_threads")
        filtered_dir: str = os.path.join(messages_path, "filtered_threads")
        requests_dir: str = os.path.join(messages_path, "message_requests")
        inbox_dir: str = os.path.join(messages_path, "inbox")

        threads_count: dict = {
            "archived" : self._get_conversation_count(archived_dir),
            "filtered" : self._get_conversation_count(filtered_dir),
            "requests" : self._get_conversation_count(requests_dir),
            "common" : self._get_conversation_count(inbox_dir)
        }

        return threads_count

    def analyze(self) -> dict:
        messages_path: str = os.path.join("data", "your_facebook_activity", "messages")
        autofill_path: str = os.path.join(messages_path, "autofill_information.json")

        autofill_info: dict = self._get_autofill_info(autofill_path)
        threads_count = self._get_threads_count(messages_path)

        res: dict = {
            "archived_count" : threads_count["archived"],
            "autofill_info" : autofill_info
        }

        self.data.update(res)
        return res;

if __name__ == "__main__":
    module = Module(tk.Tk())
    module.run_console()
