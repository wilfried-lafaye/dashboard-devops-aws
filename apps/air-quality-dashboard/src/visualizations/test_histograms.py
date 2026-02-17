import pandas as pd
from histograms import create_pollution_histogram
from plotly.io import show

data = pd.read_csv("data/cleaned/cleaned_air_quality_with_year.csv")

# Create the histogram for a pollutant
fig = create_pollution_histogram(data, "NO2")
# Display the figure in a browser window
show(fig)