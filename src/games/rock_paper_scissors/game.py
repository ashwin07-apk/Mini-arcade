import random
choices = ["rock", "paper", "scissors"]
computer = random.choice(choices)
you = input("Enter rock,papaer, or scissores: ").lower()
print("Computer chose:", computer)
if you not in choices:
    print("invalid choice!")
elif you == computer:
   print("IT's a tie!")
elif (you == "rock" and computer == "scissors") or \
     (you == "paper" and computer == "rock") or \
     (you =="scissors" and computer == "papaer"):
    print("YOU WON!!!!!!!")
else:
    print("computer wins!")
