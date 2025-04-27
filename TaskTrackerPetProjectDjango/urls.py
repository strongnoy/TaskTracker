"""
URL configuration for TaskTrackerPetProjectDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import task_views, project_views, user_views
from drf_yasg.views import get_schema_view as yasg_view
from drf_yasg import openapi
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = yasg_view(
    openapi.Info(
        title="Task Tracker API",
        default_version='v1',
        description="Документация API для проекта Task Tracker",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="youremail@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    #Задачи

    path('task/create', task_views.create_task , name='create_task'),
    path('task/update/<int:task_id>', task_views.update_task, name='update_task'),
    path('task/delete/<int:task_id>', task_views.delete_task, name='delete_task'),
    path('task/<int:task_id>', task_views.get_task, name='get_task'),
    path('task/track_time/<int:task_id>', task_views.track_time, name='track_time'),
    path('task/update_status/<int:task_id>', task_views.update_status, name='update_status'),
    path('task/update_status/<int:task_id>', task_views.update_status, name='update_status'),
    path('task/assign/<int:task_id>', task_views.assign_task, name='assign_task'),
    #Проекты

    path('project/<int:project_id>', project_views.get_project, name='get_project'),
    path('project/create', project_views.create_project, name='create_project'),
    path('project/update/<int:project_id>', project_views.update_project, name='update_project'),
    path('project/delete/<int:project_id>', project_views.delete_project, name='delete_project'),
    # Юзеры

    path('user/<int:user_id>', user_views.get_user_info, name='get_user_info'),
    path('user/create', user_views.create_user, name='create_user'),
    path('user/update/<int:user_id>', user_views.update_user, name='update_user'),
    path('user/addtoproject/<int:project_id>/<int:user_id>', user_views.add_user_to_project, name='add_to_project'),
    #Токены

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', user_views.refresh_token, name='token_refresh'),
    path('register/', user_views.register_user, name = 'auth_register'),
    path('login/', user_views.login_user, name = 'auth_login')


]
