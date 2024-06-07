import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd
import folium
import shapely.geometry
from branca.colormap import LinearColormap
from datetime import datetime


df1 = pd.read_csv('**\lunardata.txt')
df2 = pd.read_csv('**\combined.csv')

# Filter the first DataFrame
# luna_values = [16, 17, 20, 21] # luna llena + rango
# luna_values = [0, 10, 20, 30]
# filtered_df1 = df1[df1['luna'].isin(luna_values)]
filtered_df1 = df1.copy()

# Convert the 'year', 'month', 'day' columns to a single 'date' column
filtered_df1['date'] = pd.to_datetime(filtered_df1[['year', 'month', 'day']])

# Convert 'fecha_nac' in the second DataFrame to datetime
df2['fecha_nac'] = pd.to_datetime(df2['fecha_nac'], format='%d/%m/%Y')

# Merge the DataFrames on the date
merged_df = pd.merge(filtered_df1, df2, how='inner', left_on='date', right_on='fecha_nac')

# Asignar las fases lunares
def fase_lunar(luna):
    if luna == 0:
        return 'Luna Nueva'
    elif luna == 10:
        return 'Cuarto Creciente'
    elif luna == 20:
        return 'Luna Llena'
    elif luna == 30:
        return 'Cuarto Menguante'
    else:
        return 'Otras Fases'
merged_df['fase_lunar'] = merged_df['luna'].apply(fase_lunar)

print(merged_df)




# Styles
color = '#EC9059'


########## Distribucion de nacimientos a lo largo del tiempo (prematuros) ##########

# Count the occurrences of each year
year_counts = merged_df['year'].value_counts().reset_index()
year_counts.columns = ['year', 'count']

# Create a 2D bar chart with the specified color and style
fig = px.bar(year_counts, x='year', y='count', title='Conteo Total de Nacimientos por Año',
                color_discrete_sequence=[color])

fig.update_layout(
    title={'text': 'Conteo Total de Nacimientos por Año', 'x': 0.5, 'xanchor': 'center'},
    xaxis_title='Año',
    yaxis_title='Nacimientos',
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=14),
    xaxis=dict(showgrid=False, linecolor='darkgray', tickmode='linear'),
    yaxis=dict(showgrid=True, gridcolor='lightgray', linecolor='darkgray')
)

fig.show()


########## Distribucion de nacimientos a lo largo del tiempo (prematuros) ##########

# Filtrar el dataframe para excluir las filas donde fase_lunar es "Otras Fases"
df_filtrado = merged_df[(merged_df['fase_lunar'] != 'Otras Fases') & (merged_df['edad_gestal'] < 37) & (merged_df['year'] == 2018)]

# Contar el número de filas para cada fecha
df_filtrado['date_str'] = df_filtrado['date'].astype(str).str[:10]
df_filtrado['Fecha'] = df_filtrado['date_str'].apply(lambda date: datetime.strptime(date, '%Y-%m-%d'))
conteo_por_fecha = df_filtrado.groupby('Fecha').size().reset_index(name='Nacimientos Prematuros')

# Filtrar las fechas únicas donde la columna 'luna' tiene un valor de 30
fechas_con_luna_30 = df_filtrado[df_filtrado['luna'] == 30]['date_str'].unique()
fechas_con_luna_30_datetime = [datetime.strptime(fecha, '%Y-%m-%d') for fecha in fechas_con_luna_30]

# Crear el gráfico de línea usando Plotly
fig = px.line(conteo_por_fecha, x='Fecha', y='Nacimientos Prematuros', title='Distribución de Naciemientos de Prematuros a Través del Tiempo', line_shape='linear')

# Update the line color
fig.update_traces(line=dict(color=color))

# Agregar líneas verticales punteadas para las fechas con luna 30
for fecha in fechas_con_luna_30:
    marker_date = datetime.strptime(fecha, '%Y-%m-%d')
    fig.add_shape(
        type="line",
        x0=marker_date, y0=0,
        x1=marker_date, y1=1,
        xref='x', yref='paper',
        line=dict(color="#F1BC9D", width=2, dash="dot")
    )

