import sqlite3
from datetime import datetime, timedelta, date

# --------- Create tables ---------
def create_tables():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        wallet_balance REAL DEFAULT 0.0,
        role TEXT NOT NULL DEFAULT 'customer'
    )""")
    print("> Users table created successfully!")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Foods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        inventory INTEGER DEFAULT 0,
        image_path TEXT
    )""")
    print("> Foods table created successfully!")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        total_price REAL NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES Users (id)
    )''')
    print("> Orders table created successfully!")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderItems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        food_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price_per_item REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES Orders (id),
        FOREIGN KEY (food_id) REFERENCES Foods (id)
    )''')
    print("> OrderItems table created successfully!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Discounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        discount_type TEXT NOT NULL CHECK(discount_type in ('percentage', 'fixed_amount')),
        value REAL NOT NULL,
        min_purchase_amount REAL NOT NULL DEFAULT 0.0,
        is_active INTEGER NOT NULL DEFAULT 1,
        usage_limit INTEGER DEFAULT 0,
        times_used INTEGER DEFAULT 0,
        valid_from TEXT,
        valid_until TEXT
    )""")
    print("> Discount table created successfully!")

    conn.commit()
    conn.close()
    print("--> Database disconnected successfully!")

# --------- CURD For Foods ---------
# Create
def add_food(name, price, inventory, image_path):
    """ Add a new food item to the menu. """
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO Foods (name, price, inventory, image_path) VALUES (?, ?, ?, ?)
        """, (name, price, inventory, image_path))
        conn.commit()
        print(f"> {name} added to the menu successfully!")
        return True, f"غذا {name} به منو اضاف شد"
    except sqlite3.IntegrityError:
        print("You can't add the same food twice!")
        return False, "مشکلی پیش آمد"
    finally:
        conn.close()

# Read
def get_all_foods():
    """Get all food items from the menu."""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Foods")
    foods = cursor.fetchall()
    conn.close()
    return foods

# Update
def update_food(food_id, name=None, price=None, inventory=None, image_path=None):
    """ Update the details of a food item. """
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE Foods SET
    name = COALESCE(?, name),
    price = COALESCE(?, price),
    inventory = COALESCE(?, inventory),
    image_path = COALESCE(?, image_path)
    WHERE id = ?
    """, (name, price, inventory, image_path, food_id))
    conn.commit()
    conn.close()

# Delete
def delete_food(food_id):
    """ Delete a food item from the menu. """
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM Foods WHERE id = ?""", (food_id,))
    conn.commit()
    conn.close()
    print(f"> {food_id} deleted from the menu successfully!")

# --------- CURD For Users ---------
# Create
def add_user(username, password, full_name=None, wallet_balance=0, role='customer'):
    """Add new user"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO Users (username, password, full_name, wallet_balance, role) VALUES (?, ?, ?, ?, ?)""",
                       (username, password, full_name, wallet_balance, role))
        return True, f"شما با نام کاربری {username} ثبت نام شدید!"
    except sqlite3.IntegrityError:
        print(f"Username {username} already exists!")
        return False, f"نام کاربری {username} قبلا ثبت شده، نام کاربری دیگری را امتحان کنید!"
    finally:
        conn.commit()
        conn.close()
        print(f"> {username} added successfully!")
# Read
def get_all_users():
    """Get all users"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    conn.close()
    return users
# Update
def update_user(user_id, username, password, full_name, wallet_balance, role):
    """Update user details"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Users SET username = ?, password = ?, full_name = ?, wallet_balance = ?, role = ?
        WHERE id = ?
    """, (username, password, full_name, wallet_balance, role, user_id))
    conn.commit()
    conn.close()
    print(f"> User {user_id} updated successfully!")
# Delete
def delete_user(user_id):
    """Delete a user"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    print(f"> User {user_id} deleted successfully!")

