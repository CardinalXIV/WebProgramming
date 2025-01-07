from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from .serializers import ReportSerializer
from core.models import OrderInvoiceItems, Order, Inventory, Product, Report
from .calculations import get_sales_trend_data  
from django.http import HttpResponse
from django.db.models import Sum, F, Count
import csv
from datetime import date, timedelta, datetime
from django.utils import timezone
from core.permissions import HasRoleFactory


class GenerateSalesPerformanceReport(ViewSet):
    """
    ViewSet for generating sales performance reports.
    """
    permission_classes = [HasRoleFactory("Employee")]
    
    @action(detail=False, methods=['get'])
    def list(self, request):
        """
        Handle GET requests to generate sales performance reports.

        Parameters:
        - request: The request object containing query parameters 'fromDate', 'toDate', and 'reportType'.

        Returns:
        - CSV response containing the generated report.
        """
        from_date = request.query_params.get('fromDate')
        to_date = request.query_params.get('toDate')
        report_type = request.query_params.get('reportType')

        filters = {}
        if from_date:
            filters['orderID__order_datetime__gte'] = timezone.datetime.strptime(from_date, '%Y-%m-%d').replace(tzinfo=timezone.get_current_timezone())
        if to_date:
            filters['orderID__order_datetime__lte'] = timezone.datetime.strptime(to_date, '%Y-%m-%d').replace(tzinfo=timezone.get_current_timezone())

        # Generate the CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'

        writer = csv.writer(response)
        
        if report_type == 'sales-summary':
            GenerateSalesPerformanceReport.generate_sales_summary(writer, filters)
        elif report_type == 'product-analysis':
            GenerateSalesPerformanceReport.generate_product_analysis(writer, filters)
        
        return response

    @action(detail=False, methods=['get'])
    def generate_sales_summary(writer, filters):
        """
        Generate a sales summary report.

        Parameters:
        - writer: CSV writer object.
        - filters: Query filters for fetching sales data.
        """
        writer.writerow(['Sales Performance Overview'])
        writer.writerow(['Section', 'Metric', 'Value'])

        # Sales Performance Overview
        total_sales_price = OrderInvoiceItems.objects.filter(**filters).aggregate(total_sales_price=Sum(F('quantity') * F('productID__price')))['total_sales_price'] or 0
        total_sales = OrderInvoiceItems.objects.filter(**filters).count()
        avg_sale_value = total_sales_price / total_sales if total_sales else 0
        writer.writerow(['Sales Performance Overview', 'Total Sales Price', total_sales_price])
        writer.writerow(['', 'Total Sales', total_sales])
        writer.writerow(['', 'Average Sale Value', avg_sale_value])

        # Detailed Sales Breakdown by Product
        writer.writerow([])
        writer.writerow(['Detailed Sales Breakdown by Product'])
        writer.writerow(['Product', 'Units Sold', 'Total Sales Price'])
        sales_by_product = OrderInvoiceItems.objects.filter(**filters).values('productID__prodName').annotate(
            total_quantity=Sum('quantity'),
            total_sales_price=Sum(F('quantity') * F('productID__price'))
        ).order_by('-total_sales_price')
        for sale in sales_by_product:
            writer.writerow([sale['productID__prodName'], sale['total_quantity'], sale['total_sales_price']])

        # Detailed Sales Breakdown by Category
        writer.writerow([])
        writer.writerow(['Detailed Sales Breakdown by Category'])
        writer.writerow(['Category', 'Units Sold', 'Total Sales Price'])
        sales_by_category = OrderInvoiceItems.objects.filter(**filters).values('productID__category').annotate(
            total_quantity=Sum('quantity'),
            total_sales_price=Sum(F('quantity') * F('productID__price'))
        ).order_by('-total_sales_price')
        for sale in sales_by_category:
            writer.writerow([sale['productID__category'], sale['total_quantity'], sale['total_sales_price']])

        # Detailed Sales Breakdown by Region
        writer.writerow([])
        writer.writerow(['Detailed Sales Breakdown by Region'])
        writer.writerow(['Region', 'Units Sold', 'Total Sales Price'])
        sales_by_region = Order.objects.filter(order_datetime__gte=filters.get('orderID__order_datetime__gte', None), order_datetime__lte=filters.get('orderID__order_datetime__lte', None)).values('shippingID__country').annotate(
            total_quantity=Sum('orderinvoiceitems__quantity'),
            total_sales_price=Sum(F('orderinvoiceitems__quantity') * F('orderinvoiceitems__productID__price'))
        ).order_by('-total_sales_price')
        for sale in sales_by_region:
            writer.writerow([sale['shippingID__country'], sale['total_quantity'], sale['total_sales_price']])

        # Customer Analysis
        writer.writerow([])
        writer.writerow(['Customer Analysis'])
        writer.writerow(['Metric', 'Value'])
        num_new_customers = Order.objects.filter(order_datetime__gte=filters.get('orderID__order_datetime__gte', None)).count()
        repeat_customers = Order.objects.filter(order_datetime__gte=filters.get('orderID__order_datetime__gte', None), order_datetime__lte=filters.get('orderID__order_datetime__lte', None)).values('custEmail').annotate(order_count=Count('orderID')).filter(order_count__gt=1).count()
        customer_retention_rate = (repeat_customers / num_new_customers) * 100 if num_new_customers else 0
        writer.writerow(['Number of New Customers', num_new_customers])
        writer.writerow(['Repeat Customers', repeat_customers])
        writer.writerow(['Customer Retention Rate (%)', customer_retention_rate])

    @action(detail=False, methods=['get'])
    def generate_product_analysis(writer, filters):
        """
        Generate a product analysis report.

        Parameters:
        - writer: CSV writer object.
        - filters: Query filters for fetching sales data.
        """
        writer.writerow(['Product Performance Overview'])
        writer.writerow(['Section', 'Product', 'Units Sold', 'Total Sales Price'])

        # Product Performance Overview
        sales_by_product = OrderInvoiceItems.objects.filter(**filters).values('productID__prodName').annotate(
            total_quantity=Sum('quantity'),
            total_sales_price=Sum(F('quantity') * F('productID__price'))
        ).order_by('-total_sales_price')
        for sale in sales_by_product:
            writer.writerow(['Product Performance Overview', sale['productID__prodName'], sale['total_quantity'], sale['total_sales_price']])

        # Product Sales Trends
        writer.writerow([])
        writer.writerow(['Product Sales Trends'])
        writer.writerow(['Date', 'Units Sold', 'Total Sales Price'])
        sales_trends = OrderInvoiceItems.objects.filter(**filters).values('orderID__order_datetime').annotate(
            total_quantity=Sum('quantity'),
            total_sales_price=Sum(F('quantity') * F('productID__price'))
        ).order_by('orderID__order_datetime')
        for trend in sales_trends:
            writer.writerow([trend['orderID__order_datetime'].strftime('%m/%d/%y'), trend['total_quantity'], trend['total_sales_price']])

        # Product Category Analysis
        writer.writerow([])
        writer.writerow(['Product Category Analysis'])
        writer.writerow(['Category', 'Units Sold', 'Total Sales Price'])
        sales_by_category = OrderInvoiceItems.objects.filter(**filters).values('productID__category').annotate(
            total_quantity=Sum('quantity'),
            total_sales_price=Sum(F('quantity') * F('productID__price'))
        ).order_by('-total_sales_price')
        for sale in sales_by_category:
            writer.writerow([sale['productID__category'], sale['total_quantity'], sale['total_sales_price']])

        # Inventory and Restock Analysis
        writer.writerow([])
        writer.writerow(['Inventory and Restock Analysis'])
        writer.writerow(['Product', 'Current Stock', 'Restock Threshold', 'Last Restocked'])
        inventory_data = Inventory.objects.filter(batchID__productID__in=Product.objects.all()).values('batchID__productID__prodName', 'batchID__quantity', 'batchID__productID__restockThreshold', 'lastRestocked')
        for item in inventory_data:
            writer.writerow([item['batchID__productID__prodName'], item['batchID__quantity'], item['batchID__productID__restockThreshold'], item['lastRestocked']])

