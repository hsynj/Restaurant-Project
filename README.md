# Restaurant Management System (Desktop POS)

A feature-rich, desktop Point-of-Sale (POS) system for a take-out restaurant, built with Python and the PySide6 (Qt for Python) framework. This application provides a complete, role-based workflow for managing restaurant operations, from customer ordering to admin oversight.

## Key Features

### Admin Panel
- **📊 Dashboard:** Get an at-a-glance overview of key metrics, including top-selling foods, top customers by order count, daily/weekly sales summaries, and low-stock alerts.
- **🍔 Food Management:** Full CRUD (Create, Read, Update, Delete) functionality for managing food items, including name, price, inventory, and image paths.
- **👥 User Management:** Full CRUD for users (customers, admins). Includes a role-based access system.
- **💰 Discount Management:** Create and manage various types of discount codes (percentage or fixed amount) with detailed parameters like validity dates, usage limits, and minimum purchase amounts.
- **📋 Order Management:** View all customer orders, see detailed item lists for each order, update order status (e.g., "Preparing", "Shipped", "Delivered"), and cancel orders (which correctly restocks inventory and refunds the user's wallet).
- **📈 Reporting System:** Generate dynamic reports for:
  - **Food Sales:** Analyze total quantity sold and revenue per food item for various time periods (today, last 7 days, this month, all time).
  - **Customer Orders:** Generate a summary of total orders and spending per customer, or view a detailed list of all orders for a specific customer.
  - **Chart Visualization:** Reports are accompanied by Matplotlib charts for easier data interpretation.

### Customer Panel
- **🔐 Secure Authentication:** A modern, integrated page for user login and new account registration.
- **🖼️ Visual Menu:** Browse a dynamic, scrollable grid of food items, each displayed with an image, name, and price.
- **🛒 Interactive Shopping Cart:** Add items to the cart with a double-click. The cart view updates in real-time.
- **💸 Wallet System:** Each customer has a personal wallet to manage their balance. Orders are paid for using the wallet, and funds can be added via a dedicated top-up panel.
- **🏷️ Discount Application:** Apply valid discount codes to the shopping cart and see the final price update instantly.
- **📜 Order History & Timeline:** View a complete history of past orders. Select any order to see its current status in a simple timeline format (Registered, Preparing, Shipped, Delivered).
- **🎁 Usable Discounts View:** A dedicated tab lists all currently active and valid discount codes available to the user.

### Seller Panel (Planned)
- **📦 Order Fulfillment Workflow:** A dedicated interface for staff to view incoming customer orders in real-time.
- **🔄 Status Management:** Easily update order statuses through the entire fulfillment cycle (e.g., "Preparing," "Ready for Pickup," "Shipped," "Delivered").
- **📞 Point-of-Sale (POS) Functionality:** Ability to create new orders and register new customers directly, catering to phone or walk-in clients.
- 
## Screenshots

## Tech Stack

- **Language:** Python
- **GUI Framework:** PySide6 (The official Python bindings for Qt)
- **Database:** SQLite3 (for a lightweight, file-based database)
- **Charting/Plotting:** Matplotlib (for generating charts in the reporting module)
- **RTL Text Handling:** `arabic_reshaper` and `python-bidi` for proper Persian text rendering in Matplotlib charts.

## Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

- Python 3.8+
- `pip` package manager

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    cd your-repository-name
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the virtual environment
    python -m venv venv

    # Activate it (on Windows)
    .\venv\Scripts\activate
    
    # Or on macOS/Linux
    # source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **(Optional but Recommended) Seed the database with sample data:**
    The project includes a script to populate the database with a rich set of sample users, foods, discounts, and historical orders to test all features. Run the database handler directly:
    ```bash
    python database/db_handler.py
    ```

5.  **Run the application:**
    Execute the main runner script:
    ```bash
    python main_runner.py
    ```

## Usage

After seeding the database, you can log in with the following sample credentials:

-   **Admin Account:**
    -   Username: `admin`
    -   Password: `admin123`
-   **Seller Account:**
    -   Username: `seller`
    -   Password: `sel123`
-   **Customer Account:**
    -   Username: `ali_reza`
    -   Password: `pass1`
    -   (Or any other customer created in the seed script)

## Project Structure
The project is organized into packages for better maintainability:
-   `main_runner.py`: The main entry point of the application.
-   `database/`: Contains the SQLite database file and the `db_handler.py` module for all database interactions.
-   `ui/`: Contains all PySide6 UI classes, separated into main windows, dialogs, and custom widgets.
-   `core_logic/`: Holds business logic classes (e.g., `ShoppingCart`) that are independent of the UI.
-   `assets/`: For static files like stylesheets (`.qss`) and images.
