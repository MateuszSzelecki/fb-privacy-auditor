"""Moduł 2: Geotropy (GeoTracks).

Analizuje geolokalizację użytkownika na podstawie historii aktywności sesji.
"""

import os
import json
from datetime import datetime
from collections import Counter, defaultdict
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict

from .module_template import BaseModule


class Module(BaseModule):

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Analizujemy historię Twoich logowań i aktywności sesji konta.",
            "Wychwytujemy miasto, region oraz kraj każdego połączenia z Facebookiem.",
            "Sprawdzamy unikalną listę fizycznych miejsc, z których korzystałeś z aplikacji.",
            "Wizualizujemy trasy Twojego ruchu i ujawniamy, jak Facebook śledzi Cię w świecie realnym.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Geotropy"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(GeoTracks)"

    def napraw_tekst(self, tekst: str) -> str:
        if isinstance(tekst, str):
            try:
                return tekst.encode('latin1').decode('utf-8')
            except Exception:
                return tekst
        return tekst

    def analyze(self) -> dict:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        target_file = os.path.join(base_path, "security_and_login_information", "account_activity.json")

        if not os.path.exists(target_file):
            fallback_results = {
                "summary": "Nie odnaleziono pliku 'account_activity.json' w folderze security_and_login_information.",
                "details": {}
            }
            self.setup_fallback_data()
            return fallback_results

        try:
            with open(target_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            activity_list = []
            if isinstance(raw_data, list):
                activity_list = raw_data
            elif isinstance(raw_data, dict) and "account_activity_v2" in raw_data:
                activity_list = raw_data["account_activity_v2"]

            if not activity_list:
                fallback_results = {
                    "summary": "Plik historii logowań jest pusty lub ma nieprawidłową strukturę.",
                    "details": {}
                }
                self.setup_fallback_data()
                return fallback_results

            parsed_locations = []
            for item in activity_list:
                if not isinstance(item, dict):
                    continue

                timestamp = item.get("timestamp")
                city = item.get("city")
                if not timestamp or not city:
                    continue

                city_clean = self.napraw_tekst(city).strip()
                # Pomijamy wpisy bez nazwy miasta
                if not city_clean or city_clean.lower() == "null" or city_clean.lower() == "none":
                    continue

                region = item.get("region", "Nieznany")
                region_clean = self.napraw_tekst(region).strip()

                parsed_locations.append({
                    "timestamp": int(timestamp),
                    "city": city_clean,
                    "region": region_clean
                })

            if not parsed_locations:
                fallback_results = {
                    "summary": "W historii logowań nie odnaleziono poprawnych informacji o geolokalizacji.",
                    "details": {}
                }
                self.setup_fallback_data()
                return fallback_results

            total_logins = len(parsed_locations)

            # 1. Unikalne miasta
            unique_cities = set(c["city"] for c in parsed_locations)
            total_cities = len(unique_cities)

            # 2. Statystyki miast (Tabela)
            loc_counter = Counter((c["city"], c["region"]) for c in parsed_locations)
            top_locations_table = []
            for (city, region), count in loc_counter.most_common():
                pct = f"{(count / total_logins) * 100:.1f}%"
                top_locations_table.append((city, region, count, pct))

            # 3. Aktywność na przestrzeni lat (Wykres liniowy)
            year_counts = defaultdict(int)
            for c in parsed_locations:
                dt = datetime.fromtimestamp(c["timestamp"])
                year_counts[str(dt.year)] += 1
            sorted_years = sorted(year_counts.keys())
            visits_by_year = {yr: year_counts[yr] for yr in sorted_years}

            # 4. Udział logowań z poszczególnych miast (Wykres kołowy)
            city_counter = Counter(c["city"] for c in parsed_locations)
            city_share = {}
            sorted_cities = city_counter.most_common()
            limit_top = 4
            for i, (city, count) in enumerate(sorted_cities):
                if i < limit_top:
                    city_share[city] = count
                else:
                    city_share["Inne"] = city_share.get("Inne", 0) + count

            # Zapisz w self.data
            self.data["total_cities"] = total_cities
            self.data["top_locations"] = top_locations_table
            self.data["visits_by_year"] = visits_by_year
            self.data["location_counts"] = city_share

            summary_text = (
                f"Przeanalizowano łącznie {total_logins} sesji aktywności Twojego konta na Facebooku.\n"
                f"System Meta zarejestrował połączenia z {total_cities} różnych miast.\n"
                f"Najczęstszą lokalizacją logowań było miasto '{sorted_cities[0][0]}' ({sorted_cities[0][1]} logowań)."
            )

            return {
                "summary": summary_text,
                "details": {}
            }

        except Exception as e:
            fallback_results = {
                "summary": f"Błąd krytyczny podczas przetwarzania historii logowań:\n{e}",
                "details": {}
            }
            self.setup_fallback_data()
            return fallback_results

    def setup_fallback_data(self) -> None:
        self.data["total_cities"] = 0
        self.data["top_locations"] = [("Brak danych", "-", 0, "0%")]
        self.data["visits_by_year"] = {"2026": 0}
        self.data["location_counts"] = {"Brak danych": 1}

    def panel_1(self) -> None:
        # KPI: Liczba odwiedzonych miast
        total = self.data.get("total_cities", 0)
        self.add_kpi_card(
            0,
            value=str(total),
            title="Liczba odwiedzonych miast",
            subtitle="Liczba unikalnych miast na świecie, z których logowałeś się na Facebooka. Te dane są nieustannie gromadzone do analizy Twoich podróży."
        )

    def panel_2(self) -> None:
        # Tabela szczegółowa
        top_locations = self.data.get("top_locations") or []
        self.add_table(
            1,
            rows=top_locations,
            title="Historia geolokalizacji sesji konta",
            columns=["Miasto", "Województwo / Region", "Liczba logowań", "Udział procentowy"]
        )

    def panel_3(self) -> None:
        # Wykres liniowy: aktywność w latach
        visits_by_year = self.data.get("visits_by_year") or {"2026": 0}
        self.add_line_chart(
            2,
            x=visits_by_year,
            title="Aktywność lokalizacyjna w latach"
        )

    def panel_4(self) -> None:
        # Wykres kołowy: udział miast
        location_counts = self.data.get("location_counts") or {"Brak danych": 1}
        self.add_pie_chart(
            3,
            data=location_counts,
            title="Podział zarejestrowanych wizyt według miast"
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1024x768")
    root.title("Testowanie Modułu 2 - Geotropy")
    
    module = Module(root)
    module.pack(fill="both", expand=True)
    module.show_analysis()
    
    root.mainloop()
