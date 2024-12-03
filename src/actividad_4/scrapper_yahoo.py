import pandas as pd # genera informacion matricial 
import time
from selenium import webdriver # importa el modulo de webdriver
from selenium.webdriver.common.by import By #localiza elemento en una pagina web
from selenium.webdriver.chrome.service import Service as ChromeService # Clase servicio para levantar driver chrome
import pandas as pd
from datetime import datetime
#import locale


class Scrapper_yahoo:
    def __init__(self,driver_ruta="",url=""):
        self.url=url
        #locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
        options = webdriver.ChromeOptions() #permite configurar el navegador
        #options.add_argument('--headless') 
        options.add_argument('--no-sandbox') 
        options.add_argument('--disable-dev-shm-usage')
        if len(driver_ruta) >0:
            self.service = ChromeService(executable_path=driver_ruta)
            self.driver = webdriver.Chrome(service=self.service, options=options)
            self.driver.maximize_window()
        else:
            self.driver = webdriver.Chrome(options=options)
        self.meses = {
            "ene": "jan",
            "feb": "feb",
            "mar": "mar",
            "abr": "apr",
            "may": "may",
            "jun": "jun",
            "jul": "jul",
            "ago": "aug",
            "sept": "sep",
            "oct": "oct",
            "nov": "nov",
            "dic": "dec"
        }
        
    
    def cargar_url(self):
        self.driver.get(self.url)
        print("************cargo la url**************")
    def convertir_formato_numero(self,s):
        num=0.0
        if ',' in s and '.' in s:
            # Caso: "6,003.75" -> "6.003,75"
            s = s.replace(',', '')
            #s = s.replace(',', '.')
            # s = s.replace('.', 'temp')  # Reemplaza temporalmente el punto
            # s = s.replace(',', '.')     # Reemplaza las comas por puntos
            # s= s.replace('temp', ',').replace(".","")
            num = float(s)  # Reemplaza la cadena temporal por comas
        elif ',' in s:
            # Caso: "1,069,929" -> "1.069.929"
            num = float(s.replace(',', ''))
        elif '0.0' in s:
            num = float(s.replace('0.0', '0'))
        num = round(num, 2)
        return num
    # def insert_df_db(self,df = pd.DataFrame()):
    #     if len(df)>0:
            
    #         pass
    def obtener_tabla(self,xpath_tabla=""):
        try:
            tabla_element= self.driver.find_element(By.XPATH,xpath_tabla)
            if tabla_element:
                print("existe una tabla")
                columnas = []
                thead = tabla_element.find_element(By.TAG_NAME, "thead")
                header_rows= thead.find_elements(By.TAG_NAME, "tr")
                for tr in header_rows:
                    ths = tr.find_elements(By.TAG_NAME, "th")
                    for th in ths:
                        header = th.text.strip()
                        header = header.lower().replace(' ', '_')
                        columnas.append(header)
                data=[]
                tbody = tabla_element.find_element(By.TAG_NAME, "tbody")
                filas= tbody.find_elements(By.TAG_NAME, "tr")
                fecha_dt=""
                for fila in filas:
                    tds = fila.find_elements(By.TAG_NAME, "td")
                    fila_datos = [td.text.strip() for td in tds]
                    if not fila_datos[0] or fila_datos[0] == '0':
                        fila_datos[0] = datetime.now().strftime("%Y-%m-%d")
                    else:
                        # Convierte la fecha al formato adecuado
                        try:
                            for mes_es, mes_en in self.meses.items():
                                if mes_es in fila_datos[0].lower():
                                    fecha = fila_datos[0].lower().replace(mes_es, mes_en)
                            fecha_dt = datetime.strptime((fecha), "%d %b %Y")
                            fila_datos[0] = fecha_dt.strftime("%Y-%m-%d")
                        except ValueError as e:
                            # Si la fecha no tiene el formato esperado, asigna una fecha por defecto
                            print(e)
                            fila_datos[0] = datetime.now().strftime("%Y-%m-%d")
                    
                    for i in range(1, len(fila_datos)):
                        valor = fila_datos[i].strip()  
                        fila_datos[i] = self.convertir_formato_numero(valor)
                        
                    #fila_datos[1:] = [self.convertir_formato_numero(td.text.strip()) for td in fila_datos[1:]]
                    data.append(fila_datos)
                    # for td in tds:
                    #     header = td.text.strip()
                    #data.append(data_fila)
                #print(columnas)  
                df = pd.DataFrame(data, columns=columnas) 
                df_dos = df.copy()
                #df_dos = df.iloc[1:]
                #print(df.info()) 
                df_tres = self.transformar_df(df_dos)            
                return df,df_tres
        except print(0):
            pass
    def transformar_df(self, df = pd.DataFrame()):
        df = df.copy()
        df.columns = df.columns.str.lower()
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['anio']  = df['fecha'].dt.year
        df['mes'] = df['fecha'].dt.month
        df['dia'] = df['fecha'].dt.day
        df['fecha_num'] = df['fecha'].dt.strftime('%Y%m%d').astype(int)
        df['variacion'] = df['cerrar']-df['apertura']
        df['cierre_max_mes'] = df.groupby(['anio','mes'])['cerrar'].transform('max')
        df['dia_cierre_max_mes'] = df.apply(lambda x: x['fecha'].day if x['cerrar'] == x['cierre_max_mes'] else None, axis= 1)
        df['dia_cierre_max_mes'] = df['dia_cierre_max_mes'].fillna(method='bfill').fillna(method='ffill').astype(int)
        df['subida']= df.apply(lambda x : 1 if x['cerrar'] > x['apertura'] else 0, axis= 1)
        df['p_subida_dia'] = ((df['cerrar']-df['apertura'])/df['apertura']) *100
        df['p_subida_mes'] = df.groupby(['anio','mes'])['p_subida_dia'].transform('mean')
        df['p_subida_anio'] = df.groupby(['anio'])['p_subida_dia'].transform('mean')
        return df
        
        
    def capturar_imagen_tabla(self, xpath_tabla, ruta_imagen="tabla_captura.png"):
        """
        Captura una imagen de la tabla identificada por un xpath específico y la guarda en una ruta.
        """
        f_hoy = datetime.now().strftime("%Y_%m_%d")
        ruta_imagen="{}/auditoria/img/{}.png".format(ruta_imagen,str(f_hoy))
        try:
            tabla_element = self.driver.find_element(By.XPATH, xpath_tabla)
            if tabla_element:
                tabla_element.screenshot(ruta_imagen)
                print(f"Imagen de la tabla capturada y guardada en: {ruta_imagen}")
        except Exception as e:
            print(f"Error al capturar la imagen de la tabla: {e}")

    def cerrar_driver(self):
        self.driver.quit()