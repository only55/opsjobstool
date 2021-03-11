from ansible_main.models import *
# from .pythonAPI.controls import CmdTask
from celery import shared_task


@shared_task
def exec_task(exec_id):
    print(exec_id)
    # try:
    # logger.info(exec_id)
    ExecTask.objects.filter(id=exec_id).update(status=1)
    # cmd_exec = CmdTask(exec_id, inventory_file)
    # result = cmd_exec.build_task()
    result = {'success': 'success', 'failed': 'failed'}
    exec_obj = ExecTask.objects.get(id=exec_id)
    log_state = 'ok: {} fail: {} '.format(len(result['success']), len(result['failed']))
    task_log = EventLog(exec_id=exec_obj, task_log=log_state, details_log=result)
    task_log.save()
    ExecTask.objects.filter(id=exec_id).update(status=2)
    #
    # except Exception as e:
    #     task_log = EventLog(task_id=log_id, task_log='fail', details_log=e)
    #     task_log.save()
    #     UserTask.objects.filter(task_id=task_id).update(state=3)



