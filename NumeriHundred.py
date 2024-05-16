
#Versione definitiva, con punti 1, 2 e 3
somma = 0
MIN = int(input("Inserire numero da cui partire: "))
MAX = int(input("Inserire numero a cui arrivare: "))
for number in range(MIN,MAX + 1):
    if number % 7 == 0 and number != 0:
        number += 1
        print("Buzz")
    else:
        somma += number
        print(number)
print(f"La somma dei numeri è {somma}")

#Collaboratori: Giulio, Jo, Ted