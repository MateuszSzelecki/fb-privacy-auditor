import os
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict, List
from .module_template import BaseModule


class Module(BaseModule):

    def __init__(self, parent, **kwargs):
        self.data: Dict[str, Any] = {
            "device_counts": [],
            "os_counts": {},
            "locations_ips": [],
            "browser_counts": {},
            "logins_logouts": []
        }
        self.parent = parent

        super().__init__(parent, **kwargs)

        if not self.select_and_load_data():
            for widget in self.winfo_children():
                widget.destroy()
            ttk.Label(self, text="Błąd ładowania danych modułu.", font=('Helvetica', 12)).pack(expand=True)
            return

        self.panel_1()

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Parsujemy dane techniczne urządzeń z logowań i metadanych sesji.",
            "Wyciągamy systemy operacyjne, przeglądarki i unikalne identyfikatory sprzętu.",
            "Pokazujemy, jak Facebook tworzy Twój cyfrowy odcisk palca.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Cyfrowy Biom"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(BioScan)"

    def napraw_tekst(self, tekst: str) -> str:
        if isinstance(tekst, str):
            try:
                return tekst.encode('latin1').decode('utf-8')
            except Exception:
                return tekst
        return tekst

    def select_and_load_data(self) -> bool:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        target_dir = os.path.join(base_path, "security_and_login_information")
        
        if not os.path.exists(target_dir):
            messagebox.showerror("Błąd struktury", f"Nie znaleziono folderu 'security_and_login_information' in lokalizacji:\n{base_path}")
            return False

        # --- PLIK 1: where_you're_logged_in.json ---
        target_file = os.path.join(target_dir, "where_you're_logged_in.json")
        if not os.path.exists(target_file):
            messagebox.showerror("Błąd pliku", "Nie odnaleziono pliku 'where_you're_logged_in.json'.")
            return False

        try:
            with open(target_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            sessions_list = []
            if isinstance(raw_data, list):
                sessions_list = raw_data
            elif isinstance(raw_data, dict):
                if "active_sessions_v2" in raw_data:
                    sessions_list = raw_data["active_sessions_v2"]
                elif "active_sessions" in raw_data:
                    sessions_list = raw_data["active_sessions"]

            if not sessions_list:
                messagebox.showerror("Błąd zawartości", "Plik logowań jest pusty lub ma nieprawidłową strukturę.")
                return False

            slownik_urzadzen = {}
            slownik_os = {}
            slownik_browser = {}
            pary_lokalizacja_ip = set()
            
            self.data["active_sessions_list"] = []

            for session in sessions_list:
                if not isinstance(session, dict):
                    continue

                ts_created = "Brak"
                if session.get("created_timestamp"):
                    try:
                        ts_created = datetime.fromtimestamp(int(session.get("created_timestamp"))).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        ts_created = "Błędna data"

                ts_updated = "Brak"
                if session.get("updated_timestamp"):
                    try:
                        ts_updated = datetime.fromtimestamp(int(session.get("updated_timestamp"))).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        ts_updated = "Błędna data"

                raw_device = session.get("device", "Nieznane urządzenie")
                device_name = self.napraw_tekst(raw_device)
                
                app_name = session.get("app", "Nieznana")
                app_clean = self.napraw_tekst(app_name)
                
                ip_addr = session.get("ip_address", "Ukryty/Brak")
                
                raw_loc = session.get("location", "Brak danych o lokalizacji")
                clean_loc = self.napraw_tekst(raw_loc)
                
                cookie = session.get("datr_cookie", "Brak")

                self.data["active_sessions_list"].append([
                    ts_created, ts_updated, device_name, app_clean, ip_addr, clean_loc, cookie
                ])

                slownik_urzadzen[device_name] = slownik_urzadzen.get(device_name, 0) + 1

                ua = session.get("user_agent", "")
                os_found = "Inny / Nieznany"
                if "Windows" in ua or "Windows" in device_name:
                    os_found = "Windows"
                elif "Android" in ua:
                    os_found = "Android"
                elif "iPhone" in ua or "iPad" in ua:
                    os_found = "iOS"
                elif "Macintosh" in ua:
                    os_found = "macOS"
                elif "Linux" in ua:
                    os_found = "Linux"
                slownik_os[os_found] = slownik_os.get(os_found, 0) + 1

                pary_lokalizacja_ip.add((clean_loc, ip_addr))
                slownik_browser[app_clean] = slownik_browser.get(app_clean, 0) + 1

            sorted_devices = sorted(slownik_urzadzen.items(), key=lambda x: x[1], reverse=True)
            self.data["device_counts"] = [[dev, f"{count} razy"] for dev, count in sorted_devices]
            self.data["locations_ips"] = [[loc, ip] for loc, ip in sorted(list(pary_lokalizacja_ip))]
            self.data["os_counts"] = slownik_os
            self.data["browser_counts"] = slownik_browser

        except Exception as e:
            messagebox.showerror("Błąd krytyczny", f"Wystąpił problem podczas przetwarzania pliku logowań:\n{e}")
            return False

        logins_file = os.path.join(target_dir, "logins_and_logouts.json")
        if os.path.exists(logins_file):
            try:
                with open(logins_file, "r", encoding="utf-8") as f:
                    raw_logins = json.load(f)
                
                accesses_list = []
                if isinstance(raw_logins, dict) and "account_accesses_v2" in raw_logins:
                    accesses_list = raw_logins["account_accesses_v2"]
                elif isinstance(raw_logins, list):
                    accesses_list = raw_logins

                przetworzone_logowania = []
                for entry in accesses_list:
                    if not isinstance(entry, dict):
                        continue
                    
                    akcja = self.napraw_tekst(entry.get("action", "Nieznana akcja"))
                    strona = entry.get("site", "Brak danych")
                    ip = entry.get("ip_address", "Brak IP")
                    ts = entry.get("timestamp", 0)
                    
                    if ts:
                        try:
                            data_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                        except Exception:
                            data_str = "Błędna data"
                    else:
                        data_str = "Brak daty"
                    
                    przetworzone_logowania.append([data_str, akcja, strona, ip])
                
                self.data["logins_logouts"] = przetworzone_logowania

            except Exception as e:
                messagebox.showwarning("Ostrzeżenie", f"Nie udało się poprawnie załadować historii logowań z pliku:\n{e}")
        else:
            self.data["logins_logouts"] = []

        return True

    def panel_1(self) -> None:
        sessions = self.data.get("active_sessions_list")
        if not sessions:
            sessions = [["Brak danych", "-", "-", "-", "-", "-", "-"]]
        
        self.add_table(
            sessions, 
            title="Aktualnie aktywne sesje konta", 
            columns=["Utworzono", "Ostatnia aktywność", "Nazwa sprzętu", "Aplikacja", "Adres IP", "Miejscowość / Kraj", "Ciasteczko DATR"]
        )

    def panel_2(self) -> None:
        os_counts = self.data.get("os_counts") or {}
        browser_counts = self.data.get("browser_counts") or {}
        
        combined_counts = {**os_counts, **browser_counts}
        
        if combined_counts:
            sorted_counts = sorted(combined_counts.items(), key=lambda item: item[1], reverse=True)
        else:
            sorted_counts = [("Brak danych w bazie profilu", "-")]
            
        self.add_table(
            sorted_counts, 
            title="Wykryte systemy operacyjne, aplikacje i przeglądarki", 
            columns=["Środowisko / Urządzenie", "Liczba powtórzeń"]
        )


    def panel_3(self) -> None:
        locs_ips = self.data.get("locations_ips")
        if not locs_ips:
            locs_ips = [["Brak danych", "Brak danych"]]
        self.add_table(locs_ips, title="Historia lokalizacji logowań oraz powiązane adresy IP", columns=["Miejscowość / Kraj", "Adres IP (v4/v6)"])

    def panel_4(self) -> None:
        logins_logouts = self.data.get("logins_logouts")
        if not logins_logouts:
            logins_logouts = [["Brak danych", "Brak danych", "Brak danych", "Brak danych"]]
            
        self.add_table(
            logins_logouts, 
            title="Pełna historia sesji (Logowania i Wylogowania)", 
            columns=["Data i godzina", "Akcja", "Serwis/Strona", "Adres IP"]
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Modułu Cyfrowego Biom")
    root.geometry("800x600")
    module = Module(root)
    root.mainloop()