# Update x-axis to show only the labels
fig.update_xaxes(
    tickvals=fechas_con_luna_30_datetime,
    tickformat='%d-%m-%Y'
)

fig.show()


########## Porcentaje de nacimientos prematuros y no prematuros en cada fase lunar ##########

# Filtrar las fases distintas de 'Otras Fases'
merged_filtered_df = merged_df[merged_df['fase_lunar'] != 'Otras Fases']

# Contar el número de nacimientos por fase lunar
nacimientos_fase = merged_filtered_df['fase_lunar'].value_counts().reset_index()
nacimientos_fase.columns = ['Fase Lunar', 'Número de Nacimientos']

# Calcular el porcentaje de prematuros y no prematuros por fase lunar
prematuros_por_fase = merged_filtered_df[merged_filtered_df['edad_gestal'] < 37]['fase_lunar'].value_counts(normalize=True).reset_index()
prematuros_por_fase.columns = ['Fase Lunar', 'Porcentaje de Prematuros']

no_prematuros_por_fase = 1 - prematuros_por_fase['Porcentaje de Prematuros']
prematuros_por_fase['Porcentaje de Prematuros'] = prematuros_por_fase['Porcentaje de Prematuros'] * 100

# Fusionar los DataFrames de prematuros y no prematuros por fase lunar
nacimientos_fase = pd.merge(nacimientos_fase, prematuros_por_fase, on='Fase Lunar', how='left')
nacimientos_fase['Porcentaje de No Prematuros'] = no_prematuros_por_fase * 100

# Create the first graph (Percentage of Premature Births)
fig1 = px.bar(nacimientos_fase, x='Fase Lunar', y='Porcentaje de Prematuros',
              title='Porcentaje de nacimientos prematuros en cada fase lunar',
              labels={'Porcentaje de Prematuros': 'Porcentaje de Nacimientos', 'Fase Lunar': 'Fase Lunar'},
              color_discrete_sequence=[color])

# Create the second graph (Percentage of Non-Premature Births)
fig2 = px.bar(nacimientos_fase, x='Fase Lunar', y='Porcentaje de No Prematuros',
              title='Porcentaje de nacimientos no prematuros en cada fase lunar',
              labels={'Porcentaje de No Prematuros': 'Porcentaje de Nacimientos', 'Fase Lunar': 'Fase Lunar'},
              color_discrete_sequence=[color])

# Configure the layout of the graphs
fig = make_subplots(rows=1, cols=2, subplot_titles=("Porcentaje de Prematuros", "Porcentaje de No Prematuros"))

# Add the graphs to the layout
fig.add_trace(fig1['data'][0], row=1, col=1)
fig.add_trace(fig2['data'][0], row=1, col=2)

# Update the layout of the graphs
fig.update_layout(
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=14),
    xaxis=dict(showgrid=False, linecolor='darkgray', tickmode='linear'),
    yaxis=dict(showgrid=True, gridcolor='lightgray', linecolor='darkgray'),
    xaxis2=dict(showgrid=False, linecolor='darkgray', tickmode='linear'),
    yaxis2=dict(showgrid=True, gridcolor='lightgray', linecolor='darkgray')
)

# Update y-axes to add percentage symbols and set range
fig.update_yaxes(ticksuffix='% ', range=[22.5, 27.5], row=1, col=1)
fig.update_yaxes(ticksuffix='% ', range=[72.5, 77.5], row=1, col=2)

# Show the graph
fig.show()


########## Comparación del porcentaje de niñas y niños nacidos en luna llena y en cada fase lunar ##########

# Crear una lista con las fases de interés
fases_interes = ['Luna Nueva', 'Cuarto Creciente', 'Luna Llena', 'Cuarto Menguante']

