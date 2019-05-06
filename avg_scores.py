from subprocess import check_output
import statistics as stats
import re

runs = input("Enter number of runs to try: ")
try:
    r = int(runs)
    scores = []
    for i in range(1, r + 1):
        output = check_output(["python","client.py","--solver","solver"])
        print(output)
        score = float(re.sub(r'[^\d.]+', "", str.split(str(output), "Score: ")[1]))
        print("Attempt " + str(i) + ": " + str(score))
        scores.append(score)

    avg = stats.mean(scores)
    print("Average Score for " + str(r) + " runs: " + str(avg))
    exit()

except ValueError:
   print("Error: Not an int")
   exit()
