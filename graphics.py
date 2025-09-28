import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import random
from formulario import categorie_formule
import re


class NomenclaturaApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Nomenclatura Chimica")
        self.geometry("1200x850")
        self.minsize(1000, 700)
        self.configure(bg="#2b2b2b")

        # Stato
        self.formule_filtrate = []
        self.mappa_categoria = {}
        self.formula_corrente = None
        self.categoria_corrente = None

        # Stili ttk consolidati
        self.style = ttk.Style(self)
        self._configure_styles()

        # Variabili
        self.nomenclatura_var = tk.StringVar(value="tutte")
        self.modalita_var = tk.StringVar(value="formula2nome")

        # checkbutton variables for Nomenclatura and Modalità
        self.nom_vars = {}
        self.mode_vars = {}
        self.gruppi_vars = {}
        for nome in ["Ossidi Basici", "Ossidi Acidi", "Eccezioni Ossidi", "Idrossidi",
                     "Ossiacidi", "Ternari Anfoteri", "Perossidi", "Idracidi",
                     "Idruri", "Sali Binari", "Sali Ternari", "Sali Ternari Acidi"]:
            self.gruppi_vars[nome] = tk.BooleanVar(value=True)

        # Layout
        self._create_top_controls()
        self._create_molecule_display()
        self._create_input_area()
        self._create_action_buttons()
        self._create_bottom_area()

        # Inizializza
        self.aggiorna_filtri()
        self.nuova_formula()
        self.apply_theme()

    # ------------------ Creazione UI ------------------
    def _configure_styles(self):
        base_bg = "#2b2b2b"
        self.style.theme_use('default')

        self.style.configure(
            'Primary.TButton',
            background='#444',
            foreground='white',
            relief='flat',
            font=('Arial', 11, 'bold'),
            padding=6,
            borderwidth=1
        )
        self.style.map(
            'Primary.TButton',
            background=[('active', '#555')]
        )
        # Bordered button style
        self.style.configure(
            'Bordered.TButton',
            background='#444',
            foreground='white',
            font=('Arial', 11, 'bold'),
            padding=6,
            borderwidth=2,
            relief='solid',
            highlightthickness=1,
            highlightbackground='#fff'
        )
        self.style.map(
            'Bordered.TButton',
            background=[('active', '#555')]
        )
        self.style.configure('Dark.TLabelframe', background=base_bg,
                             foreground='white', font=('Arial', 10, 'bold'))
        self.style.configure('Dark.TLabelframe.Label', background=base_bg,
                             foreground='white', font=('Arial', 11, 'bold'))
        # Custom uniform button styles
        self.style.configure("Custom.TButton",
                             background="#444", foreground="white",
                             font=("Arial", 12, "bold"),
                             relief="flat", padding=10)
        self.style.map("Custom.TButton",
                       background=[("active", "#555")],
                       relief=[("pressed", "flat")])

        self.style.configure(
            "Option.TCheckbutton",
            background=base_bg,
            foreground="white",
            font=("Arial", 11, "bold"),
            indicatoron=True,
            indicatormargin=2,
            indicatordiameter=13,  
            padding=4
        )
        self.style.map(
            "Option.TCheckbutton",
            background=[("active", base_bg)],
            indicatorcolor=[("selected", "#0078d7"), ("!selected", "#2b2b2b")],
            foreground=[("active", "white")]
        )
        # Add Dark.TButton style -- visually matches entries' border and background, and more vertical padding
        self.style.configure(
            "Dark.TButton",
            background="#3a3a3a",
            foreground="white",
            font=("Arial", 11, "bold"),
            borderwidth=1,
            relief="ridge",
            padding=(12, 8)
        )
        self.style.map(
            "Dark.TButton",
            background=[("active", "#555")],
            foreground=[("active", "white")]
        )

    def _select_exclusive(self, varname, value, group_vars, group_name):
       
        for k, v in group_vars.items():
            if k == varname:
                v.set(True)
            else:
                v.set(False)
    
        if group_name == "nomenclatura":
            self.nomenclatura_var.set(value)
            self._on_modalita_changed()
            self.nuova_formula()
        elif group_name == "modalita":
            self.modalita_var.set(value)
            self._on_modalita_changed()

    def _create_top_controls(self):
        top = tk.Frame(self, bg='#2b2b2b')

        top.pack(fill='x', padx=10, pady=10)

        # --- Gruppi Frame: 4 columns x 3 rows grid, all categories, "Ossidi" and "Ternari anfoteri" in last two slots ---
        gruppi_frame = ttk.LabelFrame(top, text='Gruppi', style='Dark.TLabelframe')
        gruppi_frame.pack(side='left', padx=8, pady=5, fill='both', expand=True)
        gruppi_frame.configure(width=500)
        gruppi_frame.pack_propagate(False)


        order = [
            ("Ossidi Basici", 0, 0), ("Ossidi Acidi", 1, 0), ("Idrossidi", 2, 0),
            ("Ossiacidi", 0, 1), ("Perossidi", 1, 1), ("Idracidi", 2, 1),
            ("Idruri", 0, 2), ("Sali Binari", 1, 2), ("Sali Ternari", 2, 2),
            ("Sali Ternari Acidi", 0, 3), ("Eccezioni Ossidi", 1, 3), ("Ternari Anfoteri", 2, 3),
        ]
        for nome, r, c in order:
            if nome in self.gruppi_vars:
                cb = ttk.Checkbutton(gruppi_frame, text=nome, variable=self.gruppi_vars[nome],
                                     style='Option.TCheckbutton', command=self.aggiorna_filtri)
                cb.grid(row=r, column=c, sticky='w', padx=8, pady=4)


        side_frame_width = 130
        nom_frame = ttk.LabelFrame(top, text='Nomenclatura', style='Dark.TLabelframe')
        nom_frame.pack(side='left', padx=8, pady=5, fill='both', expand=True)
        nom_frame.configure(width=side_frame_width)
        nom_frame.pack_propagate(False)
        opts = [('Entrambe', 'tutte'), ('IUPAC', 'iupac'), ('Tradizionale', 'tradizionale')]

        for text, val in opts:
            self.nom_vars[val] = tk.BooleanVar(value=(self.nomenclatura_var.get() == val))
        for text, val in opts:
            cb = ttk.Checkbutton(
                nom_frame,
                text=text,
                variable=self.nom_vars[val],
                style='Option.TCheckbutton',
                command=lambda v=val: self._select_exclusive(v, v, self.nom_vars, "nomenclatura")
            )
            cb.pack(anchor='w', pady=2, padx=6)

        mode_frame = ttk.LabelFrame(top, text='Modalità', style='Dark.TLabelframe')
        mode_frame.pack(side='left', padx=8, pady=5, fill='both', expand=True)
        mode_frame.configure(width=side_frame_width)
        mode_frame.pack_propagate(False)
        modes = [('Formula', 'formula2nome'), ('Nome', 'nome2formula')]
        for text, val in modes:
            self.mode_vars[val] = tk.BooleanVar(value=(self.modalita_var.get() == val))
        for text, val in modes:
            cb = ttk.Checkbutton(
                mode_frame,
                text=text,
                variable=self.mode_vars[val],
                style='Option.TCheckbutton',
                command=lambda v=val: self._select_exclusive(v, v, self.mode_vars, "modalita")
            )
            cb.pack(anchor='w', pady=2, padx=6)


        def sync_height(event=None):
            h1 = gruppi_frame.winfo_height()
            h2 = nom_frame.winfo_height()
            h3 = mode_frame.winfo_height()
            max_h = max(h1, h2, h3)
            if max_h > 1:
                gruppi_frame.configure(height=max_h)
                nom_frame.configure(height=max_h)
                mode_frame.configure(height=max_h)
                gruppi_frame.pack_propagate(False)
                nom_frame.pack_propagate(False)
                mode_frame.pack_propagate(False)
        gruppi_frame.bind("<Configure>", sync_height)
        nom_frame.bind("<Configure>", sync_height)
        mode_frame.bind("<Configure>", sync_height)


        self.style.configure("Dark.TSeparator", background="#111")
        sep = ttk.Separator(self, orient='horizontal', style="Dark.TSeparator")
        sep.pack(fill='x', padx=10, pady=4)

    def _create_molecule_display(self):
        molecule_frame = tk.Frame(
            self,
            bg='#3a3a3a',
            bd=2,
            relief='ridge',
            highlightthickness=1,
            highlightbackground="#000",
            highlightcolor="#000"
        )
        molecule_frame.pack(fill='both', padx=20, pady=(30, 10), expand=False)
        molecule_frame.configure(height=180)
        molecule_frame.pack_propagate(False)

        self.formula_canvas = tk.Canvas(molecule_frame, bg='#3a3a3a', highlightthickness=0)
        self.formula_canvas.pack(fill='both', expand=True)

        self.formula_canvas.bind("<Configure>", lambda e: self._refresh_display())

    def _create_input_area(self):
        frame = tk.Frame(self, bg='#2b2b2b')
        frame.pack(pady=6, anchor='center')


        self.input_container = tk.Frame(frame, bg='#2b2b2b')
        self.input_container.pack(anchor='w')

        # Configure grid columns for alignment
        self.input_container.grid_columnconfigure(0, weight=0, minsize=150)  # labels
        self.input_container.grid_columnconfigure(1, weight=1)               # entries
        self.input_container.grid_columnconfigure(2, minsize=100)            # blank spacing between entries and buttons
        self.input_container.grid_columnconfigure(3, weight=0)               # action buttons

        # Create and store label and entry widgets as instance attributes
        self.iupac_label = tk.Label(self.input_container, text='Nome IUPAC:', bg='#2b2b2b', fg='white')
        self.iupac_entry = tk.Entry(
            self.input_container,
            font=('Arial', 12),
            width=60,
            bg='#444',
            fg='white',
            insertbackground='white',
            highlightcolor="#000",
            highlightbackground="#000",
            highlightthickness=1
        )
        self.trad_label = tk.Label(self.input_container, text='Nome Tradizionale:', bg='#2b2b2b', fg='white')
        self.trad_entry = tk.Entry(
            self.input_container,
            font=('Arial', 12),
            width=60,
            bg='#444',
            fg='white',
            insertbackground='white',
            highlightcolor="#000",
            highlightbackground="#000",
            highlightthickness=1
        )
        self.formula_label = tk.Label(self.input_container, text='Formula:', bg='#2b2b2b', fg='white')
        self.formula_entry = tk.Entry(
            self.input_container,
            font=('Arial', 12),
            width=60,
            bg='#444',
            fg='white',
            insertbackground='white',
            highlightcolor="#000",
            highlightbackground="#000",
            highlightthickness=1
        )


        self.formula_placeholder = "Ex. H2O2"
        self.formula_entry.insert(0, self.formula_placeholder)
        self.formula_entry.config(fg='#bbb')


        def _clear_placeholder(event):
            if event.widget == self.formula_entry and self.formula_entry.get() == self.formula_placeholder:
                self.formula_entry.delete(0, 'end')
                self.formula_entry.config(fg='white')

        def _add_placeholder(event):
            if event.widget == self.formula_entry and not self.formula_entry.get():
                self.formula_entry.insert(0, self.formula_placeholder)
                self.formula_entry.config(fg='#bbb')
        self.formula_entry.bind("<Button-1>", _clear_placeholder)
        self.formula_entry.bind("<FocusOut>", _add_placeholder)

        # Bind Return key to verifica on all input fields
        self.iupac_entry.bind("<Return>", lambda e: self.verifica())
        self.trad_entry.bind("<Return>", lambda e: self.verifica())
        self.formula_entry.bind("<Return>", lambda e: self.verifica())


        self.nuova_btn = ttk.Button(
            self.input_container,
            text='Nuova',
            command=self.nuova_formula,
            style="Dark.TButton"
        )
        self.verifica_btn = ttk.Button(
            self.input_container,
            text='Verifica',
            command=self.verifica,
            style="Dark.TButton"
        )


        self.iupac_label.grid(row=0, column=0, sticky='e', padx=6, pady=4)
        self.iupac_entry.grid(row=0, column=1, padx=6, pady=4, sticky='w')
        self.trad_label.grid(row=1, column=0, sticky='e', padx=6, pady=4)
        self.trad_entry.grid(row=1, column=1, padx=6, pady=4, sticky='w')
        self.formula_label.grid(row=2, column=0, sticky='e', padx=6, pady=4)
        self.formula_entry.grid(row=2, column=1, padx=6, pady=4, sticky='w')


        self.nuova_btn.grid(row=0, column=3, padx=6, pady=4, sticky='w')
        self.verifica_btn.grid(row=1, column=3, padx=6, pady=4, sticky='w')

    def _create_action_buttons(self):

        self.result_label = tk.Label(self, text='', font=('Arial', 16, 'bold'), bg='#2b2b2b', fg='white')
        self.result_label.pack(pady=6)
        self._on_modalita_changed()

    def _create_bottom_area(self):
        self.current_rule_title = None
        bottom = tk.Frame(self, bg='#222')
        bottom.pack(fill='both', expand=True, padx=10, pady=(0, 7))

        # --- Rules container now packed directly into bottom, no border frame ---
        rules_container = ttk.LabelFrame(
            bottom,
            text='Regole',
            style='Dark.TLabelframe',
            padding=(6,12),
            borderwidth=2,
            relief="ridge"
        )
        rules_container.pack(side='left', fill='both', expand=True, padx=8, pady=6)
        rules_container.pack_propagate(False)

        # --- Grid of rule buttons ---
        sel_frame = tk.Frame(rules_container, bg='#2b2b2b')

        self.rule_titles = [
            "Regole N.O.", "Ossidi basici", "Ossidi acidi", "Idrossidi",
            "Ossiacidi", "Perossidi", "Idracidi", "Idruri",
            "Sali binari", "Sali ternari", "Sali ternari acidi"
        ]

        self.rule_contents = self._default_rule_contents()

        sel_frame.grid(row=0, column=0, sticky='nsew', padx=6, pady=6)
        rules_container.grid_columnconfigure(0, weight=0)
        rules_container.grid_columnconfigure(1, weight=1)
        rules_container.rowconfigure(0, weight=1)

        rule_buttons = []
        for idx, title in enumerate(self.rule_titles):
            # Use Dark.TButton style for rule buttons and ensure padding is not clipped
            b = ttk.Button(sel_frame, text=title, style='Dark.TButton', command=lambda t=title: self._toggle_rule(t))
            rule_buttons.append(b)

        n_cols = 2
        n_rows = 5
        for i, btn in enumerate(rule_buttons):
            if i < 10:
                row = i % n_rows
                col = i // n_rows
                btn.grid(row=row, column=col, padx=2, pady=3, sticky='nsew')
            else:
                btn.grid(row=n_rows, column=0, columnspan=2, padx=2, pady=3, sticky='nsew')

        for r in range(n_rows + 1):
            sel_frame.grid_rowconfigure(r, weight=1)
        for c in range(n_cols):
            sel_frame.grid_columnconfigure(c, weight=1)

        self.rule_text = tk.Text(
            rules_container,
            wrap='word',
            font=('Arial', 13),
            bg='#3a3a3a',
            fg='white',
            insertbackground='white',
            highlightthickness=1,
            highlightbackground="#444",
            highlightcolor="#444",
            bd=0
        )
        self.rule_text.grid(row=0, column=1, sticky='nsew', padx=(22,14), pady=14)
        self.rule_text.config(state='disabled')
        self.rule_text.config(padx=6, pady=6)

        # Sezione note
        notes_frame = ttk.LabelFrame(bottom, text='Note', style='Dark.TLabelframe', padding=(6,12))
        notes_frame.pack(side='right', fill='both', expand=True, padx=8, pady=6)
        self.notes_text = tk.Text(
            notes_frame,
            wrap='word',
            font=('Arial', 11),
            bg='#333',
            fg='white',
            highlightthickness=1,
            highlightbackground="#444",
            highlightcolor="#444",
            bd=0
        )
        self.notes_text.pack(fill='both', expand=True)
        self.notes_text.config(padx=6, pady=6)

        self._show_rule(self.rule_titles[0])

    # ------------------ Funzioni di utilità ------------------
    def _on_modalita_changed(self):
        modo = self.modalita_var.get()
        if modo == 'formula2nome':

            self.formula_label.grid_remove()
            self.formula_entry.grid_remove()
            scelta = self.nomenclatura_var.get()
            if scelta == 'tutte':

                self.iupac_label.grid(row=0, column=0, sticky='e', padx=6, pady=4)
                self.iupac_entry.grid(row=0, column=1, padx=6, pady=4, sticky='w')
                self.trad_label.grid(row=1, column=0, sticky='e', padx=6, pady=4)
                self.trad_entry.grid(row=1, column=1, padx=6, pady=4, sticky='w')
            elif scelta == 'iupac':

                self.trad_label.grid_remove()
                self.trad_entry.grid_remove()
                self.iupac_label.grid(row=0, column=0, sticky='e', padx=6, pady=4)
                self.iupac_entry.grid(row=0, column=1, padx=6, pady=4, sticky='w')
            elif scelta == 'tradizionale':

                self.iupac_label.grid_remove()
                self.iupac_entry.grid_remove()
                self.trad_label.grid(row=0, column=0, sticky='e', padx=6, pady=4)
                self.trad_entry.grid(row=0, column=1, padx=6, pady=4, sticky='w')
        else:

            self.iupac_label.grid_remove()
            self.iupac_entry.grid_remove()
            self.trad_label.grid_remove()
            self.trad_entry.grid_remove()
            self.formula_label.grid(row=0, column=0, sticky='e', padx=6, pady=4)
            self.formula_entry.grid(row=0, column=1, padx=6, pady=4, sticky='w')
        self.input_container.update_idletasks()
        self.result_label.config(text='')

    def apply_theme(self):
        def _apply(w):
            for c in w.winfo_children():
                cls = c.__class__.__name__
                if cls in ('Frame', 'LabelFrame'):
                    try:
                        c.config(bg='#2b2b2b')
                    except Exception:
                        pass
                elif cls == 'Label':
                    c.config(bg='#2b2b2b', fg='white')
                elif cls == 'Entry':
                    try:

                        if hasattr(self, "formula_entry") and c == self.formula_entry:
                            if self.formula_entry.get() == getattr(self, "formula_placeholder", ""):
                                c.config(bg='#444', fg='#888', insertbackground='white')
                            else:
                                c.config(bg='#444', fg='white', insertbackground='white')
                        else:
                            c.config(bg='#444', fg='white', insertbackground='white')
                    except Exception:
                        pass
                elif cls == 'Text':
                    try:
                        c.config(bg='#333', fg='white')
                    except Exception:
                        pass
                _apply(c)
        _apply(self)

    def _show_rule(self, title):
        content = self.rule_contents.get(title, f"Contenuto di {title} non disponibile.")
        self.rule_text.config(state='normal')
        self.rule_text.delete('1.0', 'end')
        self.rule_text.insert('end', title + '\n', 'title')
        self.rule_text.insert('end', '\n' + content)
        self.rule_text.tag_config('title', font=('Arial', 18, 'bold'))
        self.rule_text.config(state='disabled')
        self.current_rule_title = title

    def _toggle_rule(self, title):
        if self.current_rule_title == title:
            self.rule_text.config(state='normal')
            self.rule_text.delete('1.0', 'end')
            self.rule_text.config(state='disabled')
            self.current_rule_title = None
        else:
            self._show_rule(title)

    def aggiorna_filtri(self):
        self.formule_filtrate.clear()
        self.mappa_categoria.clear()
        for nome_cat, var in self.gruppi_vars.items():
            if var.get():
                for formula, dati in categorie_formule[nome_cat].items():
                    self.formule_filtrate.append(formula)
                    self.mappa_categoria[formula] = nome_cat

    def nuova_formula(self):
        if not self.formule_filtrate:
            messagebox.showinfo('Info', 'Nessuna formula disponibile. Controlla i gruppi selezionati.')
            return
        self.formula_corrente = random.choice(self.formule_filtrate)
        self.categoria_corrente = self.mappa_categoria[self.formula_corrente]
        dati = categorie_formule[self.categoria_corrente][self.formula_corrente]

        if self.modalita_var.get() == 'formula2nome':
            self._set_display_text(dati.get('formula', ''))
            self.iupac_entry.delete(0, 'end')
            self.trad_entry.delete(0, 'end')
        else:
            choice = self.nomenclatura_var.get()
            if choice == 'iupac':
                nome = dati.get('iupac', '')
            elif choice == 'tradizionale':
                nome = dati.get('tradizionale', '')
            else:
                nome = f"{dati.get('iupac','')} / {dati.get('tradizionale','')}"
            self._set_display_text(nome)
            self.formula_entry.delete(0, 'end')

        self.result_label.config(text='')

    def _set_display_text(self, text):
        self.formula_canvas.delete('all')
        w = self.formula_canvas.winfo_width() or 800
        h = self.formula_canvas.winfo_height() or 120
        self.formula_canvas.create_text(w // 2, h // 2, text=text, font=('Arial', 34, 'bold'),
                                        fill='white', anchor='center')

    def verifica(self):
        if not self.formula_corrente:
            messagebox.showerror('Errore', 'Nessuna domanda in corso.')
            return
        dati = categorie_formule[self.categoria_corrente][self.formula_corrente]

        def normalize(s):

            return re.sub(r'\s+', ' ', s.strip().lower())

        if self.modalita_var.get() == 'formula2nome':
            check_iup = self.nomenclatura_var.get() in ('tutte', 'iupac')
            check_trad = self.nomenclatura_var.get() in ('tutte', 'tradizionale')
            iup_in = normalize(self.iupac_entry.get())
            trad_in = normalize(self.trad_entry.get())
            correct_iup = normalize(dati.get('iupac', ''))
            correct_trad = normalize(dati.get('tradizionale', ''))
            iup_ok = (iup_in == correct_iup) if check_iup else None
            trad_ok = (trad_in == correct_trad) if check_trad else None

            if (iup_ok or iup_ok is None) and (trad_ok or trad_ok is None):
                self.result_label.config(text='Giusto ✅', fg='lime')
            else:
                msgs = []
                if check_iup and not iup_ok:
                    msgs.append('Errato IUPAC — ' + dati.get('iupac',''))
                if check_trad and not trad_ok:
                    msgs.append('Errato Tradizionale — ' + dati.get('tradizionale',''))
                self.result_label.config(text='\n'.join(msgs), fg='red')
        else:
            correct = self.formula_corrente.strip()
            entered = self.formula_entry.get().strip()
            if entered == correct:
                self.result_label.config(text='Giusto ✅', fg='lime')
            else:
                self.result_label.config(text=f'Errato — formula corretta: {correct}', fg='red')

    # ------------------ Contenuti regole ------------------
    def _default_rule_contents(self):
        return {
    #------N.O.-------#
            "Regole N.O.": 
"""Le regole per l’assegnazione del N.O. sono:

▪ Sostanze elementari: N.O. = 0 (es: K, Cl2).
▪ Ossigeno: N.O.= ‒2, quando si trova in un perossido (−1),in un superossido (−1/2) o in OF₂ (+2).
▪ Idrogeno: N.O.= +1, quando è legato ad un metallo o al B (‒1).
▪ Ioni monoatomici: N.O.= carica dello ione (es: +2 per Ca2+).
▪ Elementi del gruppo 1: N.O.= +1.
▪ Elementi del gruppo 2: N.O.= +2.
▪ Elementi del gruppo 17: N.O.= ‒1, se legati ad O o alogeni superiori nel gruppo(+1, +3, +5, +7).
▪ Elementi con N.O. fisso: F (‒1), Ag (+1), Cd (+2), Zn (+2), Al (+3), B (+3), Si (+4).
▪ Molecole neutre: σ 𝑁. 𝑂.
▪ Ioni poliatomici: σ 𝑁. 𝑂.= 𝟎.= carica dello ione.""",

#--------------------------------#
            
            "Ossidi basici": """ Composti binari formati da metallo (M) + O.

• Nomenclatura IUPAC: prefisso-ossido + di + prefisso-M

  Prefissi: mon-, di-, tri-, tetra-, penta-, esa-, epta-
  Il prefisso mon- si mette solo davanti al termine «ossido», qualora M abbia più N.O. possibili.

• Nomenclatura tradizionale: Ossido + M-suffisso

  Suffissi: -oso per 1°N.O., -ico per 2°N.O.
  Se M ha un solo N.O. possibile, non si mette il suffisso, ma si antepone «di» al nome del M.""",

#--------------------------------#

            "Ossidi acidi": """Composti binari formati da non metallo (NM) + O.

• Nomenclatura IUPAC: prefisso-ossido + d i + prefisso-NM

  prefissi: mon-, di-, tri-, tetra-, penta-, esa-, epta-
  Il prefisso mon- si mette solo davanti al termine «ossido».

• Nomenclatura tradizionale: Anidride + (prefisso)-NM-suffisso

  Suffissi: ipo-...-osa per 1°/ N.O., -osa per 2°N.O., -ica per 3°N.O., per-...-ica per  4°N.O.
  Se ci sono solo due N.O. possibili, si considerano le due opzioni centrali (-osa e -ica).""",

#--------------------------------#

            "Idrossidi": """Composti ternari formati dalla reazione ossido basico + HO → M(OH)ₓ→ Gruppo ossidrile: (ОН)-

• Nomenclatura IUPAC: prefisso-idrossido di + M
  Prefissi: di-, tri-, ...

• Nomenclatura tradizionale: Idrossido + M-suffisso

  Suffissi: -oso per 1°N.O., -ico per 2°N.O.
  Se M ha un solo N.O. possibile, non si mette il suffisso, ma si antepone «di» al nome del M.""",

#--------------------------------#

            "Ossiacidi": """Composti ternari formati dalla reazione ossido acido + HO → HaNM,O.

• Nomenclatura IUPAC: Acido + prefisso-osso-prefisso-NM-ico + (N.O. di NM in n°romani)

  Prefissi: mon-, di-, tri-, tetra-, ..
  I l prefisso mon- si mette solo davanti al termine «osso».

• Nomenclatura tradizionale: Acido + (prefisso)-NM-suffisso

  Suffissi: ipo-...-oso per 1° N.O., -oso per 2°N.O., -ico per 3°N.O., per-..-ico per 4°N.O.
  Se ci sono solo due N.O. possibili, si considerano le opzioni centrali.  
  
  Fanno eccezione:
• Azoto: solo N(+3) e N(+5) danno ossiacidi.
• Carbonio: solo C(+4) dà ossiacidi.
• Fosforo, boro, arsenico e silicio: i loro ossidi acidi possono combinarsi con più di una molecola
  d'acqua al fine di formare un ossiacido, e ciò fa cambiare (solo) la nomenclatura tradizionale:

• Se N.O. è pari: sono state aggiunte 1 o 2 molecole di H₂O, e si utilizzano i prefissi meta- e orto-,
  rispettivamente.

• Se N.O. è dispari: sono state aggiunte 1, 2 o 3 molecole di H₂0, e si utilizzano i prefissi meta-,
  piro- e orto-, rispettivamente.""",

#--------------------------------#

            "Perossidi": """Composti binari dove O ha N.O. = - 1 quando è legato ad un altro elemento (E).

• Nomenclatura IUPAC: prefisso-ossido + di + prefisso-E
  Prefissi: di-, ...

• Nomenclatura tradizionale: Perossido di + E""",

#--------------------------------#

            "Idracidi": """Composti binari dove H e legato ad un altro elemento (E = alogeno, S, Se, CN)• Gruppo ciano: (CN)-;

• Nomenclatura IUPAC: E-uro + di idrogeno
  Si usa per la fase gassosa.

  Se c'è più di un atomo di H, la nomenclatura usa i prefissi di-, ... davanti a «idrogeno».

• Nomenclatura tradizionale: Acido + E-idrico
  Si usa per la fase liquida.""",

#--------------------------------#

            "Idruri": """Composti binari dove H è legato ad un altro elemento (E); si distingue tra:

• Idruri metallici (ionici, salini): M + H (N.O. = -1)
• Idruri covalenti: NM (o semimetallo) + H (N.O. = +1)

• Nomenclatura IUPAC: prefisso-idruro + di + E

  Prefissi: mono-, di-, tri-, tetra-, ...
  Il prefisso -mono si mette solo davanti a «idruro», qualora M abbia più N.O.

• Nomenclatura tradizionale: Idruro + E-suffisso

  Suffissi: -oso per 1°N.O., -ico per 2°N.O.
  Se M ha un solo N.O., non si mette il suffisso, ma si antepone «di» al nome del M.
  Se E non è un M, si utilizzano i nomi comuni.""",

#--------------------------------#

            "Sali binari": """Composti binari tra un M e un NM.

• Nomenclatura IUPAC: prefisso-NM-uro + di + prefisso-M

  Prefissi: mono-, di-, tri-, tetra-, penta-, esa-, epta-
  prefisso - mono s i mette solo davanti al NM, qualora il M abbia più N.O.

• Nomenclatura tradizionale: NM-uro + M-suffisso

  suffissi: -oso per 1°N.O., -ico per 2°N.O.""",

#--------------------------------#

            "Sali ternari": """Composti ternari ottenuti per parziale o totale sostituzione degli atomi di idrogeno di un ossiacido.

• Nomenclatura IUPAC: (prefisso)-prefisso-osso-NM-ato + (N.O.) + d i + M + (N.O.)

  Prefissi: mono-, di-, tri-, tetra-
  Se M (o NM) ha un solo N.O., non si esplicita il N.O.

• Nomenclatura tradizionale: (prefisso)-NM-suffisso + M-suffisso

  Suffissi per NM: ipo-..-ito per 1° N.O., -ito per 2°N.O., -ato per 3°N.O., per-...-ato per  4°N.O.
  Se ci sono solo due N.O. possibili, si considerano le opzioni centrali.

  Suffissi per M: -oso per 1°N.O., -ico per 2°N.O.
  Se M ha un solo N.O., non si mette il suffisso, ma si antepone «di» al nome del M """,

#--------------------------------#

            "Sali ternari acidi": """Si dicono sali acidi i sali ternari in cui la sostituzione degli atomi di idrogeno nell'ossiacido di partenza è stata parziale.

• Nomenclatura IUPAC: rispetto ai sali ternari standard, il «prefisso-osso» 
  viene sostituito da «n- idrogeno» (n va da mono- in su).

• Nomenclatura tradizionale: rispetto ai sali ternari standard, tra NM e M si aggiunge «n-acido» 
  (n può essere mono- o bi-).
  
  Invece, per i sali acidi derivati da H,CO3, H,SOz e H,SO4, la nomenclatura usa il prefisso 
  bi- davanti al NM (quindi non si usa il termine «n-acido»)."""
        }



    def _refresh_display(self):
        if not self.formula_corrente:
            return
        dati = categorie_formule[self.categoria_corrente][self.formula_corrente]
        if self.modalita_var.get() == "formula2nome":
            self._set_display_text(dati.get("formula", ""))
        else:
            choice = self.nomenclatura_var.get()
            if choice == "iupac":
                nome = dati.get("iupac", "")
            elif choice == "tradizionale":
                nome = dati.get("tradizionale", "")
            else:
                nome = f"{dati.get('iupac','')} / {dati.get('tradizionale','')}"
            self._set_display_text(nome)