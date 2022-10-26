from django.urls import path

from . import views

urlpatterns = [
    path('signup', views.SignupView.as_view()),
    path('projects', views.ProjectsView.as_view(), name='projects'),
    path('projects/<int:project_id>', views.ProjectView.as_view(), name='project'),
    path('projects/<int:project_id>/users', views.ProjectUsersView.as_view(), name='project_users'),
    path('projects/<int:project_id>/users/<int:user_id>', views.ProjectUsersView.as_view(), name='project_users'),
    path('projects/<int:project_id>/issues', views.ProjectIssuesView.as_view(), name='project_issues'),
    path('projects/<int:project_id>/issues/<int:issue_id>', views.ProjectIssuesView.as_view(), name='project_issues'),
    path('projects/<int:project_id>/issues/<int:issue_id>/comments', views.ProjectIssuesCommentsView.as_view(), name='project_issues_comments'),
    path('projects/<int:project_id>/issues/<int:issue_id>/comments/<int:comment_id>', views.ProjectIssuesCommentsView.as_view(), name='project_issues_comments'),
]
