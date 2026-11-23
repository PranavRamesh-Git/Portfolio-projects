from rest_framework import serializers

from .models import Reading


class ReadingSerializer(serializers.ModelSerializer):

    sensor_code = serializers.CharField(source="sensor.code",read_only=True)

    class Meta:

        model = Reading

        fields = [
            "id",
            "sensor",
            "sensor_code",
            "value",
            "recorded_at",
            "received_at",
            "is_breach"
        ]

        read_only_fields = [
            "id",
            "is_breach",
            "received_at"
        ]
