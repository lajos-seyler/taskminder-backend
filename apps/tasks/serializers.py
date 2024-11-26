from datetime import datetime, timedelta
from datetime import timezone as dt_timezone

from dateutil import rrule
from django.utils import timezone
from rest_framework import serializers

from .models import Folder, Occurrence, Project, Tag, Task


class TagSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("id",)


class FolderSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Folder
        fields = "__all__"
        read_only_fields = ("id",)


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ("id",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1


class OccurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occurrence
        fields = "__all__"
        read_only_fields = ("id",)


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    start_time = serializers.DateTimeField(write_only=True, required=False)
    end_time = serializers.DateTimeField(write_only=True, required=False)
    rrule_params = serializers.JSONField(write_only=True, required=False)
    next_occurrence = serializers.SerializerMethodField(read_only=True)

    def get_next_occurrence(self, obj):
        future_occurrences = obj.occurrences.filter(start_time__gt=timezone.now())
        if future_occurrences.exists():
            return OccurrenceSerializer(future_occurrences.earliest("start_time")).data
        return None

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ("id",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if request and request.method == "POST":
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1

    def create(self, validated_data):
        start_time = validated_data.pop("start_time", None)
        end_time = validated_data.pop("end_time", None)
        rrule_params = validated_data.pop("rrule_params", {})

        task = super().create(validated_data)

        if start_time and end_time:
            self.parse_frequency(rrule_params=rrule_params)
            self.parse_until(rrule_params=rrule_params)
            try:
                task.add_occurrences(start_time=start_time, end_time=end_time, **rrule_params)
            except Exception as e:
                raise serializers.ValidationError({"rrule_params": f"Invalid recurrence rule parameters: {e}"})

        return task

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request:
            project = request.data.get("project", None)
            instance.project_id = project

            tags = request.data.get("tags", None)
            if tags is not None:
                instance.tags.set(tags)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def parse_frequency(self, rrule_params):
        frequency_str = rrule_params.get("freq")
        if frequency_str:
            freq = getattr(rrule, frequency_str)
            rrule_params["freq"] = freq

    def parse_until(self, rrule_params):
        until_str = rrule_params.get("until")
        if until_str:
            until_datetime = datetime.strptime(until_str, "%Y-%m-%d")

            next_day = until_datetime + timedelta(days=1)
            next_day_midnight = next_day.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=dt_timezone.utc)
            rrule_params["until"] = next_day_midnight
