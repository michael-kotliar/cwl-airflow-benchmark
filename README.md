Use `pstree -s scheduler` to check if command is running.


### One step DAG without Docker

Using Web Interface

- Set `Task Instance` to `Fail`

  **What you get as a result:**
  
    ```
    command is killed
    ```

  **What happens in Webserver**

    ```
    POST to http://0.0.0.0:8080/admin/taskinstance/action/
    Data:
        csrf_token: string
        url: /admin/taskinstance/
        action: set_failed
        rowid: task_id,dag_id,execution_date
    
    # Call airflow/www/views.py:2644 where ids = rowid
    def action_set_failed(self, ids)
     
    # Call airflow/www/views.py:2699 where ids = rowid and target_state = State.FAILED
    def set_task_instance_state(self, ids, target_state, session=None)
    
    # Execute, execution_date should look like "2018-11-04 19:00:00.000000"
    UPDATE task_instance
    SET state="failed"
    WHERE task_id="task_id" AND
          dag_id="dag_id" AND
          execution_date="execution_date"
    ```
    
  **What happens in Scheduler**
  
  ```
  # Assuming your airflow.cfg includes
  executor = LocalExecutor
  task_runner = BashTaskRunner

  # Call airflow/jobs.py:2646 that monitors DB state
  def heartbeat_callback(self, session=None)
  
  # Call airflow/jobs.py:2682 when state is changed
  self.task_runner.terminate()
 
  # Call airflow/task/task_runner/base_task_runner.py:39 to initiate the termination
  def terminate(self):
         
  # Call airflow/utils/helpers.py:217 to terminate all childrens and grandchildren.
  # Tries really hard to terminate all children (including grandchildren). Will send
  # sig (SIGTERM) to the process group of pid. If any process is alive after timeout
  # a SIGKILL will be send.
  def reap_process_group(pid, log, sig=signal.SIGTERM, timeout=DEFAULT_TIME_TO_WAIT_AFTER_SIGTERM)
  ```
        
- Set `DAG Run` to `Fail`

  Results:

    ```
    Doesn't influence on Task Instances
    Updates only DAG Run's state
    ```



 
 