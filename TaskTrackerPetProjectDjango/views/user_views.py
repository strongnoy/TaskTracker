from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from TaskTrackerPetProjectDjango.models import CustomUser, Role, Project, ProjectRole, UserProject
from TaskTrackerPetProjectDjango.serializers import CustomUserSerializer, RoleSerializer, ProjectSerializer, \
    ProjectRoleSerializer, RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

@api_view(['GET'])
@api_view(['GET'])
def get_user_info(request, user_id):
    """Get information about a user"""
    if request.method == 'GET':
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Получаем роли пользователя
        user_roles = ProjectRole.objects.filter(user=user)
        user_projects = [role.project for role in user_roles]

        # Сериализация данных
        serializer = CustomUserSerializer(user)
        user_data = serializer.data
        user_data['roles'] = RoleSerializer([role.role for role in user_roles], many=True).data
        user_data['projects'] = ProjectSerializer(user_projects, many=True).data

        return Response(user_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_user(request):
    """Create a new user"""
    if request.method == 'POST':
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            system_role_id = request.data.get('system_role')
            if system_role_id:
                try:
                    system_role = Role.objects.get(id=system_role_id)
                    user.system_role = system_role
                    user.save()
                except Role.DoesNotExist:
                    return Response({'error': 'Role not found'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_user(request, user_id):
    """Update a user"""
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Обновление данных пользователя
    serializer = CustomUserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Создание связи пользователя с проектом и назначение роли
@api_view(['POST'])
def add_user_to_project(request, user_id, project_id):
    """Add a user to a project and assign a role"""
    if request.method == 'POST':
        try:
            user = CustomUser.objects.get(id=user_id)
            project = Project.objects.get(id=project_id)
        except (CustomUser.DoesNotExist, Project.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Находим роль пользователя в проекте
        role_name = request.data.get('role')  # Роль должна быть передана в теле запроса
        role = Role.objects.get(name=role_name)

        # Создаем связь проекта и пользователя
        project_role = ProjectRole.objects.create(project=project, role=role, user=user)

        # Создаем запись в UserProject для связи
        UserProject.objects.create(user_id=user, project_id=project, user_role=project_role)

        return Response({'message': 'User added to project with role'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    serializer = TokenObtainPairSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.data.serializer.validated_data['access'], status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    view = TokenRefreshView.as_view()
    return view(request._request)


