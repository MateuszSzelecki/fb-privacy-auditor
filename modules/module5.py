"""Moduł 5: Widmo Messengera (GhostChat).

Analizuje usunięte wiadomości, foldery spamowe i ukryte ślady konwersacji.
"""

import tkinter as tk
import os
import json
from datetime import datetime, timezone
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

    # archived threads
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

    # messenger structure: Inbox vs Archive vs E2EE (quantity)
    def panel_3(self) -> None:
        folder_counts: dict = self.data.get("threads_count") or {}
        self.add_pie_chart(
            data =folder_counts,
            title="Rozkład konwersacji"
        )

    # devices from your_end-to-end_encryption_enabled_messenger_device.json
    def panel_4(self) -> None:
        devices: dict = self.data.get("mobile_info") or {}
        table_rows: list = []
        for entry in devices:
            ts = entry.get("timestamp")
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            table_rows.append((
                entry.get("name"),
                dt.strftime('%Y-%m-%d %H:%M:%S')
            ))
        self.add_table(
            rows = table_rows,
            columns = ["Urządzanie", "Data dodania"],
            title = "Urządzenia wspierające szyfrowanie"
        )

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
        e2ee_dir: str = os.path.join(messages_path, "e2ee_cutover")

        threads_count: dict = {
            "archived" : self._get_conversation_count(archived_dir),
            "filtered" : self._get_conversation_count(filtered_dir),
            "requests" : self._get_conversation_count(requests_dir),
            "encrypted" : self._get_conversation_count(e2ee_dir),
            "common" : self._get_conversation_count(inbox_dir)
        }

        return threads_count

    def _get_messenger_devices(self, devices_path: str) -> list[dict]:
        if not os.path.exists(devices_path): return []
        with open(devices_path, "r", encoding = "utf-8") as f:
            data: dict = json.load(f)

        res: list = []

        for entry in data:
            timestamp: int = entry.get("timestamp") or 0
            label_values: list = entry.get("label_values")

            for item in label_values:
                label: str = item.get("label")
                if label == "Nazwa": 
                    res.append({
                        "timestamp" : timestamp,
                        "name" : item.get("value")
                    })

        return res

    def analyze(self) -> dict:
        messages_path: str = os.path.join("data", "your_facebook_activity", "messages")
        autofill_path: str = os.path.join(messages_path, "autofill_information.json")
        device_path: str = os.path.join(messages_path, "your_end-to-end_encryption_enabled_messenger_device.json")

        autofill_info: dict = self._get_autofill_info(autofill_path)
        threads_count = self._get_threads_count(messages_path)
        devices = self._get_messenger_devices(device_path)

        res: dict = {
            "archived_count" : threads_count["archived"],
            "autofill_info" : autofill_info,
            "threads_count" : threads_count,
            "mobile_info" : devices
        }

        self.data.update(res)
        return res;

