from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox, QDialogButtonBox, QFrame
)
from PySide6.QtCore import Qt
from database.db_handler import check_user_login, add_user 

class AuthPage(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("ورود یا ثبت نام کاربر")
        self.setMinimumWidth(900)
        self.setMinimumHeight(350)

        self.logged_in_user_data = None
        self.operation_type = None
        layout = QVBoxLayout(self)
        main_page_layout = QHBoxLayout()

        # login - right panel
        login_group = QWidget()
        login_layout = QVBoxLayout(login_group)
        login_layout.setAlignment(Qt.AlignTop)
        login_title = QLabel("ورود به حساب کاربری")
        login_title.setAlignment(Qt.AlignCenter)
        login_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        login_layout.addWidget(login_title)

        login_form_layout = QFormLayout()
        self.login_username_input = QLineEdit()
        self.login_password_input = QLineEdit()
        self.login_password_input.setEchoMode(QLineEdit.Password)
        login_form_layout.addRow("نام کاربری:", self.login_username_input)
        login_form_layout.addRow("رمزعبور:", self.login_password_input)
        login_layout.addLayout(login_form_layout)
        self.login_button = QPushButton("ورود")

        login_layout.addWidget(self.login_button)
        login_layout.addStretch()

        # sign up - left panel
        register_group = QWidget()
        register_layout = QVBoxLayout(register_group)
        register_layout.setAlignment(Qt.AlignTop)
        register_title = QLabel("ایجاد حساب کاربری جدید")
        register_title.setAlignment(Qt.AlignCenter)
        register_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        register_layout.addWidget(register_title)

        register_form_layout = QFormLayout()
        self.register_fullname_input = QLineEdit()
        self.register_username_input = QLineEdit()
        self.register_username_input.setPlaceholderText("حداقل ۴ کاراکتر")
        self.register_password_input = QLineEdit()
        self.register_password_input.setEchoMode(QLineEdit.Password)
        self.register_password_input.setPlaceholderText("حداقل ۶ کاراکتر")
        self.register_confirm_password_input = QLineEdit()
        self.register_confirm_password_input.setEchoMode(QLineEdit.Password)

        register_form_layout.addRow("نام و نام خانوادگی:", self.register_fullname_input)
        register_form_layout.addRow("نام کاربری:", self.register_username_input)
        register_form_layout.addRow("رمز عبور:", self.register_password_input)
        register_form_layout.addRow("تکرار رمز عبور:", self.register_confirm_password_input)
        register_layout.addLayout(register_form_layout)
        self.register_button = QPushButton("ثبت نام")
        register_layout.addWidget(self.register_button)
        login_layout.addStretch()

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        main_page_layout.addWidget(register_group, 1)
        main_page_layout.addWidget(line)
        main_page_layout.addWidget(login_group, 1)


        # guesst login
        guest_layout = QHBoxLayout()
        guest_layout.addStretch()
        self.guest_button = QPushButton("ورود به عنوان مهمان")
        guest_layout.addWidget(self.guest_button)
        guest_layout.addStretch()

        layout.addLayout(main_page_layout)
        layout.addLayout(guest_layout)

        # set signals
        self.login_button.clicked.connect(self._handle_login_attempt)
        self.register_button.clicked.connect(self._handle_registration_attempt)
        self.guest_button.clicked.connect(self._handle_guest_access)
    
    def _handle_login_attempt(self):
        username = self.login_username_input.text().strip()
        password = self.login_password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "خطای ورود", "نام کاربری و رمز عبور نمی‌توانند خالی باشند.")
            return
        
        user_data = check_user_login(username, password)

        if user_data:
            self.logged_in_user_data = user_data
            self.operation_type = "login_success"
            self.accept()
        else:
            QMessageBox.warning(self, "خطای ورود", "نام کاربری یا رمز عبور اشتباه است.")
            self.login_password_input.clear()
    
    def _handle_registration_attempt(self):
        username = self.register_username_input.text().strip()
        password = self.register_password_input.text().strip()
        confirm_password = self.register_confirm_password_input.text().strip()
        full_name = self.register_fullname_input.text().strip()

        if not username or len(username) < 4:
            QMessageBox.warning(self, "خطای ثبت نام", "نام کاربری باید حداقل ۴ کاراکتر باشد.")
            return
        if not password or len(password) < 6:
            QMessageBox.warning(self, "خطای ثبت نام", "رمز عبور باید حداقل ۶ کاراکتر باشد.")
            return
        if password != confirm_password:
            QMessageBox.warning(self, "خطای ثبت نام", "رمز عبور و تکرار آن یکسان نیستند.")
            return
        if not full_name:
            QMessageBox.warning(self, "خطای ثبت نام", "وارد کردن نام کامل الزامی است.")
            return
        
        success, message = add_user(username, password, full_name)

        if success:
            QMessageBox.information(self, "ثبت نام موفق", message + "\nاکنون می‌توانید با نام کاربری خود وارد شوید.")
            self.register_username_input.clear()
            self.register_password_input.clear()
            self.register_confirm_password_input.clear()
            self.register_fullname_input.clear()
            self.login_username_input.setText(username)
            self.login_password_input.setText(password)
        else:
            QMessageBox.warning(self, "خطا در ثبت نام", message)

    def get_logged_in_user(self):
        if self.result() == QDialog.Accepted and self.operation_type == "login_success":
            return self.logged_in_user_data
        return None
    
    def _handle_guest_access(self):
        QMessageBox.information(self, "به زوری", "این قابلیت در نسخه های بعد اضافه خواهد شد")

if __name__ == '__main__':
    print("You cant run this file currently, run main.py")