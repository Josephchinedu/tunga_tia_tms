from django.contrib.auth import get_user_model
from rest_framework import serializers

from main.models import Project
from main.models import Task as ProjectTask


class CustomDateField(serializers.ReadOnlyField):
    def to_representation(self, value):
        # Convert a datetime value to a date
        try:
            return value.date().strftime("%Y-%m-%d")
        except AttributeError:
            try:
                value.strftime("%Y-%m-%d")
            except AttributeError:
                return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["username", "email"]


class CreateAccountSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=255)
    confirm_password = serializers.CharField(max_length=255)

    def validate(self, attrs):
        if len(attrs.get("password")) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")

        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError("Passwords do not match")

        return attrs


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField(max_length=300)
    password = serializers.CharField(max_length=255)


class ProjectSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=300)
    description = serializers.CharField()


class ProjectModelSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Project
        fields = "__all__"

    def to_representation(self, instance):
        data = super(ProjectModelSerializer, self).to_representation(instance)
        user_data = data.pop("user")

        data["user"] = user_data
        return data


class TaskSerializer(serializers.Serializer):
    STATUS_OPTIONS = (
        ("TO_DO", "TO_DO"),
        ("IN_PROGRESS", "IN_PROGRESS"),
        ("COMPLETED", "COMPLETED"),
    )

    project_id = serializers.IntegerField()
    title = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=100)
    due_date = serializers.DateField()
    priority_level = serializers.CharField(max_length=100)
    status = serializers.ChoiceField(choices=STATUS_OPTIONS)


class TaskModelSerializer(serializers.ModelSerializer):
    project = ProjectModelSerializer()
    due_date = CustomDateField()

    class Meta:
        model = ProjectTask
        fields = "__all__"
        depth = 1

    def to_representation(self, instance):
        data = super(TaskModelSerializer, self).to_representation(instance)
        project = data.pop("project")

        data["project"] = project
        return data
