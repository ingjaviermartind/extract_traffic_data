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



QUERY_NUEVA = """

DECLARE @MONTH_INTERVAL INT = -6;
WITH Servicios AS
(
	SELECT 
		ser.SER,
		ser.CUS,
		ser.ESTADO_SER,
		ser.TipodePunto,
		ser.TIPO_PRODUCTO,
		ser.TARIFA,
		ser.CAPACIDADBPS,
		COALESCE(planta.Fecha_Baja_Reportada, ser.FechaBaja, planta.PV_FechaBaja) AS FechaBaja
	FROM DTM.SF_SERVICE_LEGV2 ser
	LEFT JOIN
	(
		SELECT
			p.SER,
			p.Fecha_Baja_Reportada,
			p.PV_FechaBaja,
			p.Reportada_Por,
			ROW_NUMBER() OVER (
				PARTITION BY p.SER
				ORDER BY p.[Fecha Instalacion] DESC
			) AS RN
		FROM SFDC.vw_PLANTA_INGRESO_H p
	) planta
    ON ser.SER = planta.SER
    AND planta.RN = 1
	LEFT JOIN DTM.CICLO_SERV_ACTIVOS_PLANTA cic
		ON ser.SER = cic.SERVICIO
	WHERE ser.TIPO_PRODUCTO IN 
	(
		'L2',
		'L3'
	)
	AND (
		ser.TipodePunto IS NULL
		OR ser.TipodePunto NOT LIKE '%inter%'
	)
	AND ser.CAPACIDADBPS <> 0
	AND ser.TARIFA > 1
),
ServiciosMuestra AS
(
	SELECT 
		ser.*
	FROM Servicios ser
	WHERE ser.ESTADO_SER NOT IN
	(
		'En Proceso',
		'Cancelado',
		'Error',
		'Declinado'
	)
	OR (
		FechaBaja >= DATEADD(MONTH, @MONTH_INTERVAL, GETDATE()) 
		AND FechaBaja <= GETDATE()
	)
	
)
SELECT 
	ser.SER AS [Nombre de Servicio],
	COALESCE(ser.CUS, 'Ninguno') AS CUS
FROM ServiciosMuestra ser;
"""