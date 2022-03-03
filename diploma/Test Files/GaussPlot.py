import random
import matplotlib.pyplot as plt


def gaussianPlot(mu, sigma):
    # store the random numbers in a list
    list = []

    for i in range(1000):
        temp = random.gauss(mu, sigma)
        list.append(temp)

    # plotting a graph
    plt.hist(list, bins=200)
    plt.show()
