# sales/serializers.py

from rest_framework import serializers
from core.models import Order, Report, ReportMetric, Metric, DataSource, Dashboard, DashboardLayout
from .models import Sale

class SaleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Sale model.

    Serializes all fields of the Sale model.
    """
    class Meta:
        model = Sale
        fields = '__all__'

class SalesTrendSerializer(serializers.Serializer):
    """
    Serializer for sales trend data.

    Attributes:
        months (list): List of month strings.
        total_revenue (list): List of total revenue values.
        total_quantity (list): List of total quantity values.
        sma_revenue (list): List of simple moving average revenue values (optional).
        ema_revenue (list): List of exponential moving average revenue values (optional).
        sma_quantity (list): List of simple moving average quantity values (optional).
        ema_quantity (list): List of exponential moving average quantity values (optional).
    """
    months = serializers.ListField(child=serializers.CharField())
    total_revenue = serializers.ListField(child=serializers.DecimalField(max_digits=10, decimal_places=2))
    total_quantity = serializers.ListField(child=serializers.IntegerField())
    sma_revenue = serializers.ListField(child=serializers.DecimalField(max_digits=10, decimal_places=2), required=False)
    ema_revenue = serializers.ListField(child=serializers.DecimalField(max_digits=10, decimal_places=2), required=False)
    sma_quantity = serializers.ListField(child=serializers.IntegerField(), required=False)
    ema_quantity = serializers.ListField(child=serializers.IntegerField(), required=False)

class SalesDataSerializer(serializers.Serializer):
    """
    Serializer for sales data overview.

    Attributes:
        money (int): Total money.
        sales (int): Total sales.
        money_growth (int): Money growth percentage.
        sales_growth (int): Sales growth percentage.
    """
    money = serializers.IntegerField()
    sales = serializers.IntegerField()
    money_growth = serializers.IntegerField()
    sales_growth = serializers.IntegerField()

class SalesAnalysisSerializer(serializers.Serializer):
    """
    Serializer for sales analysis data.

    Attributes:
        trend_line (str): Type of trend line.
        time_period (str): Time period of the analysis.
        trend_direction (str): Direction of the trend.
        peak_sales_month (str): Month with peak sales.
        lowest_sales_month (str): Month with lowest sales.
    """
    trend_line = serializers.CharField(max_length=100)
    time_period = serializers.CharField(max_length=100)
    trend_direction = serializers.CharField(max_length=50)
    peak_sales_month = serializers.CharField(max_length=10)
    lowest_sales_month = serializers.CharField(max_length=10)

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.

    Serializes all fields of the Order model.
    """
    class Meta:
        model = Order
        fields = '__all__'

class SalesOverviewSerializer(serializers.Serializer):
    """
    Serializer for sales overview data.

    Attributes:
        total_revenue (Decimal): Total revenue.
        total_sales (int): Total sales.
        money_growth (Decimal): Money growth percentage.
        sales_growth (Decimal): Sales growth percentage.
    """
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_sales = serializers.IntegerField()
    money_growth = serializers.DecimalField(max_digits=5, decimal_places=2)
    sales_growth = serializers.DecimalField(max_digits=5, decimal_places=2)

class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer for the Report model.

    Serializes all fields of the Report model.
    """
    class Meta:
        model = Report
        fields = '__all__'
