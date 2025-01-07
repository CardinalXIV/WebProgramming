from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  GenerateSalesPerformanceReport, SalesTrendData,  CreateReportView, ListReportsView, DeleteReportView, SalesOverview

router = DefaultRouter()

"""
    Paths:
    - '' : Includes all the router URLs that are registered.
    - 'sales_trend_data/' : URL for accessing sales trend data.
    - 'overview/' : URL for accessing the sales overview.
    - 'generate_sales_performance_report/' : URL for generating sales performance reports.
    - 'create-report/' : URL for creating a report.
    - 'reports/' : URL for listing all reports.
    - 'reports/<int:reportID>/' : URL for deleting a specific report by its ID.
"""

urlpatterns = [
    path('', include(router.urls)),

    # URL for Trends page
    path('sales_trend_data/', SalesTrendData.as_view(), name='sales_trend_data'),

    # URL for Sales page
    path('overview/', SalesOverview.as_view(), name='sales-overview'),

    # URL for Generate Report Page
    path('generate_sales_performance_report/', GenerateSalesPerformanceReport.as_view({'get': 'list'}), name='generate_sales_performance_report'),
    path('create-report/', CreateReportView.as_view(), name='create_report'),
    path('reports/', ListReportsView.as_view(), name='list_reports'),
    path('reports/<int:reportID>/', DeleteReportView.as_view(), name='delete_report'),
]
