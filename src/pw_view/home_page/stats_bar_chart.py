import flet as ft
import matplotlib.pyplot as plt

def setup_chart():
    fig, axs = plt.subplots()
    # Data for the bar chart
    fruits = ["Apple", "Blueberry", "Cherry", "Orange"]
    supply = [40, 100, 30, 60]

    # Create the bar chart

    axs.bar(fruits, supply, color=['orange', 'blue', 'red', 'green'])
    # axs.xlabel("Fruit")
    # axs.ylabel("Supply")
    # axs.ylim(0, 110)  # Set y-axis limit to match Plotly chart


    return fig, axs