

#from modelo import Modelo
#from scrapper import Scrapper
from actividad_4.scrapper_yahoo import Scrapper_yahoo
import pkg_resources
import time
import pandas as pd


ruta = pkg_resources.resource_filename(__name__,'static')
nombre_tabla ="ind_dolar_yahoo"
nombre_tabla_dos ="ind_dolar_yahoo_rep"
ruta_sql = "{}/sql/script_create_yahoo.sql".format(ruta)
ruta_xlsx ="{}/xlsx/2024_10_25.json".format(ruta)
driver_ruta = "{}/driver/chromedriver.exe".format(ruta) #D:\UIDigital\PAD_202402\repositorios\Actividad_1 Necesidad\src\actividdad_1\static\driver\chromedriver.exe
#driver_ruta = "D:/UIDigital/PAD_202402/repositorios/Actividad_1 Necesidad/src/actividdad_1/static/driver/chromedriver.exe"
url="https://www.bancolombia.com/empresas/capital-inteligente/investigaciones-economicas/indicadores"
url_yahoo_financiera=r'https://es-us.finanzas.yahoo.com/quote/ES{}3DF/history/'.format('%')
df = pd.DataFrame()
scrapper = Scrapper_yahoo(driver_ruta=driver_ruta, url=url_yahoo_financiera)
scrapper.cargar_url()
time.sleep(10)
df,df_dos = scrapper.obtener_tabla("//table")
df.to_json("datos.json")
