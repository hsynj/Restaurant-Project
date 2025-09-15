from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox,
    QLineEdit, QLabel, QTabWidget, QHeaderView, QFormLayout, QScrollArea,
    QGridLayout
)
from PySide6.QtCore import Qt
from core_logic.shopping_cart import *
from database.db_handler import *
from ui.widgets.food_item_widget import *


class CustomerWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.shopping_cart = ShoppingCart()

        self.applied_discount_info = None
        self.discount_amount_applied = 0.0

        self.setWindowTitle(f"پنل مشتری - خوش آمدید {self.user_data[3]}")
        self.resize(1000, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.order_placement_page = QWidget()
        order_placement_main_layout = QHBoxLayout(self.order_placement_page) 

        self.order_placement_page = QWidget()
        order_placement_main_layout = QHBoxLayout(self.order_placement_page)

        self.right_section_widget = QWidget()
        self.right_section_widget.setObjectName("rightLayoutSection")
        right_layout = QVBoxLayout(self.right_section_widget)

        self.top_right_layout = QWidget()
        self.top_right_layout.setObjectName("topRightLayoutSection")
        top_right_layout = QVBoxLayout(self.top_right_layout)

        # logout button
        self.logout_button = QPushButton("خروج از حساب کاربری")
        self.logout_button.clicked.connect(self.handle_logout)
        self.logout_request = False

        self.user_info_label = QWidget()
        self.user_info_label.setObjectName("userInfoLabel")
        user_info_label = QVBoxLayout(self.user_info_label)

        self.welcome_label = QLabel(f"کاربر: {self.user_data[3]}")        
        self.wallet_label = QLabel(f"موجودی کیف پول: {float(self.user_data[4]):,.0f} تومان")
        
        user_info_label.addWidget(self.welcome_label)
        user_info_label.addWidget(self.wallet_label)

        top_right_layout.addWidget(self.logout_button)
        top_right_layout.addWidget(self.user_info_label)

        right_layout.addWidget(self.top_right_layout)
        right_layout.addWidget(QLabel("سبد خرید:"))

        self.down_right_layout = QWidget()
        self.down_right_layout.setObjectName("downRightLayoutSection")
        down_right_layout = QVBoxLayout(self.down_right_layout)
        # shopping cart
        self.customer_cart_table = QWidget()
        self.customer_cart_table.setObjectName("cartTableLayout")
        customer_cart_table = QVBoxLayout(self.customer_cart_table)
        self.cart_table = QTableWidget()
        self.cart_table.setObjectName("cartTable")
        self.cart_table.setColumnCount(3)
        # self.cart_table.setHorizontalHeaderLabels(["نام غذا", "تعداد", "قیمت کل"])
        self.cart_table.horizontalHeader().setVisible(False) # Hide table header
        self.cart_table.verticalHeader().setVisible(False) # Hide table rows number
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        customer_cart_table.addWidget(self.cart_table)
        self.decrease_item_from_cart_button = QPushButton("حذف از سبد خرید")
        customer_cart_table.addWidget(self.decrease_item_from_cart_button)
        down_right_layout.addWidget(self.customer_cart_table)

        # discount code
        self.discount_layout = QWidget()
        self.discount_layout.setObjectName("discountLayout")
        discount_layout = QHBoxLayout(self.discount_layout)
        self.discount_code_input = QLineEdit()
        self.discount_code_input.setPlaceholderText("کد تخفیف")
        discount_layout.addWidget(self.discount_code_input)
        self.apply_discount_button = QPushButton("اعمال")
        discount_layout.addWidget(self.apply_discount_button)
        down_right_layout.addWidget(self.discount_layout)

        # total price label
        self.total_price_info = QWidget()
        self.total_price_info.setObjectName("totalPriceInfo")
        total_price_info = QVBoxLayout(self.total_price_info)
        self.total_price_label = QLabel("مبلغ کل: 0 تومان")
        self.total_discount_label = QLabel("مبلغ تخفیف: 0 تومان")
        self.final_price_label = QLabel("مبلغ نهایی: 0 تومان")
        self.discount_info_label = QLabel("")
        total_price_info.addWidget(self.total_price_label)
        total_price_info.addWidget(self.total_discount_label)
        total_price_info.addWidget(self.final_price_label)
        total_price_info.addWidget(self.discount_info_label)

        down_right_layout.addWidget(self.total_price_info)

        right_layout.addWidget(self.down_right_layout)
        # final sabt
        self.place_order_btn = QPushButton("ثبت نهایی سفارش")
        right_layout.addWidget(self.place_order_btn)
        order_placement_main_layout.addWidget(self.right_section_widget, 1) #

        # foods menu
        self.left_section_widget = QWidget()
        left_layout = QVBoxLayout(self.left_section_widget)
        left_layout.addWidget(QLabel("منو غذا:"))
        # self.food_menu_table = QTableWidget()
        # self.food_menu_table.setColumnCount(3)
        # self.food_menu_table.setHorizontalHeaderLabels(["نام غذا", "قیمت", "موجودی"])
        # self.food_menu_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.food_menu_table.setSelectionBehavior(QTableWidget.SelectRows)
        # self.food_menu_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # left_layout.addWidget(self.food_menu_table)
        # self.add_to_cart_btn = QPushButton("افزودن به سبد خرید")
        # left_layout.addWidget(self.add_to_cart_btn)
        self.menu_scroll_area = QScrollArea()
        self.menu_scroll_area.setWidgetResizable(True)
        self.menu_widget_container = QWidget()
        self.menu_widget_container.setObjectName("MenuWidgetContainer")
        self.menu_grid_layout = QGridLayout(self.menu_widget_container)
        self.menu_grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.menu_grid_layout.setSpacing(10)

        self.menu_scroll_area.setWidget(self.menu_widget_container)
        left_layout.addWidget(self.menu_scroll_area)

        order_placement_main_layout.addWidget(self.left_section_widget, 2) #

        # signals
        # self.add_to_cart_btn.clicked.connect(self.handle_add_to_cart)
        self.apply_discount_button.clicked.connect(self.handle_apply_discount_code)
        self.place_order_btn.clicked.connect(self.handle_place_order)
        self.decrease_item_from_cart_button.clicked.connect(self.handle_decrease_item_from_cart)
        self.load_menu_data() 
        self.update_cart_table()

        self.tabs.addTab(self.order_placement_page, "ثبت سفارش جدید")

        # order history tab
        self.order_history_page = QWidget()
        order_history_layout = QVBoxLayout(self.order_history_page)
            # time line
        self.timeline_layout = QWidget()
        self.timeline_layout.setObjectName("timelineLayout")
        timeline_layout = QHBoxLayout(self.timeline_layout)
        timeline_layout.setAlignment(Qt.AlignCenter)
        self.status_label_registered = QLabel("ثبت شده")
        self.status_label_arrow1 = QLabel("⬅️")
        self.status_label_processing = QLabel("در حال آماده‌سازی")
        self.status_label_arrow2 = QLabel("⬅️")
        self.status_label_shipped = QLabel("ارسال شده")
        self.status_label_arrow3 = QLabel("⬅️")
        self.status_label_delivered = QLabel("تحویل داده شده")
        timeline_layout.addWidget(self.status_label_registered)
        timeline_layout.addWidget(self.status_label_arrow1)
        timeline_layout.addWidget(self.status_label_processing)
        timeline_layout.addWidget(self.status_label_arrow2)
        timeline_layout.addWidget(self.status_label_shipped)
        timeline_layout.addWidget(self.status_label_arrow3)
        timeline_layout.addWidget(self.status_label_delivered)
        order_history_layout.addWidget(self.timeline_layout)
            # table
        history_label = QLabel("لیست سفارشات قبلی شما:")
        history_label.setAlignment(Qt.AlignCenter)
        order_history_layout.addWidget(history_label)

        self.order_history_table = QTableWidget()
        self.order_history_table.setColumnCount(4)
        self.order_history_table.setHorizontalHeaderLabels(["شناسه سفارش", "تاریخ ثبت", "مبلغ کل (تومان)", "وضعیت"])
        self.order_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.order_history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.order_history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.order_history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        order_history_layout.addWidget(self.order_history_table)
            # orders items
        selected_order_items_label = QLabel("آیتم‌های سفارش انتخاب شده:")
        selected_order_items_label.setAlignment(Qt.AlignCenter)
        order_history_layout.addWidget(selected_order_items_label)

        self.selected_order_items_table_customer = QTableWidget()
        self.selected_order_items_table_customer.setColumnCount(4)
        self.selected_order_items_table_customer.setHorizontalHeaderLabels(["نام غذا", "تعداد", "قیمت واحد (تومان)", "جمع قیمت آیتم (تومان)"])
        self.selected_order_items_table_customer.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.selected_order_items_table_customer.setEditTriggers(QTableWidget.NoEditTriggers)
        self.selected_order_items_table_customer.setSelectionBehavior(QTableWidget.SelectRows)
        order_history_layout.addWidget(self.selected_order_items_table_customer)
        self.order_history_table.itemSelectionChanged.connect(self.handle_order_history_selection_change)


        self.tabs.addTab(self.order_history_page, "تاریخچه سفارشات من")

        # discounts tab
        self.my_discount_page = QWidget()
        my_discount_layout = QVBoxLayout(self.my_discount_page)
        self.tabs.addTab(self.my_discount_page, "کد تخفیف های من")
        my_discount_layout.addWidget(QLabel("کد های تخفیف فعال برای شما:"))
        self.usable_discount_table = QTableWidget()
        self.usable_discount_table.setColumnCount(4)
        self.usable_discount_table.setHorizontalHeaderLabels(["کد تخفیف", 'توضیحات / مقدار', 'حداقل خرید(تومان)', 'تاریخ انقضا'])
        self.usable_discount_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.usable_discount_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.usable_discount_table.setSelectionMode(QTableWidget.SingleSelection)
        self.usable_discount_table.setEditTriggers(QTableWidget.NoEditTriggers)
        my_discount_layout.addWidget(self.usable_discount_table)
        self.apply_selected_discount_button = QPushButton('اعمال کد تخفیف انتخاب شده')
        my_discount_layout.addWidget(self.apply_selected_discount_button)
        self.apply_selected_discount_button.clicked.connect(self.handle_apply_discount_from_list)
        self.load_my_usable_discount()
        self.load_order_history()
        
        # wallet balance tab
        self.my_wallet_page = QWidget()
        my_wallet_layout = QFormLayout(self.my_wallet_page)
        self.wallet_tab_current_balance_label = QLabel(f"موجودی فعلی: {float(self.user_data[4]):,.0f} تومان")
        my_wallet_layout.addRow(self.wallet_tab_current_balance_label)
        self.top_up_amount_input = QLineEdit()
        self.top_up_amount_input.setObjectName("topupAmountInput")
        self.top_up_amount_input.setPlaceholderText("مبلغ به تومان")
        # double_validator = QDoubleValidator(0.0, 1e12, 0)
        # double_validator.setNotation(QDoubleValidator.StandardNotation)
        # self.top_up_amount_input.setValidator(double_validator)
        my_wallet_layout.addRow("مبلغ شارژ:", self.top_up_amount_input)
        self.top_up_button = QPushButton("افزایش موجودی")
        self.top_up_button.setObjectName("topupAmountButton")
        my_wallet_layout.addWidget(self.top_up_button)
        self._update_all_wallet_display()
        self.tabs.addTab(self.my_wallet_page, "کیف پول من")
        self.top_up_button.clicked.connect(self.handle_top_up_wallet)
        # set default tab
        self.tabs.setCurrentWidget(self.order_placement_page) 

    def handle_apply_discount_code(self):
        entered_code = self.discount_code_input.text().strip()
        if not entered_code:
            self.discount_info_label.setText("لطفا کد تخفیف را وارد کنید.")
            self.applied_discount_info = None
            self.discount_amount_applied = 0.0
            self.update_cart_table()
            return
        
        original_cart_total = self.shopping_cart.calculate_total()
        discount_record, message = get_valid_discount_by_code(entered_code, original_cart_total)

        if discount_record:
            # available code
            calculate_discount, new_total_after_discount = apply_discount(original_cart_total, discount_record)
            self.applied_discount_info = discount_record
            self.discount_amount_applied = calculate_discount
            self.discount_info_label.setText(f"تخفیف {calculate_discount:,.0f} تومان اعمال شد!")
            self.discount_info_label.setStyleSheet("color: green;")
        else:
            # unavailable code
            self.applied_discount_info = None
            self.discount_amount_applied = 0.0
            self.discount_info_label.setText(message)
            self.discount_info_label.setStyleSheet("color: red;")
        
        self.update_cart_table()

    # def load_menu_data(self):
    #     foods = get_available_foods()
    #     self.food_menu_table.setRowCount(len(foods))
    #     for row, food in enumerate(foods):
    #         self.food_menu_table.setItem(row, 0, QTableWidgetItem(food[1]))
    #         self.food_menu_table.setItem(row, 1, QTableWidgetItem(f"{food[2]:,.0f}"))
    #         food_inventory = 'موجود✅' if food[3] > 0 else 'نامجود❌'
    #         self.food_menu_table.setItem(row, 2, QTableWidgetItem(food_inventory))
    #         # ذخیره کردن ID غذا در آیتم جدول برای دسترسی بعدی
    #         self.food_menu_table.item(row, 0).setData(Qt.UserRole, food[0])
    def load_menu_data(self):
        """load foods menu"""
        # clear latest items
        while self.menu_grid_layout.count():
            child = self.menu_grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        foods = get_available_foods()
        if foods is None: foods = []

        row, col = 0, 0
        num_cols = 3

        for food_data in foods:
            # food_data: (id, name, price, inventory, image_path)
            food_id = food_data[0]
            name = food_data[1]
            price = float(food_data[2])
            # inventory = food_data[3] 
            image_path = food_data[4] if food_data[4] else "path/to/default_image.png"

            item_widget = FoodItemWidget(food_id, name, price, image_path)
            item_widget.clicked.connect(self.handle_food_item_selected_for_cart)

            self.menu_grid_layout.addWidget(item_widget, row, col)

            col += 1
            if col >= num_cols:
                col = 0
                row += 1

    def handle_food_item_selected_for_cart(self, food_id):
        """add food to cart when clicked on it"""
        foods_list = get_available_foods()
        selected_food_info = None
        if foods_list:
            for food in foods_list:
                if food[0] == food_id:
                    selected_food_info = food
                    break

        if selected_food_info:
            # selected_food_info: (id, name, price, inventory, image_path)
            food_name = selected_food_info[1]
            food_price = float(selected_food_info[2])

            self.shopping_cart.add_item(food_id, food_name, food_price)
            self.update_cart_table()

            QMessageBox.information(self, "افزودن به سبد", f"'{food_name}' به سبد خرید شما اضافه شد.")
        else:
            QMessageBox.warning(self, "خطا", "اطلاعات غذا برای افزودن به سبد یافت نشد.")

    def load_order_history(self):
        """Loads the logged in user's order history and displays it in a table."""
        if not self.user_data:
            print("DEBUG Customer: No user data to load order history.")
            return

        user_id = self.user_data[0]
        orders = get_orders_for_specific_customer(user_id, "all_time") 

        self.order_history_table.setRowCount(0) 
        if orders is None:
            print(f"DEBUG Customer: get_orders_for_specific_customer for user_id {user_id} returned None.")
            orders = []
        
        self.order_history_table.setRowCount(len(orders))
        for row_index, order_data in enumerate(orders):
            self.order_history_table.setItem(row_index, 0, QTableWidgetItem(str(order_data[0])))
            self.order_history_table.setItem(row_index, 1, QTableWidgetItem(order_data[1]))
            self.order_history_table.setItem(row_index, 2, QTableWidgetItem(f"{float(order_data[2]):,.0f}"))
            self.order_history_table.setItem(row_index, 3, QTableWidgetItem(order_data[3]))
        
        print(f"DEBUG Customer: Order history loaded for user_id {user_id}.")

    # def handle_add_to_cart(self):
    #     selected_row = self.food_menu_table.currentRow()
    #     if selected_row == -1:
    #         return
    #     food_id = self.food_menu_table.item(selected_row, 0).data(Qt.UserRole)
    #     food_name = self.food_menu_table.item(selected_row, 0).text()
    #     food_price_text = self.food_menu_table.item(selected_row, 1).text().replace(',', '')
    #     food_price = float(food_price_text)
    #     self.shopping_cart.add_item(food_id, food_name, food_price)
    #     self.update_cart_table()

    def update_cart_table(self):
        cart_items_dict = self.shopping_cart.get_items()
        self.cart_table.setRowCount(len(cart_items_dict))

        original_total_price = 0

        for row, (food_id, item) in enumerate(cart_items_dict.items()):
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{str(item['quantity'])} عدد"))
            item_total = item['quantity'] * item['price']
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"{item_total:,.0f}"))
            original_total_price += item_total

        final_price_after_discount = original_total_price - self.discount_amount_applied
        
        if self.discount_amount_applied > 0:
            self.total_price_label.setText(f"مبلغ اصلی: {original_total_price:,.0f} تومان")
            self.total_discount_label.setText(f"مبلغ تخفیف: {self.discount_amount_applied:,.0f} تومان")
            self.final_price_label.setText(f"مبلغ نهایی: {final_price_after_discount:,.0f} تومان")
        else:
            self.total_price_label.setText(f"مبلغ کل: {original_total_price:,.0f} تومان")
            self.final_price_label.setText(f"مبلغ نهایی: {original_total_price:,.0f} تومان")

    def handle_place_order(self):
        if self.shopping_cart.is_empty():
            QMessageBox.warning(self, "خطا", "سبد خرید شما خالی است.")
            return

        original_total = self.shopping_cart.calculate_total()
        final_price_to_pay = original_total - self.discount_amount_applied
        cart_items_for_db = self.shopping_cart.get_items()
        user_id = self.user_data[0]

        discount_id_to_pass = None
        if self.applied_discount_info:
            discount_id_to_pass = self.applied_discount_info[0]
        success, message = place_order(user_id, cart_items_for_db, final_price_to_pay, applied_discount_id=discount_id_to_pass)

        if success:
            QMessageBox.information(self, "موفقیت", message)
            self.shopping_cart.clear() # clear shopping cart
            # reset discounts lable
            self.applied_discount_info = None
            self.discount_amount_applied = 0.0
            self.discount_info_label.setText("")
            self.discount_code_input.setText("")

            self.update_cart_table()   # update table
            self.load_menu_data()      # update foods data

            self.load_order_history()

            # update user data and wallet balance
            new_user_data = check_user_login(self.user_data[1], self.user_data[2])
            if new_user_data:
                self.user_data = new_user_data
                self.wallet_label.setText(f"مودی کیف پول: {self.user_data[4]:,.0f} تومان")
        else:
            QMessageBox.critical(self, "خطا", message)

    def _update_order_timeline_display(self, current_status_text):
        statuses_ordered = ["ثبت شده", "در حال آماده‌سازی", "ارسال شده", "تحویل داده شده"]
        labels_ordered = [
            self.status_label_registered, 
            self.status_label_processing, 
            self.status_label_shipped, 
            self.status_label_delivered
        ]
        default_style = "color: gray; font-weight: normal;"
        current_style = "color: #3498db; font-weight: bold; font-size: 15px;"
        completed_style = "color: green; font-weight: normal;"

        for lable in labels_ordered:
            lable.setStyleSheet(default_style)

        try:
            current_index = statuses_ordered.index(current_status_text)
        except ValueError:
            if current_status_text.startswith("لغو شده"):
                pass
            return
        
        for i, lable in enumerate(labels_ordered):
            if i < current_index:
                lable.setStyleSheet(completed_style)
            elif i == current_index:
                lable.setStyleSheet(current_style)
            else:
                lable.setStyleSheet(default_style)

    def handle_order_history_selection_change(self):
        selected_rows = self.order_history_table.selectionModel().selectedRows()
        self._update_order_timeline_display('')
        self.selected_order_items_table_customer.setRowCount(0)

        if not selected_rows:
            return
        
        selected_row_index = selected_rows[0].row()
        order_id_item = self.order_history_table.item(selected_row_index, 0)
        status_item = self.order_history_table.item(selected_row_index, 3)
        if order_id_item is None or not order_id_item.text().strip() or \
            status_item is None or not status_item.text().strip():
            return
        try:
            order_id = int(order_id_item.text())
            current_status_text = status_item.text()

            self._update_order_timeline_display(current_status_text)
            items = get_order_items_for_admin(order_id)
            if items is None:
                items = []
            self.selected_order_items_table_customer.setRowCount(len(items))
            
            for row_idx, item_data in enumerate(items):
                # item_data: (food_name, quantity, price_per_item, item_subtotal)
                self.selected_order_items_table_customer.setItem(row_idx, 0, QTableWidgetItem(item_data[0]))
                self.selected_order_items_table_customer.setItem(row_idx, 1, QTableWidgetItem(str(item_data[1])))
                self.selected_order_items_table_customer.setItem(row_idx, 2, QTableWidgetItem(f"{float(item_data[2]):,.0f}"))
                self.selected_order_items_table_customer.setItem(row_idx, 3, QTableWidgetItem(f"{float(item_data[3]):,.0f}"))
        except ValueError:
                print(f"DEBUG Customer: Error converting order_id to int: '{order_id_item.text()}'")
        except Exception as e:
            print(f"Error in handle_order_history_selection_change loading items: {e}")
            QMessageBox.critical(self, "خطای بارگذاری", f"خطا در بارگذاری جزئیات سفارش: {e}")
    
    def load_my_usable_discount(self):
        """upload usable discount into a discount table"""
        discounts = get_active_and_valid_discounts()
        self.usable_discount_table.setRowCount(0)
        if discounts is None:
            discounts = []
        self.usable_discount_table.setRowCount(len(discounts))

        for row_index, discount_data in enumerate(discounts):
            code = discount_data[1]
            desc = ""
            if discount_data[2] == 'percentage':
                desc = f"{discount_data[3]:.0f}% تخفیف"
            elif discount_data[2] == 'fixed_amount':
                desc = f"{discount_data[3]:,.0f} تومان تخفیف"
            min_purchase = f"{discount_data[4]:,.0f}" if discount_data[4] > 0 else "ندارد"
            expiry = discount_data[5].split(" ")[0] if discount_data[5] else "نامحدود"
            self.usable_discount_table.setItem(row_index, 0, QTableWidgetItem(code))
            self.usable_discount_table.setItem(row_index, 1, QTableWidgetItem(desc))
            self.usable_discount_table.setItem(row_index, 2, QTableWidgetItem(min_purchase))
            self.usable_discount_table.setItem(row_index, 3, QTableWidgetItem(expiry))

    def handle_apply_discount_from_list(self):
        selected_rows = self.usable_discount_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "اخطار", "لطفاً ابتدا یک کد تخفیف را از لیست انتخاب کنید.")
            return
        selected_row_index = selected_rows[0].row()
        code_item = self.usable_discount_table.item(selected_row_index, 0)
        if code_item:
            discount_code_to_apply = code_item.text()

            self.tabs.setCurrentWidget(self.order_placement_page)
            self.discount_code_input.setText(discount_code_to_apply)
            self.handle_apply_discount_code()
            QMessageBox.information(self, "اعمال کد", f"کد تخفیف '{discount_code_to_apply}' برای اعمال به سبد خرید شما تنظیم شد. لطفاً وضعیت اعمال را در تب ثبت سفارش بررسی کنید.")
        else:
            QMessageBox.warning(self, "خطا", "کد تخفیف معتبری انتخاب نشده است.")

    def _update_all_wallet_display(self):
        """update the all of wallet balance display in customer window"""
        new_balance = float(self.user_data[4])
        formatted_balance = f"{new_balance:,.0f} تومان"
        if hasattr(self, 'wallet_label'): # wallet label hast ya na?
            self.wallet_label.setText(f"موجودی کیف پول: {formatted_balance}")
        if hasattr(self, 'wallet_tab_current_balance_label'):
            self.wallet_tab_current_balance_label.setText(f"موجودی فعلی: {formatted_balance}")

    def handle_top_up_wallet(self):
        amount_str = self.top_up_amount_input.text().strip()
        if not amount_str:
            QMessageBox.warning(self, "اخطار", "لطفاً مبلغ شارژ را وارد کنید.")
            return
        try:
            amount_to_add = float(amount_str)
            if amount_to_add <= 0:
                QMessageBox.warning(self, "اخطار", "مبلغ شارژ باید بیشتر از صفر باشد.")
                return
        except ValueError:
            QMessageBox.warning(self, "اخطار", "مبلغ وارد شده معتبر نیست. لطفاً فقط عدد وارد کنید.")
            return

        user_id = self.user_data[0]
        success, message = top_up_wallet(user_id, amount_to_add)
        if success:
            QMessageBox.information(self, "موفقیت", message)
            updated_user_info = check_user_login(self.user_data[1], self.user_data[2]) # user_data[1]=username, user_data[2]=password
            if updated_user_info:
                self.user_data = updated_user_info
                self._update_all_wallet_display()
            else:
                QMessageBox.critical(self, "خطا", "خطا در به‌روزرسانی اطلاعات کاربر.")

            self.top_up_amount_input.clear()
        else:
            QMessageBox.critical(self, "خطا در شارژ", message)

    def handle_decrease_item_from_cart(self):
        selected_rows = self.cart_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "اخطار", "لطفاً ابتدا یک آیتم را از سبد خرید انتخاب کنید.")
            return
        selected_row_index = selected_rows[0].row()

        food_name_item = self.cart_table.item(selected_row_index, 0)
        if not food_name_item:
            return
        food_name = food_name_item.text()
        food_id = None
        for f_id, item_details in self.shopping_cart.get_items().items():
            if item_details['name'] == food_name:
                food_id = f_id
                break
        if food_id is not None:
            success = self.shopping_cart.decrease_item_quantity(food_id)
            if success:
                self.update_cart_table()
            else:
                QMessageBox.warning(self, "خطا", "خطا در کاهش آیتم از سبد خرید.")
        else:
            QMessageBox.warning(self, "خطا", "خطا در کاهش آیتم از سبد خرید.")

    def handle_logout(self):
        reply = QMessageBox.question(self, "خروج از حساب", 
                                    "آیا مطمئن هستید که می‌خواهید از حساب خود خارج شوید؟",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.logout_requested = True
            self.close()

if __name__ == '__main__':
    print("You cant run this file currently, run main.py")