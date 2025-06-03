
from edu_pad.database import DataBase
import pandas as pd



def main():
    database = DataBase()
    df = pd.read_csv("static/csv/data_extractor.csv")
    df_db = database.guardar_df(df)
    df_db2 = database.obtener_datos() # capa 3 guardar 
    df_db2.to_csv("static/csv/data_db.csv", index=False)



if __name__ == "__main__":
    main()