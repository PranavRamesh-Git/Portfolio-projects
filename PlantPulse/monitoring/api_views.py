
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import Reading
from .serializers import ReadingSerializer


class ReadingPagination(PageNumberPagination):

    page_size = 10


class ReadingListAPIView(ListAPIView):

    serializer_class = ReadingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ReadingPagination

    def get_queryset(self):

        readings = (
            Reading.objects
            .select_related("sensor")
            .order_by("-recorded_at", "-id")
        )

        sensor_code = self.request.query_params.get("sensor_code")
        is_breach = self.request.query_params.get("is_breach")

        if sensor_code:
            readings = readings.filter(
                sensor__code=sensor_code.strip()
            )

        if is_breach == "true":
            readings = readings.filter(is_breach=True)

        elif is_breach == "false":
            readings = readings.filter(is_breach=False)

        return readings
