def hello():
    print("Hello, World!")

def bye():
    print("Goodbye, World!")

class Greeter:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f"Hello, {self.name}!")

    def farewell(self):
        print(f"Goodbye, {self.name}!")

