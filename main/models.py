from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q


# Create your models here.
class Project(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=300)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    @classmethod
    def create(cls, **kwargs):
        """
        THIS METHOD CREATES A PROJECT
        Keyword Arguments:
            **kwargs {dict} -- project data
        """
        project = cls.objects.create(**kwargs)
        return project

    @classmethod
    def filter_by_created_date(cls, start_date, end_date, user_id):
        return cls.objects.filter(
            created_at__range=[start_date, end_date], user__id=user_id
        )

    @classmethod
    def search_project(cls, search_term, user_id):
        return cls.objects.filter(
            Q(user__id=user_id)
            & (Q(name__icontains=search_term) | Q(description__icontains=search_term))
        )

    @classmethod
    def sort_data(cls, queryset, sort_by):
        if sort_by == "asc":
            return queryset.order_by("id")
        elif sort_by == "desc":
            return queryset.order_by("-id")

        return queryset


class Task(models.Model):
    STATUS_OPTIONS = (
        ("TO_DO", "TO_DO"),
        ("IN_PROGRESS", "IN_PROGRESS"),
        ("COMPLETED", "COMPLETED"),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    due_date = models.DateTimeField()
    priority_level = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=STATUS_OPTIONS, default="TO_DO")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    @classmethod
    def create(cls, **kwargs):
        task = cls.objects.create(**kwargs)
        return task

    @classmethod
    def filter_by_created_date(cls, start_date, end_date, project_ids):
        return cls.objects.filter(
            created_at__range=[start_date, end_date], project__id__in=project_ids
        )

    @classmethod
    def filter_by_due_date(cls, start_date, end_date, project_ids):
        return cls.objects.filter(
            due_date__range=[start_date, end_date], project__id__in=project_ids
        )

    @classmethod
    def filter_by_status(cls, status, project_ids):
        return cls.objects.filter(
            status=str(status).upper(), project__id__in=project_ids
        )

    @classmethod
    def search_task(cls, search_term, project_ids):
        return cls.objects.filter(
            Q(project__id__in=project_ids)
            & (Q(title__icontains=search_term) | Q(description__icontains=search_term))
        )

    @classmethod
    def sort_data(cls, queryset, sort_by):
        if sort_by == "asc":
            return queryset.order_by("id")
        elif sort_by == "desc":
            return queryset.order_by("-id")

        return queryset

    @classmethod
    def update(cls, task_id, **kwargs):
        task = cls.objects.filter(id=task_id).update(**kwargs)
        return task
