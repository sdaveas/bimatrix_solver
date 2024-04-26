import os
import sys
from subprocess import call
import numpy as np

if len(sys.argv) <= 1:
    print("Usage: python csv_lines_to_input_file.py <data_file>")
    exit(1)

def delta_mean(mean_values, equilibria):
    deltas = [0] * len(mean_values)
    for i in range(len(mean_values)):
        deltas[i] = abs(mean_values[i] - equilibria[i])
    mean = sum(deltas) / len(deltas)
    return mean

data_file = sys.argv[1]

data = np.loadtxt(data_file, delimiter=',')

first_matrix_start = 0
first_matrix_end = 64
second_matrix_start = 64
second_matrix_end = 128
mean_values_start = 128
mean_values_end = 136

output_file_name = "min_equilibria.txt"
if output_file_name in os.listdir():
    print("Output file", output_file_name, "already exists.")
    exit(1)

output_file = open(output_file_name, "a")

experiment_count = 0

# Process each line and reshape into two 8x8 matrices
for line in data:
    input_data = "8 8\n\n"

    first_half = line[first_matrix_start:first_matrix_end].reshape((8, 8))
    second_half = line[second_matrix_start:second_matrix_end].reshape((8, 8))
    mean_values = line[mean_values_start:mean_values_end]


    for row in first_half:
        input_data += " ".join(f"{x:.2f}" for x in row)
        input_data += "\n"

    input_data += "\n\n"

    for row in second_half:
        input_data += " ".join(f"{x:.2f}" for x in row)
        input_data += "\n"

    input_file = open("examples/input/temp_input.txt", "w")
    input_file.write(input_data)
    input_file.close()

    temp_output_file = open("tmp_output.txt", "w+")
    call(["python3", "solve_game.py", "-i", "./examples/input/temp_input.txt"], stdout=temp_output_file)
    temp_output_file.close()

    # read the output data 
    temp_output_file = open("tmp_output.txt", "r")
    temp_output_data = temp_output_file.read().split("\n")
    temp_output_file.close()

    # find line with "Decimal Output"
    if "Decimal Output" in temp_output_data:
        wanted_lines_start = temp_output_data.index("Decimal Output") + 2

    # find line with "Rational Output"
    if "Rational Output" in temp_output_data:
        wanted_lines_end = temp_output_data.index("Rational Output")

    needed_lines = temp_output_data[wanted_lines_start:wanted_lines_end]

    equilibria_with_deltas = []
    for line in needed_lines[:-1]:
        values = line.split("EP")[0].split(") ")[-1].split(" ")
        values = values[1:-2]
        equilibrium = []
        for value in values:
            if value != "":
                equilibrium.append(float(value))
        equilibria_with_deltas.append([delta_mean(mean_values, equilibrium), equilibrium])

    equilibria_with_deltas = sorted(equilibria_with_deltas, key=lambda x: x[0])
    print(f"[{experiment_count+1}/{len(data)}] results: {equilibria_with_deltas}")

    min_mean_diff = str(equilibria_with_deltas[0][0])
    equilibrium = equilibria_with_deltas[0][1]
    fmt_equilibrium = ",".join(f"{x:.4f}" for x in equilibrium)
    output_file.write(min_mean_diff + "," + fmt_equilibrium + "\n")

    experiment_count += 1

output_file.close()