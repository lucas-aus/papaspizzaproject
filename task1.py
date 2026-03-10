import platform, subprocess, sqlite3, json
from datetime import date

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
        self.discounted_cost = float(0)
        self.cost = float(0)

    def OrderPizzas(self):
        pizza_type_list = ["Pepperoni", "Chicken Supreme", "BBQ Meatlovers", "Veg Supreme", "Hawaiian", "Margherita"]
        ordering = True
        while ordering == True:
            pizza_type = input("Which Pizza Type do you want? Pepperoni, Chicken Supreme, BBQ Meatlovers, Veg Supreme, Hawaiian, or Margherita? ")
            pizza_type = InputValueCheck(pizza_type, pizza_type_list, "Please choose from the options Pepperoni, Chicken Supreme, BBQ Meatlovers, Veg Supreme, Hawaiian, or Margherita. ")
            #This code just checks whether the pizza type chosen is apart of the pizza type list

            pizza_number = input(f"How many {pizza_type} pizzas do you want to buy? ")
            pizza_number = InputTypeCheck(pizza_number, 'integer', f"Please enter a number. How many {pizza_type} pizzas do you want to buy? ") #Makes sure the number of pizzas is an integer
            pizza_number = InputRangeCheck(pizza_number, 0, 'none', f"Please input a number 0 or greater. How many {pizza_type} pizzas would you like to order? ") #Checks that there is not a negative number of pizzas ordered.

            self.pizzas[pizza_type] = int(pizza_number) # sets the pizzas dictionary to reflect the order so far
            
            ClearScreen()
            print(f"""Current pizzas ordered:
            {self.pizzas}""")

            finish_order = input("Would you like to order any more pizzas? (YES or NO) ") #Will let the user choose when to stop ordering
            finish_order = InputValueCheck(finish_order.upper(), ["YES", "NO"], "Please answer with YES or NO. Would you like to order more pizzas? ")
            if finish_order.upper() == 'NO':
                ordering = False
    
    def IsMember(self):
        loyalty_member = input("Are you a loyalty member? (YES or NO) ")
        InputValueCheck(loyalty_member.upper(), ["YES", "NO"], "Please answer with YES or NO. Are you a loyalty member? ")

        if loyalty_member.upper() == "YES":
            self.discount_eligible == True
        else:
            self.discount_eligible == False
    
    def CalculateSubtotal(self):
        pizza_prices = {
                "Pepperoni" : 21.00,
                "Chicken Supreme" : 23.50,
                "BBQ Meatlovers" : 25.50,
                "Veg Supreme" : 22.50,
                "Hawaiian" : 19.00,
                "Margherita" : 18.50
            }
        pizzas = ["Pepperoni", "Chicken Supreme", "BBQ Meatlovers", "Veg Supreme", "Hawaiian", "Margherita"]
        for i in range(6):
            current_pizza = pizzas[i]
            self.subtotal += self.pizzas[current_pizza] * pizza_prices[current_pizza]

    def CalculateDiscounts(self):
        if self.subtotal > 100 and self.discount_eligible == False:
            self.discount_eligible = True #Sets discount to true if order costs more than $100
        if self.discount_eligible == True:
            self.discounted_cost = self.subtotal * 0.95 #Dicounts price by 5%
        
    def CalculateFinalCost(self): #Adds GST of 10% to find the final total cost
        if self.discount_eligible == True:
            self.cost = round(self.discounted_cost * 1.1, 2)
        else:
            self.cost = round(self.subtotal * 1.1, 2)

    def DisplayOrder(self):
        ClearScreen()
        print(f"ORDER FOR {self.name}")
        print("")
        print("Order:")
        for i in range(len(self.pizzas)):
            print(f"{self.pizzas[i+1]}")
    
    def StoreOrder(self):
        conn = sqlite3.connect("orders_database.db") #this will connect to the sqlite database and make it if it doesn't exist
        cursor = conn.cursor()
        cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_date TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    pizza_data TEXT NOT NULL,
    had_discount INTEGER NOT NULL,
    subtotal_before_gst REAL NOT NULL,
    total_after_gst REAL NOT NULL
        );
        """)
        conn.commit()
        query = ("""
    INSERT INTO orders (
    order_date,
    customer_name,
    pizza_data,
    had_discount,
    subtotal_before_gst,
    total_after_gst
    ) VALUES (?, ?, ?, ?, ?, ?)
    """)
        order_tuple = (date.today(), self.name, json.dumps(self.pizzas), self.discount_eligible, self.subtotal, self.cost)
        #the pizzas part of the object is stored as a JSON file because dictionaries cannot be saved to SQLite (as far as I know)
        cursor.execute(query, order_tuple)
        conn.commit()
        conn.close()




class DeliveredOrder(Order): #DeliveredOrder is a child class of the class Order.
    def __init__(self, name):
        Order.__init__(self, name) #calls the attribute defining the Order classes attributes
        self.surcharge_cost = float(0)
    
    def AddSurcharge(self):
        if self.discount_eligible == True:
            self.surcharge_cost = self.discounted_cost + 8 #adds $8 surcharge
        else:
            self.surcharge_cost = self.subtotal + 8 #adds $8 surcharge
        self.cost = round(self.surcharge_cost * 1.1, 2) #adds a 10% GST surcharge and rounds to 2 decimal places

def NewOrder():
    name = str(input("What is the name on the order? "))
    delivery = input("Will this be a delivery? (answer with YES or NO) ")
    delivery = InputValueCheck(delivery.upper(), ["YES", "NO", ], "Please make sure to input this with YES or NO. Will this be a delivery? ") #Inputted = uppercase version of delivery, values are YES or NO, message is the string at the end.
    if delivery.upper() == "YES":
        name = DeliveredOrder(name)
    elif delivery.upper() == "NO":
        name = Order(name)
    name.OrderPizzas()
    name.IsMember()
    name.CalculateSubtotal()
    name.CalculateDiscounts()
    if delivery.upper() == "YES":
        name.AddSurcharge()
    elif delivery.upper() == "NO":
        name.CalculateFinalCost()
    print(name.cost)
    name.StoreOrder()

def InputTypeCheck(inputted, inputtype, message): #This function will check if the inputted value is of the right type, and will continually take the input with a specific message until it is of the right type.
    while True:
        if inputtype == 'integer':
            try:
                return int(inputted)
            except:
                inputted = input(message) #if converting to an integer creates an error, this will get the user to input it once again.

def InputValueCheck(inputted, values, message): #This function will make sure that an input is apart of a set of options
    while True:
        if inputted in values:
            return inputted
        else:
            inputted = input(message)

def InputRangeCheck(inputted, lowerbound, upperbound, message): #Makes sure the input is in the range
    while True:
        if lowerbound != "none":
            if int(inputted) < int(lowerbound):
                inputted = input(message)
            else:
                return inputted
        if upperbound != "none":
            if int(inputted) > int(upperbound):
                inputted = input(message)
            else:
                return inputted

def ClearScreen(): #This will clear the terminal to avoid it becoming too cluttered
    # Check the operating system
    if platform.system() == "Windows":
        # Use "cls" command on Windows
        subprocess.run(["cls"], shell=True, check=True)
    else:
        # Use "clear" command on Linux/macOS (POSIX systems)
        subprocess.run(["clear"], check=True)
            

NewOrder()