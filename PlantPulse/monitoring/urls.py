from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import MachineUpdateView,AlertsUpdateViews
from .api_views import ReadingListAPIView
from . import views

urlpatterns = [
    path("",views.home,name="home_page"),
    path("api/dashboard/", views.get_dashboard, name="get_dashboard"),
    path("api/readings/",views.get_sensor_readings, name="get_sensor_readings"),
    path("api/alerts/",views.get_sensor_alerts, name="get_sensor_alerts"),
    path("login/",LoginView.as_view(template_name="monitoring/login.html"),name="login"),
    path("logout/",LogoutView.as_view(),name="logout"),
    path("machines/<int:pk>/edit/",MachineUpdateView.as_view(),name="machine_edit"),
    path("alerts/<int:pk>/edit/",AlertsUpdateViews.as_view(),name="alert_edit"), 
    path("api/v1/readings/",ReadingListAPIView.as_view(),name="reading_list_api"),

]




