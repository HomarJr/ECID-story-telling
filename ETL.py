import glob
import pandas as pd

# Patrón de búsqueda de todos los archivos en la carpeta
patron = '**/sinac*DatosAbiertos.csv'

# Lista de columnas que nos interesan para cada rango de años
filtro_columnas = {
  '2008': [
    'fecha_nacimiento_nac_vivo',
    'semanas_gestacion_nac_vivo',
    'talla_nac_vivo',
    'peso_nac_vivo',
    'procedimiento_utilizado',
    'entidad_nacimiento'
  ],
  '2009': [
    'fecha_nacimiento_nac_vivo',
    'semanas_gestacion_nac_vivo',
    'talla_nac_vivo',
    'peso_nac_vivo',
    'procedimiento_utilizado',
    'entidad_nacimiento'
  ],
  '2010': [
    'fecha_nacimiento_nac_vivo',
    'semanas_gestacion_nac_vivo',
    'talla_nac_vivo',
    'peso_nac_vivo',
    'procedimiento_utilizado',
    'entidad_nacimiento'
  ],
  '2011': [
    'fecha_nacimiento_nac_vivo',
    'semanas_gestacion_nac_vivo',
    'talla_nac_vivo',
    'peso_nac_vivo',
    'procedimiento_utilizado',
    'entidad_nacimiento'
  ],
  '2012': [
    'fecha_nacimiento_nac_vivo',
    'semanas_gestacion_nac_vivo',
    'talla_nac_vivo',
    'peso_nac_vivo',
    'procedimiento_utilizado',
    'entidad_nacimiento'
  ],
  '2013': [
    'fecha_nacimiento_nac_vivo',
    'semanas_gestacion_nac_vivo',
    'talla_nac_vivo',
    'peso_nac_vivo',
    'procedimiento_utilizado',
    'entidad_nacimiento'
  ],
  '2014': [
    'fecha_nacimiento_nac_vivo',
    'semanas_gestacion_nac_vivo',
    'talla_nac_vivo',
    'peso_nac_vivo',
    'procedimiento_utilizado',
    'entidad_nacimiento'
  ],
  '2015': [
    'fecha_nacimiento_nac_vivo',
    'semanas_gestacion_nac_vivo',
    'talla_nac_vivo',
    'peso_nac_vivo',
    'procedimiento_utilizado',
    'entidad_nacimiento'
  ],
  '2016': [
    'fecha_nacimiento_nac_vivo',
    'semanas_gestacion_nac_vivo',
    'talla_nac_vivo',
    'peso_nac_vivo',
    'procedimiento_utilizado',
    'entidad_nacimiento'
  ],
  '2017': [
    'FECH_NACH',
    'SEXOH',
    'GESTACH',
    'TALLAH',
    'PESOH',
    'PROCNAC',
    'ENT_NAC'
  ],
  '2018': [
    'FECH_NACH',
    'SEXOH',
    'GESTACH',
    'TALLAH',
    'PESOH',
    'PROCNAC',
    'ENT_NAC'
  ],
  '2019': [
    'FECH_NACH',
    'SEXOH',
    'GESTACH',
    'TALLAH',
    'PESOH',
    'PROCNAC',
    'ENT_NAC'
  ],
  '2020': [
    'FECHANACIMIENTO',
    'SEXO',
    'EDADGESTACIONAL',
    'TALLA',
    'PESO',
    'ENTIDADFEDERATIVAPARTO',
    'TIPOCESAREA'
  ],
  '2021': [
    'FECHANACIMIENTO',
    'SEXO',
    'EDADGESTACIONAL',
    'TALLA',
    'PESO',
    'ENTIDADFEDERATIVAPARTO',
    'TIPOCESAREA'
  ],
  '2022': [
    'FECHANACIMIENTO',
    'SEXO',
    'EDADGESTACIONAL',
    'TALLA',
    'PESO',
    'ENTIDADFEDERATIVAPARTO',
    'TIPOCESAREA'
  ],
}

# Definir los nuevos nombres de columna
nuevos_nombres_columnas = {
    'fecha_nacimiento_nac_vivo': 'fecha_nac',
    'FECH_NACH': 'fecha_nac',
    'FECHANACIMIENTO': 'fecha_nac',
    'EDADGESTACIONAL': 'edad_gestal',
    'GESTACH': 'edad_gestal',
    'semanas_gestacion_nac_vivo': 'edad_gestal',
    'TALLA': 'talla',
    'talla_nac_vivo': 'talla',
    'TALLAH': 'talla',
    'PESO': 'peso',
    'peso_nac_vivo': 'peso',
    'PESOH': 'peso',
    'procedimiento_utilizado': 'procedimiento',
    'PROCNAC': 'procedimiento',
    'TIPOCESAREA': 'procedimiento',
    'entidad_nacimiento': 'entidad',
    'ENT_NAC': 'entidad',
    'ENTIDADFEDERATIVAPARTO': 'entidad',
    'SEXOH': 'sexo',
    'SEXO': 'sexo'
}

