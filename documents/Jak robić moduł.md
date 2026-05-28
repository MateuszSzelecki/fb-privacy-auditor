## Krok po Kroku: Jak zacząć?

### 1. Wybór 2 modułów do realizacji
Rozpoczynamy od zapoznania się z listą propozycji w pliku Moduly.md. 
- Wybierz dla siebie **2 moduły**.
- Przed ostatecznym wyborem zweryfikuj w pobranym archiwum danych z Facebooka, czy pliki powiązane z tymi modułami rzeczywiście istnieją i czy ich analiza jest technicznie wykonalna.
- **Masz pomysł na własny moduł?** Napisz!

### 2. Przypisanie zadań na GitHubie
Gdy masz pewność, że wybrane moduły są wykonalne:
- Przejdź do zakładki **Issues** w repozytorium projektu na GitHubie.
- Przypisz siebie (Assignee) do issue odpowiadających wybranym modułom.

### 3. Rezerwacja plików w projekcie
Przejdź do folderu `modules/` w kodzie źródłowym:
- Wybierz dla siebie **2 pliki** spośród istniejących szablonów: module1.py / module2.py / module3.py / module4.py / module5.py / module6.py / module7.py / module8.py / module9.py. 
- **Ważne:** Przed rozpoczęciem pracy upewnij się (np. na kanale komunikacyjnym zespołu lub w historii commitów), że nikt inny nie pracuje obecnie na tych samych plikach.

### 4. Modyfikacja i dostosowanie plików modułu
Otwórz wybrany plik szablonu (np. `module2.py`) i dostosuj go do założeń swojego modułu. W pliku musisz zmodyfikować i dostosować następujące elementy:

- **Tytuł i podtytuł kafelka:** Zmień zwracane wartości w metodach klasy:
  ```python
  @classmethod
  def tile_title(cls) -> str:
      return "Tytuł Twojego Modułu"

  @classmethod
  def tile_subtitle(cls) -> str:
      return "(Krótki opis, np. GeoTracks)"
  ```
- **Slajdy prezentacyjne (`slide_texts`):** Nadpisz metodę klasy `slide_texts()`, zwracając listę 3-4 zdań wprowadzających użytkownika w temat analizowanych danych:
  ```python
  @classmethod
  def slide_texts(cls) -> list[str]:
      return [
          "Pierwszy slajd.",
          "Drugi slajd.",
          "Trzeci slajd.",
      ]
  ```
- **Analiza danych w `analyze()`:** Nadpisz tę metodę, aby parsowała odpowiednie pliki JSON z pobranego archiwum Facebooka i zwracała wyniki w postaci słownika (np. podsumowanie, listy, liczby).
- **Zawartość Paneli Wynikowych:** Zaprogramuj metody `panel_1()`, `panel_2()`, `panel_3()` oraz `panel_4()`. Wykorzystaj w nich dane z analizy (`self.data`) i wyświetl je za pomocą gotowych widżetów (tabel, karty KPI lub wykresów) opisanych poniżej.

---

## Dostępne Formy Prezentacji Danych w Kafelkach

Klasa bazowa dostarcza 5 zaawansowanych metod pomocniczych do renderowania danych wewnątrz paneli (`panel_1` do `panel_4`). Poniżej znajduje się ich opis, zastosowanie oraz przykłady kodu:

### 1. Karta KPI / Duży Wskaźnik (`self.add_kpi_card`)
* **Zastosowanie:** Pokazywanie jednej kluczowej statystyki (np. procentu, liczby naruszeń) w bardzo dużej, czytelnej formie wraz z objaśniającym komentarzem. Idealna do natychmiastowego przyciągnięcia uwagi.
* **Sposób użycia:**
  ```python
  self.add_kpi_card(
      value="94%",                # Masywna wartość (liczba/tekst) na środku
      title="Wskaźnik Zagrożenia", # Nagłówek kafelka
      subtitle="Twój profil prywatności jest krytycznie naruszony przez reklamodawców." # Komentarz pod liczbą
  )
  ```
  *(Zawartość karty jest automatycznie wyśrodkowana w pionie i poziomie, a tytuł zachowuje spójny wygląd z pozostałymi kafelkami).*

### 2. Tabela (`self.add_table`)
* **Zastosowanie:** Wyświetlanie szczegółowych list, dopasowań, surowych danych lub rankingów z możliwością sortowania kolumn przez użytkownika.
* **Sposób użycia:**
  ```python
  table_rows = [
      ("Spotify", "Wysokie", "18"),
      ("Netflix", "Średnie", "12"),
      ("Tinder", "Niskie", "5")
  ]
  self.add_table(
      rows=table_rows,
      title="Najczęściej dopasowani reklamodawcy",
      columns=["Firma", "Ryzyko", "Liczba kampanii"]
  )
  ```

### 3. Wykres Kołowy (`self.add_pie_chart`)
* **Zastosowanie:** Pokazywanie proporcji lub procentowego udziału kategorii w całości (np. typy dopasowanych kontaktów).
* **Sposób użycia:**
  ```python
  pie_data = {
      "E-mail": 70,
      "Telefon": 30
  }
  self.add_pie_chart(
      data=pie_data,
      title="Źródła Śledzenia Danych"
  )
  ```

### 4. Wykres Słupkowy (`self.add_bar_chart`)
* **Zastosowanie:** Porównywanie wartości liczbowych między różnymi kategoriami (np. liczba logowań w podziale na systemy operacyjne).
* **Sposób użycia:**
  ```python
  bar_data = {
      "Android": 8,
      "Windows": 5,
      "iOS": 3
  }
  self.add_bar_chart(
      data=bar_data,
      title="Systemy operacyjne"
  )
  ```

### 5. Wykres Liniowy (`self.add_line_chart`)
* **Zastosowanie:** Pokazywanie trendów, wzrostu lub zmian aktywności w czasie (np. aktywność logowań w dniach tygodnia).
* **Sposób użycia:**
  ```python
  line_data = {
      "Pon": 10,
      "Wt": 15,
      "Śr": 30,
      "Czw": 25
  }
  self.add_line_chart(
      x=line_data,
      title="Aktywność lokalizacyjna w czasie"
  )
  ```

---

## Dobre Praktyki (Wskazówki UI/UX)
- **Różnorodność:** Staraj się nie umieszczać czterech tabel na raz. Najlepsze moduły to te, które łączą np. **jedną kartę KPI** (podsumowanie), **dwie tabele** (szczegóły) oraz **jeden wykres** (kołowy/słupkowy/liniowy dla wizualizacji).
- **Prosty język:** Pamiętaj, aby opisy pod liczbami w kartach KPI i komentarze pisać prostym, zrozumiałym dla przeciętnego użytkownika językiem.
- **Bezpieczeństwo danych:** Metoda `analyze()` może posłużyć Ci do przetworzenia surowych danych i przekazania ich do paneli za pomocą słownika `self.data`.