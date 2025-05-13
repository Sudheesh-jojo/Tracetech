from django.urls import path
from . import views  

urlpatterns = [
    path('home/', views.home, name='home'),
    path('reports/lost/', views.report_lostitem, name='report_lostitem'),
    path('reports/found/', views.general_report_found_item, name='general_report_found_item'),  
    path('check/<int:lost_item_id>/', views.check_items, name='check_items'),
    path('success2/<int:lost_item_id>/<int:found_item_id>/', views.success2, name='success2'),
]

    
