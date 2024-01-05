import pandas as pd
import matplotlib.pyplot as plt
import eclabfiles as ecf


def plot_max_capacity(mpr_file, theoretical_capacity):
    # Read the ECLab MPR file into a DataFrame
    data = ecf.to_df(mpr_file)

    # Calculate Coulombic Efficiency
    data['Coulombic Efficiency'] = (data['(Q-Qo)'] / data['Q charge/discharge']) * 100

    # Group by 'half cycle' and find the maximum values for charge, discharge, and efficiency within each cycle
    max_charge = data.groupby('half cycle')['Q charge/discharge'].max()
    max_discharge = data.groupby('half cycle')['(Q-Qo)'].max()
    max_efficiency = data.groupby('half cycle')['Coulombic Efficiency'].max()

    # Create a Matplotlib figure
    plt.figure(figsize=(12, 6))

    # Add Max Charge Capacity as a scatter plot
    plt.scatter(max_charge.index, max_charge.values, label='Max Charge Capacity', marker='o', s=50)

    # Add Max Discharge Capacity as a scatter plot
    plt.scatter(max_discharge.index, max_discharge.values, label='Max Discharge Capacity', marker='s', s=50)

    # Add Max Coulombic Efficiency as a scatter plot
    plt.scatter(max_efficiency.index, max_efficiency.values, label='Max Coulombic Efficiency', marker='^', s=50)

    # Set plot labels and legend
    plt.xlabel('Half Cycle')
    plt.ylabel('Capacity / Efficiency (%)')
    plt.title('Max Capacity and Max Coulombic Efficiency vs. Half Cycle')
    plt.legend()

    # Show the plot
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    mpr_file = r'C:\Users\fionn\Desktop\NMRVolt\Test\Cyclerfolder\FF025e_cycle.mpr'
    theoretical_capacity = 1.4  # Adjust this to the theoretical capacity value

    plot_max_capacity(mpr_file, theoretical_capacity)

