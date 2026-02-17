import plotly.graph_objects as go
from plotly.io import write_html

def create_pollution_scatter(data, insee_to_commune, pollutant_type):
    """
    Crée un graphique de dispersion pour NO2, PM10 ou O3.
    
    Args:
        data (pd.DataFrame): Le DataFrame contenant les données
        insee_to_commune (dict): Dictionnaire de correspondance codes INSEE vers noms de communes
        pollutant_type (str): Type de polluant ("NO2", "PM10" ou "O3")
    
    Returns:
        plotly.graph_objects.Figure: La figure créée
    """
    # Filter municipalities with more than 1,500 inhabitants and sort by population
    data_filtered = data[data['Population'] > 1500]
    data_sorted = data_filtered.sort_values('Population', ascending=True)
    
    # Prepare data
    communes = [insee_to_commune[code] for code in data_sorted['COM Insee']]
    if pollutant_type == 'Somo 35':
        column_name = 'Moyenne annuelle de somo 35 (ug/m3.jour)'
    elif pollutant_type == 'AOT 40':
        column_name = "Moyenne annuelle d'AOT 40 (ug/m3.heure)"
    elif pollutant_type == 'PM25':
        column_name = 'Moyenne annuelle de concentration de PM25 (ug/m3)'
    else:
        column_name = f'Moyenne annuelle de concentration de {pollutant_type} (ug/m3)'
    concentrations = data_sorted[column_name]
    populations = data_sorted['Population']
    
    # Create the plot
    trace = go.Scatter(
        x=communes,
        y=concentrations,
        mode='markers',
        name=f'Mesures {pollutant_type}',
        marker=dict(
            size=2,
            color=concentrations,
            colorscale=[[0, 'rgb(0,0,255)'], [1, 'rgb(255,0,0)']],  # Bleu à Rouge
            showscale=True
        ),
        hovertemplate="<b>%{x}</b><br>" +
                     f"{pollutant_type}: %{{y:.1f}} µg/m³<br>" +
                     "Population: %{customdata:,.0f} hab.<extra></extra>",
        customdata=populations
    )

    layout = go.Layout(
        title=dict(
            text=f'Concentration moyenne annuelle de {pollutant_type} par population de commune',
            font=dict(size=24)
        ),
        xaxis=dict(
            title='Population des communes > 1500 Hab.',
            tickangle=-45,
            tickfont=dict(size=10),
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray'
        ),
        yaxis=dict(
            title='Concentration de SOMO 35 (µg/m³)' if pollutant_type == 'SOMO 35'
            else 'Concentration de AOT 40 (µg/m³)' if pollutant_type == 'AOT 40'
            else f'Concentration de {pollutant_type} (µg/m³)', 
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray'
        ),
        annotations=[dict(
            x=0.5,
            y=-0.3,
            xref='paper',
            yref='paper',
            text="Liste des communes triées par population croissante",
            showarrow=False,
            font=dict(size=12, style='italic'),
            align='center'
        )],
        margin=dict(b=100)
    )

    fig = go.Figure(data=[trace], layout=layout)
    return fig