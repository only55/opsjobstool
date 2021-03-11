import json
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
import ansible.constants as C
from ansible import context
from optparse import Values



class PlayBookResultsCollector(CallbackBase):
    CALLBACK_VERSION = 2.0

    def __init__(self, *args, **kwargs):
        super(PlayBookResultsCollector, self).__init__(*args, **kwargs)
        self.task_ok = {}
        self.task_skipped = {}
        self.task_failed = {}
        self.task_status = {}
        self.task_unreachable = {}

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.task_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.task_failed[result._host.get_name()] = result

    def v2_runner_on_unreachable(self, result):
        self.task_unreachable[result._host.get_name()] = result

    def v2_runner_on_skipped(self, result):
        self.task_ok[result._host.get_name()] = result

    # def v2_runner_on_changed(self, result):
    #     self.task_ok[result._host.get_name()] = result

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)
            self.task_status[h] = {
                                       "ok": t['ok'],
                                       "changed": t['changed'],
                                       "unreachable": t['unreachable'],
                                       "skipped": t['skipped'],
                                       "failed": t['failures']
                                   }


class ModelResultsCollector(CallbackBase):

    def __init__(self, *args, **kwargs):
        super(ModelResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result,  *args, **kwargs):
        self.host_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result,  *args, **kwargs):
        self.host_failed[result._host.get_name()] = result

class ResultCallback(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.host_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed[result._host.get_name()] = result


class AnsibleApi(object):
    def __init__(self, inventory_file, host_list, groupname):
        self.options = {'verbosity': 0, 'ask_pass': False, 'private_key_file': None, 'remote_user': None,
                    'connection': 'smart', 'timeout': 10, 'ssh_common_args': '', 'sftp_extra_args': '',
                    'scp_extra_args': '', 'ssh_extra_args': '', 'force_handlers': False, 'flush_cache': None,
                    'become': False, 'become_method': 'sudo', 'become_user': None, 'become_ask_pass': False,
                    'tags': ['all'], 'skip_tags': [], 'check': False, 'syntax': None, 'diff': False,
                    'inventory': inventory_file,
                    'listhosts': None, 'subset': None, 'extra_vars': [], 'ask_vault_pass': False,
                    'vault_password_files': [], 'vault_ids': [], 'forks': 5, 'module_path': None, 'listtasks': None,
                    'listtags': None, 'step': None, 'start_at_task': None, 'args': ['fake']}

        self.ops = Values(self.options)
        self.loader = DataLoader()
        self.passwords = dict()
        self.results_callback = ResultCallback()
        self.inventory = InventoryManager(loader=self.loader, sources=[self.options['inventory']])
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        self.result_playbook = PlayBookResultsCollector()
        self.results_raw = {}
        self.groupname = groupname
        self.host_list = host_list
        self.add_dynamic_group(self.host_list, self.groupname)

    def add_dynamic_group(self, hosts, groupname):
        self.inventory.add_group(groupname)
        # {
        #    ip1: {key: value},
        #    ip2: {key: value},
        # }
        for host in hosts:
            self.inventory.add_host(host, group=groupname)
            my_host = self.inventory.get_host(host)
            print('add {}'.format(host))

            for var in hosts[host]:
                self.variable_manager.set_host_variable(host=my_host, varname=var, value=hosts[host][var])
        print('print inventory')
        print(self.inventory.get_groups_dict())

    def ansible_run(self, host_list, task_list):
        context._init_global_context(self.ops)
        play_source = dict(
                name="Ansible Play",
                hosts=host_list,
                gather_facts='no',
                tasks=task_list
        )
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

        tqm = None
        try:
            tqm = TaskQueueManager(
                    inventory=self.inventory,
                    variable_manager=self.variable_manager,
                    loader=self.loader,
                    # options=self.ops,
                    passwords=self.passwords,
                    stdout_callback=self.results_callback,
                    run_additional_callbacks=C.DEFAULT_LOAD_CALLBACK_PLUGINS,
                    run_tree=False,
            )
            result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()
                # shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

        results_raw = {}
        results_raw['success'] = {}
        results_raw['failed'] = {}
        results_raw['unreachable'] = {}

        for host, result in self.results_callback.host_ok.items():
            results_raw['success'][host] = json.dumps(result._result)

        for host, result in self.results_callback.host_failed.items():
            results_raw['failed'][host] = result._result['msg']

        for host, result in self.results_callback.host_unreachable.items():
            results_raw['unreachable'][host] = result._result['msg']

        return results_raw

    def playbook_run(self, playbook_path):

        # self.variable_manager.extra_vars = {'customer': 'test', 'disabled': 'yes'}
        context._init_global_context(self.ops)

        playbook = PlaybookExecutor(playbooks=playbook_path,
                                    inventory=self.inventory,
                                    variable_manager=self.variable_manager,
                                    loader=self.loader, passwords=self.passwords)

        playbook._tqm._stdout_callback = self.result_playbook
        C.HOST_KEY_CHECKING = False
        playbook.run()
        self.results_raw = {'skipped': {}, 'failed': {}, 'ok': {}, "status": {}, 'unreachable': {}, "changed": {}}
        for host, result in self.result_playbook.task_ok.items():
            self.results_raw['ok'][host] = json.dumps(result._result)

        for host, result in self.result_playbook.task_failed.items():
            self.results_raw['failed'][host] = result._result['msg']

        for host, result in self.result_playbook.task_status.items():
            self.results_raw['status'][host] = result

        for host, result in self.result_playbook.task_skipped.items():
            self.results_raw['skipped'][host] = result._result['msg']

        for host, result in self.result_playbook.task_unreachable.items():
            self.results_raw['unreachable'][host] = result._result['msg']

        return self.results_raw


if __name__ == "__main__":
    inventory_file = '/etc/ansible/hosts'
    ip = {'192.168.181.10': {
           'ansible_ssh_user': "root", 'ansible_ssh_pass':"111111", 'ansible_ssh_port': 22,
           'release_port': 11113, 'ts_hostname': 'node1'},
        # '192.168.181.12':  {
        #    'ansible_ssh_user': "root", 'ansible_ssh_pass': "111111", 'ansible_ssh_port': 22,
        #    'release_port': 11113, 'ts_hostname': 'node2'},
        # '192.168.181.13': {
        #     'ansible_ssh_user': "root", 'ansible_ssh_pass': "111111", 'ansible_ssh_port': 22,
        #     'release_port': 11113, 'ts_hostname': 'node3'}
        }

    tasks_list = [
        dict(action=dict(module='shell', args='ls /')),
        # dict(action=dict(module='shell', args='python sleep.py')),
        # dict(action=dict(module='synchronize', args='src=/home/op/test dest=/home/op/ delete=yes')),
    ]

    a = AnsibleApi(inventory_file, ip, 'comtop')

    print(type(a.ansible_run(['comtop'], tasks_list)))
    #
    # result = a.playbook_run(playbook_path=['/etc/ansible/roles/test.yml'])
    # print(result)
