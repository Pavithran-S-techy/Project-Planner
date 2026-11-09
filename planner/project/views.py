from django.shortcuts import render

from rest_framework.response import Response

from rest_framework.views import APIView

from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView,ListAPIView

from . models import Project,AssignedProjects,Task

from . serializers import ProjectSerializer,AssignedProjectSerializer,TaskSerializer

from planner.utils import generate_tasks

from django.db import transaction # for implementing transaction

from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.permissions import IsAdmin,IsProjectCoordinator

from rest_framework.permissions import IsAuthenticated

# Create your views here.

class ProjectListCreateView(ListCreateAPIView):

    authentication_classes=[JWTAuthentication]

    def get_permissions(self):

        permissions = []

        if self.request.method == 'POST':

            permissions = [IsAdmin]

        else :

            permissions[IsAuthenticated] # to prevent public from viewing company details

        return [permission() for permission in permissions]

    queryset = Project.objects.filter(active_status = True)

    serializer_class = ProjectSerializer

class ProjectRetrieveUpdateDestroyview(RetrieveUpdateDestroyAPIView):

    authentication_classes=[JWTAuthentication]

    def get_permissions(self):

        permissions = []

        if self.request.method in ['PATCH', 'DELETE']:

            permissions = [IsAdmin]

        else :
        
            permissions[IsAuthenticated] # to prevent public from viewing company details

        return [permission() for permission in permissions]

    lookup_field = 'uuid'

    queryset = Project.objects.filter(active_status = True)

    serializer_class = ProjectSerializer

    def perform_destroy(self, instance):

        # instance is the project object thats about to be deleted (sof deleted)

        instance.active_status = False

        instance.save()

class AssignedProjectsListCreateView(ListCreateAPIView):

    authentication_classes=[JWTAuthentication]

    def get_permissions(self):
    
        permissions = []

        if self.request.method == 'POST':

            permissions = [IsAdmin | IsProjectCoordinator]

        else :
                
            permissions[IsAuthenticated] # to prevent public from viewing company details

        return [permission() for permission in permissions]

    queryset = AssignedProjects.objects.filter(active_status = True).select_related('project','coordinate').prefetch_related('developers') # select_related to avoid n+1,etc such proplems. so write data with foriengkey inside this (use thier related name). prefetch_related for many to many data
    
    serializer_class = AssignedProjectSerializer

class AssignedProjectRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):

    authentication_classes=[JWTAuthentication]

    def get_permissions(self):
        
        permissions = []

        if self.request.method in ['PATCH', 'DELETE']:

            permissions = [IsAdmin | IsProjectCoordinator]

        else :
                
            permissions[IsAuthenticated] # to prevent public from viewing company details

        return [permission() for permission in permissions]

    lookup_field = 'uuid'

    queryset = AssignedProjects.objects.filter(active_status = True).select_related('project','coordinate').prefetch_related('developers')

    serializer_class = AssignedProjectSerializer

    def perform_destroy(self, instance):

        # instance is the project object thats about to be deleted (sof deleted)

        instance.active_status = False

        instance.save()

class TaskLisCreatetView(ListCreateAPIView):

    authentication_classes=[JWTAuthentication]

    def get_permissions(self):
        
        permissions = []

        if self.request.method == 'POST':

            permissions = [IsProjectCoordinator]

        return [permission() for permission in permissions]

    serializer_class = TaskSerializer

    def get_queryset(self):

        uuid = self.kwargs.get('uuid')

        assigned_project = AssignedProjects.objects.get(uuid=uuid)

        tasks = Task.objects.filter(active_status=True,assigned_project=assigned_project)

        return tasks

    def perform_create(self, serializer):

        uuid = self.kwargs.get('uuid')

        assigned_project = AssignedProjects.objects.get(uuid=uuid)

        data_copy = serializer.validated_data.copy()

        data_copy['assigned_project'] = assigned_project

        serializer.save(assigned_project=assigned_project)

class TaskRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):

    authentication_classes=[JWTAuthentication]

    def get_permissions(self):
            
        permissions = []

        if self.request.method in ['PATCH', 'DELETE']:

            permissions = [IsProjectCoordinator]

        return [permission() for permission in permissions]

    lookup_field = 'uuid'

    queryset = Task.objects.filter(active_status = True).select_related('assigned_project','assign_to')

    serializer_class = TaskSerializer

    def perform_destroy(self, instance):

        instance.active_status = False

        instance.save()

class GenerateTaskWithAIView(APIView):

    authentication_classes=[JWTAuthentication]

    permission_classes=[IsProjectCoordinator]

    def post(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        assigned_project = AssignedProjects.objects.get(uuid=uuid)

        response,developers = generate_tasks(assigned_project)

        tasks = [Task(
                        assigned_project=assigned_project,
                        assign_to_id = task.developer_id,
                        title = task.title,
                        description = task.description,
                        priority = task.priority
                    ) 
                 for task in response.tasks if task.developer_id in developers]

        with transaction.atomic(): # from implemention db transaction

            Task.objects.bulk_create(tasks) # will create easily if give as a list

        return Response(status=200)