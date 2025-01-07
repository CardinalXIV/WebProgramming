from django.db import models
from django.db.models import Sum, F, ExpressionWrapper, DecimalField 
from core.models import Order, Report, ReportMetric, Metric, DataSource, Dashboard, DashboardLayout, Product, OrderInvoiceItems
import pandas as pd

class Sale(models.Model):
    """
    Model representing a sale record.
    
    Attributes:
        product_name (str): Name of the product sold.
        quantity (int): Quantity of the product sold.
        sale_date (date): Date of the sale.
        revenue (Decimal): Revenue generated from the sale.
    """
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    sale_date = models.DateField()
    revenue = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        """
        String representation of the Sale model.
        
        Returns:
            str: The name of the product.
        """
        return self.product_name

    @staticmethod
    def get_sales_trend_data():
        """
        Static method to retrieve and calculate sales trend data.
        
        Aggregates total revenue and total quantity of sales by month.

        Returns:
            dict: A dictionary containing lists of months, total revenue, and total quantity.
                  Returns empty lists if there are no sales records.
        """
        sales = Sale.objects.values('sale_date').annotate(
            total_revenue=Sum('revenue'),
            total_quantity=Sum('quantity')
        ).order_by('sale_date')
        
        # Convert sales data to a DataFrame
        df = pd.DataFrame(sales)
        if df.empty:
            return {'months': [], 'total_revenue': [], 'total_quantity': []}
        
        # Set the sale_date as index and resample data monthly
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df.set_index('sale_date', inplace=True)
        df = df.resample('M').sum()

        # Prepare trend data for response
        trend_data = {
            'months': df.index.strftime('%Y-%m').tolist(),
            'total_revenue': df['total_revenue'].tolist(),
            'total_quantity': df['total_quantity'].tolist()
        }
        return trend_data
