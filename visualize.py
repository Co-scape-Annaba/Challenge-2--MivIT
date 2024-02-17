import base64
from io import BytesIO
import dash
from dash import dcc, html, callback, Output, Input
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# needed data
walmart_color_brand = ['#0071ce', '#ffc220']

month_names = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
    7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

# dataset
walmart_dataset = pd.read_csv('Walmart_sales.csv')

# convert date to datetime and extract te month
walmart_dataset['Date'] = pd.to_datetime(walmart_dataset['Date'], dayfirst=True)
walmart_dataset['Month'] = walmart_dataset['Date'].dt.month

# preparing data for static visualization
monthly_earnings = walmart_dataset.groupby('Month')['Weekly_Sales'].sum().reset_index()
monthly_earnings['Month'] = monthly_earnings['Month'].map(month_names)
sorted_months = monthly_earnings.sort_values(by='Weekly_Sales', ascending=False)['Month'].tolist()
earnings = [monthly_earnings.loc[monthly_earnings['Month'] == month, 'Weekly_Sales'].iloc[0] for month in sorted_months]
total_earnings = monthly_earnings['Weekly_Sales'].sum()
monthly_earnings['Contribution'] = monthly_earnings['Weekly_Sales'] / total_earnings
store_options = [{'label': store, 'value': store} for store in walmart_dataset['Store'].unique()]

# Dual-axis bar-line
fig_bar = px.bar(x=sorted_months, y=earnings, title='Walmart Earnings Across Stores for each Month of all Years',
                 width=800, height=400)
fig_bar.add_scatter(x=sorted_months, y=earnings, mode='lines', name='Earnings Trend',
                    line=dict(color='#ffc220'), marker=dict(symbol='circle', size=8))
fig_bar.update_layout(yaxis2=dict(title='Earnings Trend', side='left'))
fig_bar.update_traces(marker_color='#0071ce')

# Doughnut chart
fig_donut = px.pie(monthly_earnings, values='Contribution', names='Month',
                   title='Contribution of Months to the total Earnings',
                   hole=0.5,  # Create a donut shape
                   )

fig_donut.add_annotation(text=f"Total earnings:", x=0.5, y=0.6, font_size=10, showarrow=False)
fig_donut.add_annotation(text=f"{str(total_earnings)}", x=0.5, y=0.55, font_size=10, showarrow=False)
fig_donut.update_layout(width=800, height=400)

app = dash.Dash(__name__)

# interactive visualization
monthly_earnings = walmart_dataset.groupby(['Store', 'Month'])['Weekly_Sales'].sum().reset_index()
monthly_earnings['Month'] = monthly_earnings['Month'].map(month_names)
sorted_months = monthly_earnings.sort_values(by='Weekly_Sales', ascending=False)['Month'].tolist()
earnings = [monthly_earnings.loc[monthly_earnings['Month'] == month, 'Weekly_Sales'].iloc[0] for month in sorted_months]
total_earnings = monthly_earnings['Weekly_Sales'].sum()
monthly_earnings['Contribution'] = monthly_earnings['Weekly_Sales'] / total_earnings


# webpage layout
app.layout = html.Div([

    html.Div([
        dcc.Graph(id='static-bar-chart', figure=fig_bar),
    ], style={'width': '100vw', 'display': 'flex', 'justify-content': 'center'}),

    html.Div([
        dcc.Dropdown(
            id='store-dropdown',
            options=store_options,
            value=store_options[0]['value'],  # Default value
            multi=False
        ),
        dcc.Graph(id='earnings-bar-chart')
    ], style={'width': '100vw', 'display': 'flex', 'justify-content': 'center'}),

    html.Div([
        dcc.Graph(id='donut-chart', figure=fig_donut),
    ], style={'width': '100vw', 'display': 'flex', 'justify-content': 'center'}),
])


# Define callback to update the bar chart based on store selection
@app.callback(
    Output('earnings-bar-chart', 'figure'),
    [Input('store-dropdown', 'value')]
)
def update_bar_chart(selected_store):
    # Filter data for the selected store
    store_data = monthly_earnings[monthly_earnings['Store'] == selected_store]

    sorted_months = store_data.sort_values(by='Weekly_Sales', ascending=False)['Month'].tolist()
    earnings = [store_data.loc[store_data['Month'] == month, 'Weekly_Sales'].iloc[0] for month in sorted_months]

    # Dual-axis bar-line
    fig_bar = px.bar(x=sorted_months, y=earnings, title=f'Earnings for Store {selected_store} Across Months',
                     width=800, height=400)
    fig_bar.add_scatter(x=sorted_months, y=earnings, mode='lines', name='Earnings Trend',
                        line=dict(color='#ffc220'), marker=dict(symbol='circle', size=8))
    fig_bar.update_layout(yaxis2=dict(title='Earnings Trend', side='left'))
    fig_bar.update_traces(marker_color='#0071ce')

    return fig_bar


if __name__ == '__main__':
    app.run_server(debug=True)
