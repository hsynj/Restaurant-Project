from PySide6.QtWidgets import QVBoxLayout, QDialog, QLineEdit, QFormLayout, QDialogButtonBox

class UserDialog(QDialog):
    def __init__(self, user_data=None):
        super().__init__()
        self.is_edit_mode = user_data is not None # T & F
        self.user_id = user_data[0] if self.is_edit_mode else None
        
        window_title = "تغییر اطلاعات کاربر" if self.is_edit_mode else "اضافه کردن کاربر جدید"
        self.setWindowTitle(window_title)

        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.full_name_input = QLineEdit()
        self.wallet_input = QLineEdit()
        self.role_input = QLineEdit()

        form_layout.addRow("نام کاربری:", self.username_input)
        form_layout.addRow("رمز عبور:", self.password_input)
        form_layout.addRow("نام و نام خانوادگی", self.full_name_input)
        form_layout.addRow("موجودی کیف پول:", self.wallet_input)
        form_layout.addRow("نقش:", self.role_input)


        if self.is_edit_mode:
            self.username_input.setText(user_data[1])
            self.password_input.setText(user_data[2])
            self.full_name_input.setText(user_data[3])
            self.wallet_input.setText(str(user_data[4]))
            self.role_input.setText(user_data[5])
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.rejected)
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def get_data(self):
        return {
            "username": self.username_input.text(),
            "password": self.password_input.text(),
            "full_name": self.full_name_input.text(),
            "wallet_balance": float(self.wallet_input.text()),
            "role": self.role_input.text()
        }

if __name__ == '__main__':
    print("You cant run this file currently, run main.py")