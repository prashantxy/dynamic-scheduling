import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load and process the CSV file
@st.cache
def load_data(file_path):
    df = pd.read_csv(file_path)
    if 'No__of_Buses' not in df.columns:
        st.error("Error: Column 'No. of Buses' does not exist in the CSV file.")
        return None
    return df

def adjust_frequency(current_freq, density, baseline_density, weight):
    if density > baseline_density:
        return decrease_frequency(current_freq, density, baseline_density, weight)
    elif density < baseline_density:
        return increase_frequency(current_freq, density, baseline_density, weight)
    else:
        return current_freq

def decrease_frequency(current_freq, density, baseline_density, weight):
    change_factor = (density - baseline_density) / baseline_density
    adjustment = int(current_freq * (1 - change_factor * weight))
    return max(5, adjustment)

def increase_frequency(current_freq, density, baseline_density, weight):
    change_factor = (baseline_density - density) / baseline_density
    adjustment = int(current_freq * (1 + change_factor * weight))
    return adjustment

def plot_comparison(initial_df, adjusted_df):
    fig, ax = plt.subplots(figsize=(12, 6))
    time_slots = [f'Time Slot {i+1}' for i in range(5)]
    for i in range(5):
        ax.plot(initial_df[f'Frequency'], label=f'Initial Frequency Time Slot {i+1}', linestyle='--')
        ax.plot(adjusted_df[f'Adjusted_Frequency_{i+1}'], label=f'Adjusted Frequency Time Slot {i+1}')
    
    ax.set_xlabel('Route No.')
    ax.set_ylabel('Frequency')
    ax.set_title('Comparison of Initial and Adjusted Frequencies')
    ax.legend()
    st.pyplot(fig)

st.title("Bus Frequency Adjustment and Visualization")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        st.subheader("Initial Data")
        st.write(df.head())

        # Processing
        baseline_density = df['Density'].mean()
        weights = [0.25, 0.5, 1, 1.25, 1.5]

        for i, weight in enumerate(weights):
            df[f'Adjusted_Frequency_{i+1}'] = df.apply(lambda row: adjust_frequency(row['Frequency'], row['Density'], baseline_density, weight), axis=1)
            df[f'Bus_Requirement_{i+1}'] = df[f'Adjusted_Frequency_{i+1}'] * df['No. of Buses']

        st.subheader("Adjusted Data")
        st.write(df.head())

        # Plot comparison
        st.subheader("Frequency Comparison")
        plot_comparison(df, df)  # Adjust to plot initial vs adjusted

        # Download link for adjusted CSV
        for i in range(5):
            df.to_csv(f'outputfile_{i+1}.csv', index=False)
            st.download_button(label=f"Download Adjusted Data for Time Slot {i+1}",
                               data=f'outputfile_{i+1}.csv',
                               file_name=f'outputfile_{i+1}.csv',
                               mime='text/csv')

