from dataweb import DataWeb
import pandas as pd



def main():
    dataweb = DataWeb()
    list_indicadores = ["DOLA-USD","EURUSD%3DX","CL%3DF","GC%3DF"] # capa 1
    for indicador in list_indicadores:
        # df = dataweb.obtener_datos(indicador=indicador)
        # df = dataweb.convertir_numericos(df) # capa 2 
        # df = dataweb.formatear_fechas(df,columna_fecha="fecha") # capa 2
        df = dataweb.procesar_indicador_completo(indicador)
        df.to_csv("src/edu_pad/static/csv/yahoo_finance_hist.csv", index=False,mode="a")



if __name__ == "__main__":
    main()