# Filtrar los datos para incluir solo las fases de interés y los sexos 1 y 2 (niños y niñas)
merged_filtered_df = merged_df[(merged_df['fase_lunar'].isin(fases_interes)) & (merged_df['sexo'].isin([1, 2]))]

# Contar el número total de nacimientos en cada fase lunar
total_por_fase = merged_filtered_df.groupby('fase_lunar')['sexo'].count().reset_index()
total_por_fase.columns = ['fase_lunar', 'Total de Nacimientos']

# Contar el número de niñas y niños nacidos en cada fase lunar
niñas_niños_por_fase = merged_filtered_df.groupby(['fase_lunar', 'sexo'])['sexo'].count().unstack(fill_value=0).reset_index()

# Calcular los porcentajes de niñas y niños por fase lunar
niñas_niños_por_fase['Masculino'] = (niñas_niños_por_fase[1] / total_por_fase['Total de Nacimientos']) * 100
niñas_niños_por_fase['Femenino'] = (niñas_niños_por_fase[2] / total_por_fase['Total de Nacimientos']) * 100

# Reorganizar los datos para el gráfico
df_comparacion_porcentaje = pd.melt(niñas_niños_por_fase, id_vars=['fase_lunar'],
                                    value_vars=['Masculino', 'Femenino'],
                                    var_name='Sexo', value_name='Porcentaje')

fig = px.bar(df_comparacion_porcentaje, x='fase_lunar', y='Porcentaje', color='Sexo', barmode='group',
               title='Porcentaje de niñas y niños nacidos en cada fase lunar',
               labels={'Porcentaje': 'Porcentaje de Nacimientos (%)', 'fase_lunar': 'Fase Lunar', 'Sexo': 'Sexo'},
               color_discrete_sequence=['#F1A477', '#F1BC9D'])  # Specify the desired colors

fig.update_layout(
    title={'text': 'Porcentaje de niñas y niños nacidos en cada fase lunar', 'x': 0.5, 'xanchor': 'center'},
    xaxis_title='Fase Lunar',
    yaxis_title='Porcentaje de Nacimientos',
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=14),
    xaxis=dict(showgrid=False, linecolor='darkgray', tickmode='linear'),
    yaxis=dict(showgrid=True, gridcolor='lightgray', linecolor='darkgray')
)

fig.update_yaxes(ticksuffix='% ', range=[48, 52])

# Mostrar la gráfica
fig.show()


########## Porcentaje de Procedimientos por fase lunar ##########

# Filtrar las fases distintas de 'Otras Fases'
merged_filtered_df = merged_df[merged_df['fase_lunar'] != 'Otras Fases']

# Obtener valores únicos de 'procedimiento' y 'fase_lunar'
procedimientos_unicos = merged_filtered_df['procedimiento'].unique()
fase_lunar_unicas = merged_filtered_df['fase_lunar'].unique()

# Contar las ocurrencias de cada combinación de 'procedimiento' y 'fase_lunar'
conteo_combinaciones = merged_filtered_df.groupby(['procedimiento', 'fase_lunar']).size().unstack(fill_value=0)

# Calcular el total de ocurrencias por fase lunar
total_ocurrencias_por_fase = conteo_combinaciones.sum(axis=1)

# Calcular los porcentajes para el total de ocurrencias por fase lunar
porcentajes_por_fase = (conteo_combinaciones.div(total_ocurrencias_por_fase, axis=0) * 100)

# Calcular los porcentajes para el total de ocurrencias por fase lunar
porcentajes_por_fase = (conteo_combinaciones.div(total_ocurrencias_por_fase, axis=0) * 100)

# Ajuste del cálculo de los porcentajes para cada fase lunar
total_ocurrencias_por_fase_columna = conteo_combinaciones.sum(axis=0)
porcentajes_por_fase = (conteo_combinaciones.div(total_ocurrencias_por_fase_columna, axis=1) * 100)

# Ordenar los porcentajes de mayor a menor
porcentajes_por_fase = porcentajes_por_fase.loc[porcentajes_por_fase.sum(axis=1).sort_values(ascending=False).index]

