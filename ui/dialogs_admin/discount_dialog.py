from PySide6.QtWidgets import (QDialog, QLineEdit, QComboBox, QCheckBox, QDateTimeEdit,
                               QFormLayout,QDialogButtonBox, QVBoxLayout, QMessageBox)
from PySide6.QtCore import QDateTime

class DiscountDialog(QDialog):
    def __init__(self, discount_data=None, parent=None):
        super().__init__(parent)
        self.is_edit_mode = discount_data is not None # T & F
        self.discount_id = discount_data[0] if self.is_edit_mode else None
        
        window_title = "ویرایش کد تخفیف" if self.is_edit_mode else "اضافه کردن کد تخفیف جدید"
        self.setWindowTitle(window_title)
        self.setMinimumWidth(450)

        # Create widgets
        self.code_input = QLineEdit()
        self.discount_type_input = QComboBox()
        self.discount_type_input.addItems(['percentage', 'fixed_amount'])
        self.value_input = QLineEdit()
        self.min_purchase_amount_input = QLineEdit()
        self.min_purchase_amount_input.setPlaceholderText("0.0 (اختیاری)")

        self.is_active_input = QCheckBox("فعال")
        self.is_active_input.setCheckable(True)

        self.usage_limit_input = QLineEdit()
        self.usage_limit_input.setPlaceholderText("خالی برای نامحدود")

        self.valid_from_input = QDateTimeEdit()
        self.valid_from_input.setDateTime(QDateTime.currentDateTime())
        self.valid_from_input.setCalendarPopup(True)
        self.valid_from_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.valid_from_input.setMinimumDateTime(QDateTime(2000, 1, 1, 0, 0, 0))

        self.valid_until_input = QDateTimeEdit()
        self.valid_until_input.setDateTime(QDateTime.currentDateTime().addYears(1))
        self.valid_until_input.setCalendarPopup(True)
        self.valid_until_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.valid_until_input.setMinimumDateTime(QDateTime(2000, 1, 1, 0, 0, 0))

        # form
        form_layout = QFormLayout()
        form_layout.addRow("کد تخفیف", self.code_input)
        form_layout.addRow("نوع تخفیف", self.discount_type_input)
        form_layout.addRow("مقدار (درصد یا مبلغ)", self.value_input)
        form_layout.addRow("حداقل مبلغ خرید", self.min_purchase_amount_input)
        form_layout.addRow("محدودیت تعداد استفاده", self.usage_limit_input)
        form_layout.addRow("تاریخ شروع اعتبار", self.valid_from_input)
        form_layout.addRow("تاریخ پایان اعتبار", self.valid_until_input)
        form_layout.addRow(self.is_active_input)


        if self.is_edit_mode and discount_data:
            self.code_input.setText(discount_data[1])
            self.discount_type_input.setCurrentText(discount_data[2])
            self.value_input.setText(str(discount_data[3]))
            self.min_purchase_amount_input.setText(str(discount_data[4]))
            self.is_active_input.setChecked(bool(discount_data[5]))
            self.usage_limit_input.setText(str(discount_data[6]) if discount_data[6] is not None else "")
            
            if discount_data[8]: # valid_from
                self.valid_from_input.setDateTime(QDateTime.fromString(discount_data[8], "yyyy-MM-dd HH:mm:ss"))
            else:
                self.valid_from_input.setDateTime(QDateTime())
            if discount_data[9]: # valid_until
                self.valid_until_input.setDateTime(QDateTime.fromString(discount_data[9], "yyyy-MM-dd HH:mm:ss"))
            else:
                self.valid_until_input.setDateTime(QDateTime())

        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_dialog)
        button_box.rejected.connect(self.rejected)
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def accept_dialog(self):
        if not self.valid_from_input.dateTime().isNull() and \
           not self.valid_until_input.dateTime().isNull() and \
           self.valid_from_input.dateTime() >= self.valid_until_input.dateTime():
            QMessageBox.warning(self, "خطای تاریخ", "تاریخ پایان اعتبار باید بعد از تاریخ شروع اعتبار باشد.")
            return

        if not self.code_input.text().strip():
            QMessageBox.warning(self, "خطا", "کد تخفیف نمیتواند خالی باشد")
            return

        try:
            float(self.value_input.text())
        except ValueError:
            QMessageBox.warning(self, "خطا", "مقدار تخفیف باید یک عدد باشد.")
            return

        if self.min_purchase_amount_input.text().strip():
            try:
                float(self.min_purchase_amount_input.text())
            except ValueError:
                QMessageBox.warning(self, "خطا", "حداقل مبلغ خرید باید یک عدد باشد یا خالی بماند.")
                return

        if self.usage_limit_input.text().strip():
            try:
                int(self.usage_limit_input.text())
            except ValueError:
                QMessageBox.warning(self, "خطا", "محدودیت تعداد استفاده باید یک عدد صحیح باشد یا خالی بماند.")
                return
        self.accept()

    def get_data(self):
        code = self.code_input.text().strip()
        discount_type = self.discount_type_input.currentText()
        value = float(self.value_input.text()) if self.value_input.text().strip() else 0.0
        min_purchase_str = self.min_purchase_amount_input.text().strip()
        min_purchase = float(min_purchase_str) if min_purchase_str else 0.0
        is_active = 1 if self.is_active_input.isChecked() else 0
        usage_limit_str = self.usage_limit_input.text().strip()
        usage_limit = int(usage_limit_str) if usage_limit_str else None

        valid_from_dt = self.valid_from_input.dateTime()
        valid_from_str = valid_from_dt.toString("yyyy-MM-dd HH:mm:ss") if not valid_from_dt.isNull() else None
        
        valid_until_dt = self.valid_until_input.dateTime()
        valid_until_str = valid_until_dt.toString("yyyy-MM-dd HH:mm:ss") if not valid_until_dt.isNull() else None
        
        return {
            "code": code,
            "discount_type": discount_type,
            "value": value,
            "min_purchase_amount": min_purchase,
            "is_active": is_active,
            "usage_limit": usage_limit,
            "valid_from": valid_from_str,
            "valid_until": valid_until_str,
            "id": self.discount_id
        }

if __name__ == '__main__':
    print("You cant run this file currently, run main.py")