# Charge wallet
def top_up_wallet(user_id, amount_to_add):
    """select user wallet balance and increase it"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    try:
        p_user_id = int(user_id)
        p_amount_to_add = float(amount_to_add)
        if p_amount_to_add <= 0:
            return False, "مبلغ شارژ باید یک عدد مثبت باشد"
        cursor.execute("BEGIN TRANSACTION")
        params = (p_amount_to_add, p_user_id)
        cursor.execute("UPDATE Users SET wallet_balance = wallet_balance + ? WHERE id = ?", params)
        if cursor.rowcount == 0: # agar karbar peyda nashod
            conn.rollback()
            conn.close()
            return False, f"کاربری با شناسه {p_user_id} پیدا نشد"
        conn.commit()
        return True, f"کیف پول شما با موفقیت به مبلغ {p_amount_to_add:,.0f} تومان شارژ شد."
    except ValueError:
        if conn: 
            conn.rollback()
            conn.close()
            return False, "مبلغ وارد شده برای شارژ معتبر نیست (باید عدد باشد)."
    except sqlite3.Error as e_sql:
        print(f"DEBUG top_up_wallet: SQLite error: {e_sql} (Args: {e_sql.args})")
        if conn: 
            conn.rollback()
            return False, f"خطای پایگاه داده هنگام شارژ کیف پول: {e_sql}"
    except Exception as e_generic:
        print(f"DEBUG top_up_wallet: Generic error: {e_generic}")
        if conn: 
            conn.rollback()
            return False, f"خطای غیرمنتظره هنگام شارژ کیف پول: {e_generic}"
    finally:
        if conn:
            conn.close()

# --------- Shopping Cart ---------
def check_user_login(username, password):
    """Check users"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def get_available_foods():
    """Return a foods with inventory > 0"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Foods WHERE inventory > 0")
    foods = cursor.fetchall()
    conn.close()
    return foods


# --------- Discount Code ---------
def get_valid_discount_by_code(code, current_pruches_amount):
    """Checks a discount code for validity against multiple criteria.
    Returns (discount_record, message)"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Discounts WHERE code = ? AND is_active = 1", (code,))
    discount = cursor.fetchone()
    conn.close()
    if not discount:
        return None, "کد تخفیف نامعتبر است یا فعال نیست."
    now = datetime.now()
    if discount[8]: # Valid from
        valid_from_date = datetime.strptime(discount[8], "%Y-%m-%d %H:%M:%S")
        if now < valid_from_date:
            return None, "این کد تخفیف هنوز فعال نشده است"
    if discount[9]: # Valid until
        valid_until_date = datetime.strptime(discount[9], "%Y-%m-%d %H:%M:%S")
        if now > valid_until_date:
            return None, "زمان این کد تخفیف تمام شده است"
    if discount[6]: # usage limit
        if discount[7] >= discount[6]:
            return None, "ظرفیت استفاده از این کد تخفیف تمام شده است"
    if current_pruches_amount < discount[4]:
        return None, f"حداقل مقدار خرید برای استفاده از این کد تخفیف {discount[4]:,.0f} تومان است."
    
    return discount, "کد تخفیف معتبر است."

def apply_discount(original_total, discount_record):
    """Calculates the discount amount and the new total.
    discount_record is the tuple fetched from the database.
    Returns (calculated_discount_amount, new_total_after_discount)"""

    if not discount_record:
        return 0, original_total
    discount_type = discount_record[2]
    discount_value = discount_record[3]
    calculate_discount_amount = 0

    if discount_type == 'percentage':
        calculate_discount_amount = original_total * (discount_value/100.0)
    if discount_type == 'fixed_amount':
        calculate_discount_amount = discount_value

    calculate_discount_amount = min(calculate_discount_amount, original_total)
    new_total_after_discount = original_total - calculate_discount_amount
    
    return calculate_discount_amount, new_total_after_discount

def increment_discount_usage(discount_id):
    """Increments the usage count of a discount code."""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Discount SET times_used = times_used + 1 WHERE id = ?", discount_id)
        conn.commit()
    except Exception as e:
        print(f"Error incrementing discount usage: {e}")
    finally:
        conn.close()

