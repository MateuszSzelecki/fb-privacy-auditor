"""Moduł 5: Cień Tożsamości (ShadowID).

Analizuje zsynchronizowane kontakty, telemetrię urządzeń mobilnych/PC oraz prognozy profilowe AI.
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
            "Przeszukujemy ukryte dane w Twoim profilu pod kątem telemetrii i kontaktów.",
            "Ujawnimy informacje o zsynchronizowanych kontaktach z Twojej książki telefonicznej.",
            "Wydobędziemy szczegółowe metadane sprzętowe Twojego smartfona i komputera.",
            "Pokażemy, co algorytmy AI Meta prognozują na temat Twojego wieku i języków.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Cień Tożsamości"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(ShadowID)"

    def _fix_encoding(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        try:
            return text.encode('latin1').decode('utf-8')
        except Exception:
            return text

    def _get_contacts(self) -> list:
        contacts = []
        base_path = "data"
        contacts_path = os.path.join(base_path, "personal_information", "other_personal_information", "your_imported_contacts.json")
        contacts_before_2021 = os.path.join(base_path, "personal_information", "profile_information", "contacts_uploaded_before_2021.json")

        if os.path.exists(contacts_path):
            try:
                with open(contacts_path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                for item in d:
                    name, point, ts = "Nieznany", "Brak", "Brak"
                    for lv in item.get("label_values", []):
                        lbl = self._fix_encoding(lv.get("label"))
                        if lbl == "Imię i nazwisko kontaktu":
                            name = self._fix_encoding(lv.get("value"))
                        elif lbl == "Punkt kontaktowy":
                            point = self._fix_encoding(lv.get("value"))
                        elif lbl == "Czas aktualizacji" and lv.get("timestamp_value"):
                            ts = datetime.fromtimestamp(lv.get("timestamp_value"), tz=timezone.utc).strftime('%Y-%m-%d %H:%M')
                    contacts.append((name, point, ts))
            except Exception:
                pass

        if os.path.exists(contacts_before_2021):
            try:
                with open(contacts_before_2021, "r", encoding="utf-8") as f:
                    d = json.load(f)
                for lv in d.get("label_values", []):
                    lbl = self._fix_encoding(lv.get("label"))
                    if lbl == "Kontakty":
                        for c_dict in lv.get("vec", []):
                            name, point, ts = "Nieznany", "Brak", "Brak"
                            for item in c_dict.get("dict", []):
                                sub_lbl = self._fix_encoding(item.get("label"))
                                if sub_lbl == "Nazwa":
                                    name = self._fix_encoding(item.get("value"))
                                elif sub_lbl == "Punkt kontaktowy":
                                    point = self._fix_encoding(item.get("value"))
                                elif sub_lbl == "Time of latest import" and item.get("timestamp_value"):
                                    ts = datetime.fromtimestamp(item.get("timestamp_value"), tz=timezone.utc).strftime('%Y-%m-%d %H:%M')
                            contacts.append((name, point, ts))
            except Exception:
                pass
        
        contacts.sort(key=lambda x: x[0].lower() if x[0] else "")
        return contacts

    def _get_mobile_devices(self) -> list:
        devices = []
        devices_path = os.path.join("data", "personal_information", "profile_information", "your_devices.json")
        if os.path.exists(devices_path):
            try:
                with open(devices_path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                for item in d:
                    dev_type, manufacturer, os_type, os_ver, cpu_cores, google_accts, last_seen = "Nieznane", "Nieznany", "Nieznany", "", "", "", "Brak"
                    for lv in item.get("label_values", []):
                        lbl = self._fix_encoding(lv.get("label"))
                        if lbl == "Typ urządzenia":
                            dev_type = self._fix_encoding(lv.get("value"))
                        elif lbl == "Producent":
                            manufacturer = self._fix_encoding(lv.get("value"))
                        elif lbl == "Typ systemu operacyjnego":
                            os_type = self._fix_encoding(lv.get("value"))
                        elif lbl == "Wersja systemu operacyjnego":
                            os_ver = self._fix_encoding(lv.get("value"))
                        elif lbl == "Liczba rdzeni procesora":
                            cpu_cores = self._fix_encoding(lv.get("value"))
                        elif lbl == "Liczba kont Google":
                            google_accts = self._fix_encoding(lv.get("value"))
                        elif lbl == "Szczegółowe informacje o identyfikatorze urządzenia" and lv.get("dict"):
                            for sub in lv.get("dict", []):
                                sub_lbl = self._fix_encoding(sub.get("label"))
                                if sub_lbl == "last_seen_time" and sub.get("timestamp_value"):
                                    last_seen = datetime.fromtimestamp(sub.get("timestamp_value"), tz=timezone.utc).strftime('%Y-%m-%d %H:%M')
                    devices.append((
                        manufacturer if manufacturer != "Nieznany" else dev_type,
                        dev_type if dev_type != "Nieznane" else "-",
                        f"{os_type} {os_ver}".strip(),
                        cpu_cores if cpu_cores else "-",
                        google_accts if google_accts else "0",
                        last_seen
                    ))
            except Exception:
                pass
        return devices

    def _get_pc_hardware(self) -> list:
        pc_list = []
        pc_path = os.path.join("data", "logged_information", "other_logged_information", "detected_hardware.json")
        if os.path.exists(pc_path):
            try:
                with open(pc_path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                for item in d:
                    last_seen, gpu, ram, cpu = "Brak", "Brak", "Brak", "Brak"
                    for lv in item.get("label_values", []):
                        lbl = self._fix_encoding(lv.get("label"))
                        if lbl == "Czas ostatniego pełnego wykrycia" and lv.get("timestamp_value"):
                            last_seen = datetime.fromtimestamp(lv.get("timestamp_value"), tz=timezone.utc).strftime('%Y-%m-%d %H:%M')
                        elif lbl == "Renderer karty graficznej":
                            gpu = self._fix_encoding(lv.get("value"))
                        elif lbl == "RAM (GB)":
                            ram = self._fix_encoding(lv.get("value"))
                        elif lbl == "Liczba rdzeni procesora":
                            cpu = self._fix_encoding(lv.get("value"))
                    pc_list.append((gpu, f"{ram} GB" if ram != "Brak" else "Brak", cpu, last_seen))
            except Exception:
                pass
        return pc_list

    def _get_demographics_and_pokes(self) -> dict:
        pokes = []
        pokes_path = os.path.join("data", "your_facebook_activity", "other_activity", "pokes.json")
        if os.path.exists(pokes_path):
            try:
                with open(pokes_path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                for item in d.get("pokes_v2", []):
                    poker = self._fix_encoding(item.get("poker"))
                    pokee = self._fix_encoding(item.get("pokee"))
                    ts = datetime.fromtimestamp(item.get("timestamp"), tz=timezone.utc).strftime('%Y-%m-%d %H:%M')
                    pokes.append((poker, pokee, ts))
            except Exception:
                pass

        predicted_age = "Nieznany"
        age_path = os.path.join("data", "personal_information", "other_personal_information", "age_group_prediction.json")
        if os.path.exists(age_path):
            try:
                with open(age_path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                for lv in d.get("label_values", []):
                    lbl = self._fix_encoding(lv.get("label"))
                    if lbl == "Grupa wiekowa":
                        predicted_age = self._fix_encoding(lv.get("value"))
            except Exception:
                pass

        pred_langs = []
        lang_path = os.path.join("data", "personal_information", "profile_information", "predicted_languages.json")
        if os.path.exists(lang_path):
            try:
                with open(lang_path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                for lv in d.get("label_values", []):
                    lbl = self._fix_encoding(lv.get("label"))
                    val = self._fix_encoding(lv.get("value"))
                    if val:
                        display_lbl = lbl.replace("Języki prognozowane na podstawie ", "")
                        pred_langs.append((display_lbl, val))
            except Exception:
                pass

        return {
            "pokes": pokes,
            "predicted_age": predicted_age,
            "predicted_languages": pred_langs
        }

    def panel_1(self) -> None:
        contacts = self.data.get("contacts") or []
        table_rows = [(name, point, ts) for name, point, ts in contacts]
        self.add_table(
            rows = table_rows,
            title = f"Zsynchronizowana książka adresowa ({len(contacts)} kontaktów)",
            columns = ["Nazwa kontaktu", "Numer telefonu / Email", "Ostatni import"],
            col_widths = [200, 300, 150]
        )

    def panel_2(self) -> None:
        devices = self.data.get("mobile_devices") or []
        table_rows = [(man, model, os_info, cpu, g_accts, last_seen) for man, model, os_info, cpu, g_accts, last_seen in devices]
        self.add_table(
            rows = table_rows,
            title = "Telemetria urządzeń mobilnych",
            columns = ["Producent", "Model", "System operacyjny", "Rdzenie CPU", "Konta Google", "Ostatnia aktywność"],
            col_widths = [120, 120, 120, 100, 100, 150]
        )

    def panel_3(self) -> None:
        pc_devices = self.data.get("pc_devices") or []
        table_rows = [(gpu, ram, cpu, last_seen) for gpu, ram, cpu, last_seen in pc_devices]
        self.add_table(
            rows = table_rows,
            title = "Wykryte konfiguracje komputerów PC",
            columns = ["Karta graficzna (GPU)", "Pamięć RAM", "Rdzenie CPU", "Ostatni pełny skan"],
            col_widths = [350, 100, 100, 150]
        )

    def panel_4(self) -> None:
        ai_data = self.data.get("demographics_and_pokes") or {}
        rows = []
        
        age = ai_data.get("predicted_age", "Nieznany")
        rows.append(("Przewidywany wiek (AI)", age))
        
        langs = ai_data.get("predicted_languages") or []
        for lbl, val in langs:
            rows.append((f"Język ({lbl})", val))
            
        pokes = ai_data.get("pokes") or []
        for poker, pokee, ts in pokes:
            rows.append((f"Zaczepka: {poker} ➔ {pokee}", ts))
            
        if not rows:
            rows = [("Brak danych", "-")]
            
        self.add_table(
            rows = rows,
            title = "Przewidywania AI & Interakcje (Zaczepki)",
            columns = ["Etykieta profilu / Zdarzenie", "Szczegóły / Czas"],
            col_widths = [350, 350]
        )

    def analyze(self) -> dict:
        contacts = self._get_contacts()
        mobile_devices = self._get_mobile_devices()
        pc_devices = self._get_pc_hardware()
        demo_and_pokes = self._get_demographics_and_pokes()

        res: dict = {
            "contacts": contacts,
            "mobile_devices": mobile_devices,
            "pc_devices": pc_devices,
            "demographics_and_pokes": demo_and_pokes
        }

        self.data.update(res)
        return res
