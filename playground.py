import plotly.express as px
import pandas as pd

# Data (sum using excel)
sum_1 = 5530517
sum_2 = 5344681

# Calculate the percentages
total = sum_1 + sum_2
percent_1 = (sum_1 / total) * 100
percent_2 = (sum_2 / total) * 100

# Create a DataFrame for the plot
data = {
    'Category': ['Masculino', 'Femenino'],
    'Percentage': [percent_1, percent_2]
}
df_percentage = pd.DataFrame(data)

# Create the bar plot
fig = px.bar(df_percentage, y='Category', x='Percentage', orientation='h',
             title='Porcentaje de niños y niñas nacidos',
             labels={'Percentage': 'Porcentaje de nacimientos (%)', 'Category': 'Sexo'},
             color='Category', color_discrete_sequence=['#F1A477', '#F1BC9D'])

fig.update_layout(
    title={'text': 'Porcentaje de niños y niñas nacidos', 'x': 0.5, 'xanchor': 'center'},
    xaxis_title='Porcentaje de nacimientos',
    yaxis_title='Sexo',
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=14),
    xaxis=dict(showgrid=True, gridcolor='lightgray', linecolor='darkgray'),
    yaxis=dict(showgrid=False, linecolor='darkgray')
)

fig.update_xaxes(ticksuffix='% ', range=[47.5, 52.5])

# Show the plot
fig.show()
