import airflow
from airflow.operators.docker_operator import DockerOperator
from airflow.models import DAG


dag = DAG(dag_id='sleep_for_an_hour_docker',
          start_date=airflow.utils.dates.days_ago(1),
          schedule_interval='@once')

run_this = DockerOperator(task_id='sleep_for_an_hour_docker_task',
                          command='sleep 3600',
                          dag=dag,
                          api_version='1.38',
                          image='ubuntu:xenial',
                          network_mode='bridge')