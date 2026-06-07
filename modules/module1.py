"""Moduł 1: Cień Reklamowy (AdShadow).

Ten moduł analizuje dane reklamowe i wyświetla informacje o możliwych dopasowaniach
kontaktów przesłanych do Facebooka.
"""

import tkinter as tk
import textwrap

from .module_template import BaseModule

class Module(BaseModule):

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Sprawdzamy dopasowania pomiędzy danymi kontaktowymi a zewnętrznymi listami reklamodawców.",
            "Szacujemy liczbę firm, które mogły wykorzystać Twój e-mail lub numer telefonu.",
            "Analizujemy liczbę kliknięć reklam związanych z wykrytymi dopasowaniami.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Cień Reklamowy"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(AdShadow)"

    def panel_1(self) -> None:
        raw_companies = self.data.get("top_companies") or []
        table_rows = []

        for entry in raw_companies:
            if not isinstance(entry, dict): continue
            name = entry.get("company_name", "nieznana")
            source = entry.get("source", "nieznane")
            table_rows.append((name, source))

        self.add_table(
            rows=table_rows,
            title="Źródła reklamodawców",
            columns=[
                "Firma",
                "Źródło danych",
            ],
        )

    def panel_2(self) -> None:
        preferences = self.data.get("preferences") or {}

        table_rows: list[tuple] = []
        for label, setting in preferences.items():
            table_rows.append((label, setting))

        self.add_table(
            rows=table_rows,
            title="Preferencje reklamowe",
            columns=["Ustawienie", "Wartość"],
            col_widths=[800,100]
        )

    def panel_3(self) -> None:
        email_matches = int(self.data.get("email_matches", self.data.get("external_matches", 5)))
        phone_matches = int(self.data.get("phone_matches", 2))
        total_matches = email_matches + phone_matches

        self.add_kpi_card(
            value=str(total_matches),
            title="Suma Dopasowań Danych",
            subtitle=f"Twój e-mail dopasowano {email_matches} razy, a numer telefonu {phone_matches} razy."
        )

    def panel_4(self) -> None:
        clicks_by_month = self.data.get("clicks_by_month") or {"Jan": 3, "Feb": 5, "Mar": 10}
        self.add_bar_chart(clicks_by_month, title="Kliknięcia reklam (przybliżone)")

    def analyze(self) -> dict:
        import json
        import os

        ads_data_dir: str = os.path.join("data", "ads_information")
        advertisers_info_path: str = os.path.join(
            ads_data_dir, "advertisers_using_your_activity_or_information.json"
        )

        if not os.path.exists(advertisers_info_path):
            return {"summary": "advertisers file not found"}

        # parse advertiers using your activity or info
        with open(advertisers_info_path, "r", encoding = "utf-8") as f:
            advertisers_data = json.load(f)

        # parse stampled locations
        with open(
            os.path.join(ads_data_dir, "ad_preferences.json"), "r", encoding = "utf-8"
        ) as f:
            ad_preferences_data = json.load(f)

        advertisers: list[dict] = []
        preferences: dict = {}

        # handle advertisers data
        label_values: dict = advertisers_data.get("label_values")
        for entry in label_values:
            vec: dict = entry.get("vec")
            label: str = entry.get("label").lower()
            if "interakcje" in label:
                source: str = "interakcje z witryną/sklepem"
            elif "lista" in label:
                source: str = "listy kontaktowe"
            elif "telefon" in label or "komórk" in label:
                source: str = "telefon"
            elif "aplikac" in label:
                source: str = "aktywność w aplikacji"
            else:
                source: str = "Inne interakcje reklamowe"

            for company in vec:
                company_name = company.get("value")
                # handle meta encoding
                try:
                    company_name = company.get("value").encode("latin1").decode("utf-8")
                except:
                    company_name = company.get("value")

                if not company_name: continue
                advertisers.append({"company_name" : company_name, "source" : source})

        # handle user preferences

        label_values: dict = ad_preferences_data.get("label_values") or {}
        for entry in label_values:
            label: str = entry.get("label")

            # fix encoding
            try: label = label.encode("latin1").decode("utf-8")
            except: pass

            value: str = entry.get("value")
            if not value:
                value: str = ""
                vec: list = entry.get("vec") or []
                for item in vec:
                    value += f"{item}; "

            try: value = value.encode("latin1").decode("utf-8")
            except: pass
            if label:
                preferences[label] = value

        res: dict = {
            "top_companies" : advertisers,
            "preferences" : preferences
        }

        self.data.update(res)
        return res;


if __name__ == "__main__":
    sample_data = {
        "external_matches": 5,
        "ad_clicks": 18,
        "company_count": 4,
    }
    module = Module(tk.Tk(), data=sample_data)
    module.run_console()
