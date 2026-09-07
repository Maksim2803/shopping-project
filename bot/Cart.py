class Cart:
    def __init__(self):
        self.user_cart={}
    def add_product(self,product,quantity):
        if quantity<=0:
            raise ValueError("Количество продукта должно быть больше 0")
        if product in self.user_cart:
            self.user_cart[product]+=quantity
        else:
            self.user_cart[product]=quantity
    def remove_product(self,product):
        if product in self.user_cart:
            self.user_cart.pop(product)
    def show_cart(self):
        return self.user_cart
    def clear_cart(self):
        self.user_cart={}

