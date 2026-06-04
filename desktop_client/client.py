import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter.simpledialog import SimpleDialog
import json

class FurnitureStoreClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Интернет-магазин мебели")
        self.root.geometry("1500x700")
        
        self.base_url = "http://localhost:8000/api"
        self.token = None
        self.client_id = None
        
        self.check_server_connection()

        self.show_login()

    def check_server_connection(self):
        try:
            response = requests.get(f"{self.base_url}/", timeout=2)
            if response.status_code == 200:
                print("Сервер доступен")
            else:
                print("Сервер отвечает с ошибкой")
        except:
            messagebox.showwarning(
                "Предупреждение",
                "Сервер Django не запущен!\n"
                "Запустите сервер командой: python manage.py runserver\n"
                "Клиент будет работать некорректно."
            )
    
    def show_login(self):
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)
        
        ttk.Label(frame, text="Логин:").grid(row=0, column=0, pady=5)
        self.login_entry = ttk.Entry(frame, width=30)
        self.login_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Пароль:").grid(row=1, column=0, pady=5)
        self.password_entry = ttk.Entry(frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        
        ttk.Button(frame, text="Войти", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Регистрация", command=self.show_register).grid(row=3, column=0, columnspan=2)

    def show_register(self):
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)
        
        ttk.Label(frame, text="ФИО:").grid(row=0, column=0, pady=5)
        self.register_name = ttk.Entry(frame, width=30)
        self.register_name.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Адрес:").grid(row=1, column=0, pady=5)
        self.register_address = ttk.Entry(frame, width=30)
        self.register_address.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Логин:").grid(row=2, column=0, pady=5)
        self.register_login = ttk.Entry(frame, width=30)
        self.register_login.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Пароль:").grid(row=3, column=0, pady=5)
        self.register_password = ttk.Entry(frame, width=30, show="*")
        self.register_password.grid(row=3, column=1, pady=5)
        
        ttk.Button(frame, text="Зарегистрироваться", command=self.register).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Назад", command=self.show_login).grid(row=5, column=0, columnspan=2)
    
    def login(self):
        response = requests.post(
            f"{self.base_url}/auth/",
            json={
                "login": self.login_entry.get(),
                "password": self.password_entry.get()
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            self.client_id = data['client_id']
            self.show_main_menu()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
    
    def register(self):
        import json
    
        data = {
            "full_name": self.register_name.get(),
            "address": self.register_address.get(),
            "login": self.register_login.get(),
            "password": self.register_password.get()
        }
    
        print(f"Отправляем данные: {data}")
    
        try:
            response = requests.post(
                f"{self.base_url}/clients/",
                json=data,
                headers={"Content-Type": "application/json"}
            )
        
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
        
            if response.status_code == 201:
                messagebox.showinfo("Успех", "Регистрация успешна!")
                self.show_login()
            else:
                error_msg = "Не удалось зарегистрироваться\n"
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        for field, errors in error_data.items():
                            error_msg += f"\n{field}: {', '.join(errors)}"
                except:
                    error_msg += f"\n{response.text}"
            
                messagebox.showerror("Ошибка", error_msg)
            
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Не удалось подключиться к серверу. Запустите Django сервер.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def show_main_menu(self):
        self.clear_window()
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        catalog_frame = ttk.Frame(notebook)
        notebook.add(catalog_frame, text="Каталог")
        self.setup_catalog_tab(catalog_frame)
        
        orders_frame = ttk.Frame(notebook)
        notebook.add(orders_frame, text="Мои заказы")
        self.setup_orders_tab(orders_frame)
        
        reports_frame = ttk.Frame(notebook)
        notebook.add(reports_frame, text="Отчеты")
        self.setup_reports_tab(reports_frame)
        
        if self.client_id == 1:
            admin_frame = ttk.Frame(notebook)
            notebook.add(admin_frame, text="Управление")
            self.setup_admin_tab(admin_frame)

    def load_categories_and_styles(self):
        try:
            response = requests.get(f"{self.base_url}/categories/", headers={"Authorization": f"Token {self.token}"})
            if response.status_code == 200:
                categories = response.json()
                self.product_category['values'] = [f"{cat['id']}: {cat['name']}" for cat in categories]
        
            response = requests.get(f"{self.base_url}/styles/", headers={"Authorization": f"Token {self.token}"})
            if response.status_code == 200:
                styles = response.json()
                self.product_style['values'] = [f"{style['id']}: {style['name']}" for style in styles]
            
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
    
    def setup_catalog_tab(self, parent):
        filter_frame = ttk.LabelFrame(parent, text="Фильтры", padding="10")
        filter_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(filter_frame, text="Название").grid(row=0, column=0, padx=5)
        self.name_filter = ttk.Entry(filter_frame, width=30)
        self.name_filter.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=2, padx=5)
        self.category_filter = ttk.Combobox(filter_frame, width=20)
        self.category_filter.grid(row=0, column=3, padx=5)

        ttk.Label(filter_frame, text="Стиль:").grid(row=0, column=4, padx=5)
        self.style_filter = ttk.Combobox(filter_frame, width=20)
        self.style_filter.grid(row=0, column=5, padx=5)
    
        self.load_categories_and_styles_for_filter()
    
        ttk.Label(filter_frame, text="Мин. цена:").grid(row=0, column=6, padx=5)
        self.min_price = ttk.Entry(filter_frame, width=10)
        self.min_price.grid(row=0, column=7, padx=5)
    
        ttk.Label(filter_frame, text="Макс. цена:").grid(row=0, column=8, padx=5)
        self.max_price = ttk.Entry(filter_frame, width=10)
        self.max_price.grid(row=0, column=9, padx=5)
    
        ttk.Button(filter_frame, text="Поиск (SQL)", 
                   command=self.search_sql).grid(row=0, column=10, padx=5)
        ttk.Button(filter_frame, text="Поиск (ORM)", 
                   command=self.search_orm).grid(row=0, column=11, padx=5)
    
        ttk.Button(filter_frame, text="Сбросить фильтры", 
                   command=self.reset_filters).grid(row=0, column=12, padx=5)
    
        self.catalog_tree = ttk.Treeview(
            parent, 
            columns=('ID', 'Название', 'Цена', 'Категория', 'Стиль'), 
            show='headings',
            height=20
        )
    
        self.catalog_tree.heading('ID', text='ID')
        self.catalog_tree.heading('Название', text='Название')
        self.catalog_tree.heading('Цена', text='Цена (руб.)')
        self.catalog_tree.heading('Категория', text='Категория')
        self.catalog_tree.heading('Стиль', text='Стиль')
    
        self.catalog_tree.column('ID', width=50)
        self.catalog_tree.column('Название', width=300)
        self.catalog_tree.column('Цена', width=100)
        self.catalog_tree.column('Категория', width=150)
        self.catalog_tree.column('Стиль', width=150)
    
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.catalog_tree.yview)
        self.catalog_tree.configure(yscrollcommand=scrollbar.set)
    
        self.catalog_tree.pack(fill='both', expand=True, padx=10, pady=10, side='left')
        scrollbar.pack(side='right', fill='y', pady=10)
    
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=10, pady=5)
    
        ttk.Button(button_frame, text="Добавить в корзину", 
                   command=self.add_to_order).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить каталог", 
                   command=self.load_catalog).pack(side='left', padx=5)
    
        self.load_catalog()
    
    def load_categories_and_styles_for_filter(self):
        try:
            response = requests.get(f"{self.base_url}/categories/", headers={"Authorization": f"Token {self.token}"}, timeout=5)
            if response.status_code == 200:
                categories = response.json()
                category_list = ["Все"]
                self.categories_dict = {}
            
                for cat in categories:
                    category_list.append(cat['name'])
                    self.categories_dict[cat['name']] = cat['id']
            
                self.category_filter['values'] = category_list
                self.category_filter.set("Все")
            else:
                print(f"Ошибка загрузки категорий: {response.status_code}")
                self.category_filter['values'] = ["Все"]
                self.category_filter.set("Все")
                self.categories_dict = {}
        except Exception as e:
            print(f"Ошибка загрузки категорий: {e}")
            self.category_filter['values'] = ["Все"]
            self.category_filter.set("Все")
            self.categories_dict = {}

        try:
            response = requests.get(f"{self.base_url}/styles/", headers={"Authorization": f"Token {self.token}"}, timeout=5)
            if response.status_code == 200:
                styles = response.json()
                style_list = ["Все"]
                self.styles_dict = {}
            
                for style in styles:
                    style_list.append(style['name'])
                    self.styles_dict[style['name']] = style['id']
            
                self.style_filter['values'] = style_list
                self.style_filter.set("Все")
            else:
                print(f"Ошибка загрузки стилей: {response.status_code}")
                self.style_filter['values'] = ["Все"]
                self.style_filter.set("Все")
                self.styles_dict = {}
        except Exception as e:
            print(f"Ошибка загрузки стилей: {e}")
            self.style_filter['values'] = ["Все"]
            self.style_filter.set("Все")
            self.styles_dict = {}

    def setup_orders_tab(self, parent):
        self.orders_tree = ttk.Treeview(parent, columns=('ID', 'Дата', 'Сумма'), show='headings')
        self.orders_tree.heading('ID', text='ID')
        self.orders_tree.heading('Дата', text='Дата')
        self.orders_tree.heading('Сумма', text='Сумма')

        self.orders_tree.column('ID', width=50)
        self.orders_tree.column('Дата', width=150)
        self.orders_tree.column('Сумма', width=200)

        self.orders_tree.pack(fill='both', expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Загрузить заказы", 
               command=self.load_orders).pack(side='left', padx=5)
    
        ttk.Button(button_frame, text="Рассчитать со скидкой", 
                   command=self.calculate_discount).pack(side='left', padx=5)
    
        ttk.Button(button_frame, text="Обновить", 
                   command=self.refresh_orders).pack(side='left', padx=5)
    
    def setup_reports_tab(self, parent):
        report_frame = ttk.Frame(parent)
        report_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Button(report_frame, text="Отчет по складу (SQL)", command=self.storage_report_sql).pack(pady=5)
        ttk.Button(report_frame, text="Топ товаров (ORM)", command=self.top_products_orm).pack(pady=5)
        
        self.report_text = scrolledtext.ScrolledText(report_frame, height=20)
        self.report_text.pack(fill='both', expand=True, pady=10)
    
    def setup_admin_tab(self, parent):
        admin_notebook = ttk.Notebook(parent)
        admin_notebook.pack(fill='both', expand=True, padx=10, pady=10)
    
        products_frame = ttk.Frame(admin_notebook)
        admin_notebook.add(products_frame, text="Управление товарами")
        self.setup_products_tab(products_frame)
    
        income_frame = ttk.Frame(admin_notebook)
        admin_notebook.add(income_frame, text="Поступление товаров")
        self.setup_income_tab(income_frame)
    
        storage_frame = ttk.Frame(admin_notebook)
        admin_notebook.add(storage_frame, text="Остатки на складе")
        self.setup_storage_tab(storage_frame)

        orders_frame = ttk.Frame(admin_notebook)
        admin_notebook.add(orders_frame, text="Выполнение заказов")
        self.setup_admin_orders_tab(orders_frame)

    def setup_products_tab(self, parent):
        form_frame = ttk.LabelFrame(parent, text="Добавить товар", padding="10")
        form_frame.pack(fill='x', padx=10, pady=10)
    
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, pady=5, sticky='e')
        self.product_name = ttk.Entry(form_frame, width=30)
        self.product_name.grid(row=0, column=1, pady=5, padx=5)
    
        ttk.Label(form_frame, text="Цена:").grid(row=1, column=0, pady=5, sticky='e')
        self.product_price = ttk.Entry(form_frame, width=30)
        self.product_price.grid(row=1, column=1, pady=5, padx=5)
    
        ttk.Label(form_frame, text="Категория (ID):").grid(row=2, column=0, pady=5, sticky='e')
        self.product_category = ttk.Combobox(form_frame, width=27)
        self.product_category.grid(row=2, column=1, pady=5, padx=5)
    
        ttk.Label(form_frame, text="Стиль (ID):").grid(row=3, column=0, pady=5, sticky='e')
        self.product_style = ttk.Combobox(form_frame, width=27)
        self.product_style.grid(row=3, column=1, pady=5, padx=5)
    
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
    
        ttk.Button(btn_frame, text="Добавить (SQL)", command=self.add_product_sql).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Добавить (ORM)", command=self.add_product_orm).pack(side='left', padx=5)
    
        self.load_categories_and_styles()
    
        info_frame = ttk.LabelFrame(parent, text="Существующие категории и стили", padding="10")
        info_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
        self.info_text = scrolledtext.ScrolledText(info_frame, height=10)
        self.info_text.pack(fill='both', expand=True)
    
        self.load_info()
    
        ttk.Button(info_frame, text="Обновить список", command=self.load_info).pack(pady=5)
        ttk.Button(info_frame, text="Обновить каталог", command=self.refresh_catalog).pack(pady=5)

    def setup_income_tab(self, parent):
        form_frame = ttk.LabelFrame(parent, text="Добавить поступление товара", padding="10")
        form_frame.pack(fill='x', padx=10, pady=10)
    
        ttk.Label(form_frame, text="Склад:").grid(row=0, column=0, pady=5, sticky='e')
        self.income_warehouse = ttk.Combobox(form_frame, width=30)
        self.income_warehouse.grid(row=0, column=1, pady=5, padx=5)
    
        ttk.Label(form_frame, text="Товар:").grid(row=1, column=0, pady=5, sticky='e')
        self.income_assortment = ttk.Combobox(form_frame, width=30)
        self.income_assortment.grid(row=1, column=1, pady=5, padx=5)
    
        ttk.Label(form_frame, text="Количество:").grid(row=2, column=0, pady=5, sticky='e')
        self.income_quantity = ttk.Entry(form_frame, width=30)
        self.income_quantity.grid(row=2, column=1, pady=5, padx=5)
    
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
    
        ttk.Button(btn_frame, text="Добавить поступление (SQL)", 
                   command=self.add_income_sql).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Добавить поступление (ORM)", 
                   command=self.add_income_orm).pack(side='left', padx=5)
    
        history_frame = ttk.LabelFrame(parent, text="История поступлений", padding="10")
        history_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
        self.income_tree = ttk.Treeview(
            history_frame, 
            columns=('ID', 'Склад', 'Товар', 'Кол-во', 'Дата'), 
            show='headings',
            height=10
        )
        self.income_tree.heading('ID', text='ID')
        self.income_tree.heading('Склад', text='Склад')
        self.income_tree.heading('Товар', text='Товар')
        self.income_tree.heading('Кол-во', text='Кол-во')
        self.income_tree.heading('Дата', text='Дата')
    
        self.income_tree.column('ID', width=50)
        self.income_tree.column('Склад', width=150)
        self.income_tree.column('Товар', width=250)
        self.income_tree.column('Кол-во', width=80)
        self.income_tree.column('Дата', width=150)
    
        self.income_tree.pack(fill='both', expand=True)
    
        ttk.Button(history_frame, text="Обновить историю", 
                   command=self.load_income_history).pack(pady=5)
    
        self.load_warehouses_and_products()
        self.load_income_history()

    def setup_storage_tab(self, parent):
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill='x', padx=10, pady=10)
    
        ttk.Label(filter_frame, text="Фильтр по складу:").pack(side='left', padx=5)
        self.storage_warehouse = ttk.Combobox(filter_frame, width=30)
        self.storage_warehouse.pack(side='left', padx=5)
        self.storage_warehouse.set("Все склады")
    
        ttk.Button(filter_frame, text="Показать", 
                   command=self.load_storage).pack(side='left', padx=5)
        ttk.Button(filter_frame, text="Показать низкий остаток (<10)", 
                   command=self.load_low_stock).pack(side='left', padx=5)
        ttk.Button(filter_frame, text="Обновить", 
                   command=self.load_storage).pack(side='left', padx=5)
    
        self.storage_tree = ttk.Treeview(
            parent, 
            columns=('Склад', 'Товар', 'Кол-во', 'Стоимость'), 
            show='headings',
            height=15
        )
        self.storage_tree.heading('Склад', text='Склад')
        self.storage_tree.heading('Товар', text='Товар')
        self.storage_tree.heading('Кол-во', text='Кол-во')
        self.storage_tree.heading('Стоимость', text='Общая стоимость')
    
        self.storage_tree.column('Склад', width=150)
        self.storage_tree.column('Товар', width=300)
        self.storage_tree.column('Кол-во', width=100)
        self.storage_tree.column('Стоимость', width=150)
    
        self.storage_tree.pack(fill='both', expand=True, padx=10, pady=10)
    
        self.load_warehouses_for_filter()
        self.load_storage()

    def setup_admin_orders_tab(self, parent):
        orders_frame = ttk.LabelFrame(parent, text="Заказы", padding="10")
        orders_frame.pack(fill='both', expand=True, pady=(0, 10))
    
        self.admin_orders_tree = ttk.Treeview(
            orders_frame,
            columns=('ID', 'Клиент', 'Дата', 'Статус', 'Товаров'),
            show='headings',
            height=10
        )
        self.admin_orders_tree.heading('ID', text='ID')
        self.admin_orders_tree.heading('Клиент', text='Клиент')
        self.admin_orders_tree.heading('Дата', text='Дата')
        self.admin_orders_tree.heading('Статус', text='Статус')
        self.admin_orders_tree.heading('Товаров', text='Товаров')
    
        self.admin_orders_tree.column('ID', width=50)
        self.admin_orders_tree.column('Клиент', width=200)
        self.admin_orders_tree.column('Дата', width=150)
        self.admin_orders_tree.column('Статус', width=100)
        self.admin_orders_tree.column('Товаров', width=80)
    
        self.admin_orders_tree.pack(fill='both', expand=True)

        self.admin_orders_tree.bind('<<TreeviewSelect>>', self.on_order_select)
    
        btn_frame = ttk.Frame(orders_frame)
        btn_frame.pack(fill='x', pady=5)
    
        ttk.Button(btn_frame, text="Обновить список", 
                   command=self.load_admin_orders).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Проверить наличие", 
                   command=self.check_order_availability).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Выполнить заказ", 
                   command=self.process_order).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отменить заказ", 
                   command=self.cancel_order).pack(side='left', padx=5)
    
        details_frame = ttk.LabelFrame(parent, text="Детали заказа", padding="10")
        details_frame.pack(fill='both', expand=True)
    
        self.order_details_text = scrolledtext.ScrolledText(details_frame, height=10)
        self.order_details_text.pack(fill='both', expand=True)
    
        warehouse_frame = ttk.LabelFrame(details_frame, text="Распределение по складам", padding="10")
        warehouse_frame.pack(fill='x', pady=5)
    
        self.warehouse_items = {}
    
        self.load_warehouses_for_orders()
    
        self.load_admin_orders()

    def on_order_select(self, event):
        selected = self.admin_orders_tree.selection()
        if selected:
            order_id = self.admin_orders_tree.item(selected[0])['values'][0]
            self.show_order_details(order_id)

    def load_warehouses_and_products(self):
        headers = {"Authorization": f"Token {self.token}"}
    
        try:
            response = requests.get(f"{self.base_url}/warehouses/", headers=headers)
            if response.status_code == 200:
                warehouses = [f"{w['id']}: {w['name']}" for w in response.json()]
                self.income_warehouse['values'] = warehouses
                if warehouses:
                    self.income_warehouse.set(warehouses[0])
        except Exception as e:
            print(f"Error loading warehouses: {e}")
    
        try:
            response = requests.get(f"{self.base_url}/assortment/", headers=headers)
            if response.status_code == 200:
                products = [f"{p['id']}: {p['name']}" for p in response.json()]
                self.income_assortment['values'] = products
                if products:
                    self.income_assortment.set(products[0])
        except Exception as e:
            print(f"Error loading products: {e}")
    
    def load_warehouses_for_filter(self):
        headers = {"Authorization": f"Token {self.token}"}
    
        try:
            response = requests.get(f"{self.base_url}/warehouses/", headers=headers)
            if response.status_code == 200:
                warehouses = ["Все склады"] + [f"{w['id']}: {w['name']}" for w in response.json()]
                self.storage_warehouse['values'] = warehouses
                self.storage_warehouse.set("Все склады")
        except Exception as e:
            print(f"Error loading warehouses: {e}")
     

    def add_income_orm(self):
        try:
            if not self.income_warehouse.get() or not self.income_assortment.get():
                messagebox.showwarning("Предупреждение", "Выберите склад и товар")
                return
        
            warehouse_id = self.income_warehouse.get().split(':')[0].strip()
            assortment_id = self.income_assortment.get().split(':')[0].strip()
            quantity = int(self.income_quantity.get())
        
            if quantity <= 0:
                messagebox.showwarning("Предупреждение", "Количество должно быть больше 0")
                return
        
            response = requests.post(
                f"{self.base_url}/parishes/add_to_storage/",
                json={
                    'warehouse_id': warehouse_id,
                    'assortment_id': assortment_id,
                    'quantity': quantity,
                    'use_sql': False 
                },
                headers={"Authorization": f"Token {self.token}"}
            )
        
            if response.status_code == 201:
                messagebox.showinfo("Успех", f"Товар добавлен на склад в количестве {quantity} шт.")
                self.income_quantity.delete(0, tk.END)
                self.load_income_history()
                self.load_storage()
            else:
                error_msg = response.json().get('error', 'Неизвестная ошибка')
                messagebox.showerror("Ошибка", f"Не удалось добавить товар\n{error_msg}")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат количества")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def add_income_sql(self):
        try:
            if not self.income_warehouse.get() or not self.income_assortment.get():
                messagebox.showwarning("Предупреждение", "Выберите склад и товар")
                return
        
            warehouse_id = self.income_warehouse.get().split(':')[0].strip()
            assortment_id = self.income_assortment.get().split(':')[0].strip()
            quantity = int(self.income_quantity.get())
        
            if quantity <= 0:
                messagebox.showwarning("Предупреждение", "Количество должно быть больше 0")
                return
        
            response = requests.post(
                f"{self.base_url}/parishes/add_to_storage/",
                json={
                    'warehouse_id': warehouse_id,
                    'assortment_id': assortment_id,
                    'quantity': quantity,
                    'use_sql': True
                },
                headers={"Authorization": f"Token {self.token}"}
            )
        
            if response.status_code == 201:
                messagebox.showinfo("Успех", f"Товар добавлен на склад в количестве {quantity} шт.")
                self.income_quantity.delete(0, tk.END)
                self.load_income_history()
                self.load_storage()
            else:
                error_msg = response.json().get('error', 'Неизвестная ошибка')
                messagebox.showerror("Ошибка", f"Не удалось добавить товар\n{error_msg}")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат количества")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def load_income_history(self):
        for item in self.income_tree.get_children():
            self.income_tree.delete(item)
    
        try:
            response = requests.get(
                f"{self.base_url}/parishes/",
                headers={"Authorization": f"Token {self.token}"}
            )
        
            if response.status_code == 200:
                for parish in response.json():
                    self.income_tree.insert('', 'end', values=(
                        parish.get('id'),
                        parish.get('warehouse_name', ''),
                        parish.get('assortment_name', ''),
                        parish.get('quantity', ''),
                        parish.get('datetime', '')[:19] if parish.get('datetime') else ''
                    ))
        except Exception as e:
            print(f"Error loading income history: {e}")
    
    def load_storage(self):
        for item in self.storage_tree.get_children():
            self.storage_tree.delete(item)
    
        try:
            warehouse_filter = self.storage_warehouse.get()
        
            if warehouse_filter and warehouse_filter != "Все склады":
                warehouse_id = warehouse_filter.split(':')[0].strip()
                response = requests.get(
                    f"{self.base_url}/storage/by_warehouse/",
                    params={'warehouse_id': warehouse_id},
                    headers={"Authorization": f"Token {self.token}"}
                )
            else:
                response = requests.get(
                    f"{self.base_url}/storage/",
                    headers={"Authorization": f"Token {self.token}"}
                )
        
            if response.status_code == 200:
                for item in response.json():
                    if item.get('quantity', 0) > 0:
                        self.storage_tree.insert('', 'end', values=(
                            item.get('warehouse_name', ''),
                            item.get('assortment_name', ''),
                            item.get('quantity', 0),
                            f"{item.get('total_value', 0):,.2f} руб."
                        ))
        except Exception as e:
            print(f"Error loading storage: {e}")

    def load_low_stock(self):
        for item in self.storage_tree.get_children():
            self.storage_tree.delete(item)
    
        try:
            response = requests.get(
                f"{self.base_url}/storage/low_stock/",
                headers={"Authorization": f"Token {self.token}"}
            )
        
            if response.status_code == 200:
                for item in response.json():
                    self.storage_tree.insert('', 'end', values=(
                        item.get('warehouse_name', ''),
                        item.get('assortment_name', ''),
                        item.get('quantity', 0),
                        f"{item.get('total_value', 0):,.2f} руб."
                    ))
            
                if len(response.json()) == 0:
                    messagebox.showinfo("Информация", "Нет товаров с низким остатком")
        except Exception as e:
            print(f"Error loading low stock: {e}")

    def load_admin_orders(self):
        for item in self.admin_orders_tree.get_children():
            self.admin_orders_tree.delete(item)
    
        try:
            response = requests.get(
                f"{self.base_url}/orders/",
                headers={"Authorization": f"Token {self.token}"}
            )
        
            if response.status_code == 200:
                for order in response.json():
                    status_display = {
                        'new': '🆕 Новый',
                        'confirmed': '✅ Подтвержден',
                        'processing': '⚙️ В обработке',
                        'shipped': '📦 Отправлен',
                        'delivered': '🏠 Доставлен',
                        'cancelled': '❌ Отменен'
                    }.get(order.get('status'), order.get('status'))
                
                    self.admin_orders_tree.insert('', 'end', values=(
                        order.get('id'),
                        order.get('client_name', ''),
                        order.get('datetime', '')[:19] if order.get('datetime') else '',
                        status_display,
                        order.get('total_quantity', 0)
                    ))
        except Exception as e:
            print(f"Error loading orders: {e}")

    def load_warehouses_for_orders(self):
        try:
            response = requests.get(
                f"{self.base_url}/warehouses/",
                headers={"Authorization": f"Token {self.token}"}
            )
        
            if response.status_code == 200:
                self.warehouses = response.json()
        except Exception as e:
            print(f"Error loading warehouses: {e}")

    def show_order_details(self, order_id):
        self.order_details_text.delete(1.0, tk.END)
    
        try:
            response = requests.get(
                f"{self.base_url}/orders/{order_id}/",
                headers={"Authorization": f"Token {self.token}"}
            )
        
            if response.status_code == 200:
                order = response.json()
            
                self.order_details_text.insert(tk.END, f"Заказ №{order['id']}\n")
                self.order_details_text.insert(tk.END, f"Клиент: {order['client_name']}\n")
                self.order_details_text.insert(tk.END, f"Дата: {order['datetime']}\n")
                self.order_details_text.insert(tk.END, f"Статус: {order['status']}\n")
                self.order_details_text.insert(tk.END, "\nТовары в заказе:\n")
                self.order_details_text.insert(tk.END, "-" * 50 + "\n")
            
                total = 0
                for item in order.get('items', []):
                    if item['type'] == 'product':
                        self.order_details_text.insert(
                            tk.END,
                            f"{item['product_name']} x {item['quantity']} = {item['total']} руб.\n"
                        )
                        total += item['total']
                    elif item['type'] == 'kit':
                        self.order_details_text.insert(
                            tk.END,
                            f"Комплект: {item['kit_name']} x {item['quantity']}\n"
                        )
            
                self.order_details_text.insert(tk.END, "-" * 50 + "\n")
                self.order_details_text.insert(tk.END, f"ИТОГО: {total} руб.\n")
            
                self.check_availability_for_order(order_id)
            
        except Exception as e:
            self.order_details_text.insert(tk.END, f"Ошибка: {str(e)}")

    def check_availability_for_order(self, order_id):
        try:
            response = requests.get(
                f"{self.base_url}/orders/{order_id}/check_availability/",
                headers={"Authorization": f"Token {self.token}"}
            )
        
            if response.status_code == 200:
                data = response.json()
            
                if data['available']:
                    self.order_details_text.insert(
                        tk.END, "\n✅ Все товары есть в наличии!\n"
                    )
                else:
                    self.order_details_text.insert(
                        tk.END, "\n❌ Недостаточно товаров:\n"
                    )
                    for product in data['missing_products']:
                        self.order_details_text.insert(
                            tk.END,
                            f"  - {product['product']}: требуется {product['required']}, "
                            f"в наличии {product['available']}, не хватает {product['deficit']}\n"
                        )
        except Exception as e:
            print(f"Error checking availability: {e}")

    def check_order_availability(self):
        selected = self.admin_orders_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ")
            return
    
        order_id = self.admin_orders_tree.item(selected[0])['values'][0]
        self.show_order_details(order_id)

    def process_order(self):
        selected = self.admin_orders_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ")
            return
    
        order_id = self.admin_orders_tree.item(selected[0])['values'][0]
    
        warehouse_window = tk.Toplevel(self.root)
        warehouse_window.title(f"Списание товаров - Заказ №{order_id}")
        warehouse_window.geometry("600x500")
    
        response = requests.get(
            f"{self.base_url}/orders/{order_id}/get_picklist/",
            headers={"Authorization": f"Token {self.token}"}
        )
    
        if response.status_code != 200:
            messagebox.showerror("Ошибка", "Не удалось получить список товаров")
            return
    
        picklist = response.json().get('picklist', [])
    
        ttk.Label(warehouse_window, text="Распределите товары по складам:", font=('Arial', 10, 'bold')).pack(pady=5)
    
        frame = ttk.Frame(warehouse_window)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
    
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
    
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
    
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
    
        warehouse_entries = {}
    
        for product in picklist:
            ttk.Label(scrollable_frame, text=f"{product['name']} - {product['quantity']} шт.", 
                     font=('Arial', 9, 'bold')).pack(anchor='w', pady=5)
        
            warehouse_frame = ttk.Frame(scrollable_frame)
            warehouse_frame.pack(fill='x', padx=20)
        
            ttk.Label(warehouse_frame, text="Склад:").pack(side='left', padx=5)
            warehouse_var = tk.StringVar()
            warehouse_combo = ttk.Combobox(warehouse_frame, textvariable=warehouse_var, width=30)
        
            warehouse_list = [f"{w['id']}: {w['name']}" for w in self.warehouses]
            warehouse_combo['values'] = warehouse_list
            warehouse_combo.pack(side='left', padx=5)
        
            ttk.Label(warehouse_frame, text="Количество:").pack(side='left', padx=5)
            quantity_entry = ttk.Entry(warehouse_frame, width=10)
            quantity_entry.insert(0, str(product['quantity']))
            quantity_entry.pack(side='left', padx=5)
        
            warehouse_entries[product['assortment_id']] = {
                'warehouse_var': warehouse_var,
                'quantity_entry': quantity_entry,
                'required': product['quantity'],
                'name': product['name']
            }
        
            ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=10)
    
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def confirm_processing():
            warehouse_items = {}
        
            for product_id, data in warehouse_entries.items():
                warehouse_text = data['warehouse_var'].get()
                if not warehouse_text:
                    messagebox.showerror("Ошибка", f"Выберите склад для {data['name']}")
                    return

            for product_id, data in warehouse_entries.items():
                try:
                    quantity = int(data['quantity_entry'].get())
                except ValueError:
                    messagebox.showerror("Ошибка", f"Неверное количество для {data['name']}")
                    return

            for product_id, data in warehouse_entries.items():
                warehouse_text = data['warehouse_var'].get()
                warehouse_id = warehouse_text.split(':')[0].strip()
                quantity = int(data['quantity_entry'].get())
            
                if quantity != data['required']:
                    messagebox.showerror(
                        "Внимание", 
                        f"Для {data['name']} нужно {data['required']} шт., а указано {quantity}!"
                    )
                    return
            
                if warehouse_id not in warehouse_items:
                    warehouse_items[warehouse_id] = []
            
                warehouse_items[warehouse_id].append({
                    'assortment_id': product_id,
                    'quantity': quantity
                })
                
            try:
                response = requests.post(
                    f"{self.base_url}/orders/{order_id}/process/",
                    json={'warehouse_items': warehouse_items},
                    headers={"Authorization": f"Token {self.token}"}
                )
        
                if response.status_code == 200:
                    messagebox.showinfo("Успех", f"Заказ №{order_id} выполнен")
                    warehouse_window.destroy()
                    self.load_admin_orders()
                    self.load_storage()
                else:
                    error_msg = response.json().get('error', 'Неизвестная ошибка')
                    messagebox.showerror("Ошибка выполнения", f"Заказ не может быть выполнен:\n{error_msg}")
            except requests.exceptions.ConnectionError:
                messagebox.showerror("Ошибка", "Нет подключения к серверу")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
    
        ttk.Button(warehouse_window, text="Подтвердить выполнение", 
                  command=confirm_processing).pack(pady=10)

    def cancel_order(self):
        selected = self.admin_orders_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ")
            return
    
        order_id = self.admin_orders_tree.item(selected[0])['values'][0]
    
        if messagebox.askyesno("Подтверждение", f"Отменить заказ №{order_id}?"):
            response = requests.post(
                f"{self.base_url}/orders/{order_id}/cancel/",
                headers={"Authorization": f"Token {self.token}"}
            )
        
            if response.status_code == 200:
                messagebox.showinfo("Успех", f"Заказ №{order_id} отменен")
                self.load_admin_orders()
            else:
                messagebox.showerror("Ошибка", response.json().get('error', 'Не удалось отменить заказ'))

    def load_catalog(self):
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)
        
        self.root.config(cursor="watch")
        self.root.update()

        try:
            response = requests.get(f"{self.base_url}/assortment/using_orm/", headers={"Authorization": f"Token {self.token}"}, timeout=10)
        
            if response.status_code == 200:
                items = response.json()
            
                if isinstance(items, dict) and 'items' in items:
                    items = items['items']
            
                for item in items:
                    price = item.get('price', 0)
                    try:
                        price_str = f"{float(price):.2f}"
                    except (ValueError, TypeError):
                        price_str = str(price)

                    self.catalog_tree.insert('', 'end', values=(
                        item.get('id', ''),
                        item.get('name', ''),
                        price_str,
                        item.get('category_name', ''),
                        item.get('style_name', '')
                    ))
            
                count = len(self.catalog_tree.get_children())
                self.root.title(f"Интернет-магазин мебели - {count} товаров")
            else:
                messagebox.showerror("Ошибка", f"Не удалось загрузить каталог: {response.status_code}")
            
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Нет подключения к серверу. Запустите Django сервер.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки каталога: {str(e)}")
        finally:
            self.root.config(cursor="")

    def load_info(self):
        self.info_text.delete(1.0, tk.END)
    
        self.info_text.insert(tk.END, "=== Категории ===\n")
        try:
            response = requests.get(f"{self.base_url}/categories/", headers={"Authorization": f"Token {self.token}"})
            if response.status_code == 200:
                categories = response.json()
                for cat in categories:
                    self.info_text.insert(tk.END, f"ID {cat['id']}: {cat['name']}\n")
        except:
            self.info_text.insert(tk.END, "Не удалось загрузить категории\n")
    
        self.info_text.insert(tk.END, "\n=== Стили ===\n")
        try:
            response = requests.get(f"{self.base_url}/styles/", headers={"Authorization": f"Token {self.token}"})
            if response.status_code == 200:
                styles = response.json()
                for style in styles:
                    self.info_text.insert(tk.END, f"ID {style['id']}: {style['name']}\n")
        except:
            self.info_text.insert(tk.END, "Не удалось загрузить стили\n")
    
    def refresh_catalog(self):
        self.load_categories_and_styles_for_filter()
        self.load_catalog()

    def search_sql(self):
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)
    
        self.root.config(cursor="watch")
        self.root.update()
    
        try:
            name = self.name_filter.get().strip()
            category_name = self.category_filter.get()
            style_name = self.style_filter.get()
            min_price = self.min_price.get().strip()
            max_price = self.max_price.get().strip()
        
            params = {}
        
            if not hasattr(self, 'categories_dict') or not self.categories_dict:
                messagebox.showwarning("Предупреждение", "Список категорий не загружен. Обновите страницу.")
                self.load_categories_and_styles_for_filter()
                self.root.config(cursor="")
                return

            if not hasattr(self, 'styles_dict') or not self.styles_dict:
                messagebox.showwarning("Предупреждение", "Список стилей не загружен. Обновите страницу.")
                self.load_categories_and_styles_for_filter()
                self.root.config(cursor="")
                return
            
            if name != "":
                params['name'] = name

            if category_name != "Все" and category_name in self.categories_dict:
                params['category_id'] = self.categories_dict[category_name]
            elif category_name != "Все" and category_name not in self.categories_dict:
                messagebox.showwarning("Предупреждение", f"Категория '{category_name}' не найдена")
                self.root.config(cursor="")
                return

            if style_name != "Все" and style_name in self.styles_dict:
                params['style_id'] = self.styles_dict[style_name]
            elif style_name != "Все" and style_name not in self.styles_dict:
                messagebox.showwarning("Предупреждение", f"Стиль '{style_name}' не найден")
                self.root.config(cursor="")
                return
        
            if min_price:
                try:
                    params['min_price'] = float(min_price)
                except ValueError:
                    messagebox.showwarning("Предупреждение", "Неверный формат минимальной цены")
                    self.root.config(cursor="")
                    return
        
            if max_price:
                try:
                    params['max_price'] = float(max_price)
                except ValueError:
                    messagebox.showwarning("Предупреждение", "Неверный формат максимальной цены")
                    self.root.config(cursor="")
                    return
        
            print(f"SQL Search params: {params}")
            response = requests.get(f"{self.base_url}/assortment/using_sql/", headers={"Authorization": f"Token {self.token}"}, params=params, timeout=10)
        
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
            
                if not items:
                    messagebox.showinfo("Результат", "Товары не найдены")
            
                for item in items:
                    if isinstance(item, (list, tuple)):
                        self.catalog_tree.insert('', 'end', values=item)
                    elif isinstance(item, dict):
                        price = item.get('price', 0)
                        try:
                            price_str = f"{float(price):.2f}"
                        except (ValueError, TypeError):
                            price_str = str(price)

                        self.catalog_tree.insert('', 'end', values=(
                            item.get('id', ''),
                            item.get('name', ''),
                            price_str,
                            item.get('category_name', ''),
                            item.get('style_name', '')
                        ))
            
                count = len(self.catalog_tree.get_children())
                self.root.title(f"Интернет-магазин мебели - найдено {count} товаров")
            
            else:
                messagebox.showerror("Ошибка", f"Ошибка запроса: {response.status_code}\n{response.text}")
        
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Нет подключения к серверу.\nЗапустите Django сервер.")
        except requests.exceptions.Timeout:
            messagebox.showerror("Ошибка", "Превышено время ожидания ответа от сервера")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
            import traceback
            traceback.print_exc()
    
        finally:
            self.root.config(cursor="")
    
    def search_orm(self):
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)
    
        self.root.config(cursor="watch")
        self.root.update()
    
        try:
            name = self.name_filter.get().strip()
            category_name = self.category_filter.get()
            style_name = self.style_filter.get()
            min_price = self.min_price.get().strip()
            max_price = self.max_price.get().strip()
        
            if not hasattr(self, 'categories_dict') or not self.categories_dict:
                messagebox.showwarning("Предупреждение", "Список категорий не загружен. Обновите страницу.")
                self.load_categories_and_styles_for_filter()
                self.root.config(cursor="")
                return

            if not hasattr(self, 'styles_dict') or not self.styles_dict:
                messagebox.showwarning("Предупреждение", "Список стилей не загружен. Обновите страницу.")
                self.load_categories_and_styles_for_filter()
                self.root.config(cursor="")
                return
                 
            category_id = None
            if category_name != "Все" and category_name in self.categories_dict:
                category_id = self.categories_dict[category_name]
            elif category_name != "Все":
                messagebox.showwarning("Предупреждение", f"Категория '{category_name}' не найдена")
                self.root.config(cursor="")
                return

            style_id = None
            if style_name != "Все" and style_name in self.styles_dict:
                style_id = self.styles_dict[style_name]
            elif style_name != "Все":
                messagebox.showwarning("Предупреждение", f"Стиль '{style_name}' не найден")
                self.root.config(cursor="")
                return
        
            params = {}
        
            if min_price:
                try:
                    params['min_price'] = float(min_price)
                except ValueError:
                    messagebox.showwarning("Предупреждение", "Неверный формат минимальной цены")
                    self.root.config(cursor="")
                    return
        
            if max_price:
                try:
                    params['max_price'] = float(max_price)
                except ValueError:
                    messagebox.showwarning("Предупреждение", "Неверный формат максимальной цены")
                    self.root.config(cursor="")
                    return
            
            if name != "":
                params['name'] = name

            if category_id:
                params['category_id'] = category_id

            if style_id:
                params['style_id'] = style_id
        
            print(f"ORM Search params: {params}")
        
            if params:
                response = requests.get(f"{self.base_url}/assortment/using_orm/", headers={"Authorization": f"Token {self.token}"}, params=params, timeout=10)
            else:
                response = requests.get(f"{self.base_url}/assortment/using_orm/", headers={"Authorization": f"Token {self.token}"}, timeout=10)
        
            if response.status_code == 200:
                items = response.json()
            
                if isinstance(items, dict):
                    if 'items' in items:
                        items = items['items']
                    elif 'results' in items:
                        items = items['results']
            
                if not items:
                    messagebox.showinfo("Результат", "Товары не найдены")
            
                for item in items:                  
                    price = item.get('price', 0)
                    try:
                        price_str = f"{float(price):.2f}"
                    except (ValueError, TypeError):
                        price_str = str(price)

                    self.catalog_tree.insert('', 'end', values=(
                        item.get('id', ''),
                        item.get('name', ''),
                        price_str,
                        item.get('category_name', ''),
                        item.get('style_name', '')
                    ))
            
                count = len(self.catalog_tree.get_children())
                self.root.title(f"Интернет-магазин мебели - найдено {count} товаров")
            
            else:
                messagebox.showerror("Ошибка", f"Ошибка запроса: {response.status_code}\n{response.text}")
        
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Ошибка", "Нет подключения к серверу.\nЗапустите Django сервер.")
        except requests.exceptions.Timeout:
            messagebox.showerror("Ошибка", "Превышено время ожидания ответа от сервера")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
            import traceback
            traceback.print_exc()
    
        finally:
            self.root.config(cursor="")
    
    def reset_filters(self):
        self.name_filter.delete(0, tk.END)
        self.category_filter.set("Все")
        self.style_filter.set("Все")
        self.min_price.delete(0, tk.END)
        self.max_price.delete(0, tk.END)
        self.load_catalog()

    def add_to_order(self):
        selected = self.catalog_tree.selection()
    
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите товар для добавления в корзину")
            return
    
        item = self.catalog_tree.item(selected[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
    
        from tkinter.simpledialog import askinteger
        quantity = askinteger("Количество", f"Сколько {product_name} добавить?", 
                              minvalue=1, maxvalue=99)
    
        if not quantity:
            return
    
        try:
            response = requests.get(f"{self.base_url}/orders/", 
                                    headers={"Authorization": f"Token {self.token}"})
        
            active_order = None
        
            if response.status_code == 200:
                orders = response.json()
        
            from datetime import datetime
            today = datetime.now().date()
        
            if orders:
                for order in orders:
                    order_date = datetime.fromisoformat(order['datetime'].replace('Z', '+00:00')).date()
                    if order_date == today:
                        active_order = order
                        break
        
            if not active_order:
                response = requests.post(
                    f"{self.base_url}/orders/",
                    json={"client": self.client_id},
                    headers={"Authorization": f"Token {self.token}"}
                )
                if response.status_code == 201:
                    active_order = response.json()
                else:
                    messagebox.showerror("Ошибка", "Не удалось создать заказ")
                    return
        
            if active_order:
                response = requests.post(
                    f"{self.base_url}/order-items/",
                    json={
                        "order": active_order['id'],
                        "assortment": product_id,
                        "quantity": quantity,
                        "kit": None
                    },
                    headers={"Authorization": f"Token {self.token}"}
                )
        
                if response.status_code == 201:
                    messagebox.showinfo("Успех", f"Товар '{product_name}' добавлен в корзину в количестве {quantity} шт.")
                else:
                    messagebox.showerror("Ошибка", f"Не удалось добавить товар\n{response.text}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
    
    def load_orders(self):
        from datetime import datetime

        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
    
        try:
            response = requests.get(
                f"{self.base_url}/orders/",
                headers={"Authorization": f"Token {self.token}"}
            )
        
            if response.status_code == 200:
                orders = response.json()
            
                for order in orders:
                    total_response = requests.get(
                        f"{self.base_url}/orders/{order['id']}/calculate_total/",
                        headers={"Authorization": f"Token {self.token}"}
                    )
                
                    total_amount = "Не рассчитано"
                    if total_response.status_code == 200:
                        total_amount = f"{total_response.json().get('total', 0):,.2f} руб."
                
                    try:
                        order_datetime = datetime.fromisoformat(order['datetime'].replace('Z', '+00:00'))
                        formatted_date = order_datetime.strftime("%d.%m.%Y %H:%M")
                    except:
                        formatted_date = order.get('datetime', 'Нет даты')
                
                    self.orders_tree.insert('', 'end', values=(
                        order.get('id', ''),
                        formatted_date,
                        total_amount
                    ))
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки заказов: {str(e)}")

    def calculate_discount(self):
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ")
            return
    
        order_id = self.orders_tree.item(selected[0])['values'][0]
    
        try:
            self.root.config(cursor="watch")
            self.root.update()
        
            response = requests.post(
                f"{self.base_url}/orders/{order_id}/calculate_with_discount/",
                headers={"Authorization": f"Token {self.token}"}
            )
        
            if response.status_code == 200:
                data = response.json()
                final_price = data.get('final_price', 0)
            
                self.orders_tree.item(selected[0], values=(
                    order_id,
                    self.orders_tree.item(selected[0])['values'][1],
                    f"{final_price:,.2f} руб. (со скидкой)"
                ))
            
                messagebox.showinfo(
                    "Сумма со скидкой", 
                    f"Итоговая сумма заказа №{order_id}: {final_price:,.2f} руб."
                )
            else:
                messagebox.showerror("Ошибка", f"Не удалось рассчитать скидку: {response.text}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")
        finally:
            self.root.config(cursor="")

    def refresh_orders(self):
        self.load_orders()
        messagebox.showinfo("Обновлено", "Список заказов обновлен")
    
    def storage_report_sql(self):
        response = requests.get(f"{self.base_url}/orders/reports_sql/?type=storage", headers={"Authorization": f"Token {self.token}"})
        if response.status_code == 200:
            report = response.json().get('report', [])
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "Отчет по складу:\n\n")
            for item in report:
                self.report_text.insert(tk.END, f"Склад: {item[0]}, Товар: {item[1]}, Количество: {item[2]}\n")
    
    def top_products_orm(self):
        response = requests.get(f"{self.base_url}/orders/reports_orm/?type=top_products", headers={"Authorization": f"Token {self.token}"})
        if response.status_code == 200:
            report = response.json().get('report', [])
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "Топ товаров:\n\n")
            for item in report:
                self.report_text.insert(tk.END, f"{item.get('name', '')} - {item.get('total_quantity', 0)} шт.\n")
    
    def add_product_sql(self):
        try:
            name = self.product_name.get().strip()
            price = self.product_price.get().strip()
            raw_category_id = self.product_category.get().strip()
            raw_style_id = self.product_style.get().strip()

            category_id = ""
            style_id = ""

            for s in raw_category_id:
                if s == ":": 
                    break
                category_id += s

            for s in raw_style_id:
                if s == ":":
                   break
                style_id += s
        
            if not all([name, price, category_id, style_id]):
                messagebox.showwarning("Предупреждение", "Заполните все поля!")
                return
        
            response = requests.post(
                f"{self.base_url}/assortment/using_sql_create/",
                json={
                    "name": name,
                    "price": float(price),
                    "category_id": int(category_id),
                    "style_id": int(style_id)
                },
                headers={"Authorization": f"Token {self.token}"}
            )
        
            if response.status_code == 201:
                messagebox.showinfo("Успех", f"Товар '{name}' добавлен (SQL)")
                self.clear_product_fields()
            else:
                messagebox.showerror("Ошибка", f"Не удалось добавить товар\n{response.text}")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат данных\nЦена и ID должны быть числами")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
    
    def add_product_orm(self):
        try:
            name = self.product_name.get().strip()
            price = self.product_price.get().strip()
            raw_category_id = self.product_category.get().strip()
            raw_style_id = self.product_style.get().strip()

            category_id = ""
            style_id = ""

            for s in raw_category_id:
                if s == ":":
                   break
                category_id += s

            for s in raw_style_id:
                if s == ":":
                   break
                style_id += s
        
            if not all([name, price, category_id, style_id]):
                messagebox.showwarning("Предупреждение", "Заполните все поля!")
                return
        
            response = requests.post(
                f"{self.base_url}/assortment/",
                json={
                    "name": name,
                    "price": float(price),
                    "category": int(category_id),
                    "style": int(style_id)
                },
                headers={"Authorization": f"Token {self.token}"}
            )
        
            if response.status_code == 201:
                messagebox.showinfo("Успех", f"Товар '{name}' добавлен (ORM)")
                self.clear_product_fields()
            else:
                error_msg = "Не удалось добавить товар\n"
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        for field, errors in error_data.items():
                            error_msg += f"\n{field}: {', '.join(errors)}"
                except:
                    error_msg += f"\n{response.text}"
            
                messagebox.showerror("Ошибка", error_msg)
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат данных\nЦена и ID должны быть числами")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def clear_product_fields(self):
        self.product_name.delete(0, tk.END)
        self.product_price.delete(0, tk.END)
        self.product_category.delete(0, tk.END)
        self.product_style.delete(0, tk.END)
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

def main():
    root = tk.Tk()
    app = FurnitureStoreClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()
