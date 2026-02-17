import plotly.graph_objects as go
from plotly.io import write_html

def create_pollution_histogram(data, pollutant_type):
    """
    Creates a histogram for NO₂, PM₁₀, O₃, SOMO₃₅, AOT₄₀, or PM₂.₅.

    Returns:
    plotly.graph_objects.Figure: The created figure
    """
    if pollutant_type == 'Somo 35':
        column_name = 'Moyenne annuelle de somo 35 (ug/m3.jour)'
    elif pollutant_type == 'AOT 40':
        column_name = "Moyenne annuelle d'AOT 40 (ug/m3.heure)"
    elif pollutant_type == 'PM25':
        column_name = 'Moyenne annuelle de concentration de PM25 (ug/m3)'
    else:
        column_name = f'Moyenne annuelle de concentration de {pollutant_type} (ug/m3)'
    values = data[column_name]

    trace = go.Histogram(
        x=values,
        name=f'Distribution {pollutant_type}',
        nbinsx=30,
        marker_color='rgb(70, 130, 180)',  # Bleu acier, plus visible
        hovertemplate="<b>Concentration</b>: %{x:.1f} µg/m³<br>" +
                     "Nombre de communes: %{y}<extra></extra>"
    )

    layout = go.Layout(
        title=dict(
            text=f'Distribution des concentrations de {pollutant_type}',
            font=dict(size=24)
        ),
        xaxis=dict(
            title='Concentration de SOMO 35 (µg/m³)' if pollutant_type == 'SOMO 35'
            else 'Concentration de AOT 40 (µg/m³)' if pollutant_type == 'AOT 40'
            else f'Concentration de {pollutant_type} (µg/m³)',  
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray'
        ),
        yaxis=dict(
            title='Nombre de communes',
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray'
        )
    )

    fig = go.Figure(data=[trace], layout=layout)
    return fig