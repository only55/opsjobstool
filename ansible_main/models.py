from django.db import models
import django.utils.timezone as timezone

# Create your models here.


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    create_time = models.DateTimeField(auto_created=True)

    class Meta:
        verbose_name = u'权限'
        verbose_name_plural = verbose_name
        db_table = 'role'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_time = timezone.now()
        return super(Role, self).save(*args, **kwargs)


class User(models.Model):
    name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    create_time = models.DateTimeField(auto_created=True)
    last_time = models.DateTimeField(auto_created=True)
    role_type = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        verbose_name = u'user'
        verbose_name_plural = verbose_name
        db_table = 'user'

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_time = timezone.now()
        return super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Command(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = u'命令'
        verbose_name_plural = verbose_name
        db_table = 'command'

    def __str__(self):
        return self.name


class RoleCommand(models.Model):

    role_id = models.ForeignKey(Role, on_delete=models.CASCADE)
    command_id = models.ForeignKey(Command, on_delete=models.CASCADE)

    class Meta:
        verbose_name = u'角色命令权限'
        verbose_name_plural = verbose_name
        db_table = 'role_command'

    def __str__(self):
        return self.role_id


class CommandArgs(models.Model):

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, null=True, blank=True)
    command_name = models.ForeignKey(Command, on_delete=models.CASCADE)

    class Meta:
        verbose_name = u'命令参数'
        verbose_name_plural = verbose_name
        db_table = 'command_args'

    def __str__(self):
        return self.name


class GroupName(models.Model):
    name = models.CharField(max_length=128, unique=True)
    create_time = models.DateTimeField(auto_created=True)

    class Meta:
        verbose_name = u'组名'
        verbose_name_plural = verbose_name
        db_table = 'group_name'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_time = timezone.now()
        return super(GroupName, self).save(*args, **kwargs)


class GroupIp(models.Model):
    group_id = models.ForeignKey(GroupName, on_delete=models.CASCADE)
    login_ip = models.CharField(max_length=30)
    login_user = models.CharField(max_length=30)
    login_port = models.CharField(max_length=30)
    login_password = models.CharField(max_length=100)
    connect = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_created=True)

    class Meta:
        verbose_name = u'IP'
        verbose_name_plural = verbose_name
        db_table = 'group_ip'

    def __str__(self):
        return self.login_ip

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_time = timezone.now()
        return super(GroupIp, self).save(*args, **kwargs)


class UserTask(models.Model):

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=100)
    task_id = models.CharField(max_length=100)
    # group_id = models.CharField(max_length=100)

    state = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=0)

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_time = timezone.now()
        self.update_time = timezone.now()
        return super(UserTask, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u'用户任务列表'
        verbose_name_plural = verbose_name
        db_table = 'user_task'


class UserTaskCommand(models.Model):
    task_id = models.ForeignKey(UserTask, on_delete=models.CASCADE)
    command_name = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)
    command_task_id = models.CharField(max_length=100)

    class Meta:
        verbose_name = u'执行清单命令'
        verbose_name_plural = verbose_name
        db_table = 'user_task_command'

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_time = timezone.now()
        return super(UserTaskCommand, self).save(*args, **kwargs)


class UserTaskCommandArgs(models.Model):
    user_command_id = models.ForeignKey(UserTaskCommand, on_delete=models.CASCADE)
    command_name = models.CharField(max_length=100)
    arg_name = models.CharField(max_length=100)
    command_data = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = u'执行清单命令参数'
        verbose_name_plural = verbose_name
        db_table = 'user_task_command_args'

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_time = timezone.now()
        return super(UserTaskCommandArgs, self).save(*args, **kwargs)


class ExecTask(models.Model):
    user_task = models.ForeignKey(UserTask, on_delete=models.CASCADE)
    group_id = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default=0)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = u'任务执行表'
        verbose_name_plural = verbose_name
        db_table = 'exec_task'

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_time = timezone.now()
        return super(ExecTask, self).save(*args, **kwargs)


class EventLog(models.Model):
    exec_id = models.ForeignKey(ExecTask, on_delete=models.CASCADE)
    task_log = models.CharField(max_length=1000)
    details_log = models.CharField(max_length=10000)

    STATE = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=0)

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_time = timezone.now()
        self.update_time = timezone.now()
        return super(EventLog, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u'用户执行日志'
        verbose_name_plural = verbose_name
        db_table = 'event_log'
