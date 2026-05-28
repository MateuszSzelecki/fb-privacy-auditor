"""Moduł 4: Cyfrowy Biom (BioScan).

Analizuje dane urządzeń z logowań, User-Agent i unikalne identyfikatory sprzętowe.
"""

import tkinter as tk
from typing import Any, Dict, Optional

from .module_template import BaseModule


class Module(BaseModule):

    @classmethod
    def slide_texts(cls) -> list[str]:
        return [
            "Parsujemy dane techniczne urządzeń z logowań i metadanych sesji.",
            "Wyciągamy systemy operacyjne, przeglądarki i unikalne identyfikatory sprzętu.",
            "Pokazujemy, jak Facebook tworzy Twój cyfrowy odcisk palca.",
            "Ujawnimy, jak łatwo można zidentyfikować Cię na podstawie telefonu i sieci Wi-Fi.",
        ]

    @classmethod
    def tile_title(cls) -> str:
        return "Cyfrowy Biom"

    @classmethod
    def tile_subtitle(cls) -> str:
        return "(BioScan)"

    def panel_1(self) -> None:
        devices = self.data.get("devices") or [
            "Samsung Galaxy S10", "Windows 11 laptop", "iPad Air"
        ]
        self.add_table(devices, title="Zidentyfikowane urządzenia", columns=["Urządzenie"])

    def panel_2(self) -> None:
        os_counts = self.data.get("os_counts") or {
            "Android": 8,
            "Windows": 5,
            "iOS": 3,
        }
        self.add_bar_chart(os_counts, title="Systemy operacyjne")

    def panel_3(self) -> None:
        browser_counts = self.data.get("browser_counts") or {
            "Chrome": 9,
            "Safari": 4,
            "Firefox": 3,
        }
        self.add_bar_chart(browser_counts, title="Przeglądarki używane podczas logowań")

    def panel_4(self) -> None:
        fingerprints = self.data.get("fingerprints") or [
            "User-Agent: Chrome 118", "MAC: xx:xx:xx:xx", "SSID: domowa_siec"
        ]
        self.add_table(fingerprints, title="Elementy odcisku palca urządzenia", columns=["Element"])


if __name__ == "__main__":
    module = Module(tk.Tk())
    module.run_console()
