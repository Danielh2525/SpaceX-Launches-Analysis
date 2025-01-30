# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}
        ] + [
            {'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()
        ],
        value='ALL',
        placeholder="Select a launch site",
        searchable=True
    ),
    html.Br(),
    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    # Range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=100,
        marks={i: f"{i}" for i in range(int(min_payload), int(max_payload) + 1, 1000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),
    # Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Group by Launch Site and count successes
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='count')
        fig = px.pie(
            success_counts,
            values='count',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failure_count = filtered_df[filtered_df['class'] == 0].shape[0]
        fig = px.pie(
            values=[success_count, failure_count],
            names=['Success', 'Failure'],
            title=f'Success vs. Failure Launches for {selected_site}'
        )
    return fig

# Callback for scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]
    if selected_site == 'ALL':
        title = "Correlation Between Payload and Success for All Sites"
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        title = f"Correlation Between Payload and Success for {selected_site}"
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version',
        title=title,
        labels={'class': 'Launch Outcome (1=Success, 0=Failure)'},
        hover_data=['Launch Site']
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()