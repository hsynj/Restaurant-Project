import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.login_dialog import *
from ui.main_admin_window import *
from ui.seller_window import *
from ui.customer_window import *
from ui.auth_page import AuthPage

FONT_NAME = 'Estedad'
if __name__ == "__main__":

    app = QApplication(sys.argv)
    QApplication.setLayoutDirection(Qt.RightToLeft)
    app.setFont(QFont(FONT_NAME))

    with open('assets/stylesheet.qss', 'r', encoding='utf-8') as f:
        stylesheet = f.read()
    app.setStyleSheet(stylesheet)

    while True:
        auth_page = AuthPage()
        auth_result = auth_page.exec()
        main_app_window = None
        user_data_from_login = None

        if auth_result == QDialog.Accepted:
            user_data_from_login = auth_page.get_logged_in_user()

            if user_data_from_login:
                if user_data_from_login[5] == "admin":
                    main_app_window = MainAdminWindow(user_data=user_data_from_login)
                elif user_data_from_login[5] == 'seller':
                    main_app_window = SellerWindow(user_data=user_data_from_login)
                else:
                    main_app_window = CustomerWindow(user_data=user_data_from_login)
            else:
                print("AuthPage accepted but no user data returned. Exiting.")
                sys.exit(0)
        else:
            print("Authentication cancelled by user. Exiting.")
            sys.exit(0)
        
        if main_app_window:
            main_app_window.show()
            app.exec()
            if main_app_window.logout_request:
                main_app_window.deleteLater()
                continue
            else: # close by X
                print("Main application window closed by user. Exiting.")
                break
        else:
            print("No main application window to show. Exiting.")
            break

    sys.exit(0)