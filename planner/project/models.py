from django.db import models

import uuid

from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.

class BaseClass(models.Model):

    uuid = models.UUIDField(unique=True,default=uuid.uuid4)
    active_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True) # auto_now doesnt change
    updated_at = models.DateTimeField(auto_now_add=True) # auto_now_add changes with updates

    class Meta:

        abstract = True # to prevent it from appearing as model

class Project(BaseClass):

    name = models.CharField(max_length=250)

    description = CKEditor5Field('Description')

    document = models.FileField(upload_to='project-document')

    class Meta:

        verbose_name = 'Projects'
        verbose_name_plural = 'Projects'

    def __str__(self):

        return self.name

class AssignedProjects(BaseClass):

    project = models.ForeignKey('Project',on_delete=models.PROTECT,related_name='project')

    coordinate = models.ForeignKey('authentication.Profile',on_delete=models.PROTECT,related_name='coordinate')

    developers = models.ManyToManyField('authentication.Profile')

    project_duration = models.IntegerField()

    project_start_date = models.DateField()

    project_tentative_end_date = models.DateField()

    completed = models.BooleanField(default=False)

    completed_date = models.DateField(null=True,blank=True)

    class Meta:

        verbose_name = 'Assigned Projects'
        verbose_name_plural = 'Assigned Projects'

    def __str__(self):

        return f'{self.project.name}-{self.project_start_date}'

class PriorityChoices(models.TextChoices):

    LOW = 'Low','Low'

    MEDIUM = 'Medium','Medium'

    HIGH = 'High','High'

class Task(BaseClass):

    assigned_project = models.ForeignKey('AssignedProjects',on_delete=models.PROTECT,related_name='task_project')

    assign_to = models.ForeignKey('authentication.Profile',on_delete=models.PROTECT,related_name='task_assignment')

    title = models.CharField(max_length=225)

    description = models.TextField()

    priority = models.CharField(max_length=15,choices=PriorityChoices.choices)

    duration = models.TimeField(null=True,blank=True)

    start_date = models.DateField(null=True,blank=True)

    end_date = models.DateField(null=True,blank=True)

    completed = models.BooleanField(default=False)

    class Meta:
    
        verbose_name = 'Task'
        verbose_name_plural = 'Task'
    
    def __str__(self):
    
        return f'{self.assigned_project.project.name}-{self.assign_to.first_name}-{self.title}'