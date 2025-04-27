from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class Task(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True)  # Связь с проектом
    owner = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_tasks')  # Владелец задачи
    executioner = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='executed_tasks')  # Исполнитель задачи
    expected_time = models.DurationField(null=True, blank=True)  # Ожидаемое время
    execution_time = models.DurationField(null=True, blank=True)  # Время выполнения
    creation_date = models.DateTimeField(default=timezone.now)  # Дата создания задачи
    deadline = models.DurationField(null=True, blank=True)  # Дедлайн задачи
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )

    class Meta:
        db_table = 'tasks'

    def __str__(self):
        return f"Task: {self.project.name} - {self.status}"


class Project(models.Model):
    name = models.CharField(max_length=255, null=True)  # Название проекта
    description = models.TextField(null=True)  # Описание проекта
    date_start = models.DateField(null=True)  # Дата старта
    date_end = models.DateField(null=True)  # Дата завершения
    product_owner = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='projects', null=True)  # Владелец проекта

    class Meta:
        db_table = 'projects'

    def __str__(self):
        return self.name



# Модель для системных ролей
class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Название роли, например, "admin", "user"
    description = models.TextField(blank=True, null=True)  # Описание роли

    class Meta:
        db_table = 'system_role'

    def __str__(self):
        return self.name

# Модель для ролей внутри проекта

class ProjectRole(models.Model):
    role = models.CharField(max_length=255, unique=True, null=True, blank=True)

    class Meta:
        db_table = 'project_roles'

    def __str__(self):
        return f'{self.user.name} - {self.role.name} in {self.project.name}'



# Менеджер для кастомной модели пользователя
class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Кастомная модель пользователя
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, default='not_stated')
    password = models.CharField(max_length=255)

    # Стандартные поля
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    # Связь с ролью системы
    system_role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)


    # Устанавливаем email как уникальный идентификатор пользователя
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email

class UserProject(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    user_role = models.ForeignKey(ProjectRole, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_project'

# Изменить названия в базе данных откатить
# дата создания таски и дедлайн таски
# Получение задач по фильтрам и сортировка по исполнителю
# Привязка задачи к проекту и к исполнителю
#  Сделать оставшиеся таблицы
#
