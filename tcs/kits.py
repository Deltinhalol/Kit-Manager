import sqlite3
import tkinter as tk
from tkinter import messagebox

# ---------------------- CONFIG DO BANCO ----------------------

DB_PATH = 'Kits.db'

kits = sqlite3.connect(DB_PATH)
cursor = kits.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS kits (
        id INTEGER PRIMARY KEY,
        nome TEXT,
        camisa INTEGER,
        calca INTEGER,
        camisa_away INTEGER,
        calca_away INTEGER,
        camisa_gk INTEGER,
        calca_gk INTEGER
    )
''')

colunas_necessarias = {
    'nome': 'TEXT',
    'camisa': 'INTEGER',
    'calca': 'INTEGER',
    'camisa_away': 'INTEGER',
    'calca_away': 'INTEGER',
    'camisa_gk': 'INTEGER',
    'calca_gk': 'INTEGER',
}

cursor.execute("PRAGMA table_info(kits)")
colunas_existentes = [c[1] for c in cursor.fetchall()]

for coluna, tipo in colunas_necessarias.items():
    if coluna not in colunas_existentes:
        cursor.execute(f'ALTER TABLE kits ADD COLUMN {coluna} {tipo}')
        kits.commit()

# ---------------------- TEMA VISUAL ----------------------

BG = '#0d0d0d'
BG_CARD = '#161616'
FG = '#f2f2f2'
FG_MUTED = '#8a8a8a'
ACCENT = '#ffffff'
ACCENT_HOVER = '#d4d4d4'
ACCENT_TEXT = '#0d0d0d'
ACCENT_SOFT = '#262626'
DANGER = '#f85149'
DANGER_HOVER = '#da3933'
NEUTRAL_BTN = '#1f1f1f'
NEUTRAL_BTN_HOVER = '#2a2a2a'
FIELD_BG = '#1a1a1a'
FIELD_BORDER = '#2e2e2e'
BORDER_SUBTLE = '#242424'

FONT = ('Segoe UI', 10)
FONT_SMALL = ('Segoe UI', 9)
FONT_BOLD = ('Segoe UI', 11, 'bold')
FONT_SECTION = ('Segoe UI', 9, 'bold')
FONT_APPBAR = ('Segoe UI', 15, 'bold')
FONT_CARD_TITLE = ('Segoe UI', 13, 'bold')


def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=14, **kwargs):
    pontos = [
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
    ]
    return canvas.create_polygon(pontos, smooth=True, **kwargs)


class HoverButton(tk.Button):
    """Botão com efeito de hover suave."""

    def __init__(self, master, bg_normal, bg_hover, fg_normal='white', **kwargs):
        kwargs.setdefault('pady', 8)
        kwargs.setdefault('font', FONT_BOLD)
        super().__init__(
            master, bg=bg_normal, fg=fg_normal, activebackground=bg_hover,
            activeforeground=fg_normal, relief='flat', bd=0, cursor='hand2', **kwargs
        )
        self._bg_normal = bg_normal
        self._bg_hover = bg_hover
        self.bind('<Enter>', lambda e: self.config(bg=self._bg_hover))
        self.bind('<Leave>', lambda e: self.config(bg=self._bg_normal))


class RoundedEntry(tk.Frame):
    """Campo de texto com borda que reage ao foco."""

    def __init__(self, master, **kwargs):
        super().__init__(master, bg=FIELD_BORDER, padx=1, pady=1)
        self.entry = tk.Entry(
            self, bg=FIELD_BG, fg=FG, insertbackground=FG, relief='flat',
            font=FONT, highlightthickness=0, **kwargs
        )
        self.entry.pack(fill='both', expand=True, ipady=7, padx=10)
        self.entry.bind('<FocusIn>', lambda e: self.config(bg=ACCENT))
        self.entry.bind('<FocusOut>', lambda e: self.config(bg=FIELD_BORDER))

    def get(self):
        return self.entry.get()

    def delete(self, first, last=None):
        self.entry.delete(first, last)

    def insert(self, index, string):
        self.entry.insert(index, string)

    def set_disabled(self, disabled=True):
        self.entry.config(state='disabled' if disabled else 'normal')


class FAB(tk.Canvas):
    """Botão flutuante circular (Floating Action Button)."""

    def __init__(self, parent, command, size=56, symbol='+'):
        super().__init__(parent, width=size, height=size, bg=BG, highlightthickness=0, cursor='hand2')
        self.command = command
        self.circle = self.create_oval(2, 2, size - 2, size - 2, fill=ACCENT, outline='')
        self.create_text(size / 2, size / 2, text=symbol, fill=ACCENT_TEXT, font=('Segoe UI', 22, 'bold'))
        self.bind('<Button-1>', lambda e: self.command())
        self.bind('<Enter>', lambda e: self.itemconfig(self.circle, fill=ACCENT_HOVER))
        self.bind('<Leave>', lambda e: self.itemconfig(self.circle, fill=ACCENT))


class ScrollFrame(tk.Frame):
    """Área rolável (usada nas listas e no formulário)."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.canvas.pack(side='left', fill='both', expand=True)

        self.inner = tk.Frame(self.canvas, bg=BG)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor='nw')

        self.inner.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.inner_id, width=e.width))

        self.canvas.bind('<Enter>', self._ativar_scroll)
        self.canvas.bind('<Leave>', self._desativar_scroll)

    def _on_mousewheel(self, event):
        delta = event.delta if event.delta else (120 if event.num == 4 else -120)
        self.canvas.yview_scroll(int(-1 * (delta / 120)), 'units')

    def _ativar_scroll(self, event=None):
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind_all('<Button-4>', self._on_mousewheel)
        self.canvas.bind_all('<Button-5>', self._on_mousewheel)

    def _desativar_scroll(self, event=None):
        self.canvas.unbind_all('<MouseWheel>')
        self.canvas.unbind_all('<Button-4>')
        self.canvas.unbind_all('<Button-5>')


# ---------------------- APP ----------------------

class KitsApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Gerenciador de Kits')
        self.root.geometry('400x600')
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.active_screen = None
        self.form_fields = {}
        self._last_termo = ''

        self._build_appbar()
        self._build_navbar()

        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(fill='both', expand=True)

        self.show_menu()

    # ---------- Estrutura fixa (appbar / navbar) ----------

    def _build_appbar(self):
        self.appbar = tk.Frame(self.root, bg=BG, height=54)
        self.appbar.pack(side='top', fill='x')
        self.appbar.pack_propagate(False)

    def _set_appbar(self, titulo, back=False):
        for w in self.appbar.winfo_children():
            w.destroy()
        if back:
            voltar = tk.Label(self.appbar, text='‹', bg=BG, fg=ACCENT, font=('Segoe UI', 22, 'bold'), cursor='hand2')
            voltar.pack(side='left', padx=(8, 0))
            voltar.bind('<Button-1>', lambda e: self.show_menu())
        tk.Label(self.appbar, text=titulo, bg=BG, fg=FG, font=FONT_APPBAR).pack(side='left', padx=14, pady=12)

    def _build_navbar(self):
        self.navbar = tk.Frame(self.root, bg=BG_CARD, height=64, highlightthickness=1, highlightbackground=BORDER_SUBTLE)
        self.navbar.pack(side='bottom', fill='x')
        self.navbar.pack_propagate(False)

        self.nav_widgets = {}
        abas = [('menu', '🏠', 'Menu'), ('consulta', '🔍', 'Consulta')]

        for chave, icone, rotulo in abas:
            aba = tk.Frame(self.navbar, bg=BG_CARD, cursor='hand2')
            aba.pack(side='left', fill='both', expand=True)

            lbl_icone = tk.Label(aba, text=icone, bg=BG_CARD, font=('Segoe UI', 15))
            lbl_icone.pack(pady=(10, 0))
            lbl_texto = tk.Label(aba, text=rotulo, bg=BG_CARD, font=FONT_SMALL)
            lbl_texto.pack()

            comando = self.show_menu if chave == 'menu' else self.show_consulta
            for widget in (aba, lbl_icone, lbl_texto):
                widget.bind('<Button-1>', lambda e, c=comando: c())

            self.nav_widgets[chave] = (lbl_icone, lbl_texto)

    def _update_navbar(self):
        for chave, (lbl_icone, lbl_texto) in self.nav_widgets.items():
            ativo = chave == self.active_screen
            cor = ACCENT if ativo else FG_MUTED
            lbl_icone.config(fg=cor)
            lbl_texto.config(fg=cor, font=(FONT_SMALL[0], FONT_SMALL[1], 'bold' if ativo else 'normal'))

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ---------- Cartão de time (usado no Menu e na Consulta) ----------

    def _create_team_card(self, parent, team_id, nome, on_tap, on_delete=None, mostrar_id=True):
        card_h = 42
        c = tk.Canvas(parent, height=card_h, bg=BG, highlightthickness=0, cursor='hand2')
        c.pack(fill='x', pady=2, padx=14)

        def desenhar(event=None):
            largura = c.winfo_width()
            if largura < 10:
                largura = 320
            c.delete('all')
            draw_rounded_rect(c, 1, 1, largura - 1, card_h - 1, radius=10, fill=BG_CARD, outline=BORDER_SUBTLE)

            if mostrar_id:
                selo_w = 34
                draw_rounded_rect(c, 10, card_h / 2 - 10, 10 + selo_w, card_h / 2 + 10, radius=10,
                                   fill=ACCENT_SOFT, outline='')
                c.create_text(10 + selo_w / 2, card_h / 2, text=str(team_id), fill=ACCENT, font=('Segoe UI', 8, 'bold'))
                nome_x = 10 + selo_w + 10
            else:
                nome_x = 16

            c.create_text(nome_x, card_h / 2, text=nome, anchor='w', fill=FG, font=('Segoe UI', 10, 'bold'))

            if on_delete is not None:
                c.create_text(largura - 38, card_h / 2, text='🗑', fill=FG_MUTED, font=('Segoe UI', 10))
            c.create_text(largura - 16, card_h / 2, text='›', fill=FG_MUTED, font=('Segoe UI', 12, 'bold'))

        def clicar(event):
            largura = c.winfo_width()
            if on_delete is not None and event.x > largura - 50:
                on_delete()
            else:
                on_tap()

        c.bind('<Configure>', desenhar)
        c.bind('<Button-1>', clicar)

    # ---------- Tela: Menu ----------

    def show_menu(self):
        self.active_screen = 'menu'
        self._clear_content()
        self._set_appbar('Meus Times')
        self._update_navbar()

        cursor.execute('SELECT id, nome FROM kits ORDER BY nome')
        times = cursor.fetchall()

        if not times:
            tk.Label(self.content, text='Nenhum time cadastrado ainda.\nToque em + para adicionar.',
                     bg=BG, fg=FG_MUTED, font=FONT, justify='center').pack(expand=True, pady=80)
        else:
            lista = ScrollFrame(self.content)
            lista.pack(fill='both', expand=True)
            tk.Frame(lista.inner, bg=BG, height=4).pack()
            for tid, nome in times:
                self._create_team_card(
                    lista.inner, tid, nome,
                    on_tap=lambda i=tid: self.show_form(edit_id=i),
                    on_delete=lambda i=tid, n=nome: self._deletar_time(i, n),
                    mostrar_id=False,
                )
            tk.Frame(lista.inner, bg=BG, height=64).pack()

        fab = FAB(self.content, command=lambda: self.show_form())
        fab.place(relx=1.0, rely=1.0, x=-22, y=-22, anchor='se')

    # ---------- Tela: Consulta ----------

    def show_consulta(self):
        self.active_screen = 'consulta'
        self._clear_content()
        self._set_appbar('Consultar Kit')
        self._update_navbar()

        wrapper = tk.Frame(self.content, bg=BG)
        wrapper.pack(fill='both', expand=True, padx=16, pady=(14, 0))

        busca_card = tk.Frame(wrapper, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER_SUBTLE)
        busca_card.pack(fill='x')

        tk.Label(busca_card, text='🔍', bg=BG_CARD, fg=FG_MUTED, font=('Segoe UI', 11)).pack(side='left', padx=(12, 4))
        campo_busca = tk.Entry(busca_card, bg=BG_CARD, fg=FG, insertbackground=FG, relief='flat',
                                font=FONT, highlightthickness=0)
        campo_busca.pack(side='left', fill='x', expand=True, ipady=8, pady=4, padx=(0, 10))
        campo_busca.focus_set()

        self.consulta_area = ScrollFrame(wrapper)
        self.consulta_area.pack(fill='both', expand=True, pady=(14, 0))

        def ao_digitar(event=None):
            self._render_consulta_resultados(campo_busca.get().strip())

        campo_busca.bind('<KeyRelease>', ao_digitar)
        self._render_consulta_resultados('')

    def _render_consulta_resultados(self, termo):
        self._last_termo = termo
        for w in self.consulta_area.inner.winfo_children():
            w.destroy()

        if not termo:
            tk.Label(self.consulta_area.inner, text='Digite o nome ou o ID do time para consultar.',
                     bg=BG, fg=FG_MUTED, font=FONT, wraplength=300, justify='center').pack(pady=50)
            return

        cursor.execute('SELECT * FROM kits WHERE id = ? OR nome LIKE ?', (termo, f'%{termo}%'))
        resultados = cursor.fetchall()

        if not resultados:
            tk.Label(self.consulta_area.inner, text='Nenhum time encontrado.',
                     bg=BG, fg=FG_MUTED, font=FONT).pack(pady=50)
            return

        if len(resultados) == 1:
            self._build_detail_card(self.consulta_area.inner, resultados[0])
            return

        for row in resultados:
            self._create_team_card(
                self.consulta_area.inner, row[0], row[1],
                on_tap=lambda r=row: self._mostrar_detalhe_unico(r),
            )

    def _mostrar_detalhe_unico(self, row):
        for w in self.consulta_area.inner.winfo_children():
            w.destroy()

        voltar = tk.Label(self.consulta_area.inner, text='‹  Voltar aos resultados',
                           bg=BG, fg=ACCENT, font=FONT_SMALL, cursor='hand2')
        voltar.pack(anchor='w', pady=(0, 10), padx=4)
        voltar.bind('<Button-1>', lambda e: self._render_consulta_resultados(self._last_termo))

        self._build_detail_card(self.consulta_area.inner, row)

    def _build_detail_card(self, parent, row):
        tid, nome, camisa, calca, camisa_away, calca_away, camisa_gk, calca_gk = row

        card = tk.Frame(parent, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER_SUBTLE)
        card.pack(fill='x', pady=4)

        header = tk.Frame(card, bg=BG_CARD)
        header.pack(fill='x', padx=18, pady=(16, 8))
        tk.Label(header, text=nome, bg=BG_CARD, fg=FG, font=FONT_CARD_TITLE).pack(side='left')
        tk.Label(header, text=f'#{tid}', bg=ACCENT_SOFT, fg=ACCENT, font=FONT_SECTION,
                 padx=8, pady=2).pack(side='right')

        tk.Frame(card, bg=BORDER_SUBTLE, height=1).pack(fill='x', padx=18)

        secoes = [('HOME', camisa, calca), ('AWAY', camisa_away, calca_away), ('GOLEIRO', camisa_gk, calca_gk)]
        for label, cam, cal in secoes:
            sec = tk.Frame(card, bg=BG_CARD)
            sec.pack(fill='x', padx=18, pady=10)

            titulo_sec = tk.Frame(sec, bg=BG_CARD)
            titulo_sec.pack(fill='x')
            tk.Label(titulo_sec, text=label, bg=BG_CARD, fg=ACCENT, font=FONT_SECTION).pack(side='left')
            tk.Label(titulo_sec, text='📋 toque p/ copiar', bg=BG_CARD, fg=FG_MUTED,
                     font=('Segoe UI', 8)).pack(side='right')

            linha = tk.Frame(sec, bg=BG_CARD, cursor='hand2')
            linha.pack(fill='x', pady=(6, 0))
            self._kit_stat(linha, 'Camisa', cam).pack(side='left', fill='x', expand=True)
            self._kit_stat(linha, 'Calça', cal).pack(side='left', fill='x', expand=True)

            self._bind_recursivo(linha, lambda e, c=cam, k=cal: self._copiar_kit(c, k))

        tk.Frame(card, bg=BG_CARD, height=4).pack()

    def _kit_stat(self, parent, label, valor):
        box = tk.Frame(parent, bg=FIELD_BG, cursor='hand2')
        tk.Label(box, text=label, bg=FIELD_BG, fg=FG_MUTED, font=FONT_SMALL).pack(anchor='w', padx=10, pady=(6, 0))
        tk.Label(box, text=str(valor) if valor is not None else '—', bg=FIELD_BG, fg=FG,
                 font=FONT_BOLD).pack(anchor='w', padx=10, pady=(0, 6))
        box.pack_propagate(True)
        return box

    def _bind_recursivo(self, widget, comando):
        """Aplica o mesmo clique em um widget e em todos os seus filhos."""
        widget.bind('<Button-1>', comando)
        for filho in widget.winfo_children():
            self._bind_recursivo(filho, comando)

    def _copiar_kit(self, camisa, calca, event=None):
        def formatar(v):
            texto = str(v) if v is not None else '0'
            return texto.zfill(8)

        conteudo = f'{formatar(camisa)} {formatar(calca)}'
        self.root.clipboard_clear()
        self.root.clipboard_append(conteudo)
        self._mostrar_toast('Copiado!  ' + conteudo)

    def _mostrar_toast(self, mensagem):
        toast = tk.Label(self.root, text=mensagem, bg=ACCENT, fg=ACCENT_TEXT,
                          font=FONT_BOLD, padx=14, pady=6)
        toast.place(relx=0.5, rely=1.0, y=-74, anchor='s')
        self.root.after(1400, toast.destroy)

    # ---------- Tela: Formulário (cadastrar / editar) ----------

    def _section_badge(self, parent, texto):
        badge = tk.Frame(parent, bg=ACCENT_SOFT)
        tk.Label(badge, text=texto, bg=ACCENT_SOFT, fg=ACCENT, font=('Segoe UI', 8, 'bold'),
                 padx=8, pady=3).pack()
        return badge

    def show_form(self, edit_id=None):
        self.active_screen = None
        self._clear_content()
        self._set_appbar('Editar Kit' if edit_id else 'Novo Kit', back=True)
        self._update_navbar()

        self.form_fields = {}
        scroll = ScrollFrame(self.content)
        scroll.pack(fill='both', expand=True)

        inner = tk.Frame(scroll.inner, bg=BG)
        inner.pack(fill='both', expand=True, padx=18, pady=16)

        campos_layout = [
            ('id', 'ID do time'),
            ('nome', 'Nome do time'),
            (None, 'HOME'),
            ('camisa', 'Camisa'),
            ('calca', 'Calça'),
            (None, 'AWAY'),
            ('camisa_away', 'Camisa'),
            ('calca_away', 'Calça'),
            (None, 'GOLEIRO'),
            ('camisa_gk', 'Camisa'),
            ('calca_gk', 'Calça'),
        ]

        for chave, label in campos_layout:
            if chave is None:
                self._section_badge(inner, label).pack(anchor='w', pady=(14, 6))
                continue
            tk.Label(inner, text=label, bg=BG, fg=FG_MUTED, font=FONT_SMALL).pack(anchor='w', pady=(6, 3))
            entry = RoundedEntry(inner)
            entry.pack(fill='x')
            self.form_fields[chave] = entry

        row_atual = None
        if edit_id is not None:
            cursor.execute('SELECT * FROM kits WHERE id = ?', (edit_id,))
            row_atual = cursor.fetchone()
            if row_atual:
                chaves = ['id', 'nome', 'camisa', 'calca', 'camisa_away', 'calca_away', 'camisa_gk', 'calca_gk']
                for chave, valor in zip(chaves, row_atual):
                    if valor is not None:
                        self.form_fields[chave].insert(0, valor)
                self.form_fields['id'].set_disabled(True)

        botoes = tk.Frame(inner, bg=BG)
        botoes.pack(fill='x', pady=(22, 10))

        HoverButton(botoes, ACCENT, ACCENT_HOVER, text='✓  Salvar kit', fg_normal=ACCENT_TEXT,
                    command=self._salvar_form).pack(fill='x', pady=4)

        if edit_id is not None and row_atual:
            HoverButton(botoes, DANGER, DANGER_HOVER, text='✕  Excluir time',
                        command=lambda: self._deletar_time(edit_id, row_atual[1])).pack(fill='x', pady=4)

    def _salvar_form(self):
        valores = {chave: entry.get().strip() for chave, entry in self.form_fields.items()}

        if not valores['id'] or not valores['nome']:
            messagebox.showwarning('Campos obrigatórios', 'Preencha ao menos o ID e o Nome do time.')
            return

        try:
            id_time = int(valores['id'])
        except ValueError:
            messagebox.showerror('Erro', 'O ID precisa ser um número.')
            return

        cursor.execute('SELECT id FROM kits WHERE id = ?', (id_time,))
        existe = cursor.fetchone()

        campos_numericos = ['camisa', 'calca', 'camisa_away', 'calca_away', 'camisa_gk', 'calca_gk']
        dados = {'id': id_time, 'nome': valores['nome']}
        for campo in campos_numericos:
            v = valores[campo]
            dados[campo] = int(v) if v else None

        if existe:
            cursor.execute('''
                UPDATE kits SET nome=?, camisa=?, calca=?, camisa_away=?, calca_away=?, camisa_gk=?, calca_gk=?
                WHERE id=?
            ''', (dados['nome'], dados['camisa'], dados['calca'], dados['camisa_away'],
                  dados['calca_away'], dados['camisa_gk'], dados['calca_gk'], dados['id']))
            kits.commit()
            messagebox.showinfo('Atualizado', f'Kit do time {dados["nome"]} atualizado com sucesso.')
        else:
            cursor.execute('''
                INSERT INTO kits (id, nome, camisa, calca, camisa_away, calca_away, camisa_gk, calca_gk)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dados['id'], dados['nome'], dados['camisa'], dados['calca'], dados['camisa_away'],
                  dados['calca_away'], dados['camisa_gk'], dados['calca_gk']))
            kits.commit()
            messagebox.showinfo('Cadastrado', f'Kit do time {dados["nome"]} cadastrado com sucesso.')

        self.show_menu()

    def _deletar_time(self, id_time, nome):
        confirmar = messagebox.askyesno('Confirmar exclusão', f'Deletar o kit do time "{nome}"?')
        if not confirmar:
            return
        cursor.execute('DELETE FROM kits WHERE id = ?', (id_time,))
        kits.commit()
        self.show_menu()


# ---------------------- MAIN ----------------------

if __name__ == '__main__':
    root = tk.Tk()
    app = KitsApp(root)
    root.protocol('WM_DELETE_WINDOW', lambda: (kits.close(), root.destroy()))
    root.mainloop()
    