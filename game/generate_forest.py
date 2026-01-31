import csv
import random

with open('forest.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for _ in range(10):
        row = []
        for _ in range(10):
            if random.random() < 0.3:
                row.append(random.choice([84, 85, 86]))
            else:
                row.append(-1)
        writer.writerow(row)
