"""Moduł 6: Archiwum Emocji (MoodGraph).

Analizuje historię reakcji pod postami i komentarzami na przestrzeni lat.
"""

import os
import json
from datetime import datetime
from collections import Counter, defaultdict
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict

from .module_template import BaseModule

# Mapowanie różnych wariantów tekstowych na jednolite identyfikatory reakcji
REACTION_MAP = {
    "like": "LIKE",
    "lubi\u00c5\u0099 to!": "LIKE",
    "lubię to!": "LIKE",
    
    "love": "LOVE",
    "super": "LOVE",
    
    "haha": "HAHA",
    "ha ha": "HAHA",
    
    "wow": "WOW",
    
    "sorry": "SORRY",
    "sad": "SORRY",
    "przykro mi": "SORRY",
    
    "anger": "ANGER",
    "angry": "ANGER",
    "wrrr": "ANGER",
    "wrr": "ANGER",
    
    "care": "CARE",
    "trzymaj się": "CARE",
    "wsparcie": "CARE"
}

# Nazwy reakcji wyświetlane użytkownikowi
REACTION_DISPLAY_NAMES = {
    "LIKE": "Lubię to!",
    "LOVE": "Super",
    "HAHA": "Haha",
    "WOW": "Wow",
    "SORRY": "Przykro mi",
    "ANGER": "Wrrr",
    "CARE": "Trzymaj się"
}

# Kategorie emocjonalne grupujące reakcje
def get_emotional_category(reaction_type: str) -> str:
    if reaction_type in ("LOVE", "HAHA"):
        return "Radość / Sympatia"
    elif reaction_type == "LIKE":
        return "Aprobata"
    elif reaction_type == "WOW":
        return "Zaskoczenie"
    elif reaction_type in ("SORRY", "CARE"):
        return "Smutek / Empatia"
    elif reaction_type == "ANGER":
        return "Gniew / Irytacja"
    else:
        return "Inne"


class Module(BaseModule):

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
        return "Archiwum Emocji"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(MoodGraph)"

    def napraw_tekst(self, tekst: str) -> str:
        if isinstance(tekst, str):
            try:
                return tekst.encode('latin1').decode('utf-8')
            except Exception:
                return tekst
        return tekst

    def analyze(self) -> dict:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        target_dir = os.path.join(base_path, "your_facebook_activity", "comments_and_reactions")

        if not os.path.exists(target_dir):
            # Fallback dla braku danych
            fallback_results = {
                "summary": "Nie odnaleziono folderu z danymi reakcji. Upewnij się, że paczka danych została rozpakowana do folderu 'data'.",
                "details": {}
            }
            self.setup_fallback_data()
            return fallback_results

        # Znajdź pliki pasujące do likes_and_reactions*.json
        json_files = []
        for f in os.listdir(target_dir):
            if f.startswith("likes_and_reactions") and f.endswith(".json"):
                json_files.append(os.path.join(target_dir, f))

        if not json_files:
            fallback_results = {
                "summary": "Nie odnaleziono plików z reakcjami (np. likes_and_reactions.json) w folderze comments_and_reactions.",
                "details": {}
            }
            self.setup_fallback_data()
            return fallback_results

        all_reactions = []
        for file_path in json_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if not isinstance(data, list):
                    continue
                    
                for item in data:
                    if not isinstance(item, dict):
                        continue
                        
                    timestamp = item.get("timestamp")
                    if not timestamp:
                        continue
                        
                    # Format A (label_values)
                    reaction_val = None
                    if "label_values" in item:
                        for lv in item["label_values"]:
                            if lv.get("label") == "Reakcja":
                                reaction_val = lv.get("value")
                                break
                    # Format B (data -> reaction -> reaction)
                    elif "data" in item:
                        for entry in item["data"]:
                            if "reaction" in entry:
                                reaction_val = entry["reaction"].get("reaction")
                                break
                                
                    if reaction_val:
                        reaction_val_clean = self.napraw_tekst(reaction_val).strip()
                        all_reactions.append({
                            "timestamp": int(timestamp),
                            "reaction_raw": reaction_val_clean
                        })
            except Exception as e:
                print(f"Błąd przy wczytywaniu pliku {file_path}: {e}")

        # Mapowanie i filtrowanie
        mapped_reactions = []
        for r in all_reactions:
            raw = r["reaction_raw"].lower()
            mapped_type = REACTION_MAP.get(raw)
            if mapped_type and mapped_type != "NONE":
                mapped_reactions.append({
                    "timestamp": r["timestamp"],
                    "type": mapped_type
                })

        if not mapped_reactions:
            fallback_results = {
                "summary": "Wczytane pliki nie zawierają żadnych poprawnych danych o reakcjach.",
                "details": {}
            }
            self.setup_fallback_data()
            return fallback_results

        total_count = len(mapped_reactions)

        # 1. Podział na typy reakcji (Tabela)
        type_counts = Counter(r["type"] for r in mapped_reactions)
        top_reactions_table = []
        for r_type, count in type_counts.most_common():
            display_name = REACTION_DISPLAY_NAMES.get(r_type, r_type)
            pct = f"{(count / total_count) * 100:.1f}%"
            top_reactions_table.append((display_name, count, pct))

        # 2. Aktywność według dni tygodnia (Wykres słupkowy)
        DAYS_POLISH = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Niedz"]
        day_counts = {day: 0 for day in DAYS_POLISH}
        for r in mapped_reactions:
            dt = datetime.fromtimestamp(r["timestamp"])
            day_name = DAYS_POLISH[dt.weekday()]
            day_counts[day_name] += 1

        # 3. Trendy roczne (Wykres liniowy)
        year_counts = defaultdict(int)
        for r in mapped_reactions:
            dt = datetime.fromtimestamp(r["timestamp"])
            year_counts[str(dt.year)] += 1
        sorted_years = sorted(year_counts.keys())
        reaction_trend = {yr: year_counts[yr] for yr in sorted_years}

        # 4. Kategorie emocjonalne (Wykres kołowy)
        category_counts = defaultdict(int)
        for r in mapped_reactions:
            cat = get_emotional_category(r["type"])
            category_counts[cat] += 1

        # Zapisz w self.data na potrzeby paneli
        self.data["total_reactions"] = total_count
        self.data["top_reactions"] = top_reactions_table
        self.data["emotion_by_day"] = day_counts
        self.data["reaction_trend"] = reaction_trend
        self.data["categories"] = dict(category_counts)

        # Statystyki do podsumowania
        dominant_reaction_type = type_counts.most_common(1)[0][0]
        dominant_reaction_name = REACTION_DISPLAY_NAMES.get(dominant_reaction_type, dominant_reaction_type)
        dominant_reaction_pct = f"{(type_counts[dominant_reaction_type] / total_count) * 100:.1f}%"
        
        most_active_day = max(day_counts, key=day_counts.get)
        most_active_day_count = day_counts[most_active_day]
        
        dominant_emotion_cat = max(category_counts, key=category_counts.get)

        summary_text = (
            f"Przeanalizowano łącznie {total_count} Twoich reakcji pod postami i komentarzami na przestrzeni lat.\n"
            f"Twoim dominującym stanem emocjonalnym na Facebooku jest '{dominant_emotion_cat}'.\n"
            f"Najczęściej reagujesz jako '{dominant_reaction_name}' (stanowi to {dominant_reaction_pct} wszystkich reakcji)."
        )

        results = {
            "summary": summary_text,
            "details": {}
        }
        return results

    def setup_fallback_data(self) -> None:
        self.data["total_reactions"] = 0
        self.data["top_reactions"] = [("Brak danych", 0, "0%")]
        self.data["emotion_by_day"] = {"Pon": 0, "Wt": 0, "Śr": 0, "Czw": 0, "Pt": 0, "Sob": 0, "Niedz": 0}
        self.data["reaction_trend"] = {"2026": 0}
        self.data["categories"] = {"Brak danych": 1}

    def panel_1(self) -> None:
        # KPI Card: Łączna liczba emocji/reakcji
        total = self.data.get("total_reactions", 0)
        self.add_kpi_card(
            0,
            value=str(total),
            title="Łączna liczba emocji",
            subtitle="Całkowita liczba Twoich reakcji (Lajk, Super, Haha, Wow, Przykro mi, Wrrr) pod postami i komentarzami na Facebooku."
        )

    def panel_2(self) -> None:
        # Tabela: Szczegółowe użycie poszczególnych reakcji
        top_reactions = self.data.get("top_reactions") or []
        self.add_table(
            1,
            rows=top_reactions,
            title="Szczegółowe użycie reakcji na Facebooku",
            columns=["Reakcja", "Liczba użyć", "Udział procentowy"]
        )

    def panel_3(self) -> None:
        # Wykres liniowy: Trendy reakcji na przestrzeni lat
        reaction_trend = self.data.get("reaction_trend") or {"2026": 0}
        self.add_line_chart(
            2,
            x=reaction_trend,
            title="Aktywność emocjonalna na przestrzeni lat"
        )

    def panel_4(self) -> None:
        # Wykres kołowy: Struktura profilu emocjonalnego
        categories = self.data.get("categories") or {"Brak danych": 1}
        self.add_pie_chart(
            3,
            data=categories,
            title="Struktura Twojego profilu emocjonalnego"
        )


if __name__ == "__main__":
    # Testowy blok do uruchamiania modułu jako samodzielnej aplikacji
    root = tk.Tk()
    root.geometry("1024x768")
    root.title("Testowanie Modułu 6 - MoodGraph")
    
    module = Module(root)
    module.pack(fill="both", expand=True)
    module.show_analysis()
    
    root.mainloop()