def place_order(user_id, cart_items, total_price_after_discount, applied_discount_id=None):
    """
    Places a new order in the database. This is a transaction.
    cart_items is a dictionary like: {food_id: {'name': name, 'quantity': qty, 'price': price_per_item}}
    total_price_after_discount is the final price the user pays.
    applied_discount_id is the ID of the discount code used, if any.
    """
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    
    try:
        p_user_id = int(user_id)
        p_total_price_after_discount = float(total_price_after_discount)
        p_applied_discount_id = int(applied_discount_id) if applied_discount_id is not None else None

        cursor.execute("SELECT wallet_balance FROM Users WHERE id = ?", (p_user_id,))
        current_balance_tuple = cursor.fetchone()

        if not current_balance_tuple:
            conn.close()
            return False, "کاربر یافت نشد."
        
        current_balance = float(current_balance_tuple[0])

        if current_balance < p_total_price_after_discount:
            conn.close()
            return False, "موجودی کیف پول کافی نیست."

        # start transaction
        cursor.execute("BEGIN TRANSACTION")

        order_date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_str = "ثبت شده"
        
        order_params = (p_user_id, order_date_str, p_total_price_after_discount, status_str)
        cursor.execute("INSERT INTO Orders (user_id, order_date, total_price, status) VALUES (?, ?, ?, ?)", order_params)
        order_id = cursor.lastrowid

        for food_id_key, item_details in cart_items.items():
            p_food_id = int(food_id_key)
            p_quantity = int(item_details['quantity'])
            p_price_per_item = float(item_details['price'])

            order_item_params = (order_id, p_food_id, p_quantity, p_price_per_item)
            cursor.execute("INSERT INTO OrderItems (order_id, food_id, quantity, price_per_item) VALUES (?, ?, ?, ?)", order_item_params)
            
            food_update_params = (p_quantity, p_food_id)
            cursor.execute("UPDATE Foods SET inventory = inventory - ? WHERE id = ?", food_update_params)

        new_balance = current_balance - p_total_price_after_discount
        user_update_params = (float(new_balance), p_user_id)
        cursor.execute("UPDATE Users SET wallet_balance = ? WHERE id = ?", user_update_params)

        if p_applied_discount_id is not None:
            discount_update_params = (p_applied_discount_id,)
            cursor.execute("UPDATE Discounts SET times_used = times_used + 1 WHERE id = ?", discount_update_params)

        conn.commit()
        return True, "سفارش شما با موفقیت ثبت شد!"

    except sqlite3.Error as e_sql: 
        if conn:
            conn.rollback()
        return False, f"خطای پایگاه داده: {e_sql}"
    except ValueError as e_val: 
        if conn:
            conn.rollback()
        return False, f"خطای نوع داده: {e_val}"
    except Exception as e_generic: 
        if conn:
            conn.rollback()
        return False, f"خطای غیرمنتظره: {e_generic}"
    finally:
        if conn:
            conn.close()


# --------- CRUD Discount Codes ---------
# Create
def add_discount(code, discount_type, value, min_pruchase_amount=0.0, is_active=1, usage_limit=None, valid_from=None, valid_until=None):
    """Add new discount code"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Discounts (code, discount_type, value, min_purchase_amount, is_active, usage_limit, times_used, valid_from, valid_until) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)",
                       (code, discount_type, value, min_pruchase_amount, is_active, usage_limit, valid_from, valid_until))
    except sqlite3.IntegrityError:
        print(f"Discount code {code} already exists!")
    except Exception as e:
        print(f"خطای غیرمنتظره: {e}")
    finally:
        conn.commit()
        conn.close()
        print(f"> {code} added successfully!")
# Read
def get_all_discounts():
    """Show all discount codes"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Discounts")
    discounts = cursor.fetchall()
    conn.close()
    return discounts
# Update
def update_discount(discount_id, code, discount_type, value, min_purchase_amount, is_active, usage_limit, valid_from, valid_until):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Discounts SET code = ?, discount_type = ?, value = ?, min_purchase_amount = ?, is_active = ?, usage_limit = ?, valid_from = ?, valid_until = ? WHERE id = ?",
                   (code, discount_type, value, min_purchase_amount, is_active, usage_limit, valid_from, valid_until, discount_id))
    conn.commit()
    conn.close()
    print(f"> Discount {code} updated successfully!")
# Delete 
def delete_discount(discount_id):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Discounts WHERE id = ?", (discount_id,))
    conn.commit()
    conn.close()
    print(f"> Discount {discount_id} deleted successfully!")
