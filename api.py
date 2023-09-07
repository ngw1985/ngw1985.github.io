from flask import Flask, request, jsonify
import tabula
import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
import logging
from flask_cors import CORS  # Importa la extensión
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account


# Credenciales de servicio de Google Sheets (reemplaza con tu archivo JSON)
credentials = service_account.Credentials.from_service_account_file('C:\\Users\\ngw19\\OneDrive\\Escritorio\\Curso\\motorapi-2b71128626ea.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])
service = build('sheets', 'v4', credentials=credentials)


# ID de tu hoja de Google Sheets (reemplaza con el ID de tu hoja)
spreadsheet_id = '1Z5QRIlRXWPqdFrdnNtrmu3ql9jLwUXH47Z-H4BdKwa8'

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG) 

@app.route('/tabulate_pdf', methods=['POST'])
def tabulate_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No se proporcionó un archivo PDF"}), 400

        pdf_file = request.files['file']
        #filepath = pdf_file.filename  # Obtener el nombre del archivo
        filepath = os.path.join(os.path.dirname(__file__), pdf_file.filename)
        saldo_input = float(request.form.get('saldo'))

        # Resto de tu código para procesar el archivo PDF
        dfs = tabula.read_pdf(filepath, pages='all')

        # Unir todos los DataFrames en uno solo
        combined_df = pd.concat(dfs)

        # Agregar el campo "categoría" con un valor estático
        nomina = 'ACH - |SALARIO|NÓMINA'
        deuda = 'CASHPER|MYKREDIT|DINEO|WELP|AZLO|ASLO|MONEYMAN|TRIBE|CREDITERO|DISPON|CREDITOSI|VIVUS|TRIVE|MYKREDIT2|MONEY MAN|WANDOO|KVIKU|SIMPLEROS|CHAMPLOAN|MOVINERO|FINTYA|QUE BUENO|PRESTAMER|IBERCREDITO|MOKANI|DINEVO|SIMPLEROS|LOANEY|CREDITERO|CHAMPLOAN|AVINTO'

        combined_df['Fecha']=combined_df['Fecha'].str.replace('ago', 'aug')
        combined_df['Fecha']=combined_df['Fecha'].str.replace('ene', 'jan')
        combined_df['Fecha']=combined_df['Fecha'].str.replace('abr', 'apr')
        combined_df['Fecha']=combined_df['Fecha'].str.replace('dic', 'dec')

        combined_df['analizar'] = combined_df['Descripción'].astype(str).str.upper()
        combined_df["fecha_tx"] = pd.to_datetime(combined_df["Fecha"].astype(str))
        combined_df["per_tx"] = (combined_df["fecha_tx"].astype(str).str[:4] + combined_df["fecha_tx"].astype(str).str[5:7]).astype(str)
        combined_df['per_tx'] = combined_df['per_tx'].astype("string")

        combined_df['categoria'] = np.where(combined_df['analizar'].str.contains(nomina), 'Ingresos',
                                            np.where(combined_df['analizar'].str.contains(deuda), 'Deuda', 'Otro'))

        combined_df['monto_pre'] = combined_df['Monto'].str.replace('$', '')
        combined_df['monto_pre'] = combined_df['monto_pre'].str.replace(',', '')
        combined_df['monto'] = combined_df['monto_pre'].astype(float)

        combined_df['saldo_pre'] = combined_df['Saldo total'].str.replace('$', '')
        combined_df['saldo_pre'] = combined_df['saldo_pre'].str.replace(',', '')
        combined_df['saldo_total'] = combined_df['saldo_pre'].astype(float)

        combined_df['q'] = 1

        # Creo las semanas del mes
        combined_df['primer_dia_del_mes'] = combined_df['fecha_tx'].dt.to_period('M').dt.start_time
        combined_df['semana_del_mes'] = (combined_df['fecha_tx'] - combined_df['primer_dia_del_mes']).dt.days // 7 + 1
        combined_df['quincena_del_mes'] = (combined_df['fecha_tx'].dt.day <= 15).astype(int) + 1

        # Creo los periodos
        Periodo = datetime.datetime.now().strftime('%Y%m')
        today = datetime.date.today()
        first = datetime.date(day=1, month=today.month, year=today.year)
        Periodo_1 = (first - datetime.timedelta(days=1)).strftime("%Y%m")
        Periodo_2 = (first - datetime.timedelta(days=35)).strftime("%Y%m")
        Periodo_3 = (first - datetime.timedelta(days=65)).strftime("%Y%m")

        ingresos = combined_df[combined_df["categoria"] == 'Ingresos']
        ingresos_0 = ingresos.loc[ingresos['per_tx'] == Periodo, 'monto'].sum()
        ingresos_1 = ingresos.loc[ingresos['per_tx'] == Periodo_1, 'monto'].sum()
        ingresos_2 = ingresos.loc[ingresos['per_tx'] == Periodo_2, 'monto'].sum()
        ingresos_3 = ingresos.loc[ingresos['per_tx'] == Periodo_3, 'monto'].sum()
        ingresos_0_q = ingresos.loc[ingresos['per_tx'] == Periodo, 'q'].sum().astype(str)
        ingresos_1_q = ingresos.loc[ingresos['per_tx'] == Periodo_1, 'q'].sum().astype(str)
        ingresos_2_q = ingresos.loc[ingresos['per_tx'] == Periodo_2, 'q'].sum().astype(str)
        ingresos_3_q = ingresos.loc[ingresos['per_tx'] == Periodo_3, 'q'].sum().astype(str)

        saldo_positivo = combined_df[combined_df["saldo_total"] > 0]
        saldo_positivo_0 = saldo_positivo.loc[saldo_positivo['per_tx'] == Periodo, 'q'].sum()
        saldo_positivo_1 = saldo_positivo.loc[saldo_positivo['per_tx'] == Periodo_1, 'q'].sum()
        saldo_positivo_2 = saldo_positivo.loc[saldo_positivo['per_tx'] == Periodo_2, 'q'].sum()
        
        saldo_medio_0=0
        if ingresos_0>0:
            saldo_medio_0 = combined_df.loc[combined_df['per_tx'] == Periodo, 'saldo_total'].sum()/combined_df.loc[combined_df['per_tx'] == Periodo, 'q'].sum()
        
        saldo_medio_1 = combined_df.loc[combined_df['per_tx'] == Periodo_1, 'saldo_total'].sum()/combined_df.loc[combined_df['per_tx'] == Periodo_1, 'q'].sum()
        saldo_medio_2 = combined_df.loc[combined_df['per_tx'] == Periodo_2, 'saldo_total'].sum()/combined_df.loc[combined_df['per_tx'] == Periodo_2, 'q'].sum()

    
        # SETEAR EL MONTO MINIMO A ANALIZAR
        saldo_negativo = combined_df[combined_df["saldo_total"] < saldo_input]
        df_fechas = pd.DataFrame()

        ingresos_2_q_pre = ingresos.loc[ingresos['per_tx'] == Periodo_2, 'q'].sum()
        
        if ingresos_2_q_pre > 2:
            df_fechas = saldo_negativo.groupby(['per_tx', 'semana_del_mes'])['fecha_tx'].min().reset_index()
        else:
            df_fechas = saldo_negativo.groupby(['per_tx', 'quincena_del_mes'])['fecha_tx'].min().reset_index()


        fechas_fin_str = "\n".join(str(date) for date in df_fechas['fecha_tx'])
        fechas_ing_str = "\n".join(str(date) for date in ingresos['fecha_tx'])

   # Resultados que deseas guardar en Google Sheets
        results = {
            "b)Ingresos_mes_actual": ingresos_0,
            "c)Ingresos_mes_anterior": ingresos_1,
            "d)Ingresos_mes_2_meses_anteriores": ingresos_2,
            "e)Cantidad de ingresos en el periodo actual": ingresos_0_q,
            "f)Cantidad de ingresos en el periodo anterior": ingresos_1_q,
            "g)Cantidad de ingresos en el periodo hace 2 meses": ingresos_2_q,
            "h)Saldo medio del periodo actual": saldo_medio_0,
            "i)Saldo medio del periodo anterior": saldo_medio_1,
            "j)Saldo medio del periodo hace 2 meses": saldo_medio_2,
            "k) Fechas de cobro": fechas_ing_str,
            "l) Fechas sin fondos": fechas_fin_str
        }

# Inicializa una lista para almacenar los datos de cada variable
        datos_variables = []

# Define la lista de letras de columna para mapear variables a columnas (A, B, C, ...)
        columnas = [chr(i) for i in range(ord('A'), ord('A') + len(results))]
 # Itera a través de las variables y sus valores
        for variable, valor in results.items():
  # Crea una lista con el nombre de la variable y su valor
                datos_variable = [variable]
                datos_variable.extend([valor] * (len(results) - 1))
# Agrega la lista de datos de la variable a la lista principal
                datos_variables.append(datos_variable)

# Crear el cuerpo del mensaje
        body_datos = {
               'values': datos_variables
            }
# Define el rango de celdas para la inserción, comenzando desde la columna A
        rango_inicial = "A1"
        rango_final = f"{columnas[-1]}1" 

# Realiza la operación de apéndice en el rango especificado
        result_datos = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{rango_inicial}:{rango_final}",
            body=body_datos,
            valueInputOption="RAW"
        ).execute()


        return jsonify({"a)Message": "Procesamiento exitoso", "resultado_sheets": results})

    except Exception as e:
        return jsonify({"error": str(e), "mensaje": "Error al realizar la operación de apéndice"})

if __name__ == '__main__':
    app.run(debug=True)