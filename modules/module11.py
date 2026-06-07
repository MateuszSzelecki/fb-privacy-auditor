import os
import json
from collections import Counter
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Tuple

from .module_template import BaseModule


class Module(BaseModule):

    def __init__(self, master: Any, *args: Any, **kwargs: Any) -> None:
        super().__init__(master, *args, **kwargs)
        
        self.data = self.select_and_load_data()

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Prześwietlamy historię Twojej wyszukiwarki pod kątem ludzi i grup.",
            "Analizujemy, w jakich latach najczęściej sprawdzałeś profile innych osób.",
            "Pokazujemy listę osób, które wysłały do Ciebie zaproszenie do znajomych.",
            "Ujawniamy pełną listę osób, którym to Ty wysłałeś zaproszenie.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Widmo Znajomości"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(GhostFollow)"

    @staticmethod
    def fix_encoding(text: str) -> str:
        try:
            return text.encode('latin1').decode('utf-8')
        except Exception:
            return text

    def select_and_load_data(self) -> Dict[str, Any]:
        selected_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        
        if not selected_dir:
            return {
                "top_searched": [],
                "search_trends": {},
                "received_requests": [],
                "sent_requests": []
            }
            
        return self.load_data(selected_dir)

    def load_data(self, data_dir: str) -> Dict[str, Any]:
        result = {
            "top_searched": [],
            "search_trends": {},
            "received_requests": [],
            "sent_requests": []
        }

        search_dir = os.path.join(data_dir, "logged_information", "search")
        history_file = os.path.join(search_dir, "your_search_history.json")
        groups_file = os.path.join(search_dir, "groups_you've_searched_for.json")

        all_searches = []
        years_counter = Counter()

        if os.path.exists(history_file):
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("searches_v2", []):
                        for sub_data in item.get("data", []):
                            txt = sub_data.get("text", "").strip()
                            if txt:
                                all_searches.append(self.fix_encoding(txt))
                        ts = item.get("timestamp")
                        if ts:
                            year = str(datetime.fromtimestamp(ts).year)
                            years_counter[year] += 1
            except Exception:
                pass

        if os.path.exists(groups_file):
            try:
                with open(groups_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("group_search", []):
                        for sub_data in item.get("data", []):
                            txt = sub_data.get("text", "").strip()
                            if txt:
                                all_searches.append(self.fix_encoding(txt) + " (Grupa)")
                        ts = item.get("timestamp")
                        if ts:
                            year = str(datetime.fromtimestamp(ts).year)
                            years_counter[year] += 1
            except Exception:
                pass

        if all_searches:
            result["top_searched"] = Counter(all_searches).most_common(10)
        if years_counter:
            result["search_trends"] = dict(sorted(years_counter.items()))

        friends_dir = os.path.join(data_dir, "connections", "friends")
        if not os.path.exists(friends_dir):
            friends_dir = os.path.join(data_dir, "Connections", "friends")

        received_file = os.path.join(friends_dir, "received_friend_requests.json")
        sent_file = os.path.join(friends_dir, "sent_friend_requests.json")

        if os.path.exists(received_file):
            try:
                with open(received_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    requests_list = data.get("received_requests_v2") or data.get("received_requests") or []
                    
                    for req in requests_list:
                        name = self.fix_encoding(req.get("name", "Nieznajomy"))
                        ts = req.get("timestamp", 0)
                        date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M') if ts else "-"
                        result["received_requests"].append((name, date_str))
            except Exception:
                pass

        if os.path.exists(sent_file):
            try:
                with open(sent_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    requests_list = data.get("sent_requests_v2") or data.get("sent_requests") or []
                    
                    for req in requests_list:
                        name = self.fix_encoding(req.get("name", "Nieznajomy"))
                        ts = req.get("timestamp", 0)
                        date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M') if ts else "-"
                        result["sent_requests"].append((name, date_str))
            except Exception:
                pass

        return result

    def panel_1(self) -> None:
        top_searched = self.data.get("top_searched") or [("Brak danych w bazie profilu", "-")]
        self.add_table(top_searched, title="Najczęściej wyszukiwane frazy", columns=["Osoba / Grupa", "Liczba wyszukiwań"])

    def panel_2(self) -> None:
        search_trends = self.data.get("search_trends") or {"Brak danych": 0}
        self.add_bar_chart(search_trends, title="Intensywność wyszukiwań w latach")

    def panel_3(self) -> None:
        received_requests = self.data.get("received_requests") or [("Brak danych w bazie profilu", "-")]
        self.add_table(received_requests, title="Otrzymane zaproszenia do znajomych", columns=["Kto wysłał", "Data otrzymania"])

    def panel_4(self) -> None:
        sent_requests = self.data.get("sent_requests") or [("Brak danych w bazie profilu", "-")]
        self.add_table(sent_requests, title="Wysłane przez Ciebie zaproszenia", columns=["Do kogo", "Data wysłania"])


if __name__ == "__main__":
    root = tk.Tk()
    module = Module(root)
    module.run_console()
