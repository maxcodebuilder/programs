name = input ("Hello! What is your name? ")
birth_date = input ("Is it your birthday today? ")
year = input ("What year is it? ")
birth_year = input ("What year were you born? ")
age = int(year) - int(birth_year)
print ("Hello, " + name + "! You are " + str(age) + " years old.")
if birth_date == "yes":
    print ("Happy birthday, " + name + "!")
if birth_date == "no":
    print ("Oh, okay.")