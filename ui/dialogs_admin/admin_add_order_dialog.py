from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox, QLabel, QSpinBox,
                               QPushButton, QTableWidget, QHeaderView, QDialogButtonBox, QMessageBox, QTableWidgetItem)
from database.db_handler import get_available_foods, get_all_users

class AdminAddOrderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("ثبت سفارش جدید")
        self.setMinimumWidth(600)

        self.temporary_order_items = {} # {food_id: {'name': name, 'price': price, 'quantity': qty}}
        main_layout = QVBoxLayout()

        # 'select user' section
        form_layout = QFormLayout()
        self.user_select_combo = QComboBox()
        form_layout.addRow("انتخاب مشتری:", self.user_select_combo)
        main_layout.addLayout(form_layout)

        # 'add food' section
        add_item_layout = QHBoxLayout()
        self.food_select_combo = QComboBox()
        add_item_layout.addWidget(QLabel("غذا:"))
        add_item_layout.addWidget(self.food_select_combo, 1)

        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setMinimum(1)
        self.quantity_spinbox.setValue(1)
        add_item_layout.addWidget(QLabel("تعداد:"))
        add_item_layout.addWidget(self.quantity_spinbox)

        self.add_food_to_order_button = QPushButton("افزودن به سفارش")
        add_item_layout.addWidget(self.add_food_to_order_button)
        main_layout.addLayout(add_item_layout)

        # show items table
        main_layout.addWidget(QLabel("آیتم‌های سفارش فعلی:"))
        self.current_order_items_table = QTableWidget()
        self.current_order_items_table.setColumnCount(4)
        self.current_order_items_table.setHorizontalHeaderLabels(["نام غذا", "تعداد", "قیمت واحد", "جمع"])
        self.current_order_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.current_order_items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.current_order_items_table)

        # show total price & first status
        bottom_form_layout = QFormLayout()
        self.dialog_total_price_label = QLabel("0 تومان")
        bottom_form_layout.addRow("مبلغ کل سفارش:", self.dialog_total_price_label)

        self.initial_status_combo = QComboBox()
        self.initial_status_combo.addItems(["ثبت توسط مدیر / فروشنده", "در حال آماده‌سازی", "تکمیل شده"])
        bottom_form_layout.addRow("وضعیت اولیه سفارش:", self.initial_status_combo)
        main_layout.addLayout(bottom_form_layout)

        # buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        main_layout.addWidget(self.button_box)
        # set signals
        self.add_food_to_order_button.clicked.connect(self._add_selected_food_to_temporary_order)
        self.button_box.accepted.connect(self.accept_dialog_with_validation)
        self.button_box.rejected.connect(self.reject)

        self.setLayout(main_layout)
        
        self._populate_user_combo()
        self._populate_food_combo()

    def _populate_user_combo(self):
        """Read users from database and show in combo box."""
        self.user_select_combo.clear()
        users = get_all_users()
        if users:
            for user in users:
                # user: (id, username, password, full_name, wallet_balance, role)
                self.user_select_combo.addItem(f"{user[3]} (ID: {user[0]}, موجودی: {user[4]:,.0f})", userData=user[0]) # userData برای ذخیره ID کاربر
    
    def _populate_food_combo(self):
        """Get availble foods from db and show in combo box"""
        self.food_select_combo.clear()
        foods = get_available_foods()
        if foods:
            for food in foods:
                # food: (id, name, price, inventory, image_path)
                self.food_select_combo.addItem(f"{food[1]} - {food[2]:,.0f} تومان (موجودی: {food[3]})", userData=food) # userData برای ذخیره کل اطلاعات غذا

    def _add_selected_food_to_temporary_order(self):
        """add selected food in combo box to temp items list"""
        selected_food_index = self.food_select_combo.currentIndex()
        if selected_food_index == -1:
            QMessageBox.warning(self, "اخطار", "لطفاً یک غذا را انتخاب کنید.")
            return
        
        food_data_tuple = self.food_select_combo.itemData(selected_food_index)
        # food_data_tuple: (id, name, price, inventory, image_path)
        food_id = food_data_tuple[0]
        food_name = food_data_tuple[1]
        food_price = float(food_data_tuple[2])
        quantity_to_add = self.quantity_spinbox.value()

        if food_id in self.temporary_order_items:
            self.temporary_order_items[food_id]['quantity'] += quantity_to_add
        else:
            self.temporary_order_items[food_id] = {
                'name': food_name,
                'price': food_price,
                'quantity': quantity_to_add,
                'food_id': food_id
            }
        self._update_temporary_order_display()

    def _update_temporary_order_display(self):
        """update temp items table"""
        self.current_order_items_table.setRowCount(0) # clear table
        total_price = 0
        
        for row, item_data in enumerate(self.temporary_order_items.values()):
            self.current_order_items_table.insertRow(row)
            self.current_order_items_table.setItem(row, 0, QTableWidgetItem(item_data['name']))
            self.current_order_items_table.setItem(row, 1, QTableWidgetItem(str(item_data['quantity'])))
            self.current_order_items_table.setItem(row, 2, QTableWidgetItem(f"{item_data['price']:,.0f}"))
            subtotal = item_data['quantity'] * item_data['price']
            self.current_order_items_table.setItem(row, 3, QTableWidgetItem(f"{subtotal:,.0f}"))
            total_price += subtotal
        
        self.dialog_total_price_label.setText(f"{total_price:,.0f} تومان")

    def accept_dialog_with_validation(self):
        """validation befor accept"""
        if self.user_select_combo.currentIndex() == -1:
            QMessageBox.warning(self, "خطا", "لطفاً یک مشتری را انتخاب کنید.")
            return
        if not self.temporary_order_items:
            QMessageBox.warning(self, "خطا", "حداقل یک آیتم باید به سفارش اضافه شود.")
            return
        self.accept()

    def get_order_data(self):
        """get orders data for send to database"""
        if self.user_select_combo.currentIndex() == -1: return None

        user_id = self.user_select_combo.itemData(self.user_select_combo.currentIndex())
        
        # [{'food_id': id, 'quantity': qty, 'price_at_order': price}, ...]
        order_items_list = []
        for item_id, details in self.temporary_order_items.items():
            order_items_list.append({
                'food_id': item_id, 
                'quantity': details['quantity'],
                'price_at_order': details['price']
            })

        total_price_str = self.dialog_total_price_label.text().replace(" تومان", "").replace(",", "")
        total_price = float(total_price_str)
        initial_status = self.initial_status_combo.currentText()
        
        return {
            "user_id": user_id,
            "order_items_details": order_items_list,
            "total_price": total_price,
            "initial_status": initial_status
        }

if __name__ == '__main__':

    print("You cant run this file currently, run main.py")
