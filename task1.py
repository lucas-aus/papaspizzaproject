import platform, subprocess, sqlite3, json, sys
from datetime import date
from collections import defaultdict

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
        self.total_pizzas = 0

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
            self.discount_eligible = True
        else:
            self.discount_eligible = False
    
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
            self.discounted_cost = round(self.subtotal * 0.95, 2) #Dicounts price by 5%
        
    def CalculateFinalCost(self): #Adds GST of 10% to find the final total cost
        if self.discount_eligible == True:
            self.cost = round(self.discounted_cost * 1.1, 2)
        else:
            self.cost = round(self.subtotal * 1.1, 2)

    def DisplayPizzas(self): #Just outputs the order information to the user.
        ClearScreen()
        print(f"Order For {self.name}")
        print("")
        print("Order:")
        pizza_types = ["Pepperoni", "Chicken Supreme", "BBQ Meatlovers", "Veg Supreme", "Hawaiian", "Margherita"]
        for i in range(len(pizza_types)):
            current_pizza = pizza_types[i]
            print(f"{self.pizzas[current_pizza]} {current_pizza} Pizzas")
            self.total_pizzas += self.pizzas[current_pizza]
        print("")
        print(f"Total number of pizzas: {self.total_pizzas}")
        print("")
    
    def DisplayOrderCost(self):
        print(f"Subtotal: ${self.subtotal} AUD")
        if self.discount_eligible == True:
            print(f"5% Discount applied. New price of ${self.discounted_cost} AUD")
            print("")
            print(f"GST: ${round(self.discounted_cost / 10, 2)}")
        else:
            print("")
            print(f"GST: ${round(self.subtotal / 10, 2)}")
        print("")
        print(f"Final total: ${self.cost}")

    
    def CreateTable(self):
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
    
    def StoreOrder(self):
        conn = sqlite3.connect("orders_database.db")
        cursor = conn.cursor()
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
        if self.discount_eligible == True:
            order_tuple = (date.today().isoformat(), self.name, json.dumps(self.pizzas), self.discount_eligible, self.discounted_cost, self.cost)
        else:
            order_tuple = (date.today().isoformat(), self.name, json.dumps(self.pizzas), self.discount_eligible, self.subtotal, self.cost)
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
    
    def DisplayOrderCost(self):
        print(f"Subtotal: ${self.subtotal} AUD")
        if self.discount_eligible == True:
            print(f"5% Discount applied. New price of ${self.discounted_cost} AUD")
        print("")
        print(f"$8 Delivery Surcharge applied. New price of ${self.surcharge_cost} AUD")
        print("")
        print(f"GST of ${round(self.surcharge_cost/ 10, 2)}")
        print(f"Final Price: ${self.cost} AUD")
    
    def StoreOrder(self): #This will store the data for the Delivered Orders.
        conn = sqlite3.connect("orders_database.db")
        cursor = conn.cursor()
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
        order_tuple = (date.today().isoformat(), self.name, json.dumps(self.pizzas), self.discount_eligible, self.surcharge_cost, self.cost)
        #the pizzas part of the object is stored as a JSON file because dictionaries cannot be saved to SQLite (as far as I know)
        cursor.execute(query, order_tuple)
        conn.commit()
        conn.close()

class Summary:
    def __init__(self):
        self.pizza_total = defaultdict(int)
        self.order_number = ''
        self.total_net_revenue = 0
        self.total_gross_revenue = 0
        self.conn = sqlite3.connect("orders_database.db")
        self.cursor = self.conn.cursor()

    def CollectOrders(self):
        self.cursor.execute("SELECT COUNT(order_date) FROM orders WHERE order_date = DATE('now')") #gets the total number of orders from today
        order_number = self.cursor.fetchone()
        self.order_number = order_number[0] #This takes the integer out of the tuple

        self.cursor.execute("SELECT pizza_data FROM orders WHERE order_date = DATE('now')") #Gets a list of all of the pizza ordered data from the database
        pizzas_data = self.cursor.fetchall()
        for (json_str,) in pizzas_data: #this block of code will make the attribute pizza_data show the sum of each pizza type bought
            pizza_dict = json.loads(json_str)
            for pizza, qty in pizza_dict.items():
                self.pizza_total[pizza] += qty
    
        self.cursor.execute("SELECT subtotal_before_gst FROM orders WHERE order_date = DATE('now')") #Gets all of the Subtotals from orders today
        subtotal_data = self.cursor.fetchall()
        for i in subtotal_data:
            self.total_net_revenue += i[0]
            self.total_net_revenue = round(self.total_net_revenue, 2)
    
        self.cursor.execute("SELECT total_after_gst FROM orders WHERE order_date = DATE('now')") #collect all of the final costs from the orders
        totals_data = self.cursor.fetchall()
        for i in totals_data:
            self.total_gross_revenue += i[0]
            self.total_gross_revenue = round(self.total_gross_revenue, 2)

    def OrderSummary(self):
        print(f"Order Summary for {date.today().isoformat()}")
        print("")
        print(f"Total number of orders: {self.order_number}")
        print("")
        for pizzas in self.pizza_total: #Will output the number of each pizza type bought today
            print(f"Number of {pizzas} pizzas bought today: {self.pizza_total[pizzas]}")
        print("")
        print(f"Total Gross Revenue (Including GST): ${self.total_gross_revenue}")
        print("")
        print(f"Total Net Revenue (After GST is removed): ${self.total_net_revenue}")

def NewOrder(): #The function that will create order objects and call methods
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
    name.DisplayPizzas()
    name.DisplayOrderCost()
    name.CreateTable()
    name.StoreOrder()

def InputTypeCheck(inputted, inputtype, message): #This function will check if the inputted value is of the right type, and will continually take the input with a specific message until it is of the right type.
    while True:
        if inputtype == 'integer':
            try:
                int(inputted)
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

def ChooseFunction():
    choose_function = input("Would you like to input a new order, see today's order summary, or exit? (Input ORDER or SUMMARY or EXIT) ")
    choose_function = InputValueCheck(choose_function, ["ORDER", "SUMMARY", "EXIT"], "Please input either ORDER or SUMMARY or EXIT. Would you like to input a new order or see today's order summary or exit? ")
    if choose_function == "ORDER":
        NewOrder()
        print("")
        ChooseFunction()
    elif choose_function == "SUMMARY":
        password_input = input("What is the employee password? ")
        password = "employeepassword" #the password required to see the order summary
        if password_input != password:
            ClearScreen()
            print("Invalid password entered.")
            ChooseFunction()
        else:
            ClearScreen()
            summary = Summary()
            summary.CollectOrders()
            summary.OrderSummary()
            print("")
            ChooseFunction()
    elif choose_function == "EXIT":
        sys.exit()

ChooseFunction()