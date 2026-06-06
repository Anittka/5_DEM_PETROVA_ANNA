import customtkinter as ctk  
from tkinter import messagebox
import sqlite3
from windows.products_window import ProductsWindow


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ООО Мир Игрушек")
        self.geometry("450x380")

        # Основной фон
        self.configure(fg_color="#FFFFFF")#ЦВЕТ ПО УСЛОВИЮ

        # Заголовок
        self.title_label = ctk.CTkLabel(
            self,
            text="Ваш - Магазин игрушек",
            font=("Arial", 22, "bold"), #СДЕЛАЕМ ЖИРНЕЕ
            text_color="#000000"
        )
        self.title_label.pack(pady=25)

        # Поле логина
        self.login_entry = ctk.CTkEntry(
            self,
            placeholder_text="Введите логин",
            width=350,
            height=45,
            font=("Arial", 14),
            fg_color="#FFFFFF",
            border_color="#DEB887"#ЦВЕТ ПО УСЛОВИЮ
        )
        self.login_entry.pack(pady=10)

        # Поле пароля
        self.password_entry = ctk.CTkEntry(
            self,
            placeholder_text="Введите пароль",
            show="*",
            width=350,
            height=45,
            font=("Arial", 14),
            fg_color="#FFFFFF",
            border_color="#DEB887"
        )
        self.password_entry.pack(pady=10)

        # Кнопка входа
        self.login_button = ctk.CTkButton(
            self,
            text="Войти",
            command=self.login,
            width=350,
            height=45,
            fg_color="#DEB887",
            hover_color="#DEB887",
            text_color="#000000",
            font=("Arial", 14, "bold")
        )
        self.login_button.pack(pady=10)

        # Кнопка гостевого входа
        self.guest_button = ctk.CTkButton(
            self,
            text="Продолжить как гость",
            command=self.guest_login,
            width=350,
            height=45,
            fg_color="#F5DEB3",
            hover_color="#DEB887",
            text_color="#000000",
            font=("Arial", 14)
        )
        self.guest_button.pack(pady=5)

        # Подсказка
        self.hint_label = ctk.CTkLabel(
            self,
            text="Введите логин и пароль :)",
            font=("Arial", 14),
            text_color="#666666"#ЦВЕТ не ПО УСЛОВИЮ
        )
        self.hint_label.pack(pady=20)

    def login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, full_name, role
            FROM users
            WHERE login=? AND password=?
            """,
            (login, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            user_id, full_name, role = user

            self.destroy()

            app = ProductsWindow(
                user_id,
                full_name,
                role
            )

            app.mainloop()

        else:
            messagebox.showerror(
                "Ошибка",
                "Неверный логин или пароль;) "
            )

    def guest_login(self):
        self.destroy()

        app = ProductsWindow(
            None,
            "Гость",
            "guest"
        )

        app.mainloop()