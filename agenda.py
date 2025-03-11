import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import calendar
import json
import os

class AgendaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agenda Mensal - 2025")
        self.root.geometry("1200x700")  # Ajustando o tamanho inicial
        self.root.configure(bg="#f0f0f0")  

        self.months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                       "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.entries = {}  # Dicionário para armazenar os campos de texto (entrada por dia)
        self.undo_stack = {}  # Pilha para desfazer as alterações

        # Definição dos feriados nacionais de 2025 no Brasil
        self.feriados = {
            (1, 1): "Ano Novo", (2, 16): "Carnaval", (2, 17): "Carnaval", (4, 2): "Sexta-feira Santa", 
            (4, 21): "Tiradentes", (5, 1): "Dia do Trabalho", (6, 15): "Corpus Christi", 
            (9, 7): "Independência", (10, 12): "Nossa Senhora Aparecida", (11, 2): "Finados", 
            (11, 15): "Proclamação da República", (12, 25): "Natal"
        }

        # Inicializa variáveis de configurações
        self.current_font = ("Arial", 10)
        self.current_color = "#000000"  # Cor padrão para texto
        self.holiday_color = "#FFEB99"  # Cor de fundo para feriados

        # Lê o índice do mês ativo salvo, ou usa Janeiro (0) como padrão
        self.active_month_index = self.load_active_month()

        # Carregar dados salvos do mês
        self.saved_data = self.load_saved_data()

        # Carregar configurações salvas
        self.load_settings()

        # Configuração da interface
        self.create_ui()

    def get_file_path(self, filename):
        # Retorna o caminho absoluto do arquivo
        base_path = os.path.expanduser("~") 
        app_dir = os.path.join(base_path, "AgendaApp")
        if not os.path.exists(app_dir):
            os.makedirs(app_dir) 
        return os.path.join(app_dir, filename)

    def save_data(self, event=None):
        # Função que salva os dados digitados
        saved_data = {key: entry.get("1.0", tk.END).strip() for key, entry in self.entries.items() if entry.get("1.0", tk.END).strip()}
        with open(self.get_file_path("data.json"), "w") as f:
            json.dump(saved_data, f, indent=4)

        # Salvar o mês ativo
        with open(self.get_file_path("active_month.json"), "w") as f:
            json.dump({"active_month": self.active_month_index}, f)

        # Salvar as configurações
        settings = {
            "font": self.current_font,
            "text_color": self.current_color,
            "holiday_color": self.holiday_color
        }
        with open(self.get_file_path("settings.json"), "w") as f:
            json.dump(settings, f, indent=4)

        print("Dados e configurações salvos com sucesso!")

    def load_saved_data(self):
        # Carrega os dados salvos
        try:
            with open(self.get_file_path("data.json"), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def load_settings(self):
        # Carrega as configurações salvas
        try:
            with open(self.get_file_path("settings.json"), "r") as f:
                settings = json.load(f)
                self.current_font = tuple(settings.get("font", ("Arial", 10)))
                self.current_color = settings.get("text_color", "#000000")
                self.holiday_color = settings.get("holiday_color", "#FFEB99")
        except FileNotFoundError:
            pass  # Se o arquivo não for encontrado, utiliza as configurações padrão

    def load_active_month(self):
        # Carrega o mês ativo salvo
        try:
            with open(self.get_file_path("active_month.json"), "r") as f:
                data = json.load(f)
                return data.get("active_month", 0)
        except FileNotFoundError:
            return 0

    def on_close(self):
        self.save_data()
        self.root.quit()

    def auto_save(self, day, month):
        day_data = self.entries[f"{month+1}_{day}"].get("1.0", tk.END).strip()
        if day_data:
            self.saved_data[f"{month+1}_{day}"] = day_data
            self.save_data()  # Salva os dados a cada alteração

            # Armazena o valor anterior na pilha de desfazer
            self.push_to_undo_stack(day, month, day_data)

    def push_to_undo_stack(self, day, month, current_text):
        # Empilha o valor anterior antes de mudar
        if self.active_month_index not in self.undo_stack:
            self.undo_stack[self.active_month_index] = {}

        if f"{month+1}_{day}" not in self.undo_stack[self.active_month_index]:
            self.undo_stack[self.active_month_index][f"{month+1}_{day}"] = []

        # Adiciona o valor atual ao topo da pilha
        self.undo_stack[self.active_month_index][f"{month+1}_{day}"].append(current_text)

    def undo_last_change(self, event=None):
        # Função que desfaz a última alteração feita
        last_change = self.undo_stack.get(self.active_month_index, {}).get(f"{self.active_month_index}_{event}", None)

        if last_change:
            # Remove o valor mais recente da pilha
            last_text = self.undo_stack[self.active_month_index].pop()

            # Restaura o texto anterior
            if last_text:
                self.entries[self.active_month_index].delete(1.0, END)
                self.entries[self.active_month_index].insert(1.0, last_text)
            print("Alteração desfeita.")
        else:
            print("Nada para desfazer!")

    def create_ui(self):
        # Configuração do atalho para desfazer
        self.root.bind("<Control-z>", self.undo_last_change)

        # Criação do calendário para os 12 meses
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        for month_index, month in enumerate(self.months):
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=month)

            # Canvas
            canvas = tk.Canvas(frame)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Barra de rolagem lateral
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            canvas.config(yscrollcommand=scrollbar.set)
            calendar_frame = ttk.Frame(canvas)
            canvas.create_window((0, 0), window=calendar_frame, anchor="nw")
            self.create_calendar(calendar_frame, month_index)
            calendar_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
        notebook.select(self.active_month_index)
        notebook.bind("<<NotebookTabChanged>>", lambda event, notebook=notebook: self.update_active_month(notebook))

        self.root.bind("<Control-s>", self.save_data)

    def update_active_month(self, notebook):
        self.active_month_index = notebook.index(notebook.select())
        print(f"Mês ativo atualizado para: {self.months[self.active_month_index]}")

    def create_calendar(self, parent_frame, month_index):
        year = 2025
        days_in_month = calendar.monthrange(year, month_index + 1)[1]
        start_day = calendar.monthrange(year, month_index + 1)[0]
        days_frame = ttk.Frame(parent_frame)
        days_frame.pack(pady=10)

        weekdays = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        for i, day in enumerate(weekdays):
            label = tk.Label(days_frame, text=day, width=12, anchor='center', font=("Helvetica", 12, "bold"),
                             background="#4CAF50", foreground="white", relief="solid", bd=1)
            label.grid(row=0, column=i, padx=5, pady=5)
        row = 1
        col = start_day 
        for day in range(1, days_in_month + 1):
            is_holiday = (month_index + 1, day) in self.feriados
            holiday_name = self.feriados.get((month_index + 1, day), None)

            day_label = tk.Label(days_frame, text=f"{day}", width=10, height=2, font=("Helvetica", 12, "bold"),
                                 fg="#4CAF50", anchor='w', bg="#f0f0f0", relief="flat")
            day_label.grid(row=row, column=col, padx=(5, 0), pady=5) 

            day_text = tk.Text(days_frame, width=20, height=5, wrap=tk.WORD, bd=1, font=self.current_font, 
                               padx=5, pady=5, relief="groove", bg="#ffffff")
            day_text.config(state="normal")

            if is_holiday:
                day_text.config(bg=self.holiday_color)
                day_text.insert(tk.END, f"{holiday_name}\n")
                day_text.config(state="disabled")

            saved_day_data = self.saved_data.get(f"{month_index+1}_{day}", "")
            if saved_day_data and not is_holiday:
                day_text.insert(tk.END, saved_day_data)

            if not is_holiday:
                day_text.bind("<KeyRelease>", lambda e, day=day, month=month_index: self.auto_save(day, month))

            day_text.grid(row=row+1, column=col, padx=5, pady=5)  
            self.entries[f"{month_index+1}_{day}"] = day_text

            # Empilhando o valor de alteração
            self.push_to_undo_stack(day, month_index, saved_day_data)

            col += 1
            if col == 7:
                col = 0
                row += 2

if __name__ == "__main__":
    root = tk.Tk()
    app = AgendaApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
