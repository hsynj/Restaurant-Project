class ShoppingCart:
    def __init__(self):
        """{ food_id: {'name': str, 'price': float, 'quantity': int} }"""
        self.items = {}

    def add_item(self, food_id, food_name, food_price):
        """Add items to shopping cart"""
        if food_id in self.items:
            self.items[food_id]['quantity'] += 1
        else:
            self.items[food_id] = {
                'name': food_name,
                'price':  food_price,
                'quantity': 1
            }
            print(f"Cart updated: {self.items}")


    def get_items(self):
        """Return shopping cart's items"""
        return self.items
    

    def calculate_total(self):
        """Calculate and returning the total amount of the shopping cart"""
        total_price = 0
        for item in self.items.values():
            total_price += item['price'] * item['quantity']
        return total_price
    
    def is_empty(self):
        """Check shopping cart is empty or no"""
        return not self.items
    
    def clear(self):
        """Clear shopping card"""
        self.items.clear()
        print("Cart cleared!")

    def decrease_item_quantity(self, food_id):
        """Decrease selected item quantity -1"""
        if food_id in self.items:
            self.items[food_id]['quantity'] -= 1
            if self.items[food_id]['quantity'] == 0:
                del self.items[food_id]
            return True
        return False

if __name__ == '__main__':
    print("You cant run this file currently, run main.py")