class CreateReportView(APIView):
    """
    API view for creating a report.
    """
    permission_classes = [HasRoleFactory("Manager")]
    
    def post(self, request):
        """
        Handle POST requests to create a report.

        Parameters:
        - request: The request object containing report data.

        Returns:
        - JSON response with the created report data or errors.
        """
        data = request.data
        #data['accountID'] = 1  
        serializer = ReportSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListReportsView(APIView):
    """
    API view for listing reports.
    """
    permission_classes = [HasRoleFactory("Manager")]

    def get(self, request):
        """
        Handle GET requests to list all reports.

        Parameters:
        - request: The request object.

        Returns:
        - JSON response with the list of reports.
        """
        reports = Report.objects.all()
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteReportView(APIView):
    """
    API view for deleting a report.
    """
    permission_classes = [HasRoleFactory("Manager")]

    def delete(self, request, reportID):
        """
        Handle DELETE requests to delete a specific report.

        Parameters:
        - request: The request object.
        - reportID: The ID of the report to delete.

        Returns:
        - HTTP 204 No Content response on successful deletion or HTTP 404 Not Found if the report does not exist.
        """
        try:
            report = Report.objects.get(reportID=reportID)
            report.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Report.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class SalesTrendData(APIView):
    """
    API view for fetching sales trend data.
    """
    # permission_classes = [HasRoleFactory("Manager")]
    
    @action(detail=False, methods=['get'])
    def get(self, request):
        """
        Handle GET requests to fetch sales trend data.

        Parameters:
        - request: The request object containing query parameters 'start_date', 'end_date', and 'metric'.

        Returns:
        - JSON response with the sales trend data or errors.
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        metric = request.query_params.get('metric', 'SMA')

        # Validate dates
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Fetch sales trend data
        try:
            trend_data = get_sales_trend_data(start_date, end_date, metric)
            return Response(trend_data, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class SalesOverview(APIView):
    """
    API view for providing a sales overview.
    """
    permission_classes = [HasRoleFactory("Manager")]
    
    @action(detail=False, methods=['get'])
    def get(self, request):
        """
        Handle GET requests to provide a sales overview.

        Parameters:
        - request: The request object containing the query parameter 'date_range'.

        Returns:
        - JSON response with the sales overview data.
        """
        date_range = request.query_params.get('date_range', 'today')
        
        if date_range == '7days':
            start_date = date.today() - timedelta(days=7)
        elif date_range == 'all':
            start_date = None
        else:  # 'today' or any other invalid value
            start_date = date.today()

        if start_date:
            total_revenue = OrderInvoiceItems.objects.filter(
                orderID__order_datetime__date__gte=start_date
            ).aggregate(total_revenue=Sum(F('quantity') * F('productID__price')))['total_revenue'] or 0

            total_sales = OrderInvoiceItems.objects.filter(orderID__order_datetime__date__gte=start_date).count()
            sales_by_product = OrderInvoiceItems.objects.filter(orderID__order_datetime__date__gte=start_date).values(
                'productID__prodName'
            ).annotate(total_quantity=Sum('quantity')).annotate(total_revenue=Sum(F('quantity') * F('productID__price'))).order_by('-total_revenue')
        else:  # all time
            total_revenue = OrderInvoiceItems.objects.aggregate(total_revenue=Sum(F('quantity') * F('productID__price')))['total_revenue'] or 0

            total_sales = OrderInvoiceItems.objects.count()

            sales_by_product = OrderInvoiceItems.objects.values(
                'productID__prodName'
            ).annotate(total_quantity=Sum('quantity')).annotate(total_revenue=Sum(F('quantity') * F('productID__price'))).order_by('-total_revenue')

        money_growth = 0
        sales_growth = 0

        data = {
            'total_revenue': total_revenue,
            'total_sales': total_sales,
            'money_growth': money_growth,
            'sales_growth': sales_growth,
            'sales_by_product': list(sales_by_product)
        }

        return Response(data, status=status.HTTP_200_OK)
