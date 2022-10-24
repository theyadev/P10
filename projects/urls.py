from django.urls import path

from . import views

urlpatterns = [
    path('projects', views.ProjectsView.as_view(), name='projects'),
    path('projects/<int:project_id>', views.ProjectView.as_view(), name='project'),
    path('projects/<int:project_id>/users', views.ProjectUsersView.as_view(), name='project_users'),
]
