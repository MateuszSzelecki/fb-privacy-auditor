"""Bazowy szablon modułu dla folderu modules.

Każdy moduł powinien dziedziczyć po BaseModule i definiować:
- title
- slide_texts()           # lista tekstów slajdów
- tile_title()            # nazwa kafla
- tile_subtitle()         # tekst pod nagłówkiem kafla
- panel_1(), panel_2(), panel_3(), panel_4()  # zawartość 4 kafli
- analyze()               # opcjonalna analiza wyników
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional

class BaseModule(ttk.Frame):
    title = "Base Module"
    description = "Opis modułu"
    slides: List[str] = []

    @classmethod
    def slide_texts(cls) -> List[str]:
        return list(cls.slides)

    @classmethod
    def tile_title(cls) -> str:
        return cls.title

    @classmethod
    def tile_subtitle(cls) -> str:
        return cls.description

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
        self.analysis = self.analyze()
        self.build_ui()
        self.bind_all("<space>", self.on_space)

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

        slides = self.slide_texts()
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

        # result_frame startuje w row=3, ale zaraz to zmienimy w show_analysis
        self.result_frame = tk.Frame(self)
        self.result_frame.grid(row=3, column=0, sticky="nsew")
        self.result_frame.grid_remove()

        # Detale na sam dół ramki wynikowej
        self.result_details = ttk.Frame(self.result_frame)
        self.result_details.pack(side="bottom", fill="x", pady=(10, 0))
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
        self.panels_container = ttk.Frame(self.result_frame)
        self.panels_container.pack(side="top", fill="both", expand=True, pady=4, padx=4)
        
        self.panels_container.columnconfigure(0, weight=1, uniform="moje_panele")
        self.panels_container.columnconfigure(1, weight=1, uniform="moje_panele")
        self.panels_container.rowconfigure(0, weight=1, uniform="moje_panele")
        self.panels_container.rowconfigure(1, weight=1, uniform="moje_panele")

        self.panels = []  # type: List[tk.Frame]
        for r in range(2):
            for c in range(2):
                panel = tk.Frame(
                    self.panels_container,
                    bg="white",
                    highlightbackground="black",
                    highlightthickness=1,
                )
                panel.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
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
            lbl = tk.Label(panel, text=title, font=("Helvetica", 12), bg="white", anchor="w")
            lbl.pack(fill="x", anchor="nw", pady=(0, 6))

    def add_list(self, panel_index: int, items: List[str], title: Optional[str] = None) -> None:
        panel = self.panels[panel_index]
        self._add_title_to_panel(panel, title)

        # scrollable text area
        container = tk.Frame(panel, bg="white")
        container.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(container, orient="vertical")
        text_widget = tk.Text(container, wrap="word", bg="white", bd=0)
        scrollbar.config(command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        text_widget.pack(side="left", fill="both", expand=True)
        text_widget.insert("1.0", "\n".join(str(x) for x in items))
        text_widget.config(state="disabled")

    def add_sorted_list(self, panel_index: int, items, title: Optional[str] = None, reverse: bool = False) -> None:
        panel = self.panels[panel_index]
        self._add_title_to_panel(panel, title)
        if isinstance(items, dict):
            sorted_items = sorted(items.items(), key=lambda kv: kv[1], reverse=reverse)
            lines = [f"{k}: {v}" for k, v in sorted_items]
        else:
            sorted_items = sorted(items, reverse=reverse)
            lines = [str(x) for x in sorted_items]
        self.add_list(panel_index, lines)

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
            widget.configure(bg="white")
            fig.patch.set_facecolor("white")
        except Exception:
            pass
        widget.pack(fill="both", expand=True)

    def add_pie_chart(self, panel_index: int, data: Dict[str, float], title: Optional[str] = None) -> None:
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
            self._plot_with_matplotlib(panel, fig)
        except Exception:
            err = ttk.Label(panel, text="Cannot render pie chart", foreground="red")
            err.pack()

    def add_bar_chart(self, panel_index: int, data: Dict[str, float], title: Optional[str] = None) -> None:
        panel = self.panels[panel_index]
        self._add_title_to_panel(panel, title)
        try:
            import matplotlib.pyplot as plt

            fig = plt.Figure(figsize=(4, 3), dpi=100)
            ax = fig.add_subplot(111)
            labels = list(data.keys())
            values = list(data.values())
            ax.bar(labels, values)
            fig.tight_layout()
            self._plot_with_matplotlib(panel, fig)
        except Exception:
            err = ttk.Label(panel, text="Cannot render bar chart", foreground="red")
            err.pack()

    def add_line_chart(self, panel_index: int, x, y=None, title: Optional[str] = None) -> None:
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
            fig.tight_layout()
            self._plot_with_matplotlib(panel, fig)
        except Exception:
            err = ttk.Label(panel, text="Cannot render line chart", foreground="red")
            err.pack()

    def on_space(self, event: tk.Event) -> None:
        slides = self.slide_texts()
        if not slides:
            return

        if self.slide_index < len(slides) - 1:
            self.slide_index += 1
            self.slide_text.config(text=slides[self.slide_index])
        else:
            self.show_analysis()

    def show_analysis(self) -> None:
        self.slide_container.grid_remove()
        self.slide_hint.grid_remove()
        self.clear_panels()

        self.panel_1()
        self.panel_2()
        self.panel_3()
        self.panel_4()

        self.result_frame.grid(row=1, column=0, sticky="nsew")

    def destroy(self) -> None:
        self.unbind_all("<space>")
        super().destroy()

    def run_console(self) -> None:
        print(f"=== {self.tile_title()} ===")
        print(self.tile_subtitle())
        print("\nSlajdy:")
        for index, slide in enumerate(self.slide_texts(), start=1):
            print(f"{index}. {slide}")
        print("\nWynik analizy:\n")
        print(self.analysis.get("summary", "Brak wyniku analizy."))


if __name__ == "__main__":
    module = BaseModule(tk.Tk())
    module.run_console()