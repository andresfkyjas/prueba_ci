import pandas as pd
import sqlite3
import os

# 1 sobre escribir , 2 actualizar 3 insertar al final

class DataBase:
    def __init__(self):
        self.rutadb = "static/db/dolar_analisis.db"


    def guardar_df(self,df=pd.DataFrame()):
        df = df.copy()
        try:
            conn = sqlite3.connect(self.rutadb)
            df["fecha_create"]= "2025-05-5"
            df["fecha_update"] = "2025-05-5"
            df.to_sql("dolar_analisis",conn,if_exists='replace',index=False)
            print("*******************************************************************")
            print("Datos guardados")
            print("*******************************************************************")
            print("Se guardo el df en base de datos cantidad de registros {str(df.shape)}")
        except Exception as errores:
            print("Error al guardar el df en base de datos {}".format(df.shape))

    def obtener_datos(self,nombre_tabla="dolar_analisis"):
        try:
            conn = sqlite3.connect(self.rutadb)
            consulta = "select * from {}".format(nombre_tabla)
            df = pd.read_sql_query(consulta,conn)
            print("*******************************************************************")
            print("Se obtuvieron los datos de la base datos")
            print("*******************************************************************")
            print("Dase de datos cantidad de registros {}".format(df.shape))
            return df
        except Exception as errores:
            return df
            print("Error al obtener los datos de la tabla {str(nombre_tabla)} en base de datos {str(errores)}")