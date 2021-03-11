from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
import json
import logging
from django.core.serializers.json import DjangoJSONEncoder
import uuid
import hashlib

from ansible_main import tasks

logger = logging.getLogger('django')


def login_valid(fun):
    def inner(request, *args, **kwargs):
        cookie = request.COOKIES
        status = cookie.get('md5_id')
        try:
            if status == request.session['md5_id']:
                return fun(request, *args, **kwargs)
            else:
                return render(request, 'console/login.html')
        except Exception as e:
            logger.info(e)
            return render(request, 'console/login.html')
    return inner


@login_valid
def select_command(request):

    command_data = dict()
    command_data['task_id'] = str(uuid.uuid4())
    command_data['command_name'] = dict()
    user_id = request.session['user_id']

    # logger.info(user_id)

    data = User.objects.get(id=user_id)

    role_name = data.role_type
    role_id = Role.objects.get(name=role_name)
    # logger.info(role_id)
    command_id = RoleCommand.objects.filter(role_id=role_id).values('command_id_id')
    # logger.info(command_id)

    for info in command_id:
        command_name = Command.objects.filter(id=info['command_id_id'])
        for name in command_name.values('name'):
            command_data['command_name'][name['name']] = []
            args_name = CommandArgs.objects.filter(command_name=info['command_id_id'])
            for args in args_name.values('name'):
                command_data['command_name'][name['name']].append(args['name'])

    return HttpResponse(json.dumps({'data': command_data}, ensure_ascii=False, cls=DjangoJSONEncoder),
                        content_type="application/json,charset=utf-8")


@login_valid
def group_remove(request):
    remove_id = request.GET['remove_id']
    remove_info = GroupName.objects.get(id=remove_id)
    ip_num = remove_info.groupip_set.all()
    print(len(ip_num))
    if len(ip_num) == 0:
        remove_info.delete()
        return HttpResponse(json.dumps({'suss': u'删除成功'}, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type="application/json,charset=utf-8")
    else:
        return HttpResponse(json.dumps({'fail': '请删除该分组主机后进行操作！'}, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type="application/json,charset=utf-8")


@login_valid
def group_insert(request):
    new_group = request.GET['new_group']
    try:
        remove_info = GroupName.objects.get(name=new_group)
    except Exception as e:
        remove_info = False
        logger.info(e)

    if not remove_info:
        g1 = GroupName(name=new_group, create_time=timezone.now())
        g1.save()
        return HttpResponse(json.dumps({'suss': u'增加成功'}, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type="application/json,charset=utf-8")
    else:
        return HttpResponse(json.dumps({'fail': '组名重复'}, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type="application/json,charset=utf-8")


@login_valid
def group_update(request):
    update_id = request.GET['update_id']
    update_name = request.GET['update_name']
    try:
        GroupName.objects.filter(id=update_id).update(name=update_name)
        return HttpResponse(json.dumps({'suss': u'修改成功'}, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type="application/json,charset=utf-8")
    except Exception as e:
        logger.info(e)
        return HttpResponse(json.dumps({'fail': e}, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type="application/json,charset=utf-8")


@login_valid
def host_remove(request):
    remove_id = request.GET['remove_id']
    try:
        remove_info = GroupIp.objects.get(id=remove_id)
        remove_info.delete()
        return HttpResponse(json.dumps({'suss': u'删除成功'}, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type="application/json,charset=utf-8")
    except Exception as e:
        logger.info(e)
        return HttpResponse(json.dumps({'fail': '删除失败！'}, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type="application/json,charset=utf-8")


@login_valid
def host_insert(request):
    print(request.GET)
    group = request.GET['group_name']
    group_id = GroupName.objects.get(name=group)
    print('group_id')
    print(group_id)
    login_ip = request.GET['login_ip']
    login_user = request.GET['login_user']
    login_port = request.GET['login_port']
    login_password = request.GET['login_password']
    connection = request.GET['connect']

    insert_info = GroupIp.objects.filter(login_ip=login_ip, group_id=group_id.id)

    if not insert_info:
        print('insert')
        g1 = GroupIp(login_ip=login_ip, login_user=login_user, login_port=login_port,
                     login_password=login_password, connect=connection, group_id=group_id)
        g1.save()
        return HttpResponse(json.dumps({'suss': u'增加成功'}, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type="application/json,charset=utf-8")
    else:
        return HttpResponse(json.dumps({'fail': 'IP重复'}, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type="application/json,charset=utf-8")


@login_valid
def host_update(request):
    update_id = request.GET['update_id']
    login_ip = request.GET['login_ip']
    login_user = request.GET['login_user']
    login_port = request.GET['login_port']
    login_password = request.GET['login_password']
    connection = request.GET['connection']
    try:
        GroupIp.objects.filter(id=update_id).update(
            login_ip=login_ip, login_user=login_user, login_port=login_port, login_password=login_password,
            connect=connection)
        return HttpResponse(json.dumps({'suss': u'修改成功'}, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type="application/json,charset=utf-8")
    except Exception as e:
        logger.info(e)
        return HttpResponse(json.dumps({'fail': e}, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type="application/json,charset=utf-8")


@login_valid
def host_name(request):
    host_dict = dict()
    host_group = request.GET['host_group']
    host_list = GroupName.objects.get(name=host_group).groupip_set.all()
    for info in host_list.values():
        host_dict[info['id']] = info

    return HttpResponse(json.dumps({'data': host_dict}, ensure_ascii=False, cls=DjangoJSONEncoder),
                        content_type="application/json,charset=utf-8")


def auth(request):
    # logger.info('begin auth')
    if request.method == 'POST':
        user = request.POST.get('user', None)
        password = request.POST.get('password', None)

        if user and password:

            try:
                user_result = User.objects.get(name=user)

                if user_result.password == password:
                    # logger.info('password ok')
                    md5_id = hashlib.md5(user.encode(encoding='UTF-8')).hexdigest()
                    request.session['is_login'] = True
                    request.session['user_id'] = user_result.id
                    request.session['user_name'] = user_result.name
                    request.session['md5_id'] = md5_id

                    object_result = object_data()
                    object_result['index'][2] = '1'
                    plan_list = map(str, range(3))
                    response = render(request, 'console/index.html', locals())
                    # logger.info(md5_id)
                    response.set_cookie('md5_id', md5_id, expires=60*60*24)
                    return response

            except Exception as e:

                logger.info(e)
                return render(request, 'console/login.html')

        return render(request, 'console/login.html')


def object_data():

    object_result = {
        'index': ['主页', 'icon-home', '0'],
        # 'table': ['主机设置', 'icon-grid', '0'],
        'machine': [
            '主机管理', 'icon-user', '0', {
                '分组管理': ['0', 'group'], '设备管理': ['0', 'host']
            }, 'false', 'collapse list-unstyled'
        ],
        'task': [

            '任务', 'icon-list', '0', {
                '任务编排': ['0', 'order'], '任务清单': ['0', 'list']
            }, 'false', 'collapse list-unstyled',

        ],
        'event': [

            '事件', 'icon-interface-windows', '0', {
                '事件查询': ['0', 'log']
            }, 'false', 'collapse list-unstyled',
        ],
        'deloy': [

            '自动化部署', 'icon-website', '0', {
                'WebLogic': ['0', 'WebLogic'], 'Redis': ['0', 'Redis'], 'Tomcat': ['0', 'Tomcat'],
            }, 'false', 'collapse list-unstyled',
        ],

        'process': ['流程自动化', 'icon-page', '0'],
        'exit': ['自动出库', 'icon-page', '0'],
    }

    return object_result


@login_valid
def index(request):
    object_result = object_data()
    object_result['index'][2] = '1'
    plan_list = map(str, range(3))
    response = render(request, 'console/index.html', locals())
    return response


def login(request):
    return render(request, 'console/login.html')


def page_404(request, *key, **dic):
    object_result = object_data()
    return render(request, 'console/table.html', locals())


def logout(request):
    request.session.flush()
    return render(request, 'console/logout.html')


@login_valid
def table(request, object_name):
    object_result = object_data()
    object_result[object_name][2] = '1'
    return render(request, 'console/{}.html'.format(object_name), locals())


@login_valid
def group_name(request):
    data = []
    for info in GroupName.objects.values().values_list():
        dict_info = dict()
        dict_info['id'] = info[0]
        dict_info['createtime'] = info[1]
        dict_info['name'] = info[2]
        dict_info['count'] = '0'
        data.append(dict_info)
    return HttpResponse(json.dumps({'data': data}, ensure_ascii=False, cls=DjangoJSONEncoder),
                        content_type="application/json,charset=utf-8")


@login_valid
def machine_group(request):
    object_result = object_data()
    object_result['machine'][3]['分组管理'][0] = '1'
    object_result['machine'][4] = 'true'
    object_result['machine'][5] = 'collapse list-unstyled show'

    # logger.info(object_result)
    return render(request, 'console/machine_group.html', locals())


@login_valid
def machine_host(request, args=''):
    object_result = object_data()
    object_result['machine'][3]['设备管理'][0] = '1'
    object_result['machine'][4] = 'true'
    object_result['machine'][5] = 'collapse list-unstyled show'
    return render(request, 'console/machine_host.html', locals())


@login_valid
def task_order(request):
    object_result = object_data()
    object_result['task'][3]['任务编排'][0] = '1'
    object_result['task'][4] = 'true'
    object_result['task'][5] = 'collapse list-unstyled show'
    return render(request, 'console/task_order.html', locals())


@login_valid
def task_list(request):
    object_result = object_data()
    object_result['task'][3]['任务清单'][0] = '1'
    object_result['task'][4] = 'true'
    object_result['task'][5] = 'collapse list-unstyled show'
    return render(request, 'console/task_list.html', locals())


@login_valid
def event_log(request):
    object_result = object_data()
    object_result['event'][3]['事件查询'][0] = '1'
    object_result['event'][4] = 'true'
    object_result['event'][5] = 'collapse list-unstyled show'
    return render(request, 'console/event_log.html', locals())



# @login_valid
def accept_task(request):
    receive_data = json.loads(request.body.decode())
    # logger.info(receive_data)
    # logger.info(request.session['user_id'])
    user_id = User.objects.get(id=1)
    task_data = {
        'task_name': receive_data['task_name'],
        'task_id': receive_data['task_id'],
        # 'group_id': receive_data['group_id'],
        # 'group_id': 1,
        'user_id': user_id
    }
    # logger.info('task_data')
    # logger.info(task_data)

    user_task = UserTask(**task_data)
    user_task.save()

    task_id = UserTask.objects.get(task_id=receive_data['task_id'])

    logger.info(task_id)

    for command_info in receive_data['command_name']:
        for command_name in command_info:
            print(command_name)
            command_task_id = str(uuid.uuid4())
            task_command = UserTaskCommand(command_name=command_name,
                                           task_id=task_id,
                                           command_task_id=command_task_id)
            task_command.save()
            print('353')
            task_command_id = UserTaskCommand.objects.get(command_name=command_name,
                                                          task_id=task_id,
                                                          command_task_id=command_task_id)
            print('358')
            for arg_name in command_info[command_name]:

                task_command_args = UserTaskCommandArgs(user_command_id=task_command_id,
                                                        command_name=command_name,
                                                        arg_name=arg_name,
                                                        command_data=command_info[command_name][arg_name])
                task_command_args.save()

    # inventory_file = '/etc/hosts'
    #
    # t = threading.Thread(target=exec_task, args=(receive_data['task_id'], inventory_file))
    # t.start()
    #
    # return HttpResponse(json.dumps({'data': 'ok'}, ensure_ascii=False, cls=DjangoJSONEncoder),
    #                     content_type="application/json,charset=utf-8")


# @login_valid
def event_info(request):
    result = list()

    try:
        task_name = request.GET['task_name']
        task = UserTask.objects.filter(task_name=task_name).values()
        for task_id in task:
            temp = dict()
            temp['task_name'] = task_id['task_name']
            temp['log'] = EventLog.objects.get(task_id=task_id['id']).task_log
            temp['task_id'] = task_id['task_id']
            temp['details_info'] = EventLog.objects.get(
                                                                task_id=task_id['id']).details_log
            result.append(temp)

    except Exception as e:

        task_user = UserTask.objects.filter(user_id=request.session['user_id']).values()
        for task_id in task_user:
            temp = dict()
            temp['task_name'] = task_id['task_name']
            temp['log'] = EventLog.objects.get(task_id=task_id['id']).task_log
            temp['task_id'] = task_id['task_id']
            temp['details_info'] = EventLog.objects.get(
                                                                task_id=task_id['id']).details_log
            result.append(temp)

        logger.info(e)

    return HttpResponse(json.dumps({'data': result}, ensure_ascii=False, cls=DjangoJSONEncoder),
                        content_type="application/json,charset=utf-8")


def task_info(request):

    result = list()
    task_user = UserTask.objects.filter(user_id=request.session['user_id']).values()
    for task_id in task_user:
        temp = dict()
        temp['task_name'] = task_id['task_name']
        temp['task_id'] = task_id['id']
        temp['state'] = task_id['state']
        temp['create_time'] = task_id['create_time']
        temp['command'] = {}
        for command_info in UserTaskCommand.objects.filter(task_id=task_id['id']).values():
            command_temp = dict()
            temp['command'][command_info['command_task_id']] = list()
            command_temp['command_name'] = command_info['command_name']

            command_temp['info'] = dict()

            for args in UserTaskCommandArgs.objects.filter(user_command_id=command_info['id']).values():
                command_temp['info'][args['arg_name']] = args['command_data']

            temp['command'][command_info['command_task_id']].append(command_temp)

        result.append(temp)

    return HttpResponse(json.dumps({'data': result}, ensure_ascii=False, cls=DjangoJSONEncoder),
                        content_type="application/json,charset=utf-8")


def task_range(request):
    result = UserTask.objects.filter(user_id=request.session['user_id']).values()
    return HttpResponse(json.dumps({'data': list(result)}, ensure_ascii=False, cls=DjangoJSONEncoder),
                        content_type="application/json,charset=utf-8")


def user_exec(request):

    insert_task = ExecTask(user_task=UserTask.objects.get(id=request.GET['task_id']), group_id=request.GET['group_id'])
    insert_task.save()
    exec_id = insert_task.id
    print(exec_id)
    res = tasks.exec_task.delay(exec_id)

    return HttpResponse(json.dumps({'data': res.task_id}, ensure_ascii=False, cls=DjangoJSONEncoder),
                        content_type="application/json,charset=utf-8")
