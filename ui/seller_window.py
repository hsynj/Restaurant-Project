from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QHeaderView, QPushButton, QTableWidgetItem, QMessageBox, QLabel, QGroupBox)
from PySide6.QtCore import Qt

from database.db_handler import *
from ui.dialogs_admin.discount_dialog import *
from ui.dialogs_admin.food_dialog import *
from ui.dialogs_admin.user_dialog import *
from ui.dialogs_admin.admin_add_order_dialog import *
from ui.widgets.chart_widget import *

class SellerWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("سیستم مدیریت رستوران - پنل فروشنده")
        self.resize(800, 600)

        # tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # create tabs
        self.setup_dashboard_tab()
        self.setup_user_management_tab()
        self.setup_order_management_tab()


    def setup_dashboard_tab(self):
        self.dashboard_page = QWidget()
        dashboard_main_layout = QVBoxLayout(self.dashboard_page)
        
        top_row_layout = QHBoxLayout()
        down_row_layout = QHBoxLayout()
        admin_status_layout = QHBoxLayout()

        self.welcome_label_admin_dashboard = QLabel(f"فروشنده عزیز {self.user_data[3]} خوش آمدید")
        self.logout_button_admin_dashboard = QPushButton("خروج از حساب کاربری")
        admin_status_layout.addWidget(self.welcome_label_admin_dashboard)
        admin_status_layout.addStretch()
        admin_status_layout.addWidget(self.logout_button_admin_dashboard)
        dashboard_main_layout.addLayout(admin_status_layout)
        self.logout_request = False
        
        self.logout_button_admin_dashboard.clicked.connect(self.handle_logout) 
        dashboard_main_layout.addLayout(top_row_layout)

        admin_add_order_groupbox = QGroupBox("ثبت سفارش جدید توسط فروشنده")
        admin_add_order_form_main_layout = QVBoxLayout()

        self.temporary_admin_order_items = {}

        admin_order_form_layout = QFormLayout()
        self.admin_order_user_select_combo = QComboBox()
        admin_order_form_layout.addRow("انتخاب مشتری:", self.admin_order_user_select_combo)
        admin_add_order_form_main_layout.addLayout(admin_order_form_layout)

        admin_add_item_layout = QHBoxLayout()
        self.admin_order_food_select_combo = QComboBox()
        admin_add_item_layout.addWidget(QLabel("غذا:"))
        admin_add_item_layout.addWidget(self.admin_order_food_select_combo, 1)

        self.admin_order_quantity_spinbox = QSpinBox()
        self.admin_order_quantity_spinbox.setMinimum(1)
        self.admin_order_quantity_spinbox.setValue(1)
        admin_add_item_layout.addWidget(QLabel("تعداد:"))
        admin_add_item_layout.addWidget(self.admin_order_quantity_spinbox)

        self.admin_order_add_food_button = QPushButton("افزودن به این سفارش")
        admin_add_item_layout.addWidget(self.admin_order_add_food_button)
        admin_add_order_form_main_layout.addLayout(admin_add_item_layout)

        admin_add_order_form_main_layout.addWidget(QLabel("آیتم‌های این سفارش:"))
        self.admin_order_current_items_table = QTableWidget()
        self.admin_order_current_items_table.setColumnCount(4)
        self.admin_order_current_items_table.setHorizontalHeaderLabels(["نام غذا", "تعداد", "قیمت واحد", "جمع"])
        self.admin_order_current_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.admin_order_current_items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        admin_add_order_form_main_layout.addWidget(self.admin_order_current_items_table)

        admin_order_bottom_form_layout = QFormLayout()
        self.admin_order_total_price_label = QLabel("0 تومان")
        admin_order_bottom_form_layout.addRow("مبلغ کل سفارش:", self.admin_order_total_price_label)

        self.admin_order_initial_status_combo = QComboBox()
        self.admin_order_initial_status_combo.addItems(["ثبت توسط فروشنده", "در حال آماده‌سازی", "تکمیل شده"])
        admin_order_bottom_form_layout.addRow("وضعیت اولیه سفارش:", self.admin_order_initial_status_combo)
        admin_add_order_form_main_layout.addLayout(admin_order_bottom_form_layout)

        admin_order_action_buttons_layout = QHBoxLayout()
        self.admin_order_submit_button = QPushButton("ثبت نهایی این سفارش")
        self.admin_order_clear_button = QPushButton("پاک کردن فرم")
        admin_order_action_buttons_layout.addStretch()
        admin_order_action_buttons_layout.addWidget(self.admin_order_clear_button)
        admin_order_action_buttons_layout.addWidget(self.admin_order_submit_button)
        admin_add_order_form_main_layout.addLayout(admin_order_action_buttons_layout)
        
        admin_add_order_groupbox.setLayout(admin_add_order_form_main_layout)
        down_row_layout.addWidget(admin_add_order_groupbox, 1)

        dashboard_main_layout.addLayout(down_row_layout)

        self.tabs.addTab(self.dashboard_page, "داشبورد")
        self.tabs.setCurrentWidget(self.dashboard_page)

        self.admin_order_add_food_button.clicked.connect(self._admin_add_food_to_temporary_order)
        self.admin_order_submit_button.clicked.connect(self.handle_admin_submit_new_order)
        self.admin_order_clear_button.clicked.connect(self.handle_admin_clear_order_form)

        self._populate_admin_order_user_combo()
        self._populate_admin_order_food_combo()

    def setup_order_management_tab(self):
        """Control Orders"""
        self.order_management_page = QWidget()
        main_order_layout = QVBoxLayout(self.order_management_page)

        # orders list table
        orders_label = QLabel("لیست تمام سفارش‌ها:")
        main_order_layout.addWidget(orders_label)
        
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["شناسه سفارش", "نام مشتری", "تاریخ ثبت", "مبلغ کل (تومان)", "وضعیت"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows) # select full row
        self.orders_table.setSelectionMode(QTableWidget.SingleSelection) # just select 1 row
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_order_layout.addWidget(self.orders_table, 1)

        # order items table
        details_label = QLabel("جزئیات سفارش انتخاب شده:")
        main_order_layout.addWidget(details_label)
        
        self.order_items_table = QTableWidget()
        self.order_items_table.setColumnCount(4)
        self.order_items_table.setHorizontalHeaderLabels(["نام غذا", "تعداد", "قیمت واحد (تومان)", "جمع قیمت آیتم (تومان)"])
        self.order_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.order_items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_order_layout.addWidget(self.order_items_table, 1)

        # buttons
        controls_layout = QHBoxLayout()

        self.admin_add_order_button = QPushButton("ثبت سفارش جدید")
        controls_layout.addWidget(self.admin_add_order_button)
        self.admin_add_order_button.setEnabled(False)

        self.admin_edit_order_details_button = QPushButton("ویرایش آیتم‌های سفارش")
        controls_layout.addWidget(self.admin_edit_order_details_button)
        
        controls_layout.addStretch()

        controls_layout.addWidget(QLabel("تغییر وضعیت به:"))
        self.order_status_combo = QComboBox()
        self.order_status_combo.addItems(["ثبت شده", "در حال آماده‌سازی", "ارسال شده", "تحویل داده شده"])
        controls_layout.addWidget(self.order_status_combo)
        
        self.update_status_button = QPushButton("اعمال وضعیت")
        controls_layout.addWidget(self.update_status_button)

        self.cancel_order_button = QPushButton("حذف سفارش منتخب")
        controls_layout.addWidget(self.cancel_order_button)
        
        main_order_layout.addLayout(controls_layout)

        self.tabs.addTab(self.order_management_page, "مدیریت سفارش‌ها")

        # signals
        self.orders_table.itemSelectionChanged.connect(self.display_order_items_for_selected_order) # show selected orders item
        
        self.update_status_button.clicked.connect(self.handle_update_order_status)
        self.cancel_order_button.clicked.connect(self.handle_calncel_selected_order)
        self.admin_add_order_button.clicked.connect(self.show_admin_add_order_dialog)
        self.admin_edit_order_details_button.clicked.connect(self.handle_edit_order_details_placeholder)

        self.load_all_orders_data()

    def setup_user_management_tab(self):
        """Control Users"""
        page = QWidget()
        layout = QVBoxLayout(page)

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels(["ID", "نام کاربری", "رمز عبور", "نام و نام خانوادگی", "موجودی کیف پول", "نقش"])
        # Full width tables cloumn
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Select full row
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        # Not edit triggers
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.add_user_button = QPushButton("افزدون کاربر")
        self.edit_user_button = QPushButton("تغیر کاربر انتخاب شده")
        self.delete_user_button = QPushButton("حذف کاربر انتخاب شده")
        self.edit_user_button.setEnabled(False)
        self.delete_user_button.setEnabled(False)


        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_user_button)
        button_layout.addWidget(self.edit_user_button)
        button_layout.addWidget(self.delete_user_button)
        
        layout.addWidget(self.user_table)
        layout.addLayout(button_layout)

        # set signals
        self.add_user_button.clicked.connect(self.show_add_user_dialog)

        self.tabs.addTab(page, "مدیریت کاربران")
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # load data
        self.load_users_data()

    # slots for dashboard
    def _populate_admin_order_user_combo(self):
        """full select user combo box."""
        self.admin_order_user_select_combo.clear()
        self.admin_order_user_select_combo.addItem("-- مشتری را انتخاب کنید --", userData=None)
        users = get_all_users() 
        if users:
            for user in users:
                if user[5] == 'customer':
                    self.admin_order_user_select_combo.addItem(f"{user[3]} (ID: {user[0]})", userData=user[0])

    def _populate_admin_order_food_combo(self):
        """full select foods combo box."""
        self.admin_order_food_select_combo.clear()
        self.admin_order_food_select_combo.addItem("-- غذا را انتخاب کنید --", userData=None)
        foods = get_available_foods()
        if foods:
            for food in foods:
                self.admin_order_food_select_combo.addItem(f"{food[1]} - {food[2]:,.0f} تومان", userData=food)

    def _admin_add_food_to_temporary_order(self):
        """add food to temp order table."""
        selected_food_index = self.admin_order_food_select_combo.currentIndex()
        if selected_food_index <= 0:
            QMessageBox.warning(self, "اخطار", "لطفاً یک غذا را انتخاب کنید.")
            return
        
        food_data_tuple = self.admin_order_food_select_combo.itemData(selected_food_index)
        food_id = food_data_tuple[0]
        food_name = food_data_tuple[1]
        food_price = float(food_data_tuple[2])
        quantity_to_add = self.admin_order_quantity_spinbox.value()

        if food_id in self.temporary_admin_order_items:
            self.temporary_admin_order_items[food_id]['quantity'] += quantity_to_add
        else:
            self.temporary_admin_order_items[food_id] = {
                'name': food_name,
                'price_at_order': food_price,
                'quantity': quantity_to_add,
                'food_id': food_id 
            }
        self._update_admin_temporary_order_display()

    def _update_admin_temporary_order_display(self):
        """update temp order table and total price."""
        self.admin_order_current_items_table.setRowCount(0)
        total_price = 0
        
        for row, item_data in enumerate(self.temporary_admin_order_items.values()):
            self.admin_order_current_items_table.insertRow(row)
            self.admin_order_current_items_table.setItem(row, 0, QTableWidgetItem(item_data['name']))
            self.admin_order_current_items_table.setItem(row, 1, QTableWidgetItem(str(item_data['quantity'])))
            self.admin_order_current_items_table.setItem(row, 2, QTableWidgetItem(f"{item_data['price_at_order']:,.0f}"))
            subtotal = item_data['quantity'] * item_data['price_at_order']
            self.admin_order_current_items_table.setItem(row, 3, QTableWidgetItem(f"{subtotal:,.0f}"))
            total_price += subtotal
        
        self.admin_order_total_price_label.setText(f"{total_price:,.0f} تومان")

    def handle_admin_clear_order_form(self):
        """clear add order filds."""
        self.admin_order_user_select_combo.setCurrentIndex(0)
        self.admin_order_food_select_combo.setCurrentIndex(0)
        self.admin_order_quantity_spinbox.setValue(1)
        self.temporary_admin_order_items.clear()
        self._update_admin_temporary_order_display()
        self.admin_order_initial_status_combo.setCurrentIndex(0)

    def handle_admin_submit_new_order(self):
        """send data to database"""
        selected_user_index = self.admin_order_user_select_combo.currentIndex()
        if selected_user_index <= 0:
            QMessageBox.warning(self, "خطا", "لطفاً یک مشتری را برای سفارش انتخاب کنید.")
            return

        if not self.temporary_admin_order_items:
            QMessageBox.warning(self, "خطا", "حداقل یک آیتم باید به سفارش اضافه شود.")
            return
            
        user_id = self.admin_order_user_select_combo.itemData(selected_user_index)
        
        order_items_list_for_db = []
        for item_id, details in self.temporary_admin_order_items.items():
            order_items_list_for_db.append({
                'food_id': item_id, 
                'quantity': details['quantity'],
                'price_at_order': details['price_at_order']
            })

        total_price_str = self.admin_order_total_price_label.text().replace(" تومان", "").replace(",", "")
        total_price = float(total_price_str)
        initial_status = self.admin_order_initial_status_combo.currentText()
        
        success, new_order_id, message = admin_create_order(
            user_id=user_id,
            order_items_details=order_items_list_for_db,
            total_price=total_price,
            initial_status=initial_status
        )

        if success:
            QMessageBox.information(self, "موفقیت", f"{message}\nشناسه سفارش جدید: {new_order_id}")
            self.load_all_orders_data()
            self.handle_admin_clear_order_form()
        else:
            QMessageBox.critical(self, "خطا در ثبت سفارش", message)

    # slots for orders
    def load_all_orders_data(self):
        """Read all orders data from database"""
        try:
            orders = get_all_orders_for_admin()
            self.orders_table.setRowCount(0) # delete previus rows
            if orders is None:
                print("DEBUG: get_all_orders_for_admin() returned None.")
                orders = []

            self.orders_table.setRowCount(len(orders))

            for row_index, order_data in enumerate(orders):
                # order_data: (order_id, user_full_name, order_date, total_price, status)
                self.orders_table.setItem(row_index, 0, QTableWidgetItem(str(order_data[0]))) # order id
                self.orders_table.setItem(row_index, 1, QTableWidgetItem(order_data[1]))      # customer name
                self.orders_table.setItem(row_index, 2, QTableWidgetItem(order_data[2]))      # date
                self.orders_table.setItem(row_index, 3, QTableWidgetItem(f"{float(order_data[3]):,.0f}")) # price
                self.orders_table.setItem(row_index, 4, QTableWidgetItem(order_data[4]))      # status
                
            self.order_items_table.setRowCount(0) # clear items
            self.update_order_action_buttons_state() # update buttons

            # clear items table after reload / load orders
            self.order_items_table.setRowCount(0) 
            print("DEBUG: Orders table loaded/reloaded.")
        except Exception as e:
            print(f"Error in load_all_orders_data: {e}")
            QMessageBox.critical(self, "خطای بارگذاری", f"خطا در بارگذاری لیست سفارشات: {e}")

    def display_order_items_for_selected_order(self):
        """Show selected orders item is order items table & update buttons status"""
        selected_rows = self.orders_table.selectionModel().selectedRows()
        self.order_items_table.setRowCount(0) # clear table

        if not selected_rows:
            self.update_order_action_buttons_state()
            return

        selected_row_index = selected_rows[0].row()
        order_id_item = self.orders_table.item(selected_row_index, 0)

        if order_id_item is None or not order_id_item.text().strip():
            self.update_order_action_buttons_state()
            return
            
        try:
            order_id = int(order_id_item.text())
            print(f"DEBUG: Selected order_id: {order_id} for displaying items.")
        except ValueError:
            print(f"DEBUG: Error converting order_id to int: '{order_id_item.text()}'")
            return

        try:
            items = get_order_items_for_admin(order_id)
            if items is None:
                print(f"DEBUG: get_order_items_for_admin({order_id}) returned None.")
                items = []

            self.order_items_table.setRowCount(len(items))

            for row_index, item_data in enumerate(items):
                # item_data: (food_name, quantity, price_per_item, item_subtotal)
                self.order_items_table.setItem(row_index, 0, QTableWidgetItem(item_data[0])) # food name
                self.order_items_table.setItem(row_index, 1, QTableWidgetItem(str(item_data[1]))) # count
                self.order_items_table.setItem(row_index, 2, QTableWidgetItem(f"{float(item_data[2]):,.0f}")) # price per item
                self.order_items_table.setItem(row_index, 3, QTableWidgetItem(f"{float(item_data[3]):,.0f}")) # items count
            print(f"DEBUG: Items loaded for order_id {order_id}.")
        except Exception as e:
            print(f"Error in display_order_items_for_selected_order: {e}")
            QMessageBox.critical(self, "خطای بارگذاری", f"خطا در بارگذاری آیتم های سفارش: {e}")

        self.update_order_action_buttons_state()

    def handle_update_order_status(self):
        """Update selected order's status"""
        selected_rows = self.orders_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "اخطار", "لطفا یک سفارش را در جدول انتخاب کنید" )
            return
        selected_row_index = selected_rows[0].row()
        order_id_item = self.orders_table.item(selected_row_index, 0)

        if order_id_item is None or not order_id_item.text().strip():
            QMessageBox.critical(self, "اخطار", "شناسه سفارش برای سطر منتخب معتبر نیست")
            return
        try:
            order_id = int(order_id_item.text())
            new_status = self.order_status_combo.currentText()
            print(f"DEBUG: Attempting to update status for order_id: {order_id} to '{new_status}'")
            success = update_order_status_admin(order_id, new_status)
            if success:
                QMessageBox.information(self, "موفقیت", f"وضعیت سفارش {order_id} با موفقیت به '{new_status}' تغییر یافت.")
                self.load_all_orders_data()
                self.order_items_table.setRowCount(0) # clear table
            else:
                QMessageBox.critical(self, "خطا", f"تغییر وضعیت سفارش {order_id} ناموفق بود. لطفاً لاگ‌های برنامه را بررسی کنید یا مطمئن شوید سفارش وجود دارد.")
        except ValueError:
            QMessageBox.critical(self, "خطا", "شناسه سفارش انتخاب شده معتبر نیست (باید یک عدد باشد).")
        except Exception as e:
            QMessageBox.critical(self, "خطای عمومی", f"خطایی در هنگام به‌روزرسانی وضعیت رخ داد: {e}")
            print(f"Error in handle_update_order_status: {e}")

    def handle_calncel_selected_order(self):
        """Cancel selected order"""
        selected_rows = self.orders_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "اخطار", "لطفا یک سفارش را در جدول انتخاب کنید" )
            return
        selected_row_index = selected_rows[0].row()
        order_id_item = self.orders_table.item(selected_row_index, 0)

        if order_id_item is None or not order_id_item.text().strip():
            QMessageBox.critical(self, "اخطار", "شناسه سفارش برای سطر منتخب معتبر نیست")
            return
        try:
            order_id = int(order_id_item.text())
            confirm_message = QMessageBox.question(self, "تایید لغو سفارش", 
                                               f"آیا از لغو سفارش با شناسه {order_id} مطمئن هستید؟\n"
                                               "با این کار، وضعیت سفارش به 'لغو شده توسط مدیر' تغییر کرده،\n"
                                               "موجودی غذاهای سفارش به انبار و مبلغ سفارش به کیف پول مشتری بازگردانده خواهد شد.",
                                               QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.No)
            if confirm_message == QMessageBox.Yes:
                print(f"DEBUG: Attempting to delete order_id: {order_id}")
                success, message = cancel_order_admin(order_id)
                if success:
                    QMessageBox.information(self, "موفقیت", message)
                    self.load_all_orders_data()
                    self.order_items_table.setRowCount(0) 
                else:
                    QMessageBox.critical(self, "خطا", message)
            else:
                QMessageBox.information(self, "لغو شد", "عملیات لغو سفارش لغو شد.")
        except ValueError:
            QMessageBox.critical(self, "خطا", "شناسه سفارش انتخاب شده معتبر نیست (باید یک عدد باشد).")
        except Exception as e:
            QMessageBox.critical(self, "خطای عمومی", f"خطایی در هنگام لغو سفارش رخ داد: {e}")
            print(f"Error in handle_delete_selected_order: {e}")

    def update_order_action_buttons_state(self):
        """Disable / Enable items with orders status"""
        selected_rows = self.orders_table.selectionModel().selectedRows()

        order_selected_and_valid_for_actions = False
        current_status_of_selected_order = ""

        if selected_rows:
            selected_row_index = selected_rows[0].row()
            status_item = self.orders_table.item(selected_row_index, 4) # index 4 -> status
            if status_item:
                current_status_of_selected_order = status_item.text()

                if not current_status_of_selected_order.startswith("لغو شده") and \
                current_status_of_selected_order != "تحویل داده شده":
                    order_selected_and_valid_for_actions = True

                # set combo box 
                self.order_status_combo.setCurrentText(current_status_of_selected_order)

        self.order_status_combo.setEnabled(order_selected_and_valid_for_actions)
        self.update_status_button.setEnabled(order_selected_and_valid_for_actions)
        self.cancel_order_button.setEnabled(order_selected_and_valid_for_actions)
        self.admin_edit_order_details_button.setEnabled(order_selected_and_valid_for_actions)

        if not selected_rows: 
            self.order_items_table.setRowCount(0)
            self.order_status_combo.setCurrentIndex(-1) # reset combo box

    def show_admin_add_order_dialog(self):
        """show add orders by admin dialog"""
        dialog = AdminAddOrderDialog(parent=self)
        if dialog.exec():
            order_data = dialog.get_order_data()
            if order_data:
                success, new_order_id, message = admin_create_order(
                    user_id=order_data['user_id'],
                    order_items_details=order_data['order_items_details'],
                    total_price=order_data['total_price'],
                    initial_status=order_data['initial_status']
                )
                if success:
                    QMessageBox.information(self, "موفقیت", f"{message}\nشناسه سفارش جدید: {new_order_id}")
                    self.load_all_orders_data()
                else:
                    QMessageBox.critical(self, "خطا در ثبت سفارش", message)
            else:
                QMessageBox.warning(self, "خطا", "اطلاعات سفارش برای ثبت ناقص است.")

    def handle_edit_order_details_placeholder(self):
        selected_rows = self.orders_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "اخطار", "لطفاً ابتدا یک سفارش را از جدول انتخاب کنید.")
            return
        QMessageBox.information(self, "در دست ساخت", 
                                "قابلیت ویرایش جزئیات آیتم‌های این سفارش در حال حاضر در دست ساخت است و در نسخه‌های آینده اضافه خواهد شد.")
    
    # Slots for users
    def load_users_data(self):
        users = get_all_users()
        self.user_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user[0])))
            self.user_table.setItem(row, 1, QTableWidgetItem(user[1]))
            self.user_table.setItem(row, 2, QTableWidgetItem(user[2]))
            self.user_table.setItem(row, 3, QTableWidgetItem(user[3]))
            self.user_table.setItem(row, 4, QTableWidgetItem(str(user[4])))
            self.user_table.setItem(row, 5, QTableWidgetItem(user[5]))

    def show_add_user_dialog(self):
        dialog = UserDialog()
        if dialog.exec():
            data = dialog.get_data()
            add_user(data['username'], data['password'], data['full_name'], data['wallet_balance'], 'customer')
            self.load_users_data()

    # Slot for log out
    def handle_logout(self):
        reply = QMessageBox.question(self, "خروج از حساب", 
                                 "آیا مطمئن هستید که می‌خواهید از حساب خود خارج شوید؟",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.logout_request = True
            self.close()


if __name__ == '__main__':
    print("You cant run this file currently, run main.py")