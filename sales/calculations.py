import pandas as pd
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from core.models import OrderInvoiceItems, Product

def get_sales_data(start_date=None, end_date=None):
    """
    Fetches and aggregates sales data from the OrderInvoiceItems model.

    Args:
        start_date (str, optional): The start date for filtering data. Defaults to None.
        end_date (str, optional): The end date for filtering data. Defaults to None.

    Returns:
        DataFrame: A pandas DataFrame with resampled monthly sales data containing total quantities and total revenue.
        None: If the DataFrame is empty.
    """
    # Annotate order items with calculated revenue
    order_items = OrderInvoiceItems.objects.annotate(
        revenue=ExpressionWrapper(
            F('productID__price') - F('productID__costPrice'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).values(
        'orderID__order_datetime',
        'quantity',
        'revenue'
    )

    # Filter by date range if provided
    if start_date and end_date:
        order_items = order_items.filter(orderID__order_datetime__range=[start_date, end_date])

    # Convert to DataFrame
    df = pd.DataFrame(list(order_items))
    if df.empty:
        return None

    # Set datetime index and resample data monthly
    df['orderID__order_datetime'] = pd.to_datetime(df['orderID__order_datetime'])
    df.set_index('orderID__order_datetime', inplace=True)

    df = df.resample('M').agg({
        'quantity': 'sum',
        'revenue': 'sum'
    }).rename(columns={'quantity': 'total_quantity', 'revenue': 'total_revenue'})

    return df

def calculate_sma(data, window):
    """
    Calculates the Simple Moving Average (SMA) for a given dataset.

    Args:
        data (Series): The input data for which SMA is to be calculated.
        window (int): The window size for calculating the SMA.

    Returns:
        Series: The calculated SMA values.
    """
    return data.rolling(window=window).mean()

def calculate_ema(data, span):
    """
    Calculates the Exponential Moving Average (EMA) for a given dataset.

    Args:
        data (Series): The input data for which EMA is to be calculated.
        span (int): The span for calculating the EMA.

    Returns:
        Series: The calculated EMA values.
    """
    return data.ewm(span=span, adjust=False).mean()

def get_sales_trend_data(start_date, end_date, metric):
    """
    Fetches and calculates sales trend data for a given date range and trend metric.

    Args:
        start_date (str): The start date for filtering data in 'YYYY-MM-DD' format.
        end_date (str): The end date for filtering data in 'YYYY-MM-DD' format.
        metric (str): The trend metric to calculate ('SMA' for Simple Moving Average or 'EMA' for Exponential Moving Average).

    Returns:
        dict: A dictionary containing the sales trend data, including months, total revenue, total quantity, and the calculated trend values.
    """
    # Fetch data from OrderInvoiceItems with necessary annotations
    queryset = OrderInvoiceItems.objects.filter(
        orderID__order_datetime__date__gte=start_date,
        orderID__order_datetime__date__lte=end_date
    ).annotate(
        month=F('orderID__order_datetime__month'),
        year=F('orderID__order_datetime__year')
    ).values('month', 'year').annotate(
        total_revenue=Sum(F('quantity') * F('productID__price')),
        total_quantity=Sum('quantity')
    )

    # Convert to DataFrame
    df = pd.DataFrame(list(queryset))

    if df.empty:
        return {
            "months": [],
            "total_revenue": [],
            "total_quantity": [],
            "sma_revenue": [],
            "ema_revenue": []
        }

    # Prepare DataFrame for trend calculations
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    df.set_index('date', inplace=True)
    df = df.resample('M').sum()

    # Calculate Simple Moving Average (SMA)
    if metric == 'SMA':
        df['sma_revenue'] = df['total_revenue'].rolling(window=3).mean()

    # Calculate Exponential Moving Average (EMA)
    if metric == 'EMA':
        df['ema_revenue'] = df['total_revenue'].ewm(span=3, adjust=False).mean()

    # Fill NaN values with 0
    df.fillna(0, inplace=True)

    # Prepare data for response
    trend_data = {
        "months": df.index.strftime('%Y-%m').tolist(),
        "total_revenue": df['total_revenue'].tolist(),
        "total_quantity": df['total_quantity'].tolist(),
        "sma_revenue": df.get('sma_revenue', pd.Series()).tolist(),
        "ema_revenue": df.get('ema_revenue', pd.Series()).tolist()
    }

    return trend_data