# for customer panel
def get_active_and_valid_discounts():
    """return valid discounts list"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = """
        SELECT 
            id, code, discount_type, value, min_purchase_amount, valid_until
        FROM Discounts
        WHERE 
            is_active = 1
            AND (valid_from IS NULL OR valid_from <= ?)
            AND (valid_until IS NULL OR valid_until >= ?)
            AND (usage_limit IS NULL OR times_used < usage_limit)
        ORDER BY id DESC
    """
    params = (now_str, now_str)
    try:
        cursor.execute(query, params)
        valid_discounts = cursor.fetchall()
        return valid_discounts
    except sqlite3.Error as e:
        print(f"Database error in get_active_and_valid_discounts: {e}")
        return []
    finally:
        conn.close()

# --------- CRUD Orders ---------
# Create
def admin_create_order(user_id, order_items_details, total_price, 
                       initial_status="ثبت توسط مدیر"):
    """Creates a new order by an admin."""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    try:
        p_user_id = int(user_id)
        p_total_price = float(total_price)
        p_initial_status = str(initial_status)

        cursor.execute("SELECT id FROM Users WHERE id = ?", (p_user_id,))
        if not cursor.fetchone():
            conn.close()
            return False, None, "کاربر انتخاب شده برای سفارش معتبر نیست."

        cursor.execute("BEGIN TRANSACTION")

        order_date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        order_params = (p_user_id, order_date_str, p_total_price, p_initial_status)
        cursor.execute("INSERT INTO Orders (user_id, order_date, total_price, status) VALUES (?, ?, ?, ?)", order_params)
        order_id = cursor.lastrowid

        for item in order_items_details:
            p_food_id = int(item['food_id'])
            p_quantity = int(item['quantity'])
            p_price_at_order = float(item['price_at_order'])

            order_item_params = (order_id, p_food_id, p_quantity, p_price_at_order)
            cursor.execute("INSERT INTO OrderItems (order_id, food_id, quantity, price_per_item) VALUES (?, ?, ?, ?)", order_item_params)
            
            food_update_params = (p_quantity, p_food_id)
            cursor.execute("UPDATE Foods SET inventory = inventory - ? WHERE id = ?", food_update_params)
        

        conn.commit()
        return True, order_id, f"سفارش جدید با شناسه {order_id} توسط مدیر با موفقیت ایجاد شد."

    except sqlite3.Error as e_sql:
        if conn: conn.rollback()
        return False, None, f"خطای پایگاه داده: {e_sql}"
    except ValueError as e_val:
        if conn: conn.rollback()
        return False, None, str(e_val)
    except Exception as e_generic:
        if conn: conn.rollback()
        return False, None, f"خطای غیرمنتظره: {e_generic}"
    finally:
        if conn: conn.close()
        print("DEBUG admin_create_order: Connection closed.")
# Read
def get_all_orders_for_admin():
    """Show all discount codes"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT Orders.id, Users.full_name, Orders.order_date, Orders.total_price, Orders.status 
            FROM Orders 
            JOIN Users ON Orders.user_id = Users.id 
            ORDER BY Orders.order_date DESC
        """)
        orders = cursor.fetchall()
        return orders
    except Exception as e:
        print(f"Error fetching all orders for admin: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_order_items_for_admin(order_id):
    """Show all discount codes"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT Foods.name, OrderItems.quantity, OrderItems.price_per_item, 
                   (OrderItems.quantity * OrderItems.price_per_item) AS item_subtotal
            FROM OrderItems
            JOIN Foods ON OrderItems.food_id = Foods.id
            WHERE OrderItems.order_id = ?
        """, (order_id,))
        items = cursor.fetchall()
        return items
    except Exception as e:
        print(f"Error fetching order items for admin (order_id: {order_id}): {e}")
        return []
    finally:
        if conn:
            conn.close()
# Update
def update_order_status_admin(order_id, new_status):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Orders SET status = ? WHERE id = ?", (new_status, order_id))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Order ID {order_id} status updated to '{new_status}'.")
            return True
        else:
            print(f"Order ID {order_id} not found or status not changed.")
            return False
    except Exception as e:
        print(f"Error updating order status for order_id {order_id}: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# Delete
def cancel_order_admin(order_id, cancelled_by_role="مدیر"):
    """Delete orders for admin panel"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    new_status = f"لغو شده توسط {cancelled_by_role}"

    try:
        cursor.execute("BEGIN TRANSACTION")
        params_order_id = int(order_id)
        # get user id & total price
        cursor.execute("SELECT user_id, total_price, status FROM Orders WHERE id = ?", (params_order_id,))
        order_info = cursor.fetchone()
        if not order_info:
            conn.rollback()
            conn.close()
            print(f"DEBUG delete_order_admin: Order with id {params_order_id} not found.")
            return False, f"سفارشی با شناسه {params_order_id} یافت نشد."
        
        p_user_id = order_info[0]
        p_order_total_price = order_info[1]
        current_order_status = order_info[2]

        if current_order_status.startswith("لغو شده") or current_order_status == "تحویل داده شده":
            conn.rollback()
            conn.close()
            return False, f"سفارش با شناسه {params_order_id} قبلاً {current_order_status} و قابل لغو مجدد نیست."

        # get orders item & refund items count
        cursor.execute("SELECT food_id, quantity FROM OrderItems WHERE order_id = ?", (params_order_id,))
        order_items_to_restock = cursor.fetchall()
        for item in order_items_to_restock:
            cursor.execute("UPDATE Foods SET inventory = inventory + ? WHERE id = ?", (item[1], item[0]))
        # refund user wallet
        cursor.execute("UPDATE Users SET wallet_balance = wallet_balance + ? WHERE id = ?", (p_order_total_price, p_user_id))
        # update order status
        cursor.execute("UPDATE Orders SET status = ? WHERE id = ?", (new_status, params_order_id))
        conn.commit()
        return True, f"سفارش با موفقیت لغو شد."
    except sqlite3.Error as e_sql:
        print(f"DEBUG cancel_order_admin: SQLite error: {e_sql} (Args: {e_sql.args})")
        if conn: conn.rollback()
        return False, f"خطای پایگاه داده هنگام لغو سفارش: {e_sql}"
    except Exception as e_generic:
        print(f"DEBUG cancel_order_admin: Generic error: {e_generic}")
        if conn: conn.rollback()
        return False, f"خطای غیرمنتظره هنگام لغو سفارش: {e_generic}"
    finally:
        if conn: conn.close()
        print(f"DEBUG cancel_order_admin: Connection closed for order_id: {order_id}")

