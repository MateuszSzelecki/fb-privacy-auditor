"""Moduł 1: Cień Reklamowy (AdShadow).

Ten moduł analizuje dane reklamowe i wyświetla informacje o możliwych dopasowaniach
kontaktów przesłanych do Facebooka.
"""

import json
import os

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

    # companies which may manage users data
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

    # users ad preferences
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

    # locatization detected
    def panel_3(self) -> None:
        localization = self.data.get("localization") or {}
        table_rows = []
        for place in localization:
            table_rows.append((place,))
        self.add_table(
            rows = table_rows,
            title = "Zapisane lokalizacje",
            columns = ["Miejsce"]
        )

    # apps detected from activity or information and apps detected on your account
    def panel_4(self) -> None:
        apps: list[str] = self.data.get("detected_apps") or []
        table_rows: list = [(app,) for app in apps]

        self.add_table(
            rows = table_rows,
            title = "Sieć powiązań zewnętrznych",
            columns = ["Nazwa aplikacji"]
        )

    # expects filepath to apps detected on your account
    # located in ads_information directory
    # works for both apps_detected_from_your_activity and apps_detected_from_your_account
    def _get_ad_app_detected(self, filename: str) -> list[str]:
        if not os.path.exists(filename): return []

        # parse json data
        with open(filename, "r", encoding = "utf-8") as f:
            data: dict = json.load(f)

        # handle every entry in the list
        res: list[str] = []
        for entry in data:
            label_values: list = entry.get("label_values") or []
            if not label_values: continue

            for item in label_values:
                appname: str = item.get("value")
                if not appname: continue
                res.append(appname)
        return res

    def _get_ad_advertisers(self, filename: str ) -> list[dict]:
        if not os.path.exists(filename): return []

        # parse json data
        with open(filename, "r", encoding = "utf-8") as f:
            data: dict = json.load(f)

        res: list[dict] = []

        # handle advertisers data
        label_values: list = data.get("label_values") or []
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
                res.append({"company_name" : company_name, "source" : source})

        return res

    def _get_ad_stored_location(self, filename: str) -> list[str]:
        if not os.path.exists(filename): return []

        # parse json data
        with open(filename, "r", encoding = "utf-8") as f:
            data: dict = json.load(f)

        res: list = []
        label_values: dict = data.get("label_values") or {}
        for entry in label_values:
            label: str = entry.get("label")
            if not label.lower() == "lokalizacja": continue
            value: str = entry.get("value")
            res.append(value)
        return res

    def _get_ad_preferences(self, filename: str) -> dict:
        if not os.path.exists(filename): return {}

        # parse json data
        with open(filename, "r", encoding = "utf-8") as f:
            data: dict = json.load(f)

        res: dict = {}
        # handle user preferences
        label_values: dict = data.get("label_values") or {}
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
                res[label] = value

        return res


    def analyze(self) -> dict:

        ad_data_dir: str = os.path.join("data", "ads_information")

        advertisers_info_path: str = os.path.join(
            ad_data_dir, "advertisers_using_your_activity_or_information.json"
        )

        apps_detected_activity_path: str = os.path.join(
            ad_data_dir, "apps_detected_from_your_activity.json"
        )

        apps_detected_account_path: str = os.path.join(
            ad_data_dir, "apps_detected_on_your_account.json"
        )

        ad_preferences_path: str = os.path.join(
            os.path.join(ad_data_dir, "ad_preferences.json")
        )

        ad_location_path: str = os.path.join(ad_data_dir, "your_sampled_locations.json")

        apps_detected_account = self._get_ad_app_detected(apps_detected_account_path)
        apps_detected_activity = self._get_ad_app_detected(apps_detected_activity_path)
        detected_apps: list[str] = apps_detected_account + apps_detected_activity 

        advertisers: list[dict] = self._get_ad_advertisers(advertisers_info_path)
        preferences: dict = self._get_ad_preferences(ad_preferences_path)
        stored_locations: list[str] = self._get_ad_stored_location(ad_location_path)

        res: dict = {
            "top_companies" : advertisers,
            "preferences" : preferences,
            "localization" : stored_locations,
            "detected_apps" : detected_apps
        }

        self.data.update(res)
        return res;
