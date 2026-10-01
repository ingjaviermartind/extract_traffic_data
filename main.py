import pyodbc
import pandas as pd

conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=10.142.16.246\ACCDWH;"
    r"DATABASE=AZTECA_STAGING;"
    r"Trusted_Connection=yes;"
)

query = """
SELECT 
    SER,
    ESTADO_SER,
    CUS,
    CAPACIDADBPS,
    [PLAN]
FROM [DTM].[SF_SERVICE_LEGV2]
WHERE ESTADO_SER NOT IN (
    'Cancelado',
    'Error',
    'En Proceso',
    'Declinado'
)
"""

df = pd.read_sql(query, conn)

print(df.head(10))