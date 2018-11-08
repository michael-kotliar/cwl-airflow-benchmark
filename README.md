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

  <details>
    <summary>What happens in Webserver</summary>
        
      POST to http://0.0.0.0:8080/admin/taskinstance/action/
      Data:
          csrf_token: string
          url: /admin/taskinstance/
          action: set_failed
          rowid: task_id,dag_id,execution_date
        
      # When calling the funtction ids = rowid
      def action_set_failed(self, ids)  # airflow/www/views.py:2644
        
      # When calling the funtction ids = rowid and target_state = State.FAILED
      def set_task_instance_state(self, ids, target_state, session=None)  # airflow/www/views.py:2699
        
      # SQL equivalent, execution_date should look like "2018-11-04 19:00:00.000000"
      UPDATE task_instance
      SET state="failed"
      WHERE task_id="task_id" AND
            dag_id="dag_id" AND
            execution_date="execution_date"
        
  </details>

  <details>
    <summary>What happens in Scheduler</summary>
        
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
        
  </details>
        
- ***DAG Run***

  What you get as a result

    ```
    Doesn't influence on Task Instances
    Updates only DAG Run's state.
    Should be investigated
    ```

  <details>
    <summary>What happens in Webserver</summary>
        
      POST to http://0.0.0.0:8080/admin/dagrun/action/
      Data:
          csrf_token: string
          url: /admin/dagrun/
          action: set_failed
          rowid: 1
                  
      # When calling the function ids = rowid corresponds to id from dag_run table
      def action_set_failed(self, ids)  # airflow/www/views.py:2561
        
      # When calling the function ids = rowid corresponds to id from dag_run table and target_state = State.FAILED
      def set_dagrun_state(self, ids, target_state, session=None)  # airflow/www/views.py:2569
        
      # SQL equivalent, end_date is taken as timezone.utcnow(). In SQL it should look like "2018-11-04 19:00:00.000000"
      UPDATE dag_run
      SET state="failed", end_date="end_date"
      WHERE id=int
        
  </details>



## Terminate Scheduler

- ***Task Instance***

  What you get as a result
  
    ```
    Command is NOT killed
    ```

- ***DAG Run***

## Update DB

- ***Task Instance***

  What you get as a result
  
    ```
    command is killed
    ```

- ***DAG Run***

# One step DAG with DockerOperator
 
## Set FAIL through Web Interface

- ***Task Instance***
  
  What you get as a result
  
    ```
    Docker container is killed
    ```

  <details>
    <summary>What happens in Webserver</summary>
        
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
        
  </details>

  <details>
    <summary>What happens in Scheduler</summary>
        
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
        
  </details>

- ***DAG Run***
  
## Terminate Scheduler

- ***Task Instance***

  What you get as a result
  
    ```
    Docker container is NOT killed
    ```

- ***DAG Run***

## Update DB

- ***Task Instance***

  What you get as a result
  
    ```
    Docker container is killed
    ```

- ***DAG Run***

-------------
Findings
-------------
1. To completely stop BioWardrobe experiment you should set FAIL state for all tasks of the DAG