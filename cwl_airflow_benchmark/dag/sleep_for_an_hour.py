import airflow
from airflow.operators.bash_operator import BashOperator
from airflow.models import DAG


dag = DAG(dag_id='sleep_for_an_hour',
          start_date=airflow.utils.dates.days_ago(1),
          schedule_interval='@once')

run_this = BashOperator(task_id='sleep_for_an_hour_task',
                        bash_command='sleep 3600',
                        dag=dag)
