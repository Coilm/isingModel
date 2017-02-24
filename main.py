import random
import math
import atexit


def write_in_file():
    print("Program is closing, saving data...")
    with open("data.txt", 'w', encoding='utf8') as f:
        f.write("temperature, energy_per_site, mag_per_site, susceptibility, specific_heat, h_field")
        f.write("\n")

        for i in range(len(data_temperature)):
            string = str(data_temperature[i]) + "," \
                     + str(data_energy_per_site[i]) \
                     + "," + str(data_mag_per_site[i]) \
                     + "," + str(data_susceptibility[i]) \
                     + "," + str(data_specific_heat[i]) \
                     + "," + str(data_h_field[i])

            f.write(string)
            f.write("\n")
    print("save complete")

def compute_energy_site(grid, j, h_field, w, h):
    f_width = len(grid)
    f_height = len(grid[0])
    energy = 0

    energy += -h_field * grid[w][h]

    if w == 0:
        energy += -j * (grid[w][h]) * ((grid[f_width-1][h]) + (grid[w+1][h]))
    elif w == f_width-1:
        energy += -j * (grid[w][h]) * ((grid[w - 1][h]) + (grid[0][h]))
    else:
        energy += -j * (grid[w][h]) * ((grid[w - 1][h]) + (grid[w + 1][h]))
    if h == 0:
        energy += -j * (grid[w][h]) * ((grid[w][f_height-1]) + (grid[w][h+1]))
    elif h == f_height-1:
        energy += -j * (grid[w][h]) * ((grid[w][h - 1]) + (grid[w][0]))
    else:
        energy += -j * (grid[w][h]) * ((grid[w][h - 1]) + (grid[w][h + 1]))

    return energy


def compute_energy(grid, j, h_field):
    f_width = len(grid)
    f_height = len(grid[0])
    energy = 0

    for w in range(f_width):
        for h in range(f_height):
            energy += compute_energy_site(grid, j, h_field, w, h)

    return energy


def compute_energy_moy(grid, j, h_field):
    f_width = len(grid)
    f_height = len(grid[0])
    energy = 0

    for w in range(f_width):
        for h in range(f_height):
            energy += compute_energy_site(grid, j, h_field, w, h)

    return energy / (f_height * f_width)


def compute_energy_moy_square(grid, j, h_field):
    f_width = len(grid)
    f_height = len(grid[0])
    energy = 0

    for w in range(f_width):
        for h in range(f_height):
            energy += compute_energy_site(grid, j, h_field, w, h)**2

    return energy / (f_height * f_width)


def compute_mag_moy(grid):
    f_width = len(grid)
    f_height = len(grid[0])
    mag = 0

    for w in range(f_width):
        for h in range(f_height):
            mag += grid[h][w]

    return mag / (f_height * f_width)


def compute_mag_moy_square(grid):
    f_width = len(grid)
    f_height = len(grid[0])
    mag = 0

    for w in range(f_width):
        for h in range(f_height):
            mag += grid[h][w]**2

    return mag / (f_width * f_height)

atexit.register(write_in_file)

sim_step = 1000000
width, height = 64, 64
temperature_init, temperature_MAX, temperature_step = 1, 25, 0.1
temperature = temperature_init
spin = [1, -1]
j = 1
h_field_init, h_field_MAX, h_field_step = 0, 5, 0.1
h_field = h_field_init

h_field_MAX_step = int((h_field_MAX-h_field_init)/h_field_step)
temperature_MAX_step = int(temperature_MAX/temperature_step)
delta_energy = 0
grid = [[0 for w in range(width)] for h in range(height)]

numElement = (temperature_MAX_step) * (h_field_MAX_step)
data_temperature = [None] * numElement
data_mag_per_site = [None] * numElement
data_susceptibility = [None] * numElement
data_energy_per_site = [None] * numElement
data_specific_heat = [None] * numElement
data_h_field = [None] * numElement

for h_f in range(1, h_field_MAX_step+1):
    for t in range(1, temperature_MAX_step+1):
        # Initialization of the random grid
        for w in range(width):
            for h in range(height):
                grid[h][w] = random.choice(spin)

        for i in range(sim_step):

            # Choose a random cell, and a random probability of thermal excitation
            randChoice = [random.randint(0, width-1), random.randint(1, height-1)]
            rand_thermal = random.random()

            # Flip the spin of the cell from above
            if grid[randChoice[0]][randChoice[1]] == 1:
                grid[randChoice[0]][randChoice[1]] = -1
            else:
                grid[randChoice[0]][randChoice[1]] = 1

            # Compute the change in energy
            delta_energy = compute_energy_site(grid, j, h_field, randChoice[0], randChoice[1])

            # thermal agitation
            if delta_energy > 0 and rand_thermal > math.exp(-1/temperature * delta_energy):
                if grid[randChoice[0]][randChoice[1]] == 1:
                    grid[randChoice[0]][randChoice[1]] = -1
                else:
                    grid[randChoice[0]][randChoice[1]] = 1

        # for h in range(height):
        #     print(grid[h])

        # Compute physical properties :
        energy_per_site_moy = compute_energy_moy(grid, j, h_field)

        energy_per_site_moy_square = compute_energy_moy_square(grid, j, h_field)

        mag_per_site_moy = compute_mag_moy(grid)

        mag_per_site_moy_square = compute_mag_moy_square(grid)

        specific_heat = 1 / temperature * (- energy_per_site_moy**2 + energy_per_site_moy_square)

        susceptibility = 1 / temperature**2 * (- mag_per_site_moy**2 + mag_per_site_moy_square)

        # Put the data in a list
        data_energy_per_site[h_f*t] = energy_per_site_moy
        data_mag_per_site[h_f*t] = mag_per_site_moy
        data_susceptibility[h_f*t] = susceptibility
        data_temperature[h_f*t] = temperature
        data_specific_heat[h_f*t] = specific_heat
        data_h_field[h_f*t] = h_field

        temperature += temperature_step
        print("(", h_f, "/", h_field_MAX_step, ")", "step", t, "from step", temperature_MAX_step)
    temperature = temperature_init
    h_field += h_field_step

print("energy per site :", data_energy_per_site)
print("magnetization per site :", data_mag_per_site)
print("susceptibility : ", data_susceptibility)
print("specific heat :", data_specific_heat)
print("temperature :", data_temperature)

'''
# Normalize data
susceptibility_MAX = max(data_susceptibility)
susceptibility_MIN = min(data_susceptibility)
specific_heat_MAX = max(data_specific_heat)
specific_heat_MIN = min(data_specific_heat)
temperature_MIN = min(data_temperature)
temperature_critique = data_temperature[data_specific_heat.index(max(data_specific_heat))]
for l in range(len(data_temperature)):
    # data_energy_per_site[l] /= max(data_energy_per_site)
    # data_mag_per_site[l] /= max(data_mag_per_site)
    data_susceptibility[l] = (data_susceptibility[l] - susceptibility_MIN) / (susceptibility_MAX - susceptibility_MIN)
    data_specific_heat[l] = (data_specific_heat[l] - specific_heat_MIN) / (specific_heat_MAX - specific_heat_MIN)
    data_temperature[l] /= temperature_critique
print("Normalized data :")
print("energy per site :", data_energy_per_site)
print("magnetization per site :", data_mag_per_site)
print("susceptibility : ", data_susceptibility)
print("specific heat :", data_specific_heat)
print("temperature :", data_temperature)
print("h field :", data_h_field)
'''

'''
for h in range(height):
    print(grid[h])
'''