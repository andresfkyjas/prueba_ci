import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime

class DataWeb:
    def __init__(self):
        self.url = "https://es.finance.yahoo.com/quote/DOLA-USD/history/"
        # Diccionario con información de ubicación de indicadores
        self.indicator_locations = {
            "DOLA-USD": {
                "name": "Dólar/Peso", 
                "country": "Colombia", 
                "lat": 4.7110, 
                "lon": -74.0721,
                "region": "América del Sur",
                "currency_pair": "COP/USD"
            },
            "EURUSD%3DX": {
                "name": "Euro/Dólar", 
                "country": "Europa", 
                "lat": 50.1109, 
                "lon": 8.6821,
                "region": "Europa",
                "currency_pair": "EUR/USD"
            }, 
            "CL%3DF": {
                "name": "Petróleo WTI", 
                "country": "Estados Unidos", 
                "lat": 39.8283, 
                "lon": -98.5795,
                "region": "América del Norte",
                "currency_pair": "USD"
            },
            "GC%3DF": {
                "name": "Oro", 
                "country": "Global", 
                "lat": 40.7128, 
                "lon": -74.0060,
                "region": "Global",
                "currency_pair": "USD"
            }
        }
    
    def obtener_datos(self, indicador="DOLA-USD"):
        self.url = "https://es.finance.yahoo.com/quote/{}/history/".format(indicador)
        try:
            # url, cabeceras
            headers = {
                'User-Agent': 'Mozilla/5.0'
            }
            respuesta = requests.get(self.url, headers=headers)
            if respuesta.status_code != 200:
                print("La url saco error, no respondio o no existe")
                return pd.DataFrame()
            
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            tabla = soup.select_one('div[data-testid="history-table"] table')
            
            if not tabla:
                print(f"No se encontró tabla para el indicador {indicador}")
                return pd.DataFrame()
            
            nombre_columnas = [th.get_text(strip=True) for th in tabla.thead.find_all('th')]
            filas = []
            for tr in tabla.tbody.find_all('tr'):
                columnas = [td.get_text(strip=True) for td in tr.find_all('td')]
                if len(columnas) == len(nombre_columnas):
                    filas.append(columnas)
            
            df = pd.DataFrame(filas, columns=nombre_columnas).rename(columns={
                'Fecha': 'fecha',
                'Abrir': 'abrir',
                'Máx.': 'max',
                'Mín.': 'min',
                'CerrarPrecio de cierre ajustado para splits.': 'cerrar',
                'Cierre ajustadoPrecio de cierre ajustado para splits y distribuciones de dividendos o plusvalías.': 'cierre_ajustado',
                'Volumen': 'volumen'
            })
            
            df = self.convertir_numericos(df)
            df["indicador"] = indicador
            
            # Agregar información de ubicación
            df = self.agregar_informacion_ubicacion(df, indicador)
            
            print("*******************************************************************")
            print(f"Datos Obtenidos para {indicador}")
            print("*******************************************************************")
            print(df.head())
            
            return df
            
        except Exception as err:
            print(f"Error en la funcion obtener_datos: {err}")
            return pd.DataFrame()

    def agregar_informacion_ubicacion(self, df, indicador):
        """
        Agrega información de ubicación geográfica y metadatos al DataFrame
        
        Parámetros:
        df (pandas.DataFrame): DataFrame con los datos del indicador
        indicador (str): Código del indicador (ej: "DOLA-USD")
        
        Retorna:
        pandas.DataFrame: DataFrame con columnas de ubicación agregadas
        """
        try:
            df_resultado = df.copy()
            
            # Obtener información del indicador
            info = self.indicator_locations.get(indicador, {})
            
            # Agregar columnas de ubicación
            df_resultado['indicator_name'] = info.get('name', indicador)
            df_resultado['country'] = info.get('country', 'Unknown')
            df_resultado['lat'] = info.get('lat', 0.0)
            df_resultado['lon'] = info.get('lon', 0.0)
            df_resultado['region'] = info.get('region', 'Unknown')
            df_resultado['currency_pair'] = info.get('currency_pair', 'Unknown')
            
            print(f"Información de ubicación agregada para {indicador}: {info.get('name', indicador)}")
            
            return df_resultado
            
        except Exception as e:
            print(f"Error al agregar información de ubicación: {e}")
            return df

    def obtener_ubicacion_indicador(self, indicador):
        """
        Obtiene la información de ubicación de un indicador específico
        
        Parámetros:
        indicador (str): Código del indicador
        
        Retorna:
        dict: Diccionario con información de ubicación
        """
        return self.indicator_locations.get(indicador, {
            "name": indicador,
            "country": "Unknown", 
            "lat": 0.0, 
            "lon": 0.0,
            "region": "Unknown",
            "currency_pair": "Unknown"
        })

    def listar_indicadores_disponibles(self):
        """
        Lista todos los indicadores configurados con su información
        
        Retorna:
        dict: Diccionario con todos los indicadores y su información
        """
        return self.indicator_locations

    def convertir_numericos(self, df=pd.DataFrame()):
        df = df.copy()
        if len(df) > 0:
            for col in ('abrir', 'max', 'min', 'cerrar', 'cierre_ajustado', 'volumen'):
                if col in df.columns:
                    df[col] = (df[col]
                              .str.replace(r"\.", "", regex=True)
                              .str.replace(",", '.'))
        return df

    def completar_columnas(self, df, columna_fecha):
        try:
            # Extraer componentes y convertirlos explícitamente a enteros
            df['year'] = df['fecha_dt'].dt.year.astype('Int64')  # Tipo Int64 de pandas maneja NaN
            df['month'] = df['fecha_dt'].dt.month.astype('Int64')
            df['day'] = df['fecha_dt'].dt.day.astype('Int64')
            
            # Agregar columna year_month en formato yyyy-mm
            df['year_month'] = df['fecha_dt'].dt.strftime('%Y-%m')
            
            # Eliminar columna temporal
            df.drop('fecha_dt', axis=1, inplace=True)
            return df
            
        except Exception as e:
            # En caso de error, intentamos al menos devolver el DataFrame sin modificar
            if 'fecha_dt' in df.columns:
                df.drop('fecha_dt', axis=1, inplace=True)
            return df
    
    def formatear_fechas(self, df, columna_fecha='fecha'):
        """
        Convierte el formato de fecha de '1 abr 2004' o '07 may 2025' a 'yyyy-mm-dd' 
        y agrega columnas year, month, day
        
        Parámetros:
        df (pandas.DataFrame): DataFrame que contiene la columna de fechas
        columna_fecha (str): Nombre de la columna que contiene las fechas
        
        Retorna:
        pandas.DataFrame: DataFrame actualizado
        """
        try:
            df_resultado = df.copy()
            
            # Diccionario de mapeo de meses en español a números
            meses = {
                'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 'may': '05', 'jun': '06',
                'jul': '07', 'ago': '08', 'sept': '09', 'oct': '10', 'nov': '11', 'dic': '12'
            }
            
            def convertir_fecha(fecha_str):
                if pd.isna(fecha_str) or not isinstance(fecha_str, str):
                    return None
                    
                # Limpiar la fecha (eliminar comillas y espacios adicionales)
                fecha_str = fecha_str.strip('"\'').strip()
                
                # Extraer partes de la fecha
                partes = fecha_str.split()
                if len(partes) != 3:
                    return None
                    
                dia, mes_abr, año = partes
                mes_abr = mes_abr.lower()
                
                # Verificar si el mes está en nuestro diccionario
                if mes_abr in meses:
                    mes = meses[mes_abr]
                    # Formatear día con ceros a la izquierda si es necesario
                    dia = dia.zfill(2)
                    # Construir fecha en formato ISO (yyyy-mm-dd)
                    return f"{año}-{mes}-{dia}"
                
                return None
            
            # Aplicar la función de conversión a la columna de fechas
            df_resultado[columna_fecha] = df_resultado[columna_fecha].apply(convertir_fecha)
            
            # Convertir a datetime para extraer componentes
            df_resultado['fecha_dt'] = pd.to_datetime(df_resultado[columna_fecha], errors='coerce')
            
            # Completar columnas year, month y day
            return self.completar_columnas(df_resultado, columna_fecha)
            
        except Exception as e:
            print(f"Error en formatear_fechas: {e}")
            return df

    def procesar_indicador_completo(self, indicador):
        """
        Función de conveniencia que procesa completamente un indicador
        (obtiene datos, convierte numéricos, formatea fechas y agrega ubicación)
        
        Parámetros:
        indicador (str): Código del indicador
        
        Retorna:
        pandas.DataFrame: DataFrame completamente procesado
        """
        try:
            print(f"Procesando indicador: {indicador}")
            
            # Paso 1: Obtener datos (ya incluye ubicación)
            df = self.obtener_datos(indicador=indicador)
            
            if df.empty:
                print(f"No se pudieron obtener datos para {indicador}")
                return df
            
            # Paso 2: Convertir numéricos
            df = self.convertir_numericos(df)
            
            # Paso 3: Formatear fechas
            df = self.formatear_fechas(df, columna_fecha="fecha")
            
            print(f"Indicador {indicador} procesado exitosamente")
            return df
            
        except Exception as e:
            print(f"Error al procesar indicador {indicador}: {e}")
            return pd.DataFrame()


# # Ejemplo de uso y testing
# if __name__ == "__main__":
#     # Crear instancia de DataWeb
#     dw = DataWeb()
    
#     # Mostrar indicadores disponibles
#     print("Indicadores disponibles:")
#     for codigo, info in dw.listar_indicadores_disponibles().items():
#         print(f"- {codigo}: {info['name']} ({info['country']})")
    
#     # Probar con un indicador
#     df_test = dw.procesar_indicador_completo("DOLA-USD")
#     if not df_test.empty:
#         print("\nColumnas en el DataFrame final:")
#         print(df_test.columns.tolist())
#         print("\nPrimeras filas:")
#         print(df_test.head())