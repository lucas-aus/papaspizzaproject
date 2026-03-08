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

def NewOrder():
    name = str(input("What is the name on the order? "))
    delivery = input("Will this be a delivery? (answer with YES or NO) ")
    delivery = InputTypeCheck(delivery, 'string', "Not a valid string. Will this be a delivery? (answer with YES or NO) ")
    delivery = InputValueCheck(delivery.upper(), ["YES", "NO", ], "Please make sure to input this with YES or NO. Will this be a delivery? ") #Inputted = uppercase version of delivery, values are YES or NO, message is the string at the end.
    if delivery.upper() == "YES":
        name = DeliveredOrder(name)
    elif delivery.upper() == "NO":
        name = Order(name)

def InputTypeCheck(inputted, inputtype, message): #This function will check if the inputted value is of the right type, and will continually take the input with a specific message until it is of the right type.
    while True:
        if inputtype == 'integer':
            try:
                return int(inputted)
            except:
                inputted = input(message) #if converting to an integer creates an error, this will get the user to input it once again.
        elif inputtype == 'string':
            try:
                return str(inputted)
            except:
                inputted = input(message)

def InputValueCheck(inputted, values, message): #This function will make sure that an input is apart of a set of options
    while True:
        if inputted in values:
            return inputted
        else:
            inputted = input(message)

NewOrder()