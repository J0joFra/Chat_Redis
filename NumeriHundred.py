#Scrivere un codice in Python che stampi i numeri da 1 a 100
somma = 0
for number in range(100):
    if number % 7 == 0 and number != 0:
        number += 1
        print("Buzz")
    else:
        somma += number
        print(number)
print(f"La somma dei numeri è {somma}")



