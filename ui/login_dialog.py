from PySide6.QtWidgets import QVBoxLayout, QDialog, QLineEdit, QFormLayout, QDialogButtonBox

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ورود به سیستم")
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password) # Hide password

        form = QFormLayout()
        form.addRow("نام کاربری:", self.username_input)
        form.addRow("رمز عبور:", self.password_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()

if __name__ == '__main__':
    print("You cant run this file currently, run main.py")