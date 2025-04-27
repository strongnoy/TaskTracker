from datetime import timedelta

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Q
from TaskTrackerPetProjectDjango.models import Task, Project, CustomUser
from TaskTrackerPetProjectDjango.serializers import TaskSerializer, ProjectSerializer, CustomUserSerializer


@api_view(['POST'])
def create_task(request):
    """ Creates a new task"""
    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            # привязка к проекту
            project_id = request.data.get('Project_id')
            if project_id:
                try:
                    project = Project.objects.get(id=project_id)
                    serializer.validated_data['project'] = project
                except Project.DoesNotExist:
                    return Response({'error': 'Project not found'}, status=status.HTTP_400_BAD_REQUEST)

            user_id = request.data.get('Owner_id')
            if user_id:
                try:
                    user = CustomUser.objects.get(id=user_id)
                    serializer.validated_data['Owner_id'] = user
                except CustomUser.DoesNotExist:
                    return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_task(request, task_id):
    """ Returns task by id"""
    if request.method == 'GET':
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
def update_task(request, task_id):
    """ Updates task by id"""
    if request.method == 'PUT':
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def track_time(request, task_id):
    """Track time of task by id"""
    if request.method == 'PUT':
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        execution_time = request.data.get('Execution_time')
        if execution_time:
            try:
                # Преобразуем время из строки или числа в timedelta
                task.Execution_time = timedelta(seconds=int(execution_time))
                task.save()
                return Response({'message': 'Time tracked successfully'}, status=status.HTTP_200_OK)
            except ValueError:
                return Response({'error': 'Invalid time format'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Execution time not provided'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_task(request, task_id):
    """ Deletes task by id"""
    if request.method == 'DELETE':
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH'])
def update_status(request, task_id):
    """ Updates task status by id"""
    if request.method == 'PATCH':
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status:
            task.status = new_status
            task.save()
            return Response({'message': 'status updated'}, status=status.HTTP_200_OK)
        return Response({'error': 'Status not provided'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def assign_task(request, task_id):
    """ Assigns task to executioner"""
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    executioner_id = request.data.get('executioner_id')
    if not executioner_id:
        return Response({'error': 'executioner_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        executioner = CustomUser.objects.get(id=executioner_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    task.executioner = executioner
    task.save()

    serializer = TaskSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_tasks(request):
    """ Returns tasks with filter and sorting"""
    executioner_id = request.query_params.get('executioner_id', None)
    if executioner_id:
        try:
            executioner = CustomUser.objects.get(id=executioner_id)
            tasks = Task.objects.filter(executioner=executioner)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        tasks = Task.objects.all()

    sort_by = request.query_params.get('sort_by', 'executioner')
    tasks = tasks.order_by(sort_by)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)