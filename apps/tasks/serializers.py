from dateutil import rrule
from rest_framework import serializers

from .models import Folder, Project, Tag, Task


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


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    start_time = serializers.DateTimeField(write_only=True, required=False)
    end_time = serializers.DateTimeField(write_only=True, required=False)
    rrule_params = serializers.JSONField(write_only=True, required=False)

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
            try:
                task.add_occurrences(start_time=start_time, end_time=end_time, **rrule_params)
            except Exception as e:
                raise serializers.ValidationError({"rrule_params": f"Invalid recurrence rule parameters: {e}"})

        return task

    def parse_frequency(self, rrule_params):
        frequency_str = rrule_params.get("freq")
        if frequency_str:
            freq = getattr(rrule, frequency_str)
            rrule_params["freq"] = freq
