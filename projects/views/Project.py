from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User
from django.db.models import Q

from ..models.Project import Project, ProjectSerializer
from ..models.Contributor import Contributor, ContributorSerializer
from ..models.Issue import Issue, IssueSerializer
from ..models.Comment import Comment, CommentSerializer


class ProjectsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = Project.objects.filter(
            Q(contributors=request.user))

        return Response(ProjectSerializer(projects, many=True).data)

    def post(self, request):
        required_fields = ['title', 'description', 'type']

        for field in required_fields:
            if not field in request.data:
                return Response(status=400, data={'error': f'Missing required fields. ({field})'})

        project = Project.objects.create(
            title=request.data['title'], description=request.data['description'], type=request.data['type'])
        project.contributors.add(request.user, through_defaults={
                                 'permission': 'author', 'role': 'author'})
        return Response(ProjectSerializer(project).data)


class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, _, project_id):
        project = Project.objects.get(id=project_id)
        return Response(ProjectSerializer(project).data)

    def put(self, request, project_id):
        project = Project.objects.get(id=project_id)

        if request.user not in project.contributors.all():
            return Response(status=403, data={'message': 'You are not a contributor to this project.'})

        project.title = request.data.get('title', project.title)
        project.description = request.data.get(
            'description', project.description)
        project.type = request.data.get('type', project.type)

        project.save()
        return Response(ProjectSerializer(project).data)

    def delete(self, request, project_id):
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

    def get(self, _, project_id):
        users = Contributor.objects.filter(project_id=project_id)

        return Response(ContributorSerializer(users, many=True).data)

    def post(self, request, project_id):
        project = Project.objects.get(id=project_id)

        if request.user not in project.contributors.all():
            return Response(status=403, data={'message': 'You are not a contributor to this project.'})

        required_fields = ['user_id', 'permission']

        for field in required_fields:
            if not field in request.data:
                return Response(status=400, data={'error': f'Missing required fields. ({field})'})

        permission = request.data['permission']

        if permission not in ['author', 'editor']:
            return Response(status=400, data={'error': 'Invalid permission.'})

        user = User.objects.filter(id=request.data['user_id']).first()

        if not user:
            return Response(status=400, data={'error': 'Invalid user.'})

        if user in project.contributors.all():
            return Response(status=400, data={'error': 'User is already a contributor to this project.'})

        project.contributors.add(user, through_defaults={
                                 'permission': permission, 'role': request.data.get('role', permission)})

        return Response(status=204, data={'message': 'User added to project.'})

    def delete(self, request, project_id, user_id):
        project = Project.objects.get(id=project_id)

        if request.user not in project.contributors.all():
            return Response(status=403, data={'message': 'You are not a contributor to this project.'})

        contributor = Contributor.objects.get(
            user=request.user, project=project)

        if contributor.permission != 'author':
            return Response(status=403, data={'message': 'You are not an author of this project.'})

        user = User.objects.get(id=user_id)

        if user not in project.contributors.all():
            return Response(status=400, data={'error': 'User is not a contributor to this project.'})

        contributor = Contributor.objects.get(
            user=user, project=project)

        if contributor.permission == 'author':
            return Response(status=403, data={'message': 'You cannot remove an author from a project.'})

        project.contributors.remove(user)

        return Response(status=204, data={'message': 'User removed from project.'})


class ProjectIssuesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, _, project_id):
        issues = Issue.objects.filter(project_id=project_id)

        return Response(IssueSerializer(issues, many=True).data)

    def post(self, request, project_id):
        project = Project.objects.get(id=project_id)

        if request.user not in project.contributors.all():
            return Response(status=403, data={'message': 'You are not a contributor to this project.'})

        required_fields = ['title', 'description',
                           'tag', 'priority', 'status']

        for field in required_fields:
            if not field in request.data:
                return Response(status=400, data={'error': f'Missing required fields. ({field})'})

        assignee = None

        if 'assignee' in request.data:
            if not User.objects.filter(id=request.data['assignee']).exists():
                return Response(status=400, data={'error': 'Invalid assignee.'})

            assignee = User.objects.get(id=request.data['assignee'])

        issue = Issue.objects.create(
            title=request.data['title'],
            description=request.data['description'],
            tag=request.data['tag'],
            priority=request.data['priority'],
            status=request.data['status'],
            assignee=assignee,
            project=project,
            author=request.user)

        return Response(IssueSerializer(issue).data)

    def put(self, request, project_id, issue_id):
        project = Project.objects.get(id=project_id)

        if request.user not in project.contributors.all():
            return Response(status=403, data={'message': 'You are not a contributor to this project.'})

        issue = Issue.objects.filter(id=issue_id).first()

        if not issue:
            return Response(status=400, data={'error': 'Invalid issue.'})

        if issue.project != project:
            return Response(status=400, data={'error': 'Issue does not belong to this project.'})

        issue.title = request.data.get('title', issue.title)
        issue.description = request.data.get(
            'description', issue.description)
        issue.tag = request.data.get('tag', issue.tag)
        issue.priority = request.data.get('priority', issue.priority)
        issue.status = request.data.get('status', issue.status)

        if 'assignee' in request.data:
            if not User.objects.filter(id=request.data['assignee']).exists():
                return Response(status=400, data={'error': 'Invalid assignee.'})

            issue.assignee = User.objects.get(id=request.data['assignee'])

        issue.save()

        return Response(IssueSerializer(issue).data)

    def delete(self, request, project_id, issue_id):
        project = Project.objects.get(id=project_id)

        if request.user not in project.contributors.all():
            return Response(status=403, data={'message': 'You are not a contributor to this project.'})

        issue = Issue.objects.filter(id=issue_id).first()

        if not issue:
            return Response(status=404, data={'error': 'Issue not found.'})

        if issue.project != project:
            return Response(status=400, data={'error': 'Issue does not belong to this project.'})

        issue.delete()

        return Response(status=204, data={'message': 'Issue deleted.'})


class ProjectIssuesCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, _, project_id, issue_id, comment_id=None):
        if comment_id:
            comments = Comment.objects.filter(id=comment_id).first()

            return Response(CommentSerializer(comments).data)

        comments = Comment.objects.filter(issue_id=issue_id)

        return Response(CommentSerializer(comments, many=True).data)

    def post(self, request, project_id, issue_id):
        project = Project.objects.get(id=project_id)

        if request.user not in project.contributors.all():
            return Response(status=403, data={'message': 'You are not a contributor to this project.'})

        issue = Issue.objects.filter(id=issue_id).first()

        if not issue:
            return Response(status=400, data={'error': 'Invalid issue.'})

        if issue.project != project:
            return Response(status=400, data={'error': 'Issue does not belong to this project.'})

        required_fields = ['description']

        for field in required_fields:
            if not field in request.data:
                return Response(status=400, data={'error': f'Missing required fields. ({field})'})

        comment = Comment.objects.create(
            description=request.data['description'],
            issue=issue,
            author=request.user)

        return Response(CommentSerializer(comment).data)

    def delete(self, request, project_id, issue_id, comment_id):
        project = Project.objects.get(id=project_id)

        if request.user not in project.contributors.all():
            return Response(status=403, data={'message': 'You are not a contributor to this project.'})

        issue = Issue.objects.filter(id=issue_id).first()

        if not issue:
            return Response(status=400, data={'error': 'Invalid issue.'})

        if issue.project != project:
            return Response(status=400, data={'error': 'Issue does not belong to this project.'})

        comment = Comment.objects.filter(id=comment_id).first()

        if not comment:
            return Response(status=404, data={'error': 'Comment not found.'})

        if comment.issue != issue:
            return Response(status=400, data={'error': 'Comment does not belong to this issue.'})

        comment.delete()

        return Response(status=204, data={'message': 'Comment deleted.'})

    def put(self, request, project_id, issue_id, comment_id):
        project = Project.objects.get(id=project_id)

        if request.user not in project.contributors.all():
            return Response(status=403, data={'message': 'You are not a contributor to this project.'})

        issue = Issue.objects.filter(id=issue_id).first()

        if not issue:
            return Response(status=400, data={'error': 'Invalid issue.'})

        if issue.project != project:
            return Response(status=400, data={'error': 'Issue does not belong to this project.'})

        comment = Comment.objects.filter(id=comment_id).first()

        if not comment:
            return Response(status=404, data={'error': 'Comment not found.'})

        if comment.issue != issue:
            return Response(status=400, data={'error': 'Comment does not belong to this issue.'})

        comment.description = request.data.get(
            'description', comment.description)

        comment.save()

        return Response(CommentSerializer(comment).data)
