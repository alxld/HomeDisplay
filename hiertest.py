class Grandparent:
    def __init__(self, name):
        self.name = name
        print("Grandparent __init__ called")

class Parent(Grandparent):
    def __init__(self, name, age):
        super().__init__(name)  # Call Grandparent's __init__
        self.age = age
        print("Parent __init__ called")

class Child(Parent):
    def __init__(self, name, age, hobby):
        super().__init__(name, age)  # Call Parent's __init__
        self.hobby = hobby
        print("Child __init__ called")

# Create a child object
child = Child("Alice", 20, "painting")