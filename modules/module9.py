"""Moduł 9: Cyfrowy Zegar (LifeTime).

Bada znaczniki czasu aktywności, aby określić Twój cyfrowy rytm dobowy.
"""

import tkinter as tk
import threading
from typing import Any, Dict, Optional
from .module_template import BaseModule

# Global variables for caching background analysis results and thread control
_analysis_result = None
_analysis_exception = None
_analysis_thread = None
_analysis_lock = threading.Lock()

def start_background_analysis():
    global _analysis_thread
    with _analysis_lock:
        if _analysis_thread is None:
            _analysis_thread = threading.Thread(target=_run_analysis, daemon=True)
            _analysis_thread.start()

def _run_analysis():
    global _analysis_result, _analysis_exception
    try:
        import os
        import json
        from datetime import datetime
        from collections import Counter, defaultdict

        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        data_path = os.path.join(base_path, "your_facebook_activity")

        if not os.path.exists(data_path):
            _analysis_result = {
                "summary": "Nie odnaleziono folderu z danymi aktywności. Upewnij się, że dane są rozpakowane do folderu 'data'.",
                "details": {}
            }
            return

        json_files = []
        for root_dir, dirs, files in os.walk(data_path):
            for file in files:
                if file.endswith(".json"):
                    json_files.append(os.path.join(root_dir, file))

        timestamps = []
        for file_path in json_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                def extract_ts(obj):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if k in ("timestamp", "timestamp_value", "created_timestamp", "updated_timestamp"):
                                if isinstance(v, (int, float)):
                                    timestamps.append(v)
                                elif isinstance(v, str):
                                    try:
                                        timestamps.append(float(v))
                                    except ValueError:
                                        pass
                            else:
                                extract_ts(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_ts(item)
                            
                extract_ts(data)
            except Exception:
                pass

        # Filter and clean timestamps
        cleaned_timestamps = []
        for ts in timestamps:
            if ts > 1e11:
                ts = ts / 1000.0
            # Keep timestamps from year 2000 to 2030
            if 946684800 < ts < 1893456000:
                cleaned_timestamps.append(ts)

        if not cleaned_timestamps:
            _analysis_result = {
                "summary": "Brak poprawnych znaczników czasu w plikach profilu.",
                "details": {}
            }
            return

        total_events = len(cleaned_timestamps)

        # 1. Distribution of hours
        hours = [datetime.fromtimestamp(ts).hour for ts in cleaned_timestamps]
        hour_counts = Counter(hours)
        
        # Group hours into 2-hour blocks for cleaner display
        two_hour_blocks = {
            "00-02": sum(hour_counts.get(h, 0) for h in (0, 1)),
            "02-04": sum(hour_counts.get(h, 0) for h in (2, 3)),
            "04-06": sum(hour_counts.get(h, 0) for h in (4, 5)),
            "06-08": sum(hour_counts.get(h, 0) for h in (6, 7)),
            "08-10": sum(hour_counts.get(h, 0) for h in (8, 9)),
            "10-12": sum(hour_counts.get(h, 0) for h in (10, 11)),
            "12-14": sum(hour_counts.get(h, 0) for h in (12, 13)),
            "14-16": sum(hour_counts.get(h, 0) for h in (14, 15)),
            "16-18": sum(hour_counts.get(h, 0) for h in (16, 17)),
            "18-20": sum(hour_counts.get(h, 0) for h in (18, 19)),
            "20-22": sum(hour_counts.get(h, 0) for h in (20, 21)),
            "22-24": sum(hour_counts.get(h, 0) for h in (22, 23))
        }

        # 2. Day of week distribution
        DAYS_POLISH = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Niedz"]
        weekdays = [DAYS_POLISH[datetime.fromtimestamp(ts).weekday()] for ts in cleaned_timestamps]
        weekday_counts = Counter(weekdays)
        weekday_distribution = {day: weekday_counts.get(day, 0) for day in DAYS_POLISH}

        # 3. Night vs Day
        night_owl_count = sum(hour_counts.get(h, 0) for h in range(0, 6)) # 00:00 - 05:59
        morning_count = sum(hour_counts.get(h, 0) for h in range(6, 12)) # 06:00 - 11:59
        afternoon_count = sum(hour_counts.get(h, 0) for h in range(12, 18)) # 12:00 - 17:59
        evening_count = sum(hour_counts.get(h, 0) for h in range(18, 24)) # 18:00 - 23:59

        # 4. Activity over years (Timeline)
        years = [datetime.fromtimestamp(ts).year for ts in cleaned_timestamps]
        year_counts = Counter(years)
        sorted_years = sorted(year_counts.keys())
        timeline = {str(yr): year_counts[yr] for yr in sorted_years}

        # 5. Table rows for circadian rhythm details
        pct_night = (night_owl_count / total_events) * 100
        pct_morning = (morning_count / total_events) * 100
        pct_afternoon = (afternoon_count / total_events) * 100
        pct_evening = (evening_count / total_events) * 100

        rhythm_details_table = [
            ("Rano (06:00 - 12:00)", morning_count, f"{pct_morning:.1f}%"),
            ("Popołudnie (12:00 - 18:00)", afternoon_count, f"{pct_afternoon:.1f}%"),
            ("Wieczór (18:00 - 24:00)", evening_count, f"{pct_evening:.1f}%"),
            ("Noc (00:00 - 06:00)", night_owl_count, f"{pct_night:.1f}%")
        ]

        # Determine dominant circadian rhythm
        max_period = max([
            ("Ranny Ptaszek", morning_count),
            ("Pracownik Dnia", afternoon_count),
            ("Wieczorny Domator", evening_count),
            ("Nocny Marek", night_owl_count)
        ], key=lambda x: x[1])

        dominant_label = max_period[0]

        summary_text = (
            f"Przeanalizowano łącznie {total_events:,} znaczników czasu Twojej aktywności.\n"
            f"Twój dominujący cyfrowy rytm dobowy to: {dominant_label}.\n"
            f"W godzinach nocnych (00:00 - 06:00) wykonano {night_owl_count} interakcji (co stanowi {pct_night:.1f}% ogółu)."
        )

        results = {
            "total_events": total_events,
            "two_hour_blocks": two_hour_blocks,
            "weekday_distribution": weekday_distribution,
            "timeline": timeline,
            "rhythm_details_table": rhythm_details_table,
            "dominant_label": dominant_label,
            "night_owl_pct": pct_night,
            "night_owl_count": night_owl_count,
            "summary": summary_text,
            "details": {}
        }
        _analysis_result = results
    except Exception as e:
        _analysis_exception = e


class Module(BaseModule):

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Analizujemy znaczniki czasu każdej aktywności Facebookowej.",
            "Wyznaczamy Twój cyfrowy rytm dnia i nocny cykl aktywności.",
            "Pokazujemy godziny, w których najczęściej korzystasz z Facebooka.",
            "Ujawnimy, kiedy Twoje konto jest najbardziej aktywne i kiedy najczęściej śpisz.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Cyfrowy Zegar"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(LifeTime)"

    def panel_1(self) -> None:
        total = self.data.get("total_events", 0)
        dominant = self.data.get("dominant_label", "Nieznany")
        
        # Formatting for a premium KPI Card appearance
        total_str = f"{total:,}".replace(",", " ")
        self.add_kpi_card(
            0,
            value=total_str,
            title="Liczba zarejestrowanych działań",
            subtitle=f"Twój dominujący profil aktywności:\n{dominant}"
        )

    def panel_2(self) -> None:
        two_hour_blocks = self.data.get("two_hour_blocks") or {
            "00-02": 0, "02-04": 0, "04-06": 0, "06-08": 0, "08-10": 0, "10-12": 0,
            "12-14": 0, "14-16": 0, "16-18": 0, "18-20": 0, "20-22": 0, "22-24": 0
        }
        self.add_bar_chart(1, two_hour_blocks, title="Profil aktywności w ciągu doby (co 2h)")

    def panel_3(self) -> None:
        timeline = self.data.get("timeline") or {"2026": 0}
        self.add_line_chart(2, timeline, title="Trend roczny aktywności")

    def panel_4(self) -> None:
        rhythm_table = self.data.get("rhythm_details_table") or []
        self.add_table(
            3,
            rows=rhythm_table,
            title="Szczegółowy rozkład por dnia",
            columns=["Pora dnia", "Liczba działań", "Udział procentowy"]
        )

    def analyze(self) -> dict:
        global _analysis_result
        if _analysis_result is not None:
            self.data.update(_analysis_result)
            return _analysis_result
        return {
            "summary": "Analiza cyfrowego zegara w toku...",
            "details": {}
        }

    def show_analysis(self) -> None:
        global _analysis_result, _analysis_exception

        if _analysis_exception is not None:
            # Display exception
            self.slide_container.grid_remove()
            self.slide_hint.grid_remove()
            err_label = tk.Label(
                self,
                text=f"Błąd podczas analizy:\n{_analysis_exception}",
                font=("Helvetica", 14),
                fg="red",
                bg="white"
            )
            err_label.grid(row=1, column=0, sticky="nsew", pady=20)
            return

        if _analysis_result is not None:
            self.data.update(_analysis_result)
            super().show_analysis()
        else:
            self.slide_container.grid_remove()
            self.slide_hint.grid_remove()

            self.loading_frame = tk.Frame(self, bg="white", bd=2, relief="solid")
            self.loading_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
            
            lbl = tk.Label(
                self.loading_frame,
                text="Trwa odczytywanie cyfrowego zegara...\nProszę czekać.",
                font=("Helvetica", 24),
                bg="white",
                fg="black",
                justify="center"
            )
            lbl.pack(expand=True)
            self.check_analysis_complete()

    def check_analysis_complete(self) -> None:
        global _analysis_result, _analysis_exception

        if not self.winfo_exists():
            return

        if _analysis_exception is not None:
            if hasattr(self, "loading_frame") and self.loading_frame.winfo_exists():
                self.loading_frame.destroy()
            err_label = tk.Label(
                self,
                text=f"Błąd podczas analizy:\n{_analysis_exception}",
                font=("Helvetica", 14),
                fg="red",
                bg="white"
            )
            err_label.grid(row=1, column=0, sticky="nsew", pady=20)
            return

        if _analysis_result is not None:
            if hasattr(self, "loading_frame") and self.loading_frame.winfo_exists():
                self.loading_frame.destroy()
            self.data.update(_analysis_result)
            super().show_analysis()
        else:
            self.after(100, self.check_analysis_complete)


# Start the analysis in background immediately when this module is imported
start_background_analysis()
