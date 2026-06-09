import importlib
import pkgutil
import tkinter as tk
from tkinter import ttk, messagebox
import os
import random
import webbrowser

from modules.module_template import BaseModule

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        self.root.title("Facebook Privacy Auditor")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)

        try:
            self.root.state('zoomed')
        except Exception:
            try:
                self.root.attributes('-zoomed', True)
            except Exception:
                pass

        self.style = ttk.Style(self.root)
        self.style.configure('Tile.TFrame', background='#f0f0f0')
        self.style.configure('TileTitle.TLabel', font=('Helvetica', 20, 'bold'), background='#f0f0f0')
        self.style.configure('TileSubtitle.TLabel', font=('Helvetica', 16), background='#f0f0f0')
        self.style.configure('Back.TButton', font=('Helvetica', 12), padding=8)

        self.tiles_config = self.discover_tile_modules()

        self.current_frame = None
        self.show_tile_grid()
        self.root.update_idletasks()
        self.root.after(0, self.root.deiconify)

    def discover_tile_modules(self):
        try:
            modules_package = importlib.import_module('modules')
        except Exception:
            return []

        tiles = []
        for finder, module_name, is_pkg in pkgutil.iter_modules(modules_package.__path__):
            if module_name.startswith('_') or module_name == 'module_template':
                continue

            try:
                module = importlib.import_module(f'modules.{module_name}')
            except Exception:
                continue

            module_class = self.find_module_class(module)
            if module_class is None:
                continue

            title = module_class.tile_title() if callable(getattr(module_class, 'tile_title', None)) else getattr(module_class, 'title', module_name)
            subtitle = module_class.tile_subtitle() if callable(getattr(module_class, 'tile_subtitle', None)) else getattr(module_class, 'description', '')

            tiles.append({
                'title': title,
                'subtitle': subtitle,
                'module_name': module_name,
            })

        tiles.sort(key=lambda item: item['module_name'])
        return tiles

    def find_module_class(self, module):
        candidates = ['Module', 'App', 'Main']
        for candidate in candidates:
            module_class = getattr(module, candidate, None)
            if isinstance(module_class, type) and issubclass(module_class, BaseModule) and module_class is not BaseModule:
                return module_class

        for obj in vars(module).values():
            if isinstance(obj, type) and issubclass(obj, BaseModule) and obj is not BaseModule:
                return obj

        return None

    def show_tile_grid(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = ttk.Frame(self.root, padding=16)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame.rowconfigure(0, weight=0)
        self.current_frame.rowconfigure(1, weight=1)
        self.current_frame.rowconfigure(2, weight=1)
        self.current_frame.rowconfigure(3, weight=1)
        self.current_frame.columnconfigure((0, 1, 2), weight=1)

        header_label = ttk.Label(self.current_frame, text='Facebook Privacy Auditor', font=('Helvetica', 28, 'bold'), cursor='hand2')
        header_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        header_label.bind('<Button-1>', lambda e: self.show_authors())

        for index, tile in enumerate(self.tiles_config, start=1):
            row = (index - 1) // 3
            col = (index - 1) % 3
            row += 1

            tile_frame = ttk.Frame(self.current_frame, style='Tile.TFrame', relief='ridge', padding=12)
            tile_frame.grid(row=row, column=col, sticky='nsew', padx=10, pady=10)
            tile_frame.columnconfigure(0, weight=1)
            tile_frame.rowconfigure(0, weight=1)
            tile_frame.rowconfigure(3, weight=1)

            title_label = ttk.Label(tile_frame, text=tile['title'], style='TileTitle.TLabel', anchor='center', justify='center')
            title_label.grid(row=1, column=0, sticky='ew')

            subtitle_label = ttk.Label(tile_frame, text=tile['subtitle'], style='TileSubtitle.TLabel', anchor='center', wraplength=260, justify='center')
            subtitle_label.grid(row=2, column=0, sticky='ew', pady=(8, 12))

            tile_frame.bind('<Button-1>', lambda e, i=index: self.open_tile_module(i))
            title_label.bind('<Button-1>', lambda e, i=index: self.open_tile_module(i))
            subtitle_label.bind('<Button-1>', lambda e, i=index: self.open_tile_module(i))

    def open_tile_module(self, index):
        tile = self.tiles_config[index - 1]
        self.show_module_view(tile)

    def show_module_view(self, tile):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = ttk.Frame(self.root, padding=16)
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame.rowconfigure(1, weight=1)
        self.current_frame.columnconfigure(0, weight=1)

        header_frame = ttk.Frame(self.current_frame)
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        header_frame.columnconfigure(1, weight=0)
        header_frame.columnconfigure(2, weight=0)

        ttk.Label(header_frame, text=tile['title'], font=('Helvetica', 28, 'bold')).grid(row=0, column=0, sticky='w')
        back_button = ttk.Button(header_frame, text='Powrót', command=self.show_tile_grid, style='Back.TButton')
        back_button.grid(row=0, column=2, sticky='e')

        self.history_button = None

        module_frame = ttk.Frame(self.current_frame, padding=16)
        module_frame.grid(row=1, column=0, sticky='nsew')
        module_frame.columnconfigure(0, weight=1)
        module_frame.rowconfigure(0, weight=1)

        inner_frame = ttk.Frame(module_frame, style='Tile.TFrame', padding=12)
        inner_frame.grid(row=0, column=0, sticky='nsew')
        inner_frame.columnconfigure(0, weight=1)
        inner_frame.rowconfigure(0, weight=1)

        module_widget = self.load_module_widget(tile['module_name'], inner_frame)
        module_widget.grid(row=0, column=0, sticky='nsew')
        module_widget.module_name = tile['module_name']

        # Setup callbacks for "Historia" button
        stories_dir = os.path.join('modules', 'stories', tile['module_name'])
        if os.path.isdir(stories_dir):
            def on_analysis_shown():
                self.show_history_button(header_frame, module_widget)
            def on_slideshow_ended():
                if self.history_button:
                    self.history_button.configure(text='Historia')
            module_widget.on_analysis_shown_cb = on_analysis_shown
            module_widget.on_slideshow_ended_cb = on_slideshow_ended

    def show_history_button(self, header_frame, module_widget):
        if self.history_button:
            self.history_button.destroy()

        self.history_button = ttk.Button(
            header_frame,
            text='Historia',
            command=lambda: self.toggle_history(module_widget),
            style='Back.TButton'
        )
        self.history_button.grid(row=0, column=1, sticky='e', padx=(0, 10))

    def toggle_history(self, module_widget):
        if getattr(module_widget, 'in_history_slideshow', False):
            module_widget.hide_history_slideshow()
            if self.history_button:
                self.history_button.configure(text='Historia')
        else:
            module_widget.show_history_slideshow()
            if self.history_button:
                self.history_button.configure(text='Analiza')

    def show_authors(self):
        authors = [
            "Mateusz Szelecki - pomysł; templatka pod cały projekt; moduły: Cień Tożsamości, Archiwum Emocji",
            "Kacper Rothkegel - moduły: coś",
            "Mateusz Zawieracz - moduły: coś",
            "Mikołaj Osękowski - historie w modułach"
        ]
        random.shuffle(authors)

        sources = [
            ("Centrum Pomocy Meta", "https://www.facebook.com/help/212802592074644", "Instrukcja pobierania kopii swoich danych osobowych"),
            ("Polityka Prywatności Meta", "https://www.facebook.com/privacy/policy", "Zasady zbierania i wykorzystywania danych użytkowników"),
            ("Portal informacyjny RODO (Art. 15)", "https://gdpr-info.eu/art-15-gdpr/", "Prawo dostępu realizowane przez eksport danych"),
            ("The Guardian (Cambridge Analytica)", "https://www.theguardian.com/news/series/cambridge-analytica-files", "Śledztwo o masowym nadużyciu danych z Facebooka"),
            ("Niebezpiecznik.pl", "https://niebezpiecznik.pl/", "Analizy wycieków danych i incydentów prywatności w sieci"),
            ("Biblioteka Matplotlib", "https://matplotlib.org/", "Dokumentacja silnika wykresów statystycznych"),
            ("Biblioteka Tkinter", "https://docs.python.org/3/library/tkinter.html", "Dokumentacja środowiska GUI dla języka Python"),
            ("Tematyka analizy danych na GitHub", "https://github.com/topics/facebook-data-analysis", "Projekty Open Source badające prywatność w Meta"),
            ("Platforma Canva", "https://www.canva.com/", "Projektowanie szablonów graficznych i slajdów do historii")
        ]

        popup = tk.Toplevel(self.root)
        popup.title("Autorzy i źródła projektu")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        popup.configure(bg="#f8f9fa")

        popup_frame = tk.Frame(popup, bg="#ffffff", bd=1, relief="solid")
        popup_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        title_lbl = tk.Label(popup_frame, text="Autorzy Projektu", font=("Helvetica", 16, "bold"), bg="#ffffff", fg="#333333")
        title_lbl.pack(pady=(10, 8))

        for author in authors:
            parts = author.split(" - ", 1)
            name = parts[0]
            role = parts[1] if len(parts) > 1 else ""

            author_frame = tk.Frame(popup_frame, bg="#ffffff")
            author_frame.pack(fill="x", padx=20, pady=4)

            name_lbl = tk.Label(author_frame, text=name, font=("Helvetica", 10, "bold"), bg="#ffffff", fg="#0056b3", anchor="w")
            name_lbl.pack(side="left")

            role_lbl = tk.Label(author_frame, text=f" - {role}", font=("Helvetica", 10), bg="#ffffff", fg="#555555", anchor="w", wraplength=420, justify="left")
            role_lbl.pack(side="left", fill="x", expand=True)

        separator = tk.Frame(popup_frame, height=1, bg="#dddddd", bd=0)
        separator.pack(fill="x", padx=20, pady=(15, 10))

        sources_title_lbl = tk.Label(popup_frame, text="Źródła i Dokumentacja", font=("Helvetica", 16, "bold"), bg="#ffffff", fg="#333333")
        sources_title_lbl.pack(pady=(5, 8))

        for name, url, desc in sources:
            source_frame = tk.Frame(popup_frame, bg="#ffffff")
            source_frame.pack(fill="x", padx=20, pady=4)

            top_frame = tk.Frame(source_frame, bg="#ffffff")
            top_frame.pack(fill="x", anchor="w")

            name_lbl = tk.Label(top_frame, text=name, font=("Helvetica", 9, "bold"), bg="#ffffff", fg="#495057", anchor="w")
            name_lbl.pack(side="left")

            desc_lbl = tk.Label(top_frame, text=f" - {desc}", font=("Helvetica", 9), bg="#ffffff", fg="#6c757d", anchor="w")
            desc_lbl.pack(side="left")

            url_lbl = tk.Label(source_frame, text=url, font=("Courier", 8, "underline"), bg="#ffffff", fg="#007bff", cursor="hand2", anchor="w")
            url_lbl.pack(side="top", anchor="w", padx=(10, 0))
            url_lbl.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

        # Dynamically calculate window height
        popup.update_idletasks()
        popup_w = 640
        popup_h = popup.winfo_reqheight()

        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()

        x = root_x + (root_w - popup_w) // 2
        y = root_y + (root_h - popup_h) // 2
        popup.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

    def load_module_widget(self, module_name, parent):
        try:
            module = importlib.import_module(f'modules.{module_name}')
        except ModuleNotFoundError:
            return ttk.Label(parent, text=f'Brak modułu: {module_name}', font=('Helvetica', 14), foreground='red')

        module_class = None
        for candidate in ['Module', 'App', 'Main', f'{module_name.capitalize()}']:
            module_class = getattr(module, candidate, None)
            if module_class:
                break

        if module_class is None:
            return ttk.Label(parent, text=f'Brak klasy modułu w {module_name}', font=('Helvetica', 14), foreground='red')

        try:
            widget = module_class(parent)
            return widget
        except Exception as exc:
            return ttk.Label(parent, text=f'Błąd uruchomienia modułu:\n{exc}', font=('Helvetica', 14), foreground='red', justify='center')


if __name__ == '__main__':
    root = tk.Tk()
    MainApp(root)
    root.mainloop()
