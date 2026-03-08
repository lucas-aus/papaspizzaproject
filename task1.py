class Order:
    def __init__(self, name): #function for defining all of the attributes of the class
        self.name = name
        self.pizzas = {
            "Pepperoni" : 0,
            "Chicken Supreme" : 0,
            "BBQ Meatlovers" : 0,
            "Veg Supreme" : 0,
            "Hawaiian" : 0,
            "Margherita" : 0
        }
        self.discount_eligible = False
        self.subtotal = float(0)
        self.cost = float(0)

class DeliveredOrder(Order): #DeliveredOrder is a child class of the class Order.
    def __init__(self, name):
        Order.__init__(self, name) #calls the attribute defining the Order classes attributes
        self.surcharge = 8