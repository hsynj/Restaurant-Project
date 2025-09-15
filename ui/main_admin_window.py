from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QHeaderView, QPushButton, QTableWidgetItem, QMessageBox, QLabel, QGroupBox)
from PySide6.QtCore import Qt

from database.db_handler import *
from ui.dialogs_admin.discount_dialog import *
from ui.dialogs_admin.food_dialog import *
from ui.dialogs_admin.user_dialog import *
from ui.dialogs_admin.admin_add_order_dialog import *
from ui.widgets.chart_widget import *

class MainAdminWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("سیستم مدیریت رستوران - پنل مدیریت")
        self.resize(800, 600)

        # tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # create tabs
        self.setup_dashboard_tab()
        self.setup_food_management_tab()
        self.setup_user_management_tab()
        self.setup_discount_management_tab()
        self.setup_order_management_tab()
        self.setup_reports_tab()

    def setup_dashboard_tab(self):
        self.dashboard_page = QWidget()
        dashboard_main_layout = QVBoxLayout(self.dashboard_page)
        top_row_layout = QHBoxLayout()
        down_row_layout = QHBoxLayout()

        # admin welcome label
        self.welcome_label = QLabel(f"جناب آقای {self.user_data[3]} خوش آمدید")
        self.logout_button_admin = QPushButton("خروج از حساب کاربری")
        admin_status_layout = QHBoxLayout()
        admin_status_layout.addWidget(self.welcome_label)
        admin_status_layout.addWidget(self.logout_button_admin)
        admin_status_layout.addStretch()
        dashboard_main_layout.addLayout(admin_status_layout, 1)
        self.logout_button_admin.clicked.connect(self.handle_logout)
        self.logout_request = False

        dashboard_main_layout.addLayout(top_row_layout, 1)
        dashboard_main_layout.addLayout(down_row_layout, 1)

        # 3 top foods
        top_foods = QGroupBox("3 غذای پر فروش")
        top_foods_layout = QVBoxLayout()
        self.top_food_1_label = QLabel("1. - ")
        self.top_food_2_label = QLabel("2. - ")
        self.top_food_3_label = QLabel("3. - ")
        top_foods_layout.addWidget(self.top_food_1_label)
        top_foods_layout.addWidget(self.top_food_2_label)
        top_foods_layout.addWidget(self.top_food_3_label)
        top_foods_layout.addStretch()
        self.foods_report_more_button = QPushButton("مشاهده گزارش کامل غذاها..")
        self.foods_report_more_button.clicked.connect(self._goto_foods_reports_tab)
        top_foods_layout.addWidget(self.foods_report_more_button)
        top_foods.setLayout(top_foods_layout)
        top_row_layout.addWidget(top_foods)

        # 3 top users
        top_users = QGroupBox("3 کاربر برتر")
        top_users_layout = QVBoxLayout()
        self.top_user_1_label = QLabel("1. - ")
        self.top_user_2_label = QLabel("2. - ")
        self.top_user_3_label = QLabel("3. - ")
        top_users_layout.addWidget(self.top_user_1_label)
        top_users_layout.addWidget(self.top_user_2_label)
        top_users_layout.addWidget(self.top_user_3_label)
        top_users_layout.addStretch()
        self.users_report_more_button = QPushButton("مشاهده گزارش کامل کاربران..")
        self.users_report_more_button.clicked.connect(self._goto_users_reports_tab)
        top_users_layout.addWidget(self.users_report_more_button)
        top_users.setLayout(top_users_layout)
        top_row_layout.addWidget(top_users)

        # summary sales
        sales_summary = QGroupBox("خلاصه فروش و سفارشات")
        sales_summary_layout = QVBoxLayout()
        self.sales_today_label = QLabel("سفارشات امروز: - | درآمد امروز: - تومان")
        self.sales_this_week_label = QLabel("سفارشات هفته جاری: - | درآمد هفته جاری: - تومان")
        sales_summary_layout.addWidget(self.sales_today_label)
        sales_summary_layout.addWidget(self.sales_this_week_label)
        sales_summary.setLayout(sales_summary_layout)
        down_row_layout.addWidget(sales_summary)
        # low qunatity foods
        low_stock = QGroupBox("غذاهای درحال اتمام")
        self.low_stock_layout = QVBoxLayout()
        low_stock.setLayout(self.low_stock_layout)
        down_row_layout.addWidget(low_stock)
        # general static
        general_static = QGroupBox("آمار کلی رستوان")
        general_static_layout = QVBoxLayout()
        self.active_users = QLabel("تعداد کل مشتریان فعال: -")
        self.active_foods = QLabel("تعداد کل غذاهای منو: -")
        general_static_layout.addWidget(self.active_users)
        general_static_layout.addWidget(self.active_foods)
        general_static.setLayout(general_static_layout)
        down_row_layout.addWidget(general_static)

        self.tabs.addTab(self.dashboard_page, "داشبورد")
        self._load_dashboard_data()

    def setup_food_management_tab(self):
        """Control Foods"""
        page = QWidget()
        layout = QVBoxLayout(page)

        self.food_table = QTableWidget()
        self.food_table.setColumnCount(5)
        self.food_table.setHorizontalHeaderLabels(["ID", "نام", "قیمت", "موجودی", "تصویر"])
        # Full width tables cloumn
        self.food_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Select full row
        self.food_table.setSelectionBehavior(QTableWidget.SelectRows)
        # Not edit triggers
        self.food_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.add_food_button = QPushButton("افزدون غذا")
        self.edit_food_button = QPushButton("تغیر غذای انتخاب شده")
        self.delete_food_button = QPushButton("حذف غذای انتخاب شده")


        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_food_button)
        button_layout.addWidget(self.edit_food_button)
        button_layout.addWidget(self.delete_food_button)
        
        layout.addWidget(self.food_table)
        layout.addLayout(button_layout)

        # set signals
        self.add_food_button.clicked.connect(self.show_add_food_dialog)
        self.edit_food_button.clicked.connect(self.show_edit_food_dialog)
        self.delete_food_button.clicked.connect(self.delete_selected_food_dialog)

        self.tabs.addTab(page, "مدیریت غذاها")
        self.food_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # load data
        self.load_foods_data()

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


        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_user_button)
        button_layout.addWidget(self.edit_user_button)
        button_layout.addWidget(self.delete_user_button)
        
        layout.addWidget(self.user_table)
        layout.addLayout(button_layout)

        # set signals
        self.add_user_button.clicked.connect(self.show_add_user_dialog)
        self.edit_user_button.clicked.connect(self.show_edit_user_dialog)
        self.delete_user_button.clicked.connect(self.delete_selected_user)

        self.tabs.addTab(page, "مدیریت کاربران")
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # load data
        self.load_users_data()

    def setup_discount_management_tab(self):
        """Control discounts"""
        page = QWidget()
        layout = QVBoxLayout()

        self.discount_table = QTableWidget()
        self.discount_table.setColumnCount(10)
        self.discount_table.setHorizontalHeaderLabels(['ID', 'کد', 'تایپ', 'مقدار', 'حداقل مقدار خرید', 'وضعیت', 'محدودیت استفاده', 'تعداد استفاده', 'از', 'تا'])
        # Full width tables cloumn
        self.discount_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Select full row
        self.discount_table.setSelectionBehavior(QTableWidget.SelectRows)
        # Not edit triggers
        self.discount_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # Buttons
        self.add_discount_btn = QPushButton("افزدون کد تخفیف")
        self.edit_discount_btn = QPushButton("ویرایش کد تخفیف")
        self.delete_discount_btn = QPushButton("حذف کد تخفیف")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_discount_btn)
        button_layout.addWidget(self.edit_discount_btn)
        button_layout.addWidget(self.delete_discount_btn)
        layout.addWidget(self.discount_table)
        layout.addLayout(button_layout)
        # Set buttons signal
        self.add_discount_btn.clicked.connect(self.show_add_discount_dialog)
        self.edit_discount_btn.clicked.connect(self.show_edit_discount_dialog)
        self.delete_discount_btn.clicked.connect(self.delete_selected_discount_dialog)
        # Tabs
        page.setLayout(layout)
        self.tabs.addTab(page, "مدیریت کد تخفیف ها")
        # load data
        self.load_discount_data()

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

    def setup_reports_tab(self):
        self.reports_page = QWidget()
        reports_main_layout = QVBoxLayout(self.reports_page)
        self.report_sub_tabs = QTabWidget()
        reports_main_layout.addWidget(self.report_sub_tabs)
        self.food_sales_report_page = QWidget()
        food_sales_layout = QVBoxLayout(self.food_sales_report_page)
        filter_layout = QHBoxLayout()
        # select food combo box
        filter_layout.addWidget(QLabel("انتخاب غذا:"))
        self.report_food_select_combo = QComboBox()
        filter_layout.addWidget(self.report_food_select_combo)
        self._populate_report_food_combo()
        # select time
        filter_layout.addWidget(QLabel("انتخاب غذا:"))
        self.report_time_period_combo = QComboBox()
        self.report_time_period_combo.addItem("کل فروش ها", userData="all_time")
        self.report_time_period_combo.addItem("امروز", userData="today")
        self.report_time_period_combo.addItem("7 روز گذشته", userData="last_7_days")
        self.report_time_period_combo.addItem("ماه گذشته", userData="this_month")
        filter_layout.addWidget(self.report_time_period_combo)

        self.generate_food_sales_report_button = QPushButton("تولید گزارش فروش")
        filter_layout.addWidget(self.generate_food_sales_report_button)
        filter_layout.addStretch() # be samte rast hol midahad
        food_sales_layout.addLayout(filter_layout)
            # table
        food_sales_layout.addWidget(QLabel("اطلاعات به صورت جدولی:"))
        self.food_sales_report_table = QTableWidget()
        self.food_sales_report_table.setColumnCount(3)
        self.food_sales_report_table.setHorizontalHeaderLabels(["نام غذا", "تعداد کل فروخته شده", "مبلغ کل فروش (تومان)"])
        self.food_sales_report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.food_sales_report_table.setEditTriggers(QTableWidget.NoEditTriggers)
        food_sales_layout.addWidget(self.food_sales_report_table)
            # chart
        food_sales_layout.addWidget(QLabel("اطلاعات به صورت نموداری:"))
        self.food_sales_chart_widget = MatplotlibChartWidget()
        food_sales_layout.addWidget(self.food_sales_chart_widget)

        self.report_sub_tabs.addTab(self.food_sales_report_page, "گزارش فروش غذاها")
        self.generate_food_sales_report_button.clicked.connect(self.handle_generate_food_sales_report)

        self.tabs.addTab(self.reports_page, "گزارش‌ها")

        # users reports
        self.customer_orders_report_page = QWidget()
        customer_orders_layout = QVBoxLayout(self.customer_orders_report_page)

        customer_filter_layout = QHBoxLayout()
        
        customer_filter_layout.addWidget(QLabel("انتخاب مشتری:"))
        self.report_customer_select_combo = QComboBox()
        customer_filter_layout.addWidget(self.report_customer_select_combo)
        self._populate_report_customer_combo()

        customer_filter_layout.addWidget(QLabel("دوره زمانی:"))
        self.report_customer_time_period_combo = QComboBox()
        self.report_customer_time_period_combo.addItem("کل سفارشات", userData="all_time")
        self.report_customer_time_period_combo.addItem("امروز", userData="today")
        self.report_customer_time_period_combo.addItem("۷ روز گذشته", userData="last_7_days")
        self.report_customer_time_period_combo.addItem("ماه جاری", userData="this_month")
        customer_filter_layout.addWidget(self.report_customer_time_period_combo)

        self.generate_customer_report_button = QPushButton("تولید گزارش مشتریان")
        customer_filter_layout.addWidget(self.generate_customer_report_button)
        
        customer_filter_layout.addStretch()
        customer_orders_layout.addLayout(customer_filter_layout)

        self.customer_orders_report_table = QTableWidget()

        customer_orders_layout.addWidget(self.customer_orders_report_table)
        self.customer_orders_report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customer_orders_report_table.setEditTriggers(QTableWidget.NoEditTriggers)

                
        customer_orders_layout.addWidget(QLabel("اطلاعات به صورت نموداری:"))
        self.customer_orderS_chart_widget = MatplotlibChartWidget()
        customer_orders_layout.addWidget(self.customer_orderS_chart_widget)

        self.generate_customer_report_button.clicked.connect(self.handle_generate_customer_orders_report)

        self.report_sub_tabs.addTab(self.customer_orders_report_page, "گزارش سفارشات مشتریان")

        self.tabs.addTab(self.reports_page, "گزارش‌ها")

    # slots for dashboard
    def _load_dashboard_data(self):
        # for top row => top 3 foods and users
        top_foods = get_top_selling_foods()
        top_users = get_top_ordering_customers()
        if top_users is None:
            print("DEBUG: get_top_ordering_customers() returned None.")
            top_users = []
        if top_foods is None:
            print("DEBUG: get_top_selling_foods() returned None.")
            top_foods = []
        
        food_labels = [self.top_food_1_label, self.top_food_2_label, self.top_food_3_label]
        for i in range(len(food_labels)):
            if top_foods and i < len(top_foods):
                food_name = top_foods[i][0]
                total_revenue = top_foods[i][1]
                food_labels[i].setText(f"{i+1}. {food_name} - {total_revenue:,.0f} تومان")
            else:
                food_labels[i].setText(f"{i+1}. - ")
        
        user_labels = [self.top_user_1_label, self.top_user_2_label, self.top_user_3_label]
        for i in range(len(user_labels)):
            if top_users and i < len(top_users):
                user_name = top_users[i][0]
                total_revenue = top_users[i][1]
                user_labels[i].setText(f"{i+1}. {user_name} - {total_revenue} سفارش")
            else:
                user_labels[i].setText(f"{i+1}. - ")
        
        # for down row
            # summary sales
        try:
            orders_today, revenue_today = get_sales_summary_for_period('today')
            self.sales_today_label.setText(f"سفارشات امروز: {orders_today} عدد | درآمد امروز: {revenue_today:,.0f} تومان")
            orders_week, revenue_week = get_sales_summary_for_period('this_week')
            self.sales_this_week_label.setText(f"سفارشات هفته جاری: {orders_week} عدد | درآمد هفته جاری: {revenue_week:,.0f} تومان")
        except Exception as e:
            print(f"Error loading sales summary for dashboard: {e}")
            self.sales_today_label.setText("خلاصه فروش امروز: خطای بارگذاری")
            self.sales_this_week_label.setText("خلاصه فروش هفته: خطای بارگذاری")
            
            # low quantity foods
        while self.low_stock_layout.count():
            child = self.low_stock_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        try:
            low_stock_foods = get_low_stock_foods(threshold=5)
            if low_stock_foods:
                for food_name, inventory in low_stock_foods:
                    self.low_stock_layout.addWidget(QLabel(f"{food_name} (موجودی: {inventory})"))
            else:
                self.low_stock_layout.addWidget(QLabel("موردی یافت نشد."))
            print(f"DEBUG: Low stock foods loaded: {low_stock_foods}")
        except Exception as e:
            print(f"Error loading low stock foods for dashboard: {e}")
            self.low_stock_layout.addWidget(QLabel("خطا در بارگذاری لیست موجودی کم"))

            # general statics
        try:
            total_cust, total_foods = get_general_stats()
            self.active_users.setText(f"تعداد کل مشتریان فعال: {total_cust}")
            self.active_foods.setText(f"تعداد کل غذاها در منو: {total_foods}")
            print(f"DEBUG: General stats loaded. Customers: {total_cust}, Foods: {total_foods}")
        except Exception as e:
            print(f"Error loading general stats for dashboard: {e}")
            self.active_users.setText("تعداد مشتریان: خطای بارگذاری")
            self.active_foods.setText("تعداد غذاها: خطای بارگذاری")
    
    def _goto_foods_reports_tab(self):
        self.tabs.setCurrentWidget(self.reports_page)
        self.report_sub_tabs.setCurrentWidget(self.food_sales_report_page)
    def _goto_users_reports_tab(self):
        self.tabs.setCurrentWidget(self.reports_page)
        self.report_sub_tabs.setCurrentWidget(self.customer_orders_report_page)
    # slots for reports
    def _populate_report_food_combo(self):
        """fill combo box from foods in database"""
        self.report_food_select_combo.clear()
        self.report_food_select_combo.addItem("همه غذاها", userData="ALL")
        foods = get_all_foods()
        if foods:
            for food in foods:
                self.report_food_select_combo.addItem(food[1], userData=food[0])

    def handle_generate_food_sales_report(self):
        """show tables item by selected filters"""
        select_food_id = self.report_food_select_combo.currentData()
        if select_food_id == 'ALL':
            select_food_id = None

        select_time_period_key = self.report_time_period_combo.currentData()
        try:
            report_data = get_food_sales_report(select_time_period_key, select_food_id)
            self.food_sales_report_table.setRowCount(0)
            if report_data is None: report_data = []   
            self.food_sales_report_table.setRowCount(len(report_data))
            food_names_for_chart = []
            revenues_for_chart = []
            for row_index, row_data in enumerate(report_data):
                # row_data: (food_name, total_quantity_sold, total_revenue)
                food_name = str(row_data[0])
                quantity_sold = int(row_data[1])
                total_revenue = float(row_data[2])
                self.food_sales_report_table.setItem(row_index, 0, QTableWidgetItem(food_name)) # food name
                self.food_sales_report_table.setItem(row_index, 1, QTableWidgetItem(quantity_sold)) # quantity
                self.food_sales_report_table.setItem(row_index, 2, QTableWidgetItem(f"{total_revenue:,.0f}")) # total price
                food_names_for_chart.append(food_name)
                revenues_for_chart.append(total_revenue)

            if report_data:
                self.food_sales_chart_widget.plot_bar_chart(
                    x_labels=food_names_for_chart, 
                    y_values=revenues_for_chart, 
                    title="",
                    x_axis_label="",
                    y_axis_label=""
                )
            else:
                self.food_sales_chart_widget.clear_chart()
                QMessageBox.information(self, "گزارش", "داده‌ای برای نمایش با این فیلترها یافت نشد.")

        except Exception as e:
            self.food_sales_chart_widget.clear_chart()
            QMessageBox.critical(self, "خطا در گزارش‌گیری", f"خطایی در هنگام تولید گزارش رخ داد: {e}")
            print(f"Error in handle_generate_food_sales_report: {e}")

    def _populate_report_customer_combo(self):
        """Fill select user combo box with user list."""
        self.report_customer_select_combo.clear()
        self.report_customer_select_combo.addItem("همه مشتریان", userData="ALL") # یا None
        
        users = get_all_users()
        if users:
            for user in users:
                # user: (id, username, password, full_name, wallet_balance, role)
                if user[5] == 'customer':
                    self.report_customer_select_combo.addItem(f"{user[3]} (ID: {user[0]})", userData=user[0])

    def handle_generate_customer_orders_report(self):
        """Generates and displays customer orders report based on filters."""
        customer_selection_data = self.report_customer_select_combo.currentData()
        time_period_key = self.report_customer_time_period_combo.currentData()

        self.customer_orders_report_table.setRowCount(0)
        report_data = []

        if customer_selection_data == "ALL":
            report_data = get_customer_order_summary_report(time_period_key)
            self.customer_orders_report_table.setColumnCount(3)
            self.customer_orders_report_table.setHorizontalHeaderLabels(["نام مشتری", "تعداد کل سفارشات", "مجموع خرید (تومان)"])
            user_names_for_chart = []
            user_revenues_for_chart = []

            if report_data:
                self.customer_orders_report_table.setRowCount(len(report_data))
                for row_idx, row in enumerate(report_data):
                    # row: (user_full_name, total_orders, total_spent_by_user)
                    self.customer_orders_report_table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
                    self.customer_orders_report_table.setItem(row_idx, 1, QTableWidgetItem(str(row[1])))
                    self.customer_orders_report_table.setItem(row_idx, 2, QTableWidgetItem(f"{float(row[2]):,.0f}"))
                    user_names_for_chart.append(str(row[0]))
                    user_revenues_for_chart.append(float(row[2]))
                    
            if report_data:
                self.customer_orderS_chart_widget.plot_bar_chart(
                    x_labels=user_names_for_chart, 
                    y_values=user_revenues_for_chart, 
                    title="",
                    x_axis_label="",
                    y_axis_label=""
                )
            else:
                self.customer_orderS_chart_widget.clear_chart()
                QMessageBox.information(self, "گزارش", "داده‌ای برای نمایش با این فیلترها یافت نشد.")

        else:
            customer_id = customer_selection_data
            print(f"DEBUG: Generating orders for specific customer ID: {customer_id}, period: {time_period_key}")
            report_data = get_orders_for_specific_customer(customer_id, time_period_key)
            self.customer_orders_report_table.setColumnCount(4)
            self.customer_orders_report_table.setHorizontalHeaderLabels(["شناسه سفارش", "تاریخ", "مبلغ کل (تومان)", "وضعیت"])
            
            user_names_for_chart = []
            user_revenues_for_chart = []

            if report_data:
                self.customer_orders_report_table.setRowCount(len(report_data))
                for row_idx, row in enumerate(report_data):
                    # row: (order_id, order_date, total_price, status)
                    self.customer_orders_report_table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
                    self.customer_orders_report_table.setItem(row_idx, 1, QTableWidgetItem(str(row[1])))
                    self.customer_orders_report_table.setItem(row_idx, 2, QTableWidgetItem(f"{float(row[2]):,.0f}"))
                    self.customer_orders_report_table.setItem(row_idx, 3, QTableWidgetItem(str(row[3])))
                    user_names_for_chart.append(str(row[0]))
                    user_revenues_for_chart.append(float(row[2]))
                    
            if report_data:
                self.customer_orderS_chart_widget.plot_bar_chart(
                    x_labels=user_names_for_chart, 
                    y_values=user_revenues_for_chart, 
                    title="",
                    x_axis_label="",
                    y_axis_label=""
                )
            else:
                self.customer_orderS_chart_widget.clear_chart()
                QMessageBox.information(self, "گزارش", "داده‌ای برای نمایش با این فیلترها یافت نشد.")

        if not report_data:
            QMessageBox.information(self, "گزارش", "داده‌ای برای نمایش با این فیلترها یافت نشد.")

        self.customer_orders_report_table.resizeColumnsToContents()

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
    
    # Slots for discount codes
    def load_discount_data(self):
        """Reads discounts data from the database and populates the table with it."""
        discounts = get_all_discounts()
        self.discount_table.setRowCount(len(discounts))
        for index, discount in enumerate(discounts):
            self.discount_table.setItem(index, 0, QTableWidgetItem(str(discount[0]))) # ID
            self.discount_table.setItem(index, 1, QTableWidgetItem(discount[1]))      # Code
            self.discount_table.setItem(index, 2, QTableWidgetItem(discount[2])) # Discount Type
            self.discount_table.setItem(index, 3, QTableWidgetItem(str(discount[3]))) # Value
            self.discount_table.setItem(index, 4, QTableWidgetItem(str(discount[4]))) # Minimum pruchase amount
            self.discount_table.setItem(index, 5, QTableWidgetItem(str(discount[5]))) # Is avtive
            self.discount_table.setItem(index, 6, QTableWidgetItem(str(discount[6]))) # Usage limit
            self.discount_table.setItem(index, 7, QTableWidgetItem(str(discount[7]))) # Times used
            self.discount_table.setItem(index, 8, QTableWidgetItem(discount[8])) # Valid from
            self.discount_table.setItem(index, 9, QTableWidgetItem(discount[9])) # Valid until

    def show_add_discount_dialog(self):
        """Show add discount pop-up"""
        dialog = DiscountDialog()
        if dialog.exec():
            data = dialog.get_data()
            add_discount(data['code'], data['discount_type'], data['value'], data['min_purchase_amount'], data['is_active'], data['usage_limit'], data['valid_from'], data['valid_until'])
            self.load_discount_data()
    
    def show_edit_discount_dialog(self):
        """Show edit discount pop-up"""
        selected_row = self.discount_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "اخطار", "لطفا یک کد تخفیف را برای ویرایش انتخاب کنید")
            return

        discount_id_str = self.discount_table.item(selected_row, 0).text()
        code_str = self.discount_table.item(selected_row, 1).text()
        discount_type_str = self.discount_table.item(selected_row, 2).text()
        value_str = self.discount_table.item(selected_row, 3).text()
        min_purchase_amount_str = self.discount_table.item(selected_row, 4).text()
        is_active_str = self.discount_table.item(selected_row, 5).text() 
        usage_limit_str = self.discount_table.item(selected_row, 6).text()
        times_used_str = self.discount_table.item(selected_row, 7).text()
        valid_from_str = self.discount_table.item(selected_row, 8).text() 
        valid_until_str = self.discount_table.item(selected_row, 9).text() 
        
        
        data_for_dialog = [
            int(discount_id_str),
            code_str,
            discount_type_str,
            float(value_str), 
            float(min_purchase_amount_str), 
            int(is_active_str),
            int(usage_limit_str) if usage_limit_str and usage_limit_str.strip() and usage_limit_str.lower() != 'none' else None,
            int(times_used_str),
            valid_from_str if valid_from_str and valid_from_str.strip() and valid_from_str.lower() != 'none' else None,
            valid_until_str if valid_until_str and valid_until_str.strip() and valid_until_str.lower() != 'none' else None
        ]

        dialog = DiscountDialog(discount_data=data_for_dialog, parent=self)
        if dialog.exec():
            new_data = dialog.get_data()
            
            update_discount(
                new_data['id'],
                new_data['code'],
                new_data['discount_type'],
                new_data['value'],
                new_data['min_purchase_amount'],
                new_data['is_active'],
                new_data['usage_limit'],
                new_data['valid_from'],
                new_data['valid_until']
            )
            self.load_discount_data()

    def delete_selected_discount_dialog(self):
        selected_row = self.discount_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "لطفا یک کد تخفیف را برای حذف کردن انتخاب کنید")
            return
        confirm = QMessageBox.question(self, "Confirm", "از حذف کردن این کد تخفیف مطمئن هستید؟")
        if confirm == QMessageBox.Yes:
            discount_id = int(self.discount_table.item(selected_row, 0).text())
            delete_discount(discount_id)
            self.load_discount_data()

    # Slots for foods
    def load_foods_data(self):
        """Reads foods data from the database and populates the table with it."""
        foods = get_all_foods()
        self.food_table.setRowCount(len(foods))
        for index, food in enumerate(foods):
            self.food_table.setItem(index, 0, QTableWidgetItem(str(food[0]))) # ID
            self.food_table.setItem(index, 1, QTableWidgetItem(food[1]))      # Name
            self.food_table.setItem(index, 2, QTableWidgetItem(str(food[2]))) # Price
            self.food_table.setItem(index, 3, QTableWidgetItem(str(food[3]))) # Inventory
            self.food_table.setItem(index, 4, QTableWidgetItem(food[4])) # Image Path
   
    def show_add_food_dialog(self):
        """Show add foods pop-up"""
        dialog = FoodDialog()
        if dialog.exec():
            data = dialog.get_data()
            add_food(data['name'], data['price'], data['inventory'], data['image_path'])
            self.load_foods_data()
        
    def show_edit_food_dialog(self):
        """Edit selected foods pop-up"""
        selected_row = self.food_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "لطفا یک غذا را برای ویرایش انتخاب کنید")
            return

        food_id = int(self.food_table.item(selected_row, 0).text())
        name = self.food_table.item(selected_row, 1).text()
        price = float(self.food_table.item(selected_row, 2).text())
        inventory = int(self.food_table.item(selected_row, 3).text())
        image_path = self.food_table.item(selected_row, 4).text()

        food_data = [food_id, name, price, inventory, image_path]

        # open dialog with default entries
        dialog = FoodDialog(food_data=food_data)
        if dialog.exec():
            new_data = dialog.get_data()
            update_food(food_id, new_data['name'], new_data['price'], new_data['inventory'], new_data['image_path'])
            self.load_foods_data()

    def delete_selected_food_dialog(self):
        """Delete selected food"""
        selected_row = self.food_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "لطفا یک غذا را برای حذف انتخاب کنید")
            return

        confrim_message = QMessageBox.question(self, "Confrim Delete",
                                               "از حذف کردن این غذا مطمئن هستید؟",
                                               QMessageBox.Yes | QMessageBox.No)
        if confrim_message == QMessageBox.Yes:
            food_id = int(self.food_table.item(selected_row, 0).text())
            delete_food(food_id)
            self.load_foods_data()

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
            add_user(data['username'], data['password'], data['full_name'], data['wallet_balance'], data['role'])
            self.load_users_data()

    def show_edit_user_dialog(self):
        selected_row = self.user_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "لطفا یک کاربر برای ویرایش انتخاب کنید.")
            return
        user_id = int(self.user_table.item(selected_row, 0).text())
        username = self.user_table.item(selected_row, 1).text()
        password = self.user_table.item(selected_row, 2).text()
        full_name = self.user_table.item(selected_row, 3).text()
        wallet = float(self.user_table.item(selected_row, 4).text())
        role = self.user_table.item(selected_row, 5).text()
        user_data = [user_id, username, password, full_name, wallet, role]

        dialog = UserDialog(user_data=user_data)
        if dialog.exec():
            new_data = dialog.get_data()
            update_user(user_id, new_data['username'], new_data['password'], new_data['full_name'], new_data['wallet_balance'], new_data['role'])
            self.load_users_data()

    def delete_selected_user(self):
        selected_row = self.user_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "لطفا یک کاربر را برای حذف کردن انتخاب کنید")
            return
        confirm = QMessageBox.question(self, "Confirm", "از حذف کردن این کاربر مطمئن هستید؟")
        if confirm == QMessageBox.Yes:
            user_id = int(self.user_table.item(selected_row, 0).text())
            delete_user(user_id)
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