# Resetear el índice para convertir 'procedimiento' en una columna regular
porcentajes_por_fase = porcentajes_por_fase.reset_index()

# Define the base colors and add three similar colors
colors = ['#F1BC9D', '#F1A477', '#EC9059', '#D98946', '#B5733E', '#8E5D35']

# Create the bar chart
fig = go.Figure()

# Create bars for each 'procedimiento'
for i, procedimiento in enumerate(procedimientos_unicos):
    porcentajes = porcentajes_por_fase.loc[porcentajes_por_fase['procedimiento'] == procedimiento].iloc[:, 1:].squeeze()
    fig.add_trace(go.Bar(
        y=fase_lunar_unicas,
        x=porcentajes,
        name=procedimiento,
        orientation='h',
        marker_color=colors[i % len(colors)]
    ))

# Customize the layout
fig.update_layout(
    title={
        'text': 'Porcentaje de Procedimientos por Fase Lunar',
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis_title='Porcentaje',
    yaxis_title='Fase Lunar',
    barmode='stack',
    bargap=0.15,
    bargroupgap=0.1,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=14),
    xaxis=dict(
        showgrid=False,
        linecolor='darkgray',
        tickmode='array',
        tickvals=[i for i in range(0, 101, 20)],
        ticktext=[f'{i}%' for i in range(0, 101, 20)]
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='lightgray',
        linecolor='darkgray'
    )
)

# Order the labels in the legend
fig.update_layout(legend=dict(traceorder='normal'))

# Show the chart
fig.show()

########## Cuántos nacimientos (porcentaje) hay por entidad ##########

# Contar los nacimientos totales por entidad
nacimientos_por_entidad = merged_df['entidad'].value_counts().reset_index()
nacimientos_por_entidad.columns = ['entidad', 'nacimientos_totales']
nacimientos_totales = nacimientos_por_entidad['nacimientos_totales'].sum()

# Calcular el porcentaje de nacimientos por entidad
nacimientos_por_entidad['porcentaje_nacimientos'] = (nacimientos_por_entidad['nacimientos_totales'] / nacimientos_totales) * 100

# Filtrar las entidades del 0 al 32
datos_por_entidad = nacimientos_por_entidad.head(33)

# Cargar el archivo GeoJSON de México con los límites de los estados
url_geojson = 'https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json'
mexico_geojson = gpd.read_file(url_geojson)

# Unir los datos de nacimientos con el GeoDataFrame
# Diccionario de mapeo de nombres de entidades
mapeo_entidades = {
    'MÉXICO': 'México',
    'VERACRUZ DE IGNACIO DE LA LLAVE': 'Veracruz',
    'DISTRITO FEDERAL': 'Ciudad de México',
    'MICHOACÁN DE OCAMPO': 'Michoacán',
    'COAHUILA DE ZARAGOZA': 'Coahuila',
    'BAJA CALIFORNIA': 'Baja California',
    'SAN LUIS POTOSÍ': 'San Luis Potosí',
    'CIUDAD DE MÉXICO': 'Ciudad de México',
    'QUINTANA ROO': 'Quintana Roo',
    'YUCATÁN': 'Yucatán',
    'NUEVO LEÓN': 'Nuevo León',
    'Baja California Sur': 'Baja California Sur',
    'Baja California': 'Baja California',
    'Aguascalientes': 'Aguascalientes',
    'BAJA CALIFORNIA SUR': 'Baja California Sur',
    'ZACATECAS': 'Zacatecas',
    'TLAXCALA': 'Tlaxcala',
    'TAMAULIPAS': 'Tamaulipas',
    'TABASCO': 'Tabasco',
    'SONORA': 'Sonora',
    'SINALOA': 'Sinaloa',
    'QUERÉTARO': 'Querétaro',
    'PUEBLA': 'Puebla',
    'OAXACA': 'Oaxaca',
    'NAYARIT': 'Nayarit',
    'MORELOS': 'Morelos',
    'JALISCO': 'Jalisco',
    'HIDALGO': 'Hidalgo',
    'GUERRERO': 'Guerrero',
    'GUANAJUATO': 'Guanajuato',
    'DURANGO': 'Durango',
    'COLIMA': 'Colima',
    'CHIHUAHUA': 'Chihuahua',
    'CHIAPAS': 'Chiapas',
    'CAMPECHE': 'Campeche',
    'AGUASCALIENTES': 'Aguascalientes'
}
datos_por_entidad['name'] = datos_por_entidad['entidad'].map(mapeo_entidades)
mexico_geojson = mexico_geojson.merge(datos_por_entidad, on='name', how='left')

# Define the color map
colors = ['#F1BC9D', '#F1A477', '#EC9059', '#D98946', '#B5733E', '#8E5D35']
colormap = LinearColormap(colors, vmin=mexico_geojson['porcentaje_nacimientos'].min(), vmax=mexico_geojson['porcentaje_nacimientos'].max())
colormap.caption = 'Porcentaje de Nacimientos (%)'

# Convert the DataFrame to a GeoJSON-like dictionary
features = []
for _, row in mexico_geojson.iterrows():
    feature = {
        "type": "Feature",
        "geometry": shapely.geometry.mapping(row["geometry"]),
        "properties": {
            "name": row["name"],
            "porcentaje_nacimientos": row["porcentaje_nacimientos"]
        }
    }
    features.append(feature)

geojson_data = {
    "type": "FeatureCollection",
    "features": features
}

# Crear el mapa de México con el color asignado según el porcentaje de nacimientos
mapa = folium.Map(location=[23.6345, -102.5528], zoom_start=6)

# Add the choropleth layer manually
for feature in geojson_data['features']:
    properties = feature['properties']
    region = properties['name']
    porcentaje_nacimientos = properties['porcentaje_nacimientos']
    
    color = colormap(porcentaje_nacimientos)
    folium.GeoJson(
        feature,
        style_function=lambda x, color=color: {'fillColor': color, 'color': 'black', 'weight': 0.5, 'fillOpacity': 0.7},
        tooltip=folium.GeoJsonTooltip(fields=['name', 'porcentaje_nacimientos'],
                                      aliases=['Estado:', 'Porcentaje de Nacimientos:'])
    ).add_to(mapa)

# Add the colormap to the map
colormap.add_to(mapa)

# Guardar el mapa en un archivo HTML
mapa.save('mapa_nacimientos.html')


########## Cuántos nacimientos de prematuros (porcentaje) hay por entidad ##########

# Filtrar los nacimientos prematuros (edad gestacional < 37 semanas)
prematuros_df = merged_df[merged_df['edad_gestal'] < 37]

# Contar los nacimientos totales por entidad
nacimientos_por_entidad = merged_df['entidad'].value_counts().reset_index()
nacimientos_por_entidad.columns = ['entidad', 'nacimientos_totales']

# Contar los nacimientos prematuros por entidad
prematuros_por_entidad = prematuros_df['entidad'].value_counts().reset_index()
prematuros_por_entidad.columns = ['entidad', 'nacimientos_prematuros']

# Unir los datos de nacimientos totales y prematuros por entidad
datos_por_entidad = pd.merge(nacimientos_por_entidad, prematuros_por_entidad, on='entidad', how='left')

# Calcular el porcentaje de nacimientos prematuros por entidad
datos_por_entidad['porcentaje_prematuros'] = (datos_por_entidad['nacimientos_prematuros'] / datos_por_entidad['nacimientos_totales']) * 100

# Filtrar las entidades del 0 al 32
datos_por_entidad = datos_por_entidad.head(33)

# Cargar el archivo GeoJSON de México con los límites de los estados
url_geojson = 'https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json'
mexico_geojson = gpd.read_file(url_geojson)

# Unir los datos de nacimientos prematuros con el GeoDataFrame
# Diccionario de mapeo de nombres de entidades
mapeo_entidades = {
    'MÉXICO': 'México',
    'VERACRUZ DE IGNACIO DE LA LLAVE': 'Veracruz',
    'DISTRITO FEDERAL': 'Ciudad de México',
    'MICHOACÁN DE OCAMPO': 'Michoacán',
    'COAHUILA DE ZARAGOZA': 'Coahuila',
    'BAJA CALIFORNIA': 'Baja California',
    'SAN LUIS POTOSÍ': 'San Luis Potosí',
    'CIUDAD DE MÉXICO': 'Ciudad de México',
    'QUINTANA ROO': 'Quintana Roo',
    'YUCATÁN': 'Yucatán',
    'NUEVO LEÓN': 'Nuevo León',
    'Baja California Sur': 'Baja California Sur',
    'Baja California': 'Baja California',
    'Aguascalientes': 'Aguascalientes',
    'BAJA CALIFORNIA SUR': 'Baja California Sur',
    'ZACATECAS': 'Zacatecas',
    'TLAXCALA': 'Tlaxcala',
    'TAMAULIPAS': 'Tamaulipas',
    'TABASCO': 'Tabasco',
    'SONORA': 'Sonora',
    'SINALOA': 'Sinaloa',
    'QUERÉTARO': 'Querétaro',
    'PUEBLA': 'Puebla',
    'OAXACA': 'Oaxaca',
    'NAYARIT': 'Nayarit',
    'MORELOS': 'Morelos',
    'JALISCO': 'Jalisco',
    'HIDALGO': 'Hidalgo',
    'GUERRERO': 'Guerrero',
    'GUANAJUATO': 'Guanajuato',
    'DURANGO': 'Durango',
    'COLIMA': 'Colima',
    'CHIHUAHUA': 'Chihuahua',
    'CHIAPAS': 'Chiapas',
    'CAMPECHE': 'Campeche',
    'AGUASCALIENTES': 'Aguascalientes'
}
datos_por_entidad['name'] = datos_por_entidad['entidad'].map(mapeo_entidades)
mexico_geojson = mexico_geojson.merge(datos_por_entidad, on='name', how='left')

# Define the color map
colors = ['#F1BC9D', '#F1A477', '#EC9059', '#D98946', '#B5733E', '#8E5D35']
colormap = LinearColormap(colors, vmin=mexico_geojson['porcentaje_prematuros'].min(), vmax=mexico_geojson['porcentaje_prematuros'].max())
colormap.caption = 'Porcentaje de Nacimientos Prematuros (%)'

# Convert the DataFrame to a GeoJSON-like dictionary
features = []
for _, row in mexico_geojson.iterrows():
    feature = {
        "type": "Feature",
        "geometry": shapely.geometry.mapping(row["geometry"]),
        "properties": {
            "name": row["name"],
            "porcentaje_prematuros": row["porcentaje_prematuros"]
        }
    }
    features.append(feature)

geojson_data = {
    "type": "FeatureCollection",
    "features": features
}

# Crear el mapa de México con el color asignado según el porcentaje de prematuros
mapa = folium.Map(location=[23.6345, -102.5528], zoom_start=6)

# Add the choropleth layer manually
for feature in geojson_data['features']:
    properties = feature['properties']
    region = properties['name']
    porcentaje_prematuros = properties['porcentaje_prematuros']
    
    color = colormap(porcentaje_prematuros)
    folium.GeoJson(
        feature,
        style_function=lambda x, color=color: {'fillColor': color, 'color': 'black', 'weight': 0.5, 'fillOpacity': 0.7},
        tooltip=folium.GeoJsonTooltip(fields=['name', 'porcentaje_prematuros'],
                                      aliases=['Estado:', 'Porcentaje de Nacimientos Prematuros:'])
    ).add_to(mapa)

# Add the colormap to the map
colormap.add_to(mapa)

# Guardar el mapa en un archivo HTML
mapa.save('mapa_prematuros_porcentaje.html')
