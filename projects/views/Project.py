from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User
from django.db.models import Q

from ..models.Project import Project, ProjectSerializer
from ..models.Contributor import Contributor, ContributorSerializer


class ProjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        projects = Project.objects.filter(
            Q(contributors=request.user))

        return Response(ProjectSerializer(projects, many=True).data)

    def post(self, request, format=None):
        if not 'title' in request.data or not 'description' in request.data or not 'type' in request.data:
            return Response(status=400, data={'error': 'Missing required fields. (title, description, type)'})

        project = Project.objects.create(
            title=request.data['title'], description=request.data['description'], type=request.data['type'])
        project.contributors.add(request.user, through_defaults={
                                 'permission': 'author', 'role': 'author'})
        return Response(ProjectSerializer(project).data)


class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, format=None):
        project = Project.objects.get(id=project_id)
        return Response(ProjectSerializer(project).data)

    def put(self, request, project_id, format=None):
        project = Project.objects.get(id=project_id)

        if request.user not in project.contributors.all():
            return Response(status=403, data={'message': 'You are not a contributor to this project.'})

        project.title = request.data.get('title', project.title)
        project.description = request.data.get(
            'description', project.description)
        project.type = request.data.get('type', project.type)

        project.save()
        return Response(ProjectSerializer(project).data)

    def delete(self, request, project_id, format=None):
        project = Project.objects.get(id=project_id)

        if request.user not in project.contributors.all():
            return Response(status=403, data={'message': 'You are not a contributor to this project.'})

        contributor = Contributor.objects.get(
            user=request.user, project=project)

        if contributor.permission != 'author':
            return Response(status=403, data={'message': 'You are not an author of this project.'})

        project.delete()
        return Response(status=204, data={'message': 'Project deleted.'})


class ProjectUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, format=None):
        users = Contributor.objects.filter(project_id=project_id)

        return Response(ContributorSerializer(users, many=True).data)

    def post(self, request, project_id, format=None):
        project = Project.objects.get(id=project_id)

        if request.user not in project.contributors.all():
            return Response(status=403, data={'message': 'You are not a contributor to this project.'})

        if not 'user_id' in request.data:
            return Response(status=400, data={'error': 'Missing required fields. (user_id)'})

        user = User.objects.get(id=request.data['user_id'])

        if user in project.contributors.all():
            return Response(status=400, data={'error': 'User is already a contributor to this project.'})

        project.contributors.add(user)

        return Response(status=204, data={'message': 'User added to project.'})
