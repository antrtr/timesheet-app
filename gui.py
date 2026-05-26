import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import datetime
import database

class TimesheetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учёт рабочего времени")
        self.root.geometry("800x550")
        
        self.style = ttk.Style()
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')
            
        self.configure_styles()

        self.is_running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.dt_start = None

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.employee_tab = ttk.Frame(self.notebook)
        self.manager_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.employee_tab, text="Рабочий стол сотрудника")
        self.notebook.add(self.manager_tab, text="Панель руководителя")

        self.create_employee_widgets()
        self.create_manager_widgets()

    def configure_styles(self):
        default_font = ('Helvetica', 10)
        self.style.configure(".", font=default_font)
        self.style.configure("TButton", padding=6, font=('Helvetica', 10, 'bold'))
        self.style.configure("Start.TButton", foreground="green")
        self.style.configure("Stop.TButton", foreground="red")
        self.style.configure("TLabelFrame", font=('Helvetica', 10, 'bold'))
        self.style.configure("Timer.TLabel", font=('Helvetica', 42, 'bold'), foreground='#333333')
        self.style.configure("Treeview", rowheight=30, font=default_font)
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'), background="#e0e0e0")

    # --- ИНТЕРФЕЙС СОТРУДНИКА ---
    def create_employee_widgets(self):
        settings_frame = ttk.LabelFrame(self.employee_tab, text=" Настройки задачи ", padding=(20, 10))
        settings_frame.pack(fill=tk.X, padx=20, pady=20)

        ttk.Label(settings_frame, text="Сотрудник:").grid(row=0, column=0, pady=10, padx=10, sticky="e")
        self.user_var = tk.StringVar()
        self.user_cb = ttk.Combobox(settings_frame, textvariable=self.user_var, state="readonly", width=40)
        self.user_cb.grid(row=0, column=1, pady=10, sticky="w")

        ttk.Label(settings_frame, text="Проект:").grid(row=1, column=0, pady=10, padx=10, sticky="e")
        self.project_var = tk.StringVar()
        self.project_cb = ttk.Combobox(settings_frame, textvariable=self.project_var, state="readonly", width=40)
        self.project_cb.grid(row=1, column=1, pady=10, sticky="w")

        ttk.Label(settings_frame, text="Описание:").grid(row=2, column=0, pady=10, padx=10, sticky="e")
        self.desc_entry = ttk.Entry(settings_frame, width=42)
        self.desc_entry.grid(row=2, column=1, pady=10, sticky="w")

        self.update_comboboxes() # Инициализация данных

        timer_frame = ttk.Frame(self.employee_tab)
        timer_frame.pack(pady=20)

        self.time_label = ttk.Label(timer_frame, text="00:00:00", style="Timer.TLabel")
        self.time_label.pack(pady=10)

        btn_frame = ttk.Frame(timer_frame)
        btn_frame.pack()
        self.btn_start = ttk.Button(btn_frame, text="▶ Старт", style="Start.TButton", command=self.start_timer, width=15)
        self.btn_start.pack(side=tk.LEFT, padx=10)
        self.btn_stop = ttk.Button(btn_frame, text="■ Стоп", style="Stop.TButton", command=self.stop_timer, state=tk.DISABLED, width=15)
        self.btn_stop.pack(side=tk.LEFT, padx=10)

    def update_comboboxes(self):
        """Обновляет списки пользователей и проектов из БД"""
        self.users_data = {name: uid for uid, name in database.get_users()}
        self.user_cb['values'] = list(self.users_data.keys())
        if self.user_cb['values'] and self.user_var.get() not in self.user_cb['values']:
            self.user_cb.current(0)
            
        self.projects_data = {name: pid for pid, name in database.get_projects()}
        self.project_cb['values'] = list(self.projects_data.keys())
        if self.project_cb['values'] and self.project_var.get() not in self.project_cb['values']:
            self.project_cb.current(0)

    def start_timer(self):
        if not self.desc_entry.get().strip() or not self.user_var.get() or not self.project_var.get():
            messagebox.showwarning("Внимание", "Заполните все поля!")
            return
            
        self.is_running = True
        self.start_time = time.time()
        self.dt_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.user_cb.config(state=tk.DISABLED)
        self.project_cb.config(state=tk.DISABLED)
        self.desc_entry.config(state=tk.DISABLED)
        self.update_timer()

    def stop_timer(self):
        self.is_running = False
        dt_end = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_id = self.users_data[self.user_var.get()]
        project_id = self.projects_data[self.project_var.get()]
        
        database.save_time_entry(user_id, project_id, self.dt_start, dt_end, int(self.elapsed_time), self.desc_entry.get().strip())
        messagebox.showinfo("Успех", f"Учтено: {time.strftime('%H:%M:%S', time.gmtime(self.elapsed_time))}\nОтправлено на проверку.")

        self.elapsed_time = 0
        self.time_label.config(text="00:00:00")
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.user_cb.config(state="readonly")
        self.project_cb.config(state="readonly")
        self.desc_entry.config(state=tk.NORMAL)
        self.desc_entry.delete(0, tk.END)
        self.refresh_manager_table()

    def update_timer(self):
        if self.is_running:
            self.elapsed_time = time.time() - self.start_time
            self.time_label.config(text=time.strftime('%H:%M:%S', time.gmtime(self.elapsed_time)))
            self.root.after(1000, self.update_timer)

    # --- ИНТЕРФЕЙС РУКОВОДИТЕЛЯ ---
    def create_manager_widgets(self):
        toolbar = ttk.Frame(self.manager_tab, padding=10)
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="✓ Утвердить", command=lambda: self.change_status("Утверждено")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✗ Отклонить", command=lambda: self.change_status("Отклонено")).pack(side=tk.LEFT, padx=2)
        
        # Кнопки управления справочниками
        ttk.Button(toolbar, text="👥 Сотрудники", command=self.manage_users_dialog).pack(side=tk.RIGHT, padx=2)
        ttk.Button(toolbar, text="📁 Проекты", command=self.manage_projects_dialog).pack(side=tk.RIGHT, padx=2)
        ttk.Button(toolbar, text="📊 Зарплатный отчет", command=self.show_report).pack(side=tk.RIGHT, padx=10)

        table_frame = ttk.Frame(self.manager_tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("id", "user", "project", "date", "duration", "desc")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=40, anchor="center")
        self.tree.heading("user", text="Сотрудник")
        self.tree.column("user", width=120)
        self.tree.heading("project", text="Проект")
        self.tree.column("project", width=140)
        self.tree.heading("date", text="Начало")
        self.tree.column("date", width=140, anchor="center")
        self.tree.heading("duration", text="Время")
        self.tree.column("duration", width=80, anchor="center")
        self.tree.heading("desc", text="Описание задачи")
        self.tree.column("desc", width=180)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        self.refresh_manager_table()

    def refresh_manager_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        records = database.get_pending_entries()
        for r in records:
            dur_str = time.strftime('%H:%M:%S', time.gmtime(r[4]))
            self.tree.insert("", tk.END, values=(r[0], r[1], r[2], r[3], dur_str, r[5]))

    def change_status(self, status):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись!")
            return
        entry_id = self.tree.item(selected)['values'][0]
        database.update_entry_status(entry_id, status)
        self.refresh_manager_table()

    def show_report(self):
        data = database.get_approved_report()
        if not data:
            messagebox.showinfo("Зарплатный отчет", "Нет утвержденных записей.")
            return
        report_text = "СВОДНЫЙ ОТЧЕТ:\n" + "—"*30 + "\n\n"
        for row in data:
            report_text += f"👤 {row[0]}\n📁 {row[1]}\n⏱ Отработано: {round(row[2] / 3600, 2)} ч.\n\n"
        messagebox.showinfo("Отчет", report_text)

    # --- ОКНА УПРАВЛЕНИЯ СПРАВОЧНИКАМИ ---
    def manage_users_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Управление сотрудниками")
        win.geometry("350x400")
        win.transient(self.root) # Привязка к главному окну
        win.grab_set() # Блокировка основного окна

        listbox = tk.Listbox(win, font=('Helvetica', 10))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def refresh_list():
            listbox.delete(0, tk.END)
            for uid, name in database.get_users():
                listbox.insert(tk.END, f"{uid} | {name}")
            self.update_comboboxes()

        refresh_list()

        def add_btn():
            name = simpledialog.askstring("Новый сотрудник", "Введите ФИО:", parent=win)
            if name:
                database.add_user(name)
                refresh_list()

        def del_btn():
            selected = listbox.curselection()
            if selected:
                uid = listbox.get(selected).split(" | ")[0]
                if messagebox.askyesno("Подтверждение", "Удалить сотрудника?"):
                    database.delete_user(uid)
                    refresh_list()
                    self.refresh_manager_table()

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="➕ Добавить", command=add_btn).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑 Удалить", command=del_btn).pack(side=tk.LEFT, padx=5)

    def manage_projects_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Управление проектами")
        win.geometry("350x400")
        win.transient(self.root)
        win.grab_set()

        listbox = tk.Listbox(win, font=('Helvetica', 10))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def refresh_list():
            listbox.delete(0, tk.END)
            for pid, name in database.get_projects():
                listbox.insert(tk.END, f"{pid} | {name}")
            self.update_comboboxes()

        refresh_list()

        def add_btn():
            name = simpledialog.askstring("Новый проект", "Введите название:", parent=win)
            if name:
                database.add_project(name)
                refresh_list()

        def edit_btn():
            selected = listbox.curselection()
            if selected:
                item = listbox.get(selected)
                pid, old_name = item.split(" | ")
                new_name = simpledialog.askstring("Изменить проект", "Новое название:", initialvalue=old_name, parent=win)
                if new_name and new_name != old_name:
                    database.edit_project(pid, new_name)
                    refresh_list()
                    self.refresh_manager_table()

        def del_btn():
            selected = listbox.curselection()
            if selected:
                pid = listbox.get(selected).split(" | ")[0]
                if messagebox.askyesno("Подтверждение", "Удалить проект? Все связанные записи времени тоже будут удалены."):
                    database.delete_project(pid)
                    refresh_list()
                    self.refresh_manager_table()

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="➕", width=3, command=add_btn).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✏ Изменить", command=edit_btn).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑 Удалить", command=del_btn).pack(side=tk.LEFT, padx=2)
