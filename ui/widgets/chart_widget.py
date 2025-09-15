import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

try:
    plt.rcParams['font.family'] = 'IRAN' # یا هر فونت فارسی دیگری که دارید مثل 'Tahoma'
    plt.rcParams['axes.unicode_minus'] = False # برای نمایش صحیح علامت منفی
except Exception as e:
    print(f"Could not set Persian font for Matplotlib: {e}")

class MatplotlibChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_bar_chart(self, x_labels, y_values, title="Nemoodar", x_axis_label="x", y_axis_label="y"):
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            bars = ax.bar(x_labels, y_values, color='#3498db')
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05 * max(y_values) if y_values else 0, # تنظیم فاصله متن از بالای میله
                        f'{yval:,.0f}', ha='center', va='bottom', fontsize=9)
                
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.set_xlabel(x_axis_label, fontsize=10)
            ax.set_ylabel(y_axis_label, fontsize=10)

            if x_labels and isinstance(x_labels[0], str) and max(len(label) for label in x_labels) > 5:
                 ax.tick_params(axis='x', rotation=45, labelsize=8) # تغییرات اینجا برای چرخش بهتر
                 self.figure.subplots_adjust(bottom=0.25) # ایجاد فضای بیشتر برای لیبل های چرخانده شده
            else:
                 ax.tick_params(axis='x', labelsize=8)
                 self.figure.subplots_adjust(bottom=0.15)
            
            ax.grid(True, linestyle='--', alpha=0.7)
            self.canvas.draw()

        except Exception as e:
            print(f"Error plotting bar chart: {e}")
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "خطا در رسم نمودار", horizontalalignment='center', verticalalignment='center')
            self.canvas.draw()
            
    def clear_chart(self):
        """Clear chart."""
        self.figure.clear()
        self.canvas.draw()