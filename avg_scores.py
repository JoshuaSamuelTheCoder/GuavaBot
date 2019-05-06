from subprocess import check_output
import statistics as stats
import re

runs = input("Enter number of runs to try: ")
num_scouts = 0
try:
    r = int(runs)
    scores10 = []
    scores20 = []
    scores40 = []
    for i in range(1, r + 1):
        output = check_output(["python","client.py","--solver","solver"])

        a = output[221:229]

        print(a)

        print(a[0:2])
        num_scouts = int(a[0:2])
        print(num_scouts)
        score = float(re.sub(r'[^\d.]+', "", str.split(str(output), "Score: ")[1]))
        print("Attempt " + str(i) + ": " + str(score))

        if num_scouts == 40:
            scores40.append(score)
        elif num_scouts == 20:
            scores20.append(score)
        elif num_scouts == 10:
            scores10.append(score)

    print("Average Score for " + str(r) + " runs: " + "\n")


    if len(scores10) > 0:
        avg10 = stats.mean(scores10)
        print("Average Score for 10 students " + str(avg10) + "\n")
    if len(scores20) > 0:
        avg20 = stats.mean(scores20)
        print("Average Score for 20 students " + str(avg20) + "\n")
    if len(scores40) > 0:
        avg40 = stats.mean(scores40)
        print("Average Score for 40 students " + str(avg40) + "\n")

    exit()

except ValueError:
   print("Error: Not an int")

   print("Average Score for " + str(r) + " runs: " + "\n")


   if len(scores10) > 0:
        avg10 = stats.mean(scores10)
        print("Average Score for 10 students " + str(avg10) + "\n")
   if len(scores20) > 0:
        avg20 = stats.mean(scores20)
        print("Average Score for 20 students " + str(avg20) + "\n")
   if len(scores40) > 0:
        avg40 = stats.mean(scores40)
        print("Average Score for 40 students " + str(avg40) + "\n")



   exit()
