Use `pstree -s scheduler` to check if command is running.

Use 'docker ps' to check if container is running.

Supported Python Docker SDK 2.7.0

When running on MacOS make sure to share `/var/folders` with Docker

Assuming your `airflow.cfg` includes
      
  ```
  executor = LocalExecutor
  task_runner = BashTaskRunner
  ```


# One step DAG with BashOperator 

## Set FAIL through Web Interface

- ***Task Instance***
  
  What you get as a result
  
    ```
    command is killed
    ```

  What happens in Webserver

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
    
  What happens in Scheduler
  
  ```
  # Monitore DB state 
    def heartbeat_callback(self, session=None)  # airflow/jobs.py:2646
  
  # If state is changed, initiate task termination
    self.task_runner.terminate()  # airflow/jobs.py:2682
 
  # Depending on a task_runner type, proceed with termination further
    def terminate(self)  # airflow/task/task_runner/base_task_runner.py:39
         
  # Send SIGTERM to all childrens and grandchildren. After timeout sends SIGKILL
    def reap_process_group(pid, log, sig=signal.SIGTERM, timeout=DEFAULT_TIME_TO_WAIT_AFTER_SIGTERM)  # airflow/utils/helpers.py:217
  
  # Catch SIGTERM from TaskInstance class
    def signal_handler(signum, frame)  # airflow/models.py:1609
  
  # Send SIGTERM signal to bash process group 
    def on_kill(self)  # airflow/operators/bash_operator.py:123
  ```
        
- ***DAG Run***

  What you get as a result

    ```
    Doesn't influence on Task Instances
    Updates only DAG Run's state
    Should be investigated more deeply
    ```

## Terminate Scheduler

## Update DB

# One step DAG with DockerOperator
 
## Set FAIL through Web Interface

- ***Task Instance***
  
  What you get as a result
  
    ```
    Docker container is killed
    ```

  What happens in Webserver

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
    
  What happens in Scheduler
  
  ```
  # Monitore DB state 
    def heartbeat_callback(self, session=None)  # airflow/jobs.py:2646
  
  # If state is changed, initiate task termination
    self.task_runner.terminate()  # airflow/jobs.py:2682
 
  # Depending on a task_runner type, proceed with termination further
    def terminate(self)  # airflow/task/task_runner/base_task_runner.py:39
         
  # Send SIGTERM to all childrens and grandchildren. After timeout sends SIGKILL
    def reap_process_group(pid, log, sig=signal.SIGTERM, timeout=DEFAULT_TIME_TO_WAIT_AFTER_SIGTERM)  # airflow/utils/helpers.py:217
  
  # Catch SIGTERM from TaskInstance class
    def signal_handler(signum, frame)  # airflow/models.py:1609
  
  # Call stop to the running container through Docker API
    def on_kill(self)  # airflow/operators/docker_operator.py:236
  ```
  
## Terminate Scheduler

- ***Task Instance***

  What you get as a result
  
    ```
    Docker container is NOT killed
    ```

    If we could catch SIGTINT or SIGTERM from `execute` function of `DockerOperator`,
    we could call `on_kill` and stop Docker container. However, all this signals are cought in Scheduler.
    
    ```python
    def signal_handler(signum, frame):
        self.log.error("Received SIGTERM. Terminating Docker Container.")
        self.on_kill()
        raise AirflowException("Task received SIGTERM signal")

    signal.signal(signal.SIGTERM, signal_handler)
    ```
