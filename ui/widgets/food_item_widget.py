from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt, Signal, QSize
import sys

class FoodItemWidget(QWidget):
    clicked = Signal(int)
    def __init__(self, food_id, name, price, image_path, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.food_id = food_id
        self.food_name = name
        self.food_price = price

        self.setMinimumSize(180, 220)
        self.setMaximumSize(220, 280)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        # show food picture
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.image_label.setText("عکس موجود نیست")
            self.image_label.setFixedSize(150, 150)
            self.image_label.setStyleSheet("border: 1px solid gray; background-color: #eee;")
        else:
            self.image_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(self.image_label)
        # show food name
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setFont(QFont("Vazirmatn", 11, QFont.Bold))
        self.name_label.setWordWrap(True) # chand khat..
        layout.addWidget(self.name_label)
        # show food price
        self.price_label = QLabel(f"{price:,.0f} تومان")
        self.price_label.setAlignment(Qt.AlignCenter)
        self.price_label.setFont(QFont("Vazirmatn", 10))
        self.price_label.setStyleSheet("color: green;")
        layout.addWidget(self.price_label)
        self.setLayout(layout)

        self.setStyleSheet("""
            FoodItemWidget {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: black;
                margin: 5px;
            }
            FoodItemWidget:hover {
                background-color: #f0f0f0; /* تغییر رنگ پس زمینه با رفتن موس روی آن */
            }
        """)
    def mouseDoubleClickEvent(self, event):
        """وقتی روی این ویجت دوبار کلیک شد، سیگنال clicked را با شناسه غذا منتشر می کند."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.food_id)
        super().mouseDoubleClickEvent(event) # رویداد را به کلاس والد ارسال می کنیم

if __name__ == '__main__':
    print("You cant run this file currently, run main.py")