"""Moduł 1: Cień Reklamowy (AdShadow).

Ten moduł analizuje dane reklamowe i wyświetla informacje o możliwych dopasowaniach
kontaktów przesłanych do Facebooka.
"""

import tkinter as tk
from typing import Any, Dict, Optional

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
        raw_companies = self.data.get("top_companies") or [
            "Spotify",
            "Uber",
            "Tinder",
            "Netflix",
            "Allegro"
        ]
        
        # Słownik z przykładowymi szczegółami dla znanych marek
        company_details = {
            "Spotify": ("Usługi strumieniowe / Muzyka", "Bardzo wysokie", "Adres e-mail", "18"),
            "Uber": ("Transport i logistyka", "Wysokie", "Numer telefonu", "12"),
            "Tinder": ("Dating & social networking", "Wysokie", "Lista kontaktów", "9"),
            "Netflix": ("Rozrywka / VOD", "Średnie", "Adres e-mail", "15"),
            "Allegro": ("E-commerce / Zakupy", "Bardzo wysokie", "Adres e-mail & Tel", "24"),
        }
        
        table_rows = []
        for item in raw_companies:
            if isinstance(item, (list, tuple)):
                table_rows.append(item)
            elif isinstance(item, str):
                if item in company_details:
                    table_rows.append((item,) + company_details[item])
                else:
                    # Generowanie deterministycznych danych dla innych nazw firm
                    h = sum(ord(c) for c in item)
                    industries = ["E-commerce", "Marketing/PR", "Finanse", "Usługi IT", "Rozrywka"]
                    probabilities = ["Bardzo wysokie", "Wysokie", "Średnie"]
                    sources = ["Adres e-mail", "Numer telefonu", "Zewnętrzny partner"]
                    
                    industry = industries[h % len(industries)]
                    prob = probabilities[h % len(probabilities)]
                    src = sources[h % len(sources)]
                    camps = str((h % 15) + 3)
                    
                    table_rows.append((item, industry, prob, src, camps))
            else:
                table_rows.append(item)

        self.add_table(
            table_rows,
            title="Najbardziej prawdopodobne firmy",
            columns=["Firma", "Branża", "Prawdopodobieństwo", "Źródło danych", "Liczba kampanii"]
        )

    def panel_2(self) -> None:
        company_counts = self.data.get("company_counts") or {
            "Spotify": 8,
            "Uber": 5,
            "Tinder": 3,
            "Netflix": 2,
            "Allegro": 1
        }
        
        categories = {
            "Spotify": "Rozrywka",
            "Uber": "Medyczna/Transport",
            "Tinder": "Social Media",
            "Netflix": "Rozrywka",
            "Allegro": "E-commerce"
        }
        
        table_rows = []
        for company, count in company_counts.items():
            cat = categories.get(company, "Inne")
            # Deterministyczna liczba dni/tygodni temu
            h = sum(ord(c) for c in company)
            days = (h % 14) + 1
            last_seen = f"{days} dni temu" if days < 7 else f"{days // 7} tyg. temu"
            table_rows.append((company, count, cat, last_seen))
            
        self.add_table(
            table_rows,
            title="Liczba dopasowań (posortowane)",
            columns=["Firma", "Dopasowania", "Kategoria", "Ostatnie wykrycie"]
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


if __name__ == "__main__":
    sample_data = {
        "external_matches": 5,
        "ad_clicks": 18,
        "company_count": 4,
    }
    module = Module(tk.Tk(), data=sample_data)
    module.run_console()
