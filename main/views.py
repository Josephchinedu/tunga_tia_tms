from datetime import datetime

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from requests import delete
from rest_framework import exceptions, status
from rest_framework.decorators import authentication_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from main.models import Project
from main.models import Task as ProjectTask
from main.serializer import (
    CreateAccountSerializer,
    LoginSerializer,
    ProjectModelSerializer,
    ProjectSerializer,
    TaskModelSerializer,
    TaskSerializer,
)

# error_codes = {
#     "40001": "User not found",
#     "40002": "Invalid input",
#     "40003": "Unauthorized access",
#     "40004": "Resource not found",
#     "40005": "Validation failed",
#     "40006": "Duplicate entry",
#     "40007": "Invalid request",
#     "40008": "Permission denied",
#     "40009": "Invalid token",
#     "40010": "Expired token"
# }


# Create your views here.
""" USER ACCOUNT SECTION """


class CreateAccountApiView(APIView):
    serializer_class = CreateAccountSerializer

    create_user_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING),
            "email": openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
            ),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
            "confirm_password": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["username", "email", "password", "confirm_password"],
    )

    create_user_response_schema = {
        status.HTTP_400_BAD_REQUEST: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        status.HTTP_201_CREATED: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "code": openapi.Schema(type=openapi.TYPE_STRING),
                "tokens": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            },
        ),
    }

    @method_decorator(csrf_exempt)
    @swagger_auto_schema(
        tags=["authentications"],
        request_body=create_user_schema,
        responses=create_user_response_schema,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        email = serializer.validated_data.get("email")

        User = get_user_model()

        # check if user email or username already exists
        if User.objects.filter(email=email).exists():
            raise exceptions.ValidationError({"email": "Email already exists"})
        elif User.objects.filter(username=username).exists():
            raise exceptions.ValidationError({"username": "Username already exists"})
        else:
            user = User.objects.create(
                username=username, password=make_password(password), email=email
            )
            user.save()

            tokenr = TokenObtainPairSerializer().get_token(user)
            tokena = AccessToken().for_user(user)

            data = {
                "error": False,
                "code": "201",
            }

            data["tokens"] = {"refresh": str(tokenr), "access": str(tokena)}

            return Response(data, status=status.HTTP_201_CREATED)


class LoginApiView(APIView):
    serilaier_class = LoginSerializer

    login_schema = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username_or_email": openapi.Schema(type=openapi.TYPE_STRING),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["username_or_email", "password"],
    )

    login_response_schema = {
        status.HTTP_400_BAD_REQUEST: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "code": openapi.Schema(type=openapi.TYPE_STRING),
                "message": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "error": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "code": openapi.Schema(type=openapi.TYPE_STRING),
                "tokens": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            },
        ),
    }

    @method_decorator(csrf_exempt)
    @swagger_auto_schema(
        tags=["authentications"],
        request_body=login_schema,
        responses=login_response_schema,
    )
    def post(self, request):
        serilaizer = self.serilaier_class(data=request.data)
        serilaizer.is_valid(raise_exception=True)

        username_or_email = serilaizer.validated_data.get("username_or_email")
        password = serilaizer.validated_data.get("password")

        try:
            user = authenticate(email=username_or_email, password=password)
        except Exception as e:
            data = {
                "error": True,
                "code": "40001",
                "message": str(e),
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        tokenr = TokenObtainPairSerializer().get_token(user)
        tokena = AccessToken().for_user(user)

        data = {
            "error": False,
            "code": "200",
        }

        data["tokens"] = {"refresh": str(tokenr), "access": str(tokena)}

        return Response(data, status=status.HTTP_200_OK)


class ProjectApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    serializer_class = ProjectSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        create_project_payload = {
            "user": request.user,
            "name": serializer.validated_data.get("name"),
            "description": serializer.validated_data.get("description"),
        }

        project = Project.create(**create_project_payload)

        data = {
            "error": False,
            "code": "201",
            "project": ProjectModelSerializer(project).data,
        }

        return Response(data, status=status.HTTP_201_CREATED)

    def get(self, request):
        sort_by = request.GET.get("sort_by")
        search = request.GET.get("search")
        created_date_from = request.GET.get("created_date_from")
        created_date_to = request.GET.get("created_date_to")

        sort_options = ["asc", "desc"]

        if sort_by and sort_by not in sort_options:
            data = {
                "error": True,
                "code": "40007",
                "message": "Invalid sort option",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if created_date_from and not created_date_to:
            data = {
                "error": True,
                "code": "40007",
                "message": "End date is required",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if created_date_to and not created_date_from:
            data = {
                "error": True,
                "code": "40007",
                "message": "Start date is required",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if created_date_from and created_date_to:
            # formate date
            try:
                if created_date_from:
                    datetime.strptime(created_date_from, "%Y-%m-%d")
                if created_date_to:
                    datetime.strptime(created_date_to, "%Y-%m-%d")
            except:
                data = {
                    "error": True,
                    "code": "40007",
                    "message": "Invalid date format. Date format should be YYYY-MM-DD",
                }

                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if created_date_from and created_date_to:
            project_qs = Project.filter_by_created_date(
                start_date=created_date_from,
                end_date=created_date_to,
                user_id=request.user.id,
            )
        elif search:
            project_qs = Project.search_project(
                search_term=search, user_id=request.user.id
            )

        else:
            project_qs = Project.objects.filter(user__id=request.user.id)

        if sort_by:
            project_qs = Project.sort_data(queryset=project_qs, sort_by=sort_by)

        paginator = PageNumberPagination()
        paginator.page_size = 10

        result_page = paginator.paginate_queryset(project_qs, request)

        serialized_data = ProjectModelSerializer(result_page, many=True).data

        data = {
            "error": False,
            "code": "200",
            "message": "data fetched successfully",
            "data": serialized_data,
        }

        return paginator.get_paginated_response(data)

    def put(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        project_id = request.GET.get("project_id")

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            data = {
                "error": True,
                "code": "40004",
                "message": "Project not found",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        project.name = serializer.validated_data.get("name")
        project.description = serializer.validated_data.get("description")
        project.save()

        data = {
            "error": False,
            "code": "200",
            "message": "Project updated successfully",
            "project": ProjectModelSerializer(project).data,
        }

        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request):
        project_id = request.GET.get("project_id")

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            data = {
                "error": True,
                "code": "40004",
                "message": "Project not found",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        name = request.data.get("name", project.name)
        description = request.data.get("description", project.description)
        is_active = request.data.get("is_active", project.is_active)

        project.name = name
        project.description = description
        project.is_active = is_active
        project.save()

        data = {
            "error": False,
            "code": "200",
            "message": "Project updated successfully",
            "project": ProjectModelSerializer(project).data,
        }

        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request):
        project_id = request.GET.get("project_id")

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            data = {
                "error": True,
                "code": "40004",
                "message": "Project not found",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        project.delete()

        data = {
            "error": False,
            "code": "200",
            "message": "Project deleted successfully",
        }

        return Response(data, status=status.HTTP_200_OK)


class ProjectTaskApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    serializer_class = TaskSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        project_id = serializer.validated_data.get("project_id")
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            data = {
                "error": True,
                "code": "40004",
                "message": "Project not found",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        create_task_payload = {
            "project": project,
            "title": serializer.validated_data.get("title"),
            "description": serializer.validated_data.get("description"),
            "due_date": serializer.validated_data.get("due_date"),
            "priority_level": serializer.validated_data.get("priority_level"),
            "status": serializer.validated_data.get("status"),
        }

        task = ProjectTask.create(**create_task_payload)

        data = {
            "error": False,
            "code": "201",
            "task": TaskModelSerializer(task).data,
        }

        return Response(data, status=status.HTTP_201_CREATED)

    def get(self, request):
        sort_by = request.GET.get("sort_by")
        search = request.GET.get("search")
        created_date_from = request.GET.get("created_date_from")
        created_date_to = request.GET.get("created_date_to")
        due_date_from = request.GET.get("due_date_from")
        due_date_to = request.GET.get("due_date_to")

        sort_options = ["asc", "desc"]

        if sort_by and sort_by not in sort_options:
            data = {
                "error": True,
                "code": "40007",
                "message": "Invalid sort option",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if created_date_from and not created_date_to:
            data = {
                "error": True,
                "code": "40007",
                "message": "End date is required",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if created_date_to and not created_date_from:
            data = {
                "error": True,
                "code": "40007",
                "message": "Start date is required",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if due_date_from and not due_date_to:
            data = {
                "error": True,
                "code": "40007",
                "message": "End date is required",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if due_date_to and not due_date_from:
            data = {
                "error": True,
                "code": "40007",
                "message": "Start date is required",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if due_date_from and due_date_to:
            # formate date
            try:
                if due_date_from:
                    datetime.strptime(due_date_from, "%Y-%m-%d")
                if due_date_to:
                    datetime.strptime(due_date_to, "%Y-%m-%d")
            except:
                data = {
                    "error": True,
                    "code": "40007",
                    "message": "Invalid date format. Date format should be YYYY-MM-DD",
                }

                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if created_date_from and created_date_to:
            # formate date
            try:
                if created_date_from:
                    datetime.strptime(created_date_from, "%Y-%m-%d")
                if created_date_to:
                    datetime.strptime(created_date_to, "%Y-%m-%d")
            except:
                data = {
                    "error": True,
                    "code": "40007",
                    "message": "Invalid date format. Date format should be YYYY-MM-DD",
                }

                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        project_ids = request.user.projects.values_list("id", flat=True)

        if created_date_from and created_date_to:
            task_qs = ProjectTask.filter_by_created_date(
                start_date=created_date_from,
                end_date=created_date_to,
                project_ids=project_ids,
            )

        elif due_date_from and due_date_to:
            task_qs = ProjectTask.filter_by_due_date(
                start_date=due_date_from,
                end_date=due_date_to,
                project_ids=project_ids,
            )

        elif search:
            task_qs = ProjectTask.search_task(
                search_term=search, project_ids=project_ids
            )

        else:
            task_qs = ProjectTask.objects.filter(project__id__in=project_ids)

        if sort_by:
            task_qs = ProjectTask.sort_data(queryset=task_qs, sort_by=sort_by)

        paginator = PageNumberPagination()
        paginator.page_size = 10

        result_page = paginator.paginate_queryset(task_qs, request)

        serialized_data = TaskModelSerializer(result_page, many=True).data

        data = {
            "error": False,
            "code": "200",
            "message": "data fetched successfully",
            "data": serialized_data,
        }

        return paginator.get_paginated_response(data)

    def put(self, request):
        task_id = request.GET.get("task_id")

        try:
            task = ProjectTask.objects.get(id=task_id)
        except ProjectTask.DoesNotExist:
            data = {
                "error": True,
                "code": "40004",
                "message": "Task not found",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_payload = {
            "title": serializer.validated_data.get("title"),
            "description": serializer.validated_data.get("description"),
            "due_date": serializer.validated_data.get("due_date"),
            "priority_level": serializer.validated_data.get("priority_level"),
            "status": serializer.validated_data.get("status"),
        }

        ProjectTask.update(task_id=task_id, **update_payload)

        task = ProjectTask.objects.get(id=task_id)

        data = {
            "error": False,
            "code": "200",
            "message": "Task updated successfully",
            "task": TaskModelSerializer(task).data,
        }

        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request):
        task_id = request.GET.get("task_id")

        try:
            task = ProjectTask.objects.get(id=task_id)
        except ProjectTask.DoesNotExist:
            data = {
                "error": True,
                "code": "40004",
                "message": "Task not found",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        title = request.data.get("title", task.title)
        description = request.data.get("description", task.description)
        due_date = request.data.get("due_date", task.due_date)
        priority_level = request.data.get("priority_level", task.priority_level)
        _status = request.data.get("status", task.status)

        update_payload = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "priority_level": priority_level,
            "status": _status,
        }

        ProjectTask.update(task_id=task_id, **update_payload)
        task = ProjectTask.objects.get(id=task_id)

        data = {
            "error": False,
            "code": "200",
            "message": "Task updated successfully",
            "task": TaskModelSerializer(task).data,
        }

        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request):
        task_id = request.GET.get("task_id")

        try:
            task = ProjectTask.objects.get(id=task_id)
        except ProjectTask.DoesNotExist:
            data = {
                "error": True,
                "code": "40004",
                "message": "Task not found",
            }

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        task.delete()

        data = {
            "error": False,
            "code": "200",
            "message": "Task deleted successfully",
        }

        return Response(data, status=status.HTTP_200_OK)
