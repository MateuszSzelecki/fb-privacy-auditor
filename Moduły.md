### 1. Cień Reklamowy (AdShadow)
- **Co robi:** Facebook pokazuje nam "aktualne preferencje reklamowe", ale ukrywa historię. Ten moduł parsuje pliki związane z reklamodawcami, którzy przesłali na Facebooka listy z Twoimi danymi kontaktowymi (np. e-mail, telefon) zdobytymi poza platformą.
- **Efekt:** Pokazuje listę firm zewnętrznych, które "wgrały Cię" do systemu Facebooka, oraz listę reklam, w które kliknąłeś nawet kilka lat temu, tworząc oś czasu Twoich konsumenckich słabości.

### 2. Geotropy (GeoTracks)
- **Co robi:** Wyciąga metadane z historii logowań, historii powiadomień oraz – co najciekawsze – **współrzędne geograficzne zaszyte w wysłanych przez Ciebie zdjęciach** na Messengerze.
- **Efekt:** Generuje mapę (lub listę) Twoich najczęstszych fizycznych lokalizacji. Pokazuje sekwencję miejsc, z których korzystałeś z aplikacji, demaskując, jak dokładnie Facebook śledzi Twój ruch w świecie realnym.

### 3. Matryca Relacji (CoreCircle)
- **Co robi:** Facebook nie mówi nam, kogo uważa za naszych najbliższych przyjaciół. Ten moduł analizuje archiwum Messengera: liczbę wymienionych znaków, częstotliwość interakcji oraz to, _kto pierwszy_ zaczyna rozmowę.
- **Efekt:** Tworzy ukryty "ranking algorytmiczny" Twoich znajomych. Pokazuje też tzw. "zombie-znajomych" – osoby, z którymi nie masz kontaktu od lat, ale Facebook nadal trzyma ich dane w kontekście Twoich relacji.

### 4. Cyfrowy Biom (BioScan)
- **Co robi:** Parsuje dane techniczne urządzeń (User-Agent), z których się logowałeś. Wyciąga informacje o systemach operacyjnych, przeglądarkach, a nawet unikalnych identyfikatorach sprzętowych i sieciach Wi-Fi.
- **Efekt:** Pokazuje "odcisk palca" Twojego sprzętu (device fingerprinting). Obnaża, jak precyzyjnie Facebook potrafi rozpoznać, że Ty to Ty, nawet jeśli zalogujesz się z nowego konta, ale na tym samym telefonie.

### 5. Widmo Messengera (GhostChat)
- **Co robi:** Skupia się na tym, co usunięte lub niewidoczne. Analizuje historię cofniętych wiadomości (Facebook często zostawia w logach ślad/znacznik, że wiadomość istniała) oraz ukryte wiadomości z folderów "Inne" lub "Spam".
- **Efekt:** Pokazuje statystyki dotyczące Twoich "wpadkach" komunikacyjnych (ile wiadomości usunąłeś) oraz ujawnia zapomniane, ukryte interakcje od obcych osób, o których istnieniu nie miałeś pojęcia.

### 6. Archwium Emocji (MoodGraph)
- **Co robi:** Analizuje historię Twoich reakcji (Lajk, Super, Woah, Przykro mi, Wrrr) pod postami na przestrzeni lat, korelując je z porami dnia lub dniami tygodnia.
- **Efekt:** Tworzy profil behawioralno-emocjonalny. Pokazuje np., w jakie dni jesteś najbardziej podatny na irytację (dużo reakcji "Wrrr"), a kiedy jesteś najbardziej nostalgiczny. To kluczowe dane, których Facebook używa do targetowania emocjonalnego.

### 7. Poza Systemem (OffFacebook)
- **Co robi:** Przetwarza pliki z sekcji "Off-Facebook Activity". To dane przesyłane przez zewnętrzny skrypt (Facebook Pixel) z innych stron internetowych (sklepów, portali informacyjnych, aplikacji bankowych), które odwiedzasz.
- **Efekt:** Wizualizuje ogrom szpiegowania poza Facebookiem. Pokazuje listę aplikacji (np. Tinder, Spotify, aplikacja bankowa), które doniosły Facebookowi o tym, co robisz na swoim telefonie, w ujęciu sekundowym.

### 8. Słowa Klucze (TagCloud)
- **Co robi:** Analizuje teksty Twoich postów, komentarzy i wiadomości na Messengerze pod kątem najczęściej używanych rzeczowników i przymiotników, odrzucając tzw. stop-words (i, w, z, pod).
- **Efekt:** Tworzy profil Twoich zainteresowań w formie chmury tagów i kategorii semantycznych. Pokazuje, w jakie "szufladki tematyczne" (np. polityka, sport, kryptowaluty) algorytm mógł Cię wrzucić na podstawie samej analizy tekstu pisanego.

### 9. Cyfrowy Zegar (LifeTime)
- **Co robi:** Bada dokładne znaczniki czasu (timestamps) każdej Twojej aktywności (kliknięcie, polubienie, wiadomość) z ostatnich kilku lat.
- **Efekt:** Wyznacza Twój cyfrowy dobowy cykl życia. Pokazuje wykres Twojej bezsenności (aktywność w godzinach 2:00-5:00) oraz precyzyjnie określa godziny, w których powinieneś być w pracy/szkole, a mimo to "siedzisz na Facebooku".

### 10. How To
- Przydałby się też moduł, który konkretnie pokazuje jak możemy pobrać odpowiednie dane, czyli pliki JSON, z facebooka. Najlepiej screeny kroków do wykonania z informacją że generowanie tych danych trwa kilka dni.
- Następnie można również pokazać jak te pliki wgrać do naszego programu.
- Pomocna może być instrukcja pobierania.

### 11. Widmo Znajomości (GhostFollow)
- **Co robi:** Analizuje pliki z historią wyszukiwań (tak, Facebook rejestruje każde wpisane w lupkę imię i nazwisko), historią wysłanych i odrzuconych zaproszeń do znajomych oraz profile, które odwiedzasz najczęściej, mimo że nie macie się w znajomych.
- **Efekt:** Tworzy listę Twoich "cichych interakcji". Pokazuje, kogo najczęściej "stalkujesz" (wyszukujesz w aplikacji) oraz kto znajduje się w Twoim cyfrowym otoczeniu, mimo że oficjalnie na liście znajomych ta osoba nie istnieje.

### 12. Czystka Pamięci (DataRetention)
- **Co robi:** Najbardziej "cyberbezpieczeństwowy" moduł. Skupia się na analizie retencji danych – sprawdza, czy w pobranej paczce znajdują się informacje, które teoretycznie powinieneś był usunąć. Parsuje logi w poszukiwaniu starych numerów telefonów (które odpiąłeś od konta lat temu), starych adresów e-mail czy usuniętych wydarzeń z kalendarza.
- **Efekt:** Pokazuje "pamięć absolutną" Facebooka. Uświadamia użytkownikowi, że kliknięcie "usuń" w interfejsie Facebooka bardzo często oznacza jedynie ukrycie danej informacji przed ludźmi, podczas gdy w bazach danych Meta (i w plikach kopii zapasowej) te powiązania wciąż istnieją.