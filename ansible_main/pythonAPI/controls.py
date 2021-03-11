from ansible_main.models import *
# from .AnsiblePlaybook import AnsibleApi
import logging


class CmdTask:
    def __init__(self, exec_id, inventory_file):
        self.logger = logging.getLogger('django')
        self.inventory_file = inventory_file
        self.ip = dict()
        self.exec_id = ExecTask.objects.get(exec_id=exec_id)
        self.group_name = ''
        self.create_data()
        self.group_id = exec_id.group_id

    def create_data(self):
        logging.info('control')
        logging.info(self.task_id)

        self.group_name = GroupName.objects.get(id=self.group_id).name
        ip_list = GroupIp.objects.filter(group_id=self.group_id).values()
        for info in ip_list:
            self.ip[info['login_ip']] = dict()
            self.ip[info['login_ip']]['ansible_ssh_user'] = info['login_user']
            self.ip[info['login_ip']]['ansible_ssh_pass'] = info['login_password']
            self.ip[info['login_ip']]['ansible_ssh_port'] = info['login_port']
            # self.ip[info['login_ip']]['ansible_connection'] = info['connect']
        return self.ip

    def build_task(self):
        tasks_list = list()
        arg_map = {
            '强制覆盖': 'force',
            '权限': 'mode',
            '目标': 'dest',
            '源': 'src',
        }
        command_list = UserTaskCommand.objects.filter(task_id=self.task_id).values()
        for command in command_list:
            args = ''
            args_list = UserTaskCommandArgs.objects.filter(user_command_id=command['id']).values()
            module = command['command_name']
            for arg in args_list:
                try:
                    args = args + arg_map[arg['arg_name']] + '=' + arg['command_data'] + ' '

                except KeyError:
                    if arg['arg_name'] == '命令名称':
                        args = arg['command_data'] + ' ' + args
                    else:
                        args = args + arg['command_data']

            tasks_list.append(dict(action=dict(module=module, args=args)))

        # a = AnsibleApi(self.inventory_file, self.ip, self.group_name)
        # return a.ansible_run([self.group_name], tasks_list)
        return tasks_list
