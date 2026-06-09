"""Bazowy szablon modułu dla folderu modules.

Każdy moduł powinien dziedziczyć po BaseModule i definiować:
- slide_texts()           # lista tekstów slajdów
- tile_title()            # nazwa kafla
- tile_subtitle()         # tekst pod nagłówkiem kafla
- panel_1(), panel_2(), panel_3(), panel_4()  # zawartość 4 kafli
- analyze()               # opcjonalna analiza wyników
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional
import os
import glob
import re
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class ImageSlideshowFrame(tk.Frame):
    def __init__(self, parent, image_paths, on_finish=None, **kwargs):
        super().__init__(parent, bg="white", **kwargs)
        self.image_paths = image_paths
        self.on_finish = on_finish
        self.current_index = 0
        
        self.label = tk.Label(self, bg="white")
        self.label.pack(fill="both", expand=True)
        
        self.label.bind("<Configure>", self.on_resize)
        
        self.pil_image = None
        self.tk_image = None
        
        if not Image or not ImageTk:
            self.label.config(text="Biblioteka Pillow (PIL) jest niedostępna.", fg="red", font=("Helvetica", 16))
        elif not self.image_paths:
            self.label.config(text="Brak zdjęć w folderze historii.", fg="black", font=("Helvetica", 16))
        else:
            self.load_image()
        
    def load_image(self):
        if not self.image_paths or self.current_index >= len(self.image_paths):
            return
        path = self.image_paths[self.current_index]
        try:
            self.pil_image = Image.open(path)
            self.display_image()
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            self.label.config(text=f"Błąd ładowania obrazu:\n{os.path.basename(path)}", fg="red", font=("Helvetica", 14))
            
    def display_image(self):
        if not self.pil_image:
            return
            
        # Get label dimensions
        width = self.label.winfo_width()
        height = self.label.winfo_height()
        
        # If dimensions are too small, use container dimensions or fallback
        if width <= 10 or height <= 10:
            width = self.winfo_width()
            height = self.winfo_height()
        if width <= 10 or height <= 10:
            width = 800
            height = 600
            
        # Calculate scale ratio to preserve aspect ratio
        img_width, img_height = self.pil_image.size
        ratio = min(width / img_width, height / img_height)
        new_width = max(1, int(img_width * ratio))
        new_height = max(1, int(img_height * ratio))
        
        # Resize image
        resized_pil = self.pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized_pil)
        
        self.label.config(image=self.tk_image, text="") # clear text
        
    def on_resize(self, event):
        self.display_image()
        
    def next_slide(self, loop=True):
        if not self.image_paths:
            return False
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.load_image()
            return True
        elif loop:
            self.current_index = 0
            self.load_image()
            return True
        else:
            if self.on_finish:
                self.on_finish()
            return False

    def prev_slide(self, loop=True):
        if not self.image_paths:
            return False
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()
            return True
        elif loop:
            self.current_index = len(self.image_paths) - 1
            self.load_image()
            return True
        return False


class BaseModule(ttk.Frame):
    @classmethod
    def slide_texts(cls) -> List[str]:
        return []

    @classmethod
    def tile_title(cls) -> str:
        return cls.__name__

    @classmethod
    def tile_subtitle(cls) -> str:
        return ""

    def panel_1(self) -> None:
        return None

    def panel_2(self) -> None:
        return None

    def panel_3(self) -> None:
        return None

    def panel_4(self) -> None:
        return None

    def __init__(self, parent: tk.Widget, data: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.data = data or {}
        self.slide_index = 0
        self.in_history_slideshow = False
        self.slideshow_frame = None

        # Pobieramy slajdy zdefiniowane w podklasie
        raw_slides = list(self.slide_texts())
        # Automatycznie upewniamy się, że ostatni slajd to "W Twoim przypadku ..."
        if raw_slides:
            if raw_slides[-1] != "W Twoim przypadku ...":
                raw_slides.append("W Twoim przypadku ...")
        else:
            raw_slides = ["W Twoim przypadku ..."]
        self.slides = raw_slides

        self.analysis = self.analyze()
        self.build_ui()
        self.bind_all("<space>", self.on_space)
        self.bind_all("<Left>", self.on_left)
        self.bind_all("<Right>", self.on_right)

    def analyze(self) -> Dict[str, Any]:
        return {
            "summary": "Brak danych do analizy.",
            "details": {},
        }
    
    def build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        # Wiersz 1 (tam gdzie są slajdy) musi mieć pełną wagę rozciągania
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)

        self.slide_container = tk.Frame(self, bg="white", bd=2, relief="solid")
        self.slide_container.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.slide_container.columnconfigure(0, weight=1)
        self.slide_container.rowconfigure(0, weight=1)

        slides = self.slides
        self.slide_text = tk.Label(
            self.slide_container,
            text=slides[0] if slides else "Brak slajdów.",
            wraplength=900,
            justify="center",
            bg="white",
            fg="black",
            font=("Helvetica", 32),
        )
        self.slide_text.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)

        self.slide_hint = ttk.Label(self, text="Naciśnij SPACJĘ, aby przejść dalej", font=("Helvetica", 10))
        self.slide_hint.grid(row=2, column=0, sticky="e", pady=(0, 10))

        # result_frame startuje w row=3, wyzerowane ramki i grubości podświetlenia
        self.result_frame = tk.Frame(self, bd=0, highlightthickness=0)
        self.result_frame.grid(row=3, column=0, sticky="nsew")
        self.result_frame.grid_remove()

        # Detale na sam dół ramki wynikowej
        self.result_details = ttk.Frame(self.result_frame)
        self.result_details.pack(side="bottom", fill="x", pady=0)
        self.result_details.columnconfigure(0, weight=1)

        details = self.analysis.get("details", {})
        for row_index, (key, value) in enumerate(details.items(), start=0):
            detail_label = ttk.Label(
                self.result_details,
                text=f"{key.replace('_', ' ').capitalize()}: {value}",
                wraplength=900,
                justify="left",
            )
            detail_label.grid(row=row_index, column=0, sticky="w", pady=(0, 2))

        # Kontener na kafle zajmuje CAŁĄ pozostałą przestrzeń w result_frame
        # Zamiana na tk.Frame z bd=0 aby całkowicie pozbyć się ukrytych marginesów ttk
        self.panels_container = tk.Frame(self.result_frame, bd=0, highlightthickness=0)
        self.panels_container.pack(side="top", fill="both", expand=True, pady=0, padx=0)
        
        self.panels_container.columnconfigure(0, weight=1, uniform="moje_kolumny")
        self.panels_container.columnconfigure(1, weight=1, uniform="moje_kolumny")
        self.panels_container.rowconfigure(0, weight=1, uniform="moje_wiersze")
        self.panels_container.rowconfigure(1, weight=1, uniform="moje_wiersze")

        self.panels = []  # type: List[tk.Frame]
        
        # --- Ustawienie 12 pikseli na środku ---
        gap = 12 
        half_gap = gap // 2 # 6 pikseli na kafel

        for r in range(2):
            for c in range(2):
                panel = tk.Frame(
                    self.panels_container,
                    bg="white",
                    highlightbackground="black",
                    highlightthickness=1,
                    bd=0 # Zabezpieczenie przed dodatkową ramką
                )
                
                # Asymetryczny padding dla kolumn: z lewej / z prawej
                pad_x = (0, half_gap) if c == 0 else (half_gap, 0)
                
                # Asymetryczny padding dla wierszy: z góry / z dołu
                pad_y = (0, half_gap) if r == 0 else (half_gap, 0)

                panel.grid(row=r, column=c, sticky="nsew", padx=pad_x, pady=pad_y)
                
                panel.pack_propagate(False)
                panel.grid_propagate(False)
                self.panels.append(panel)

    # -- Panel helpers -------------------------------------------------
    def clear_panels(self) -> None:
        for panel in self.panels:
            for child in panel.winfo_children():
                child.destroy()

    def _add_title_to_panel(self, panel: tk.Widget, title: Optional[str]) -> None:
        if title:
            lbl = tk.Label(panel, text=title, font=("Helvetica", 14, "bold"), bg="white", anchor="w")
            lbl.pack(fill="x", anchor="nw", padx=(4, 0), pady=(4, 6))

    def add_table(self, panel_index: Optional[int] = None, rows=None, title: Optional[str] = None, columns: Optional[List[str]] = None, col_widths: Optional[List[int]] = None) -> None:
        if panel_index is None:
            panel_index = getattr(self, "_current_panel_index", 0)
        elif not isinstance(panel_index, int):
            if rows is None:
                rows = panel_index
            else:
                columns = title
                title = rows
                rows = panel_index
            panel_index = getattr(self, "_current_panel_index", 0)

        panel = self.panels[panel_index]
        self._add_title_to_panel(panel, title)

        container = tk.Frame(panel, bg="white", bd=0, highlightthickness=0)
        container.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        if isinstance(rows, dict):
            rows = list(rows.items())

        if columns is None:
            if rows and isinstance(rows[0], dict):
                columns = list(rows[0].keys())
            elif rows and isinstance(rows[0], (list, tuple)):
                columns = [f"Kolumna {i + 1}" for i in range(len(rows[0]))]
            else:
                columns = ["Wartość"]

        tree = ttk.Treeview(container, columns=columns, show="headings", selectmode="none")
        for i, col in enumerate(columns):
            tree.heading(col, text=col) # set header
            if col_widths and i < len(col_widths):
                # set specified column widths 
                tree.column(col, width=col_widths[i], minwidth=50, stretch=True)
            else:
                # default width
                tree.column(col, width=140, minwidth=60, stretch=True)
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        def parse_value(value):
            try:
                return float(str(value).replace(",", "."))
            except Exception:
                return str(value).lower()

        def sort_treeview_column(col, reverse=False):
            items = [(parse_value(tree.set(k, col)), k) for k in tree.get_children("")]
            items.sort(reverse=reverse, key=lambda x: x[0])
            for index, (_, item) in enumerate(items):
                tree.move(item, "", index)
            tree._sort_reverse[col] = not reverse

            for heading_col in columns:
                arrow = ""
                if heading_col == col:
                    arrow = " ▼" if reverse else " ▲"
                tree.heading(
                    heading_col,
                    text=tree._heading_texts[heading_col] + arrow,
                    anchor="center",
                    command=lambda col=heading_col: sort_treeview_column(col, tree._sort_reverse.get(col, False)),
                )

        tree._sort_reverse = {}
        tree._heading_texts = {column: column for column in columns}

        for column in columns:
            tree.heading(
                column,
                text=column,
                anchor="center",
                command=lambda col=column: sort_treeview_column(col, tree._sort_reverse.get(col, False)),
            )

        tree.tag_configure("oddrow", background="white")
        tree.tag_configure("evenrow", background="#f5f5f5")

        if rows:
            for row_index, row in enumerate(rows):
                if isinstance(row, dict):
                    values = [str(row.get(col, "")) for col in columns]
                elif isinstance(row, (list, tuple)):
                    values = [str(v) for v in row]
                else:
                    values = [str(row)]
                tag = "evenrow" if row_index % 2 else "oddrow"
                tree.insert("", "end", values=values, tags=(tag,))

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

    def _plot_with_matplotlib(self, panel: tk.Widget, fig) -> None:
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except Exception:
            err = ttk.Label(panel, text="Matplotlib not available", foreground="red")
            err.pack()
            return
        canvas = FigureCanvasTkAgg(fig, master=panel)
        canvas.draw()
        widget = canvas.get_tk_widget()
        try:
            widget.configure(bg="white", bd=0, highlightthickness=0)
            fig.patch.set_facecolor("white")
        except Exception:
            pass
        widget.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    def add_pie_chart(self, panel_index: Optional[int] = None, data: Dict[str, float] = None, title: Optional[str] = None) -> None:
        if panel_index is None:
            panel_index = getattr(self, "_current_panel_index", 0)
        elif not isinstance(panel_index, int):
            if data is None:
                data = panel_index
            else:
                title = data
                data = panel_index
            panel_index = getattr(self, "_current_panel_index", 0)

        panel = self.panels[panel_index]
        self._add_title_to_panel(panel, title)
        try:
            import matplotlib.pyplot as plt

            fig = plt.Figure(figsize=(4, 3), dpi=100)
            ax = fig.add_subplot(111)
            labels = list(data.keys())
            sizes = list(data.values())
            ax.pie(sizes, labels=labels, autopct="%1.1f%%")
            ax.axis("equal")
            
            # pad=0 zmniejsza wewnętrzne marginesy samego wykresu
            fig.tight_layout(pad=0) 
            self._plot_with_matplotlib(panel, fig)
        except Exception:
            err = ttk.Label(panel, text="Cannot render pie chart", foreground="red")
            err.pack(padx=4, pady=(0, 4))

    def add_bar_chart(self, panel_index: Optional[int] = None, data: Dict[str, float] = None, title: Optional[str] = None) -> None:
        if panel_index is None:
            panel_index = getattr(self, "_current_panel_index", 0)
        elif not isinstance(panel_index, int):
            if data is None:
                data = panel_index
            else:
                title = data
                data = panel_index
            panel_index = getattr(self, "_current_panel_index", 0)

        panel = self.panels[panel_index]
        self._add_title_to_panel(panel, title)
        try:
            import matplotlib.pyplot as plt

            fig = plt.Figure(figsize=(4, 3), dpi=100)
            ax = fig.add_subplot(111)
            labels = list(data.keys())
            values = list(data.values())
            ax.bar(labels, values)
            
            fig.tight_layout(pad=0.2)
            self._plot_with_matplotlib(panel, fig)
        except Exception:
            err = ttk.Label(panel, text="Cannot render bar chart", foreground="red")
            err.pack(padx=4, pady=(0, 4))

    def add_line_chart(self, panel_index: Optional[int] = None, x=None, y=None, title: Optional[str] = None) -> None:
        if panel_index is None:
            panel_index = getattr(self, "_current_panel_index", 0)
        elif not isinstance(panel_index, int):
            if x is None:
                x = panel_index
            elif y is None:
                if isinstance(x, str):
                    title = x
                    x = panel_index
                else:
                    y = x
                    x = panel_index
            else:
                title = y
                y = x
                x = panel_index
            panel_index = getattr(self, "_current_panel_index", 0)

        panel = self.panels[panel_index]
        self._add_title_to_panel(panel, title)
        try:
            import matplotlib.pyplot as plt

            fig = plt.Figure(figsize=(4, 3), dpi=100)
            ax = fig.add_subplot(111)
            if y is None and isinstance(x, dict):
                labels = list(x.keys())
                values = list(x.values())
                ax.plot(values)
                ax.set_xticks(range(len(labels)))
                ax.set_xticklabels(labels, rotation=45, ha="right")
            else:
                ax.plot(x, y)
                
            fig.tight_layout(pad=0.2)
            self._plot_with_matplotlib(panel, fig)
        except Exception:
            err = ttk.Label(panel, text="Cannot render line chart", foreground="red")
            err.pack(padx=4, pady=(0, 4))

    def add_kpi_card(
        self,
        panel_index: Optional[int] = None,
        value: str = "",
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        badge_text: Optional[str] = None,  # Ignorowane (przestarzałe)
        badge_type: str = "info"            # Ignorowane (przestarzałe)
    ) -> None:
        if panel_index is None:
            panel_index = getattr(self, "_current_panel_index", 0)
        elif not isinstance(panel_index, int):
            if value == "":
                value = panel_index
            else:
                subtitle = title
                title = value
                value = panel_index
            panel_index = getattr(self, "_current_panel_index", 0)

        panel = self.panels[panel_index]
        self._add_title_to_panel(panel, title)

        container = tk.Frame(panel, bg="white", bd=0, highlightthickness=0)
        container.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Wewnętrzny kontener wyśrodkowany pionowo i poziomo w przestrzeni pod tytułem
        inner_container = tk.Frame(container, bg="white")
        inner_container.pack(expand=True)

        # Wyraźnie zwiększona wartość główna KPI dla efektu premium
        val_lbl = tk.Label(
            inner_container,
            text=value,
            font=("Helvetica", 64, "bold"),
            bg="white",
            fg="#111111"
        )
        val_lbl.pack(anchor="center")

        # Minimalnie zwiększony komentarz poniżej wartości (z 10 na 12)
        if subtitle:
            sub_lbl = tk.Label(
                inner_container,
                text=subtitle,
                font=("Helvetica", 12),
                bg="white",
                fg="#555555",
                wraplength=240,
                justify="center"
            )
            sub_lbl.pack(pady=(6, 0), anchor="center")

    def on_space(self, event: tk.Event) -> None:
        if getattr(self, "in_history_slideshow", False):
            return

        slides = self.slides
        if not slides:
            return

        if self.slide_index < len(slides) - 1:
            self.slide_index += 1
            self.slide_text.config(text=slides[self.slide_index])
        else:
            self.show_analysis()

    def on_left(self, event: tk.Event) -> None:
        if getattr(self, "in_history_slideshow", False) and self.slideshow_frame:
            self.slideshow_frame.prev_slide(loop=True)

    def on_right(self, event: tk.Event) -> None:
        if getattr(self, "in_history_slideshow", False) and self.slideshow_frame:
            self.slideshow_frame.next_slide(loop=True)

    def show_analysis(self) -> None:
        self.slide_container.grid_remove()
        self.slide_hint.grid_remove()
        self.clear_panels()

        for idx, panel_method in enumerate([self.panel_1, self.panel_2, self.panel_3, self.panel_4]):
            self._current_panel_index = idx
            panel_method()

        self.result_frame.grid(row=1, column=0, sticky="nsew")

        if hasattr(self, 'on_analysis_shown_cb') and self.on_analysis_shown_cb:
            self.on_analysis_shown_cb()

    def show_history_slideshow(self) -> None:
        self.in_history_slideshow = True
        self.result_frame.grid_remove()
        
        if self.slideshow_frame:
            self.slideshow_frame.destroy()
            
        module_name = getattr(self, "module_name", None) or self.__class__.__module__.split('.')[-1]
        stories_dir = os.path.join('modules', 'stories', module_name)
        
        extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif']
        image_paths = []
        if os.path.isdir(stories_dir):
            for ext in extensions:
                image_paths.extend(glob.glob(os.path.join(stories_dir, ext)))
                image_paths.extend(glob.glob(os.path.join(stories_dir, ext.upper())))
                
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]
            
        image_paths = sorted(list(set(image_paths)), key=lambda x: natural_sort_key(os.path.basename(x)))
        
        self.slideshow_frame = ImageSlideshowFrame(
            self, 
            image_paths, 
            on_finish=self.hide_history_slideshow
        )
        self.slideshow_frame.grid(row=1, column=0, sticky="nsew")
        self.slideshow_frame.focus_set()

    def hide_history_slideshow(self) -> None:
        self.in_history_slideshow = False
        if self.slideshow_frame:
            self.slideshow_frame.destroy()
            self.slideshow_frame = None
        self.result_frame.grid(row=1, column=0, sticky="nsew")
        
        if hasattr(self, 'on_slideshow_ended_cb') and self.on_slideshow_ended_cb:
            self.on_slideshow_ended_cb()

    def destroy(self) -> None:
        self.unbind_all("<space>")
        self.unbind_all("<Left>")
        self.unbind_all("<Right>")
        super().destroy()

    def run_console(self) -> None:
        print(f"=== {self.tile_title()} ===")
        print(self.tile_subtitle())
        print("\nSlajdy:")
        for index, slide in enumerate(self.slides, start=1):
            print(f"{index}. {slide}")
        print("\nWynik analizy:\n")
        print(self.analysis.get("summary", "Brak wyniku analizy."))


if __name__ == "__main__":
    # Testowy blok do uruchamiania modułu jako samodzielnej aplikacji
    root = tk.Tk()
    root.geometry("1024x768")
    root.title("Testowanie układu siatki")
    
    # Subklasa do przetestowania wszystkich dostępnych typów prezentacji
    class TestModule(BaseModule):
        def panel_1(self) -> None:
            self.add_table(
                0,
                rows=[
                    ("Spotify", "Wysokie", "18"),
                    ("Netflix", "Średnie", "12"),
                    ("Tinder", "Niskie", "5")
                ],
                title="Przykładowa Tabela",
                columns=["Firma", "Ryzyko", "Kampanie"]
            )

        def panel_2(self) -> None:
            self.add_kpi_card(
                1,
                value="94%",
                title="Wskaźnik Zagrożenia",
                subtitle="Profil prywatności użytkownika jest krytycznie naruszony"
            )

        def panel_3(self) -> None:
            self.add_line_chart(
                2,
                x={"Sty": 10, "Lut": 15, "Mar": 30, "Kwi": 25},
                title="Wzrost Dopasowań w Czasie"
            )

        def panel_4(self) -> None:
            self.add_pie_chart(
                3,
                data={"E-mail": 70, "Telefon": 30},
                title="Źródła Śledzenia Danych"
            )
            
    module = TestModule(root)
    # Rozszerzenie do absolutnych krawędzi okna przy teście:
    module.pack(fill="both", expand=True, padx=0, pady=0) 
    
    module.show_analysis()
    
    root.mainloop()
