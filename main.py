import random
import math
import matplotlib.pyplot as plt
import matplotlib.tri as tri


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


sim_step = 1000000
width, height = 64, 64
temperature_init, temperature_MAX, temperature_step = 0.5, 8, 0.3
temperature = temperature_init
spin = [1, -1]
j = 1
h_field_init, h_field_MAX, h_field_step = -3, 3, 0.3
h_field = h_field_init
data_number = 0
h_field_MAX_step = int((h_field_MAX-h_field_init)/h_field_step)
temperature_MAX_step = int(temperature_MAX/temperature_step)
delta_energy = 0
grid = [[0 for w in range(width)] for h in range(height)]

numElement = temperature_MAX_step * h_field_MAX_step
data_temperature = [0] * numElement
data_mag_per_site = [0] * numElement
data_susceptibility = [0] * numElement
data_energy_per_site = [0] * numElement
data_specific_heat = [0] * numElement
data_h_field = [0] * numElement

plot_data_temperature = []
plot_data_mag = []
plot_data_energy = []
plot_data_susceptibility = []
plot_data_specific_heat = []

for h_f in range(1, h_field_MAX_step+1):
    for t in range(1, temperature_MAX_step+1):
        data_number += 1
        # Initialization of the random grid
        for w in range(width):
            for h in range(height):
                grid[h][w] = random.choice(spin)
        for i in range(sim_step):

            # Choose a random cell, and a random probability of thermal excitation
            randChoice = [random.randint(0, width-1), random.randint(0, height-1)]
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

        # Compute physical properties :

        energy_per_site_moy = compute_energy_moy(grid, j, h_field)

        energy_per_site_moy_square = compute_energy_moy_square(grid, j, h_field)

        mag_per_site_moy = compute_mag_moy(grid)

        mag_per_site_moy_square = compute_mag_moy_square(grid)

        specific_heat = 1 / temperature * (- energy_per_site_moy**2 + energy_per_site_moy_square)

        susceptibility = 1 / temperature**2 * (- mag_per_site_moy**2 + mag_per_site_moy_square)

        # Put the data in a list
        data_energy_per_site[data_number-1] = energy_per_site_moy
        data_mag_per_site[data_number-1] = mag_per_site_moy
        data_susceptibility[data_number-1] = susceptibility
        data_temperature[data_number-1] = temperature
        data_specific_heat[data_number-1] = specific_heat
        data_h_field[data_number-1] = h_field

        temperature += temperature_step

        print("(", h_f, "/", h_field_MAX_step, ")", "step", t, "from step", temperature_MAX_step,
              "(", round(data_number * 100 / (h_field_MAX_step * temperature_MAX_step), 2), "% )")
    temperature = temperature_init
    h_field += h_field_step

with open("data.txt", 'w', encoding='utf8') as f:
    f.write("temperature, energy_per_site, mag_per_site, susceptibility, specific_heat, h_field")
    f.write("\n")

    for ii in range(len(data_temperature)):
        string = str(data_temperature[ii]) + "," \
                 + str(data_energy_per_site[ii]) \
                 + "," + str(data_mag_per_site[ii]) \
                 + "," + str(data_susceptibility[ii]) \
                 + "," + str(data_specific_heat[ii]) \
                 + "," + str(data_h_field[ii])

        f.write(string)
        f.write("\n")
print("save complete")

print("Plotting graphs...")
for k in range(len(data_temperature)):
    if data_h_field[k] == h_field_init:
        plot_data_temperature.append(data_temperature[k])
        plot_data_specific_heat.append(data_specific_heat[k])
        plot_data_susceptibility.append(data_susceptibility[k])
        plot_data_energy.append(data_energy_per_site[k])
        plot_data_mag.append(data_mag_per_site[k])

triangles = tri.Triangulation(data_temperature, data_h_field)

print(plot_data_mag)
print(plot_data_energy)

plt.figure(1)
plt.subplot(121)
plt.plot(plot_data_temperature, plot_data_specific_heat)
plt.xlabel('Temperature')
plt.ylabel('Specific heat')
plt.subplot(122)
plt.plot(plot_data_temperature, plot_data_susceptibility)
plt.xlabel('Temperature')
plt.ylabel('Susceptibility')
'''
plt.subplot(223)
plt.subplot(plot_data_temperature, plot_data_mag)
plt.xlabel('Temperature')
plt.ylabel('magnetisation per site')
plt.subplot(224)
plt.subplot(plot_data_temperature, plot_data_energy)
plt.xlabel('Temperature')
plt.ylabel('Energy per site')
'''

fig_2 = plt.figure(2)

ax_1 = fig_2.add_subplot(111, projection='3d')
ax_1.plot_trisurf(triangles, data_susceptibility, cmap=plt.cm.CMRmap)
ax_1.set_xlabel('Temperature')
ax_1.set_ylabel('h field')
ax_1.set_zlabel('Susceptiblity')

fig_3 = plt.figure(3)
ax_2 = fig_3.add_subplot(111, projection='3d')
ax_2.plot_trisurf(triangles, data_specific_heat, cmap=plt.cm.CMRmap)
ax_2.set_xlabel('Temperature')
ax_2.set_ylabel('h field')
ax_2.set_zlabel('Specific heat')
print("Graphs plotted")
plt.show()