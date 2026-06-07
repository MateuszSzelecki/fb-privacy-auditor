import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict
from datetime import datetime
from .module_template import BaseModule

class Module(BaseModule):

    def __init__(self, parent, **kwargs):
        self.data: Dict[str, Any] = {
            "lista_firm": []
        }
        self.parent = parent
        
        super().__init__(parent, **kwargs)
        
        if not self.select_and_load_data():
            for widget in self.winfo_children():
                widget.destroy()
            ttk.Label(self, text="Anulowano ładowanie danych modułu - kliknij powrót.", font=('Helvetica', 12)).pack(expand=True)
            return
            
        self.panel_1()

    @classmethod
    def tile_title(cls) -> str:
        return "Poza Systemem"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(OffFacebook)"

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Przetwarzamy dane z Off-Facebook Activity, czyli wszystko, co Facebook wie o Tobie poza platformą.",
            "Pokazujemy aplikacje i strony, które doniosły Facebookowi o Twoich działaniach.",
            "Ujawnimy zakres szpiegowania z użyciem Facebook Pixel i zewnętrznych skryptów.",
            "Pokażemy, jak duży ruch poza Facebookiem trafia do Meta na Twój temat.",
        ]

    def select_and_load_data(self) -> bool:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

        target_dir = os.path.join(base_path, "apps_and_websites_off_of_facebook")
        if not os.path.exists(target_dir):
            messagebox.showerror("Błąd struktury", f"Nie znaleziono folderu 'apps_and_websites_off_of_facebook' w ścieżce:\n{base_path}")
            return False

        json_files = os.listdir(target_dir)
        target_file = None
        name = "your_activity_off_meta_technologies.json"
        if name in json_files:
            target_file = os.path.join(target_dir, name)
                
        if not target_file:
            fallback_files = [f for f in json_files if f.endswith('.json')]
            if fallback_files:
                target_file = os.path.join(target_dir, fallback_files[0])

        if not target_file:
            messagebox.showerror("Błąd danych", "W folderze nie znaleziono żadnego pliku archiwum JSON.")
            return False

        try:
            with open(target_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                
            if isinstance(raw_data, list):
                activity_list = raw_data
            elif isinstance(raw_data, dict):
                activity_list = None
                known_keys = ["off_meta_technologies_activity", "off_facebook_activity_v2", "off_facebook_activity"]
                for key in known_keys:
                    if key in raw_data:
                        activity_list = raw_data[key]
                        break

            if not activity_list:
                messagebox.showerror("Błąd zawartości", "Plik JSON jest pusty lub ma nieprawidłową strukturę główną.")
                return False

            firmy_schowek = {}
            
            for item in activity_list:
                if not isinstance(item, dict):
                    continue
                
                app_name = item.get("title", "Nieznana aplikacja")
                label_values = item.get("label_values", [])
                
                for lv in label_values:
                    if isinstance(lv, dict) and lv.get("label") == "Wydarzenia":
                        events_list = lv.get("vec", [])
                        if not events_list:
                            continue
                            
                        if app_name not in firmy_schowek:
                            firmy_schowek[app_name] = {
                                "nazwa": app_name,
                                "suma_wszystkich_zdarzen": len(events_list),
                                "statystyka_akcji": {},
                                "rejestr_zdarzen": []
                            }
                        
                        for event_wrapper in events_list:
                            single_dict_list = event_wrapper.get("dict", [])
                            typ_akcji = "UNKNOWN"
                            znacznik_czasu = 0
                            
                            for element in single_dict_list:
                                label = element.get("label")
                                if label == "Zdarzenie":
                                    typ_akcji = element.get("value", "UNKNOWN")
                                elif label == "Otrzymano":
                                    znacznik_czasu = element.get("timestamp_value", 0)
                            
                            firmy_schowek[app_name]["rejestr_zdarzen"].append({
                                "typ": typ_akcji,
                                "timestamp": znacznik_czasu
                            })
                            
                            firmy_schowek[app_name]["statystyka_akcji"][typ_akcji] = \
                                firmy_schowek[app_name]["statystyka_akcji"].get(typ_akcji, 0) + 1
                        break

            lista_wynikowa = list(firmy_schowek.values())
            if not lista_wynikowa:
                messagebox.showerror("Brak danych", "W wybranym pliku nie odnaleziono żadnych aktywności zewnętrznych.")
                return False

            lista_wynikowa.sort(key=lambda x: x["suma_wszystkich_zdarzen"], reverse=True)
            self.data["lista_firm"] = lista_wynikowa
            return True

        except Exception as e:
            messagebox.showerror("Błąd krytyczny", f"Wystąpił problem podczas przetwarzania pliku:\n{e}")
            return False

    def panel_1(self) -> None:
        firmy = self.data.get("lista_firm")
        if not firmy:
            return

        tabela_firm = []
        for f in firmy:
            tabela_firm.append([f["nazwa"], f"{f['suma_wszystkich_zdarzen']}"])

        self.add_table(tabela_firm, title="Strony, które doniosły", columns=["Aplikacja / Strona", "Liczba doniesień"])

    def panel_2(self) -> None:
        firmy = self.data.get("lista_firm")
        if not firmy:
            return

        globalne_akcje = {}
        for f in firmy:
            for akcja, ile in f["statystyka_akcji"].items():
                globalne_akcje[akcja] = globalne_akcje.get(akcja, 0) + ile

        sorted_akcje = dict(sorted(globalne_akcje.items(), key=lambda x: x[1], reverse=True))
        tabela_akcji = [[akcja, f"{ile}"] for akcja, ile in sorted_akcje.items()]

        self.add_table(tabela_akcji, title="Rodzaje aktywności", columns=["Typ zdarzenia", "Łączna ilość"])

    def panel_3(self) -> None:
        firmy = self.data.get("lista_firm")
        if not firmy:
            return

        from datetime import datetime

        lista_wszystkich_wydarzen = []

        for f in firmy:
            nazwa_firmy = f["nazwa"]
            rejestr = f.get("rejestr_zdarzen", [])
            
            for zdarzenie in rejestr:
                typ_akcji = zdarzenie.get("typ", "UNKNOWN")
                ts = zdarzenie.get("timestamp", 0)

                lista_wszystkich_wydarzen.append({
                    "firma": nazwa_firmy,
                    "typ": typ_akcji,
                    "timestamp": ts
                })

        lista_wszystkich_wydarzen.sort(key=lambda x: x["timestamp"], reverse=True)

        tabela_wydarzen = []
        for ev in lista_wszystkich_wydarzen:
            ts = ev["timestamp"]
            
            if ts > 0:
                try:
                    czytelna_data = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    czytelna_data = f"Błąd znacznika ({ts})"
            else:
                czytelna_data = "Brak danych"

            wiersz = [
                ev["firma"],
                ev["typ"],
                czytelna_data
            ]
            tabela_wydarzen.append(wiersz)

        self.add_table(
            tabela_wydarzen, 
            title="Globalna historia aktywności", 
            columns=["Aplikacja / Strona", "Typ zdarzenia", "Dokładna data i godzina"]
        )
    
    def panel_4(self) -> None:
        firmy = self.data.get("lista_firm")
        if not firmy:
            return

        globalne_akcje = {}
        for f in firmy:
            for akcja, ile in f["statystyka_akcji"].items():
                globalne_akcje[akcja] = globalne_akcje.get(akcja, 0) + ile

        sorted_akcje = dict(sorted(globalne_akcje.items(), key=lambda x: x[1], reverse=True))
        wykres_akcje = {}
        limit_top = 4
        licznik = 0
        suma_pozostalych = 0

        for akcja, ile in sorted_akcje.items():
            if licznik < limit_top:
                wykres_akcje[akcja] = ile
                licznik += 1
            else:
                suma_pozostalych += ile

        if suma_pozostalych > 0:
            wykres_akcje["INNE"] = suma_pozostalych

        self.add_pie_chart(wykres_akcje, title="Udział typów inwigilacji")

if __name__ == "__main__":
    root = tk.Tk()
    module = Module(root)
    root.mainloop()


