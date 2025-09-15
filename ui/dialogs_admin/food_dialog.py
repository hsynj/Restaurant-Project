from PySide6.QtWidgets import QVBoxLayout, QDialog, QLineEdit, QFormLayout, QDialogButtonBox

class FoodDialog(QDialog):
    def __init__(self, food_data=None):
        super().__init__()

        self.is_edit_mode = food_data is not None # T & F
        self.food_id = food_data[0] if self.is_edit_mode else None
        window_title = "تغییر اطلاعات غذا" if self.is_edit_mode else "اضافه کردن غذا جدید"
        self.setWindowTitle(window_title)

        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.price_input = QLineEdit()
        self.inventory_input = QLineEdit()
        self.image_path = QLineEdit()
        
        form_layout.addRow("نام:", self.name_input)
        form_layout.addRow("قیمت:", self.price_input)
        form_layout.addRow("موجودی:", self.inventory_input)
        form_layout.addRow("تصویر", self.image_path)


        # if in edit mode
        if self.is_edit_mode:
            self.name_input.setText(food_data[1])
            self.price_input.setText(str(food_data[2]))
            self.inventory_input.setText(str(food_data[3]))
            self.image_path.setText(food_data[4])


        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # create main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)


    def get_data(self):
        """Return the information entered by the user."""
        return {
        "name": self.name_input.text(),
        "price": float(self.price_input.text()),
        "inventory": int(self.inventory_input.text()),
        "image_path": self.image_path.text()
        }

if __name__ == '__main__':
    print("You cant run this file currently, run main.py")