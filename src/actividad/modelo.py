
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from datetime import datetime
from io import StringIO

class Modelo:
    def __init__(self, host="", port="", nombredb="", user="", password="",schema=""):
        self.host = host
        self.port = port
        self.nombredb = nombredb
        self.user = user
        self.password = password
        self.schema = schema
        self.conection = None
        self.conect()
        
    def conect(self):
        try:
            self.conection = create_engine(
                f'postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.nombredb}'
            )
            with self.conection.connect() as connection:
                print("Conexión exitosa")
        except SQLAlchemyError as e:
            print(f"Conexión errónea: {e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado durante la conexión: {e}")
    
    def create_schema(self, nombre_schema=""):
        try:
            nombre_schema = nombre_schema.replace(".","")
            with self.conection.connect() as conexion:
                create_schema = f'CREATE SCHEMA IF NOT EXISTS {nombre_schema};'
                conexion = conexion.execution_options(isolation_level="AUTOCOMMIT")
                conexion.execute(text(create_schema))
                print("Creación de esquema exitosa")
        except SQLAlchemyError as e:
            print(f"Error al crear el esquema: {e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado al crear el esquema: {e}")
    #nombre_tbl=nombre_tabla,schema=nombre_schema,ruta_sql=ruta_sql
    
    def create_table_dos(self, nombre_tbl="", ruta_sql="",schema=""):
        print(ruta_sql)
        try:
            with open(ruta_sql, 'r') as file:
                script_tabla = file.read()
                print(script_tabla)
            with self.conection.connect() as conexion:
                conexion = conexion.execution_options(isolation_level="AUTOCOMMIT")
                #script_tabla = script_tabla.format(schema,nombre_tbl,columnas)
                script_tabla = script_tabla.format(schema,nombre_tbl)
                print(script_tabla)
                conexion.execute(text(script_tabla))
                print("Creación exitosa de tabla")
        except FileNotFoundError as e:
            print(f"Archivo SQL no encontrado: {e}")
        except SQLAlchemyError as e:
            print(f"Creación errónea de tabla: {e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado al crear la tabla: {e}")
    
    def extension_df(self, ruta_insumo="") :
        df= pd.DataFrame()
        extension = ruta_insumo.split(".")[1].lower()
        if extension == "csv":
            df = pd.read_csv(ruta_insumo, index_col=False,delimiter=";")
        elif extension == "xlsx" or extension == "xls":
            df = pd.read_excel(ruta_insumo, index_col=False)
        elif extension == "json" :
            df = pd.read_json(ruta_insumo)        
        return df   
    def _dos(self,nombre_schema="",nombre_tbl="",ruta_sql=""):
        try:
            with open(ruta_sql,'r') as file:
                script_tabla = file.read()
            with self.conection.connect() as conexion:
                conexion = conexion.execution_options(isolation_level="AUTOCOMMIT")
                conexion.execute(text(script_tabla.format(nombre_schema,nombre_tbl)))
                print("creacion exitosa de tabla")
            print(0)
        except SQLAlchemyError as e:
            print("creacion erronea de tabla : {}".format(e))
    
    def create_table_df(self,ruta_insumo="",  ruta_sql="",nombre_tabla="",schema="", tipo="xlsx"):
        try:
            df = self.extension_df(ruta_insumo)
            columnas=""
            cont=1
            for columna in df.columns:
                tipo=""

                if df[columna].dtype == "float64":
                    tipo= " DECIMAL(6, 2) NOT NULL"
                elif df[columna].dtype == "datetime64[ns]":
                    tipo= " DATE NOT NULL"
                elif df[columna].dtype == "datetime64[ns]":
                    tipo= " DATE NOT NULL"
                elif df[columna].dtype == "int64":
                    tipo= "DECIMAL(6, 2) NOT NULL"
                if cont==1:
                    columnas = " {} {}".format( columna.replace("á","a").replace("Ú","U").replace(";"," ").replace("í","i").lower(), tipo)
                else:
                    columnas = "{} , {} {}".format(columnas, columna.replace("á","a").replace("Ú","U").replace("í","i").lower(), tipo)
                    #print(df[columna].dtype)
                cont=cont+1
            #print(columnas)
            with open(ruta_sql, 'r') as file:
                script_tabla = file.read()
            with self.conection.connect() as conexion:
                conexion = conexion.execution_options(isolation_level="AUTOCOMMIT")
                script_tabla = script_tabla.format(schema,nombre_tabla,columnas)
                conexion.execute(text(script_tabla))
        except FileNotFoundError as e:
            print(f"No se pudo crear el dataframe, archivo no encontrado: {e}")
            return
    
    def create_df_tbl(self,df=pd.DataFrame(),nombre_tabla="",nombre_schema=""):
        try:
            df.to_sql(
                name=nombre_tabla,
                #name=schema_tabla,
                con=self.conection,
                schema=nombre_schema.replace(".",""),  # Asegurar que schema es None
                if_exists="replace",
                index=False
            )
            print(f"Se insertó correctamente en {nombre_tabla}")
        except SQLAlchemyError as e:
            print(f"No se insertó en {nombre_tabla}, error: {e}")
        
    def insert_df(self, ruta_insumo="", df=pd.DataFrame(),nombre_tabla="",nombre_schema="", tipo_insert='append', tipo="xlsx",delimiter=";"):
        fecha_actual = datetime.now()
        schema_tabla = "{}{}".format(nombre_schema,nombre_tabla)
        try:
            if len(ruta_insumo)>0:
                df = self.extension_df(ruta_insumo=ruta_insumo)
                df.columns = df.columns.str.lower()
                df["f_creacion"] = fecha_actual
                df["f_update"] = fecha_actual
            elif len(df)>0:
                df = df
                df.columns = df.columns.str.lower()
                #columnas[6] = 
                #df.rename(columns={'cierre ajustado' : 'cierre_ajustado' }, inplace=True)
                df.to_excel("yahoo.xlsx")
                #df=df[["apertura" ,"alto" ,"bajo" ,"cierre" ,"cierre_ajustado" ,"volumen" ]] = df[["apertura" ,"alto" ,"bajo" ,"cierre" ,"cierre_ajustado" ,"volumen" ]].apply(pd.to_numeric)
                
                #print(df.columns)
        except FileNotFoundError as e:
            print(f"No se pudo crear el dataframe, archivo no encontrado: {e}")
            return
        except Exception as e:
            print(f"No se pudo crear el dataframe: {e}")
            return
        
        try:
            df.to_sql(
                name=nombre_tabla,
                #name=schema_tabla,
                con=self.conection,
                schema=nombre_schema.replace(".",""),  # Asegurar que schema es None
                if_exists=tipo_insert,
                index=False
            )
            print(f"Se insertó correctamente en {nombre_tabla}")
        except SQLAlchemyError as e:
            print(f"No se insertó en {nombre_tabla}, error: {e}")
        except TypeError as e:
            print(f"Error de tipo al insertar en {nombre_tabla}: {e}")
        except Exception as e:
            print(f"No se insertó en {nombre_tabla}, error inesperado: {e}")
            
    def auditar_tabla(self, nombre_tabla, ruta_salida):

        try:
            
            f_hoy = datetime.now().strftime("%Y_%m_%d")
            ruta_txt="{}/auditoria/logs/{}{}.txt".format(ruta_salida,str(f_hoy),nombre_tabla)
            df = pd.read_sql(f"SELECT * FROM {nombre_tabla}", con=self.conection)
            with open(ruta_txt, 'w') as archivo:
                archivo.write("Información del DataFrame:\n")
                buffer = StringIO()
                df.info(buf=buffer)
                archivo.write(buffer.getvalue() + "\n\n")
                archivo.write("Estadísticas descriptivas:\n")
                archivo.write(df.describe().to_string() + "\n\n")
                archivo.write("Número de valores nulos por columna:\n")
                archivo.write(df.isnull().sum().to_string() + "\n\n")
                archivo.write("Dimensiones del DataFrame:\n")
                archivo.write(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}\n")

            print(f"Auditoría de la tabla '{nombre_tabla}' guardada en: {ruta_salida}")

        except SQLAlchemyError as e:
            print(f"Error al consultar la tabla '{nombre_tabla}': {e}")
        except Exception as e:
            print(f"Error al auditar la tabla '{nombre_tabla}': {e}")
