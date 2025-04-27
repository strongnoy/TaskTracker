from rest_framework import serializers
from .models import Task, CustomUser, Project, Role, ProjectRole, UserProject
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = '__all__'

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class ProjectSerializer(serializers.ModelSerializer):
    product_owner = CustomUserSerializer(read_only=True)
    product_owner_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),  # Ожидаем только ID
        source="product_owner",  # Связываем с product_owner
        write_only=True  # Не отображаем в ответе
    )

    class Meta:
        model = Project
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class ProjectRoleSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)  # Для сериализации связанных данных проекта
    role = RoleSerializer(read_only=True)  # Для сериализации связанных данных роли

    class Meta:
        model = ProjectRole
        fields = '__all__'


class UserProjectSerializer(serializers.ModelSerializer):
    user_id = CustomUserSerializer(read_only=True)  # Вложенный сериализатор для отображения пользователя
    project_id = ProjectSerializer(read_only=True)  # Вложенный сериализатор для отображения проекта

    class Meta:
        model = UserProject
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
