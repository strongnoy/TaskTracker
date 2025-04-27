from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from TaskTrackerPetProjectDjango.models import Project, CustomUser
from TaskTrackerPetProjectDjango.serializers import ProjectSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project(request, project_id):
    """Get project by id"""
    if request.method == 'GET':
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ТУТ НЕПРАВИЛЬНО ТУТ СОХРАНЯЕТСЯ АЙДИ ВМЕСТО ОБЪЕКТА ОВНЕРА
@extend_schema(
    request=ProjectSerializer,
    responses={201: ProjectSerializer},
)
@api_view(['POST'])
def create_project(request):
    """Create a new project"""
    if request.method == 'POST':
        product_owner_id = request.data.get('product_owner')
        if product_owner_id:
            try:
                product_owner = CustomUser.objects.get(id=product_owner_id)
            except CustomUser.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
            request.data['product_owner'] = product_owner

        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_project(request, project_id):
    """Update project by id"""
    if request.method == 'PUT':
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)



        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_project(request, project_id):
    """Delete project by id"""
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.user != project.product_owner:
        return Response({"detail": "You do not have permission to delete this project."},
                        status=status.HTTP_403_FORBIDDEN)

    project.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
