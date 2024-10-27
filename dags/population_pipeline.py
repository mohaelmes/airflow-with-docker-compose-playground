# dags/population_pipeline.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import requests

# URLs y paths
DATA_URL = "https://raw.githubusercontent.com/datasets/population/master/data/population.csv"
PROCESSED_PATH = "/tmp/processed_data.csv"
REPORT_PATH = "/tmp/report.txt"

# Funciones de procesamiento
def download_data():
    response = requests.get(DATA_URL)
    with open("/tmp/raw_data.csv", "w") as f:
        f.write(response.text)

def process_data():
    df = pd.read_csv("/tmp/raw_data.csv")
    # Obtener últimos datos disponibles por país
    latest_data = df.sort_values('Year').groupby('Country Name').last()
    # Top 5 países por población
    top_5 = latest_data.sort_values('Value', ascending=False).head()
    top_5.to_csv(PROCESSED_PATH)

def generate_report():
    df = pd.read_csv(PROCESSED_PATH)
    with open(REPORT_PATH, "w") as f:
        f.write("Top 5 Países por Población\n")
        f.write("=========================\n\n")
        for _, row in df.iterrows():
            f.write(f"{row['Country Name']}: {row['Value']:,.0f}\n")

# Definición del DAG
default_args = {
    'owner': 'student',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'population_analysis',
    default_args=default_args,
    description='Un simple pipeline de análisis de población',
    schedule_interval=timedelta(days=1),
)

# Tareas
t1 = PythonOperator(
    task_id='download_data',
    python_callable=download_data,
    dag=dag,
)

t2 = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    dag=dag,
)

t3 = PythonOperator(
    task_id='generate_report',
    python_callable=generate_report,
    dag=dag,
)

# Definir dependencias
t1 >> t2 >> t3