# Definir como se va a renombrar las entidades (a partir de 2017)
mapa_entidades = {
  0: 'NO ESPECIFICADO',
  1: 'AGUASCALIENTES',
  2: 'BAJA CALIFORNIA',
  3: 'BAJA CALIFORNIA SUR',
  4: 'CAMPECHE',
  5: 'COAHUILA DE ZARAGOZA',
  6: 'COLIMA',
  7: 'CHIAPAS',
  8: 'CHIHUAHUA',
  9: 'CIUDAD DE MÉXICO',
  'CIUDAD DE MEXICO': 'CIUDAD DE MÉXICO',
  10: 'DURANGO',
  11: 'GUANAJUATO',
  12: 'GUERRERO',
  13: 'HIDALGO',
  14: 'JALISCO',
  15: 'MÉXICO',
  'MEXICO': 'MÉXICO',
  16: 'MICHOACÁN DE OCAMPO',
  'MICHOACAN DE OCAMPO': 'MICHOACÁN DE OCAMPO',
  17: 'MORELOS',
  18: 'NAYARIT',
  19: 'NUEVO LEÓN',
  'NUEVO LEON': 'NUEVO LEÓN',
  20: 'OAXACA',
  21: 'PUEBLA',
  22: 'QUERÉTARO',
  'QUERETARO': 'QUERÉTARO',
  'QUERETARO  DE ARTEAGA': 'QUERÉTARO',
  23: 'QUINTANA ROO',
  24: 'SAN LUIS POTOSÍ',
  'SAN LUIS POTOSI': 'SAN LUIS POTOSÍ',
  25: 'SINALOA',
  26: 'SONORA',
  27: 'TABASCO',
  28: 'TAMAULIPAS',
  29: 'TLAXCALA',
  30: 'VERACRUZ DE IGNACIO DE LA LLAVE',
  31: 'YUCATÁN',
  'YUCATAN': 'YUCATÁN',
  32: 'ZACATECAS',
  88: 'NO APLICA',
  99: 'SE IGNORA',
  'N.E.': 'NO ESPECIFICADO',
  2100: 'NO ESPECIFICADO',
  99999: 'NO ESPECIFICADO'
}

# Definir como se va a renombrar los tipos de procedimientos (a partir de 2017)
mapa_procedimiento = {
  0: 'NO ESPECIFICADO',
  1: 'EUTÓCICO',
  2: 'CESÁREA',
  3: 'FARCEPS',
  4: 'DISTACICO',
  8: 'OTRO',
  9: 'NO ESPECIFICADO',
  'N.E.': 'NO ESPECIFICADO',
  'FÓRCEPS': 'FARCEPS',
  'DISTÓCICO': 'DISTACICO'
}

# Lista para almacenar los DataFrames filtrados y renombrados
dataframes = []
dataframes_small = []

# Itera sobre todos los archivos que coincidan con el patrón
for archivo in glob.glob(patron):
    # Lee una hoja de cálculo Excel y la convierte en un DataFrame
    dataframe = pd.read_csv(archivo, low_memory=False)
    # Filtrar solamente las columnas que nos interesan
    año = archivo.split('sinac')[1][:4]
    dataframe = dataframe[filtro_columnas[año]]
    # Renombrar las columnas
    dataframe.rename(columns=nuevos_nombres_columnas, inplace=True)
    # Convertir numeros a texto y/o corregir errores detectatos a mano
    dataframe['procedimiento'] = dataframe['procedimiento'].replace(mapa_procedimiento)
    dataframe['entidad'] = dataframe['entidad'].replace(mapa_entidades)
    # Agregar el DataFrame filtrado y renombrado a la lista
    dataframes.append(dataframe)
    dataframes_small.append(dataframe.head(10))

# Concatenar todos los DataFrames en uno solo
combined_dataframe = pd.concat(dataframes, ignore_index=True)
combined_dataframe_small = pd.concat(dataframes_small, ignore_index=True)

# Guardar el DataFrame combinado en un archivo CSV
combined_dataframe.to_csv('combined.csv', index=False)
combined_dataframe_small.to_csv('combined_small.csv', index=False)

# Mostrar todos los valores de las columnas
for column in combined_dataframe[['procedimiento', 'entidad', 'sexo']]:
    print(f'todos los datos unicos para {column}')
    print(sorted(list(combined_dataframe[column].unique())))
