import logging
from airflow.operators.python_operator import PythonOperator
from airflow.models import DAG, DagRun, DagStat, TaskInstance
from airflow.utils.dates import days_ago
from airflow.utils.helpers import reap_process_group
from airflow.utils.db import provide_session


logger = logging.getLogger(__name__)


@provide_session
def clean_db(dr, session=None):

    # Clean task_instance table
    for ti in dr.get_task_instances():
        session.query(TaskInstance).filter(
            TaskInstance.task_id == ti.task_id,
            TaskInstance.dag_id == ti.dag_id).delete(synchronize_session='fetch')

    # Clean dag_run table
    session.query(DagRun).filter(
        DagRun.dag_id == dr.dag_id,
        DagRun.run_id == dr.run_id,
    ).delete(synchronize_session='fetch')
    session.commit()

    # Update statistics in dag_stats table
    DagStat.update(dr.dag_id, dirty_only=False, session=session)


def kill_tasks(dr):
    for ti in dr.get_task_instances():
        reap_process_group(pid=ti.pid, log=logger)


def clean_dag_run(**context):
    dag_id = context.get("dag_id", None)
    run_id = context.get("run_id", None)
    dr_list = DagRun.find(dag_id=dag_id, run_id=run_id)
    for dr in dr_list:
        kill_tasks(dr)
        clean_db(dr)


dag = DAG(dag_id="clean_dag_run",
          start_date=days_ago(1),
          schedule_interval=None)

run_this = PythonOperator(task_id='clean_dag_run',
                          python_callable=clean_dag_run,
                          provide_context=True,
                          dag=dag)