# --------- Reports ---------
def get_food_sales_report(time_period_key, food_id=None):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    end_date = datetime.now()
    if time_period_key == 'today':
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_period_key == 'last_7_days':
        start_date = end_date - timedelta(days=7)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_period_key == 'this_month':
        start_date = end_date.replace(day=1 ,hour=0, minute=0, second=0, microsecond=0)
    elif time_period_key == 'all_time':
        start_date = None
        end_date = None
    # convert times to str for sql 'YYYY-MM-DD HH:MM:SS'
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S") if start_date else None
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S") if end_date else None

    query = """
        SELECT 
            F.name, 
            SUM(OI.quantity) as total_quantity_sold,
            SUM(OI.quantity * OI.price_per_item) as total_revenue
        FROM OrderItems OI
        JOIN Foods F ON OI.food_id = F.id
        JOIN Orders O ON OI.order_id = O.id
    """

    conditions = []
    params = []

    if start_date_str and end_date_str:
        conditions.append("O.order_date BETWEEN ? AND ?")
        params.extend([start_date_str, end_date_str])

    if food_id is not None and food_id != 0 and str(food_id).upper() != 'ALL':
        conditions.append("F.id = ?")
        params.append(food_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " GROUP BY F.id, F.name ORDER BY total_revenue DESC"

    try:
        cursor.execute(query, tuple(params))
        report_data = cursor.fetchall()
        return report_data
    except sqlite3.Error as e:
        print(f"Database error in get_food_sales_report: {e}")
        return []
    finally:
        conn.close()

def _calculate_date_range(time_period_key):
    """calculate date range"""
    end_date = datetime.now()
    start_date = None

    if time_period_key == "today":
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_period_key == "last_7_days":
        start_date = end_date - timedelta(days=7)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_period_key == "this_month":
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif time_period_key == "all_time":
        return None, None 
    else:
        print(f"Warning: Unknown time_period_key: {time_period_key} in _calculate_date_range. Defaulting to all_time.")
        return None, None

    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    return start_date_str, end_date_str

def get_customer_order_summary_report(time_period_key):
    """Order summary report for all customers (number of orders, total purchases)"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    
    start_date_str, end_date_str = _calculate_date_range(time_period_key)
    
    query = """
        SELECT 
            U.full_name, 
            COUNT(O.id) as order_count,
            SUM(O.total_price) as total_spent
        FROM Orders O
        JOIN Users U ON O.user_id = U.id
    """
    params = []
    conditions = []

    if start_date_str and end_date_str:
        conditions.append("O.order_date BETWEEN ? AND ?")
        params.extend([start_date_str, end_date_str])
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " GROUP BY U.id, U.full_name ORDER BY total_spent DESC"
    
    print(f"DEBUG: get_customer_order_summary_report query: {query} with params: {params}")
    try:
        cursor.execute(query, tuple(params))
        report_data = cursor.fetchall()
        return report_data
    except sqlite3.Error as e:
        print(f"Database error in get_customer_order_summary_report: {e}")
        return []
    finally:
        conn.close()

def get_orders_for_specific_customer(customer_id, time_period_key):
    """return one customer's orders list by time period"""
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    start_date_str, end_date_str = _calculate_date_range(time_period_key)

    query = """
        SELECT
            O.id, 
            O.order_date, 
            O.total_price, 
            O.status
        FROM Orders O
        WHERE O.user_id = ?
    """
    params = [customer_id]
    
    if start_date_str and end_date_str:
        query += " AND O.order_date BETWEEN ? AND ?"
        params.extend([start_date_str, end_date_str])
        
    query += " ORDER BY O.order_date DESC"

    print(f"DEBUG: get_orders_for_specific_customer query: {query} with params: {params}")
    try:
        cursor.execute(query, tuple(params))
        report_data = cursor.fetchall()
        return report_data
    except sqlite3.Error as e:
        print(f"Database error in get_orders_for_specific_customer: {e}")
        return []
    finally:
        conn.close()

# --------- Admin Dashboard ---------
def get_top_selling_foods(limit=3):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT F.name, SUM(OI.quantity * OI.price_per_item) as total_revenue
        FROM OrderItems OI
        JOIN Foods F ON OI.food_id = F.id
        GROUP BY F.id, F.name
        ORDER BY total_revenue DESC
        LIMIT ?
    """, (limit,))
    top_foods = cursor.fetchall()
    return top_foods

def get_top_ordering_customers(limit=3):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT U.full_name, COUNT(O.id) as order_count
    FROM Orders O
    JOIN Users U ON O.user_id = U.id
    GROUP BY U.id, U.full_name
    ORDER BY order_count DESC
    LIMIT ?
    """, (limit,))
    top_users = cursor.fetchall()
    return top_users

def get_sales_summary_for_period(period_key):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    now = datetime.now()
    if period_key == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif period_key == "this_week":
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    else:
        conn.close()
        return 0, 0.0
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    query = """
        SELECT 
            COUNT(id) as order_count,
            SUM(total_price) as total_revenue
        FROM Orders
        WHERE order_date BETWEEN ? AND ?
    """
    params = (start_date_str, end_date_str)
    try:
        cursor.execute(query, params)
        result = cursor.fetchone()
        order_count = result[0] if result and result[0] is not None else 0
        total_revenue = result[1] if result and result[1] is not None else 0.0
        return order_count, total_revenue
    except sqlite3.Error as e:
        print(f"Database error in get_sales_summary_for_period: {e}")
        return 0, 0.0
    finally:
        conn.close()

def get_low_stock_foods(threshold=5):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    query = """
            SELECT name, inventory
            FROM Foods
            WHERE inventory < ? AND inventory > 0 
            ORDER BY inventory ASC
        """
    params = (threshold,)
    try:
        cursor.execute(query, params)
        low_stock_foods = cursor.fetchall()
        return low_stock_foods
    except sqlite3.Error as e:
        print(f"Database error in get_general_stats: {e}")
        return 0, 0
    finally:
        conn.close()

def get_general_stats():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    total_customers = 0
    total_food_items = 0
    try:
        cursor.execute("SELECT COUNT(id) FROM Users WHERE role = 'customer'")
        result_users = cursor.fetchone()
        total_customers = result_users[0] if result_users else 0

        cursor.execute("SELECT COUNT(id) FROM Foods")
        result_foods = cursor.fetchone()
        total_food_items = result_foods[0] if result_foods else 0
        
        return total_customers, total_food_items
    except sqlite3.Error as e:
        print(f"Database error in get_general_stats: {e}")
        return 0, 0
    finally:
        conn.close()
