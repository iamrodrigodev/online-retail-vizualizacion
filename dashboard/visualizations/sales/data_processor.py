"""
Procesador de datos para la visualización de tendencias de ventas diarias.
"""
import polars as pl
from dashboard.visualizations.shared.data_loader import load_online_retail_data


def detectar_outliers_iqr(df, columna):
    """Detecta outliers usando el método IQR"""
    Q1 = df[columna].quantile(0.25)
    Q3 = df[columna].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return lower_bound, upper_bound


def get_sales_trend_data(country=None, customer_profile=None, start_date=None, end_date=None):
    """
    Obtiene los datos de tendencia de ventas diarias.
    
    Args:
        country: País para filtrar (opcional)
        customer_profile: Perfil de cliente para filtrar (opcional)
        start_date: Fecha de inicio en formato YYYY-MM (opcional)
        end_date: Fecha de fin en formato YYYY-MM (opcional)
    
    Returns:
        dict con datos de ventas por fecha y año
    """
    df = load_online_retail_data()
    
    if df is None or df.height == 0:
        return None
    
    # Asegurar que InvoiceDate sea datetime
    df = df.with_columns([
        pl.col('InvoiceDate').str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").alias('InvoiceDate')
    ])
    
    # Filtrar por rango de fechas si se especifica
    if start_date:
        start_datetime = pl.lit(start_date + "-01").str.strptime(pl.Datetime, "%Y-%m-%d")
        df = df.filter(pl.col('InvoiceDate') >= start_datetime)
    
    if end_date:
        # Calcular el último día del mes
        import datetime
        year, month = map(int, end_date.split('-'))
        if month == 12:
            next_month = datetime.datetime(year + 1, 1, 1)
        else:
            next_month = datetime.datetime(year, month + 1, 1)
        last_day = next_month - datetime.timedelta(days=1)
        end_datetime = pl.lit(last_day.strftime("%Y-%m-%d") + " 23:59:59").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S")
        df = df.filter(pl.col('InvoiceDate') <= end_datetime)
    
    # Filtrar por país si se especifica
    if country:
        df = df.filter(pl.col('Country') == country)
    
    # Filtrar por perfil de cliente si se especifica
    if customer_profile:
        # Crear columna Total si no existe
        if 'Total' not in df.columns:
            df = df.with_columns(
                (pl.col('Quantity') * pl.col('UnitPrice')).alias('Total')
            )
        
        # Detectar outliers en Total y UnitPrice
        total_lower, total_upper = detectar_outliers_iqr(df, 'Total')
        price_lower, price_upper = detectar_outliers_iqr(df, 'UnitPrice')
        
        # Clasificar cada transacción
        df = df.with_columns(
            pl.when((pl.col('Total') > total_upper) & (pl.col('UnitPrice') <= price_upper))
            .then(pl.lit('Mayorista Estándar'))
            .when((pl.col('Total') <= total_upper) & (pl.col('UnitPrice') > price_upper))
            .then(pl.lit('Minorista Lujo'))
            .when((pl.col('Total') > total_upper) & (pl.col('UnitPrice') > price_upper))
            .then(pl.lit('Mayorista Lujo'))
            .otherwise(pl.lit('Minorista Estándar'))
            .alias('Perfil')
        )
        
        # Filtrar por el perfil especificado
        df = df.filter(pl.col('Perfil') == customer_profile)
    
    # Calcular Sales si no existe
    if 'Sales' not in df.columns:
        df = df.with_columns([
            (pl.col('Quantity') * pl.col('UnitPrice')).alias('Sales')
        ])
    
    # Extraer fecha y año
    df = df.with_columns([
        pl.col('InvoiceDate').dt.date().alias('Fecha'),
        pl.col('InvoiceDate').dt.year().alias('Año')
    ])
    
    # Agrupar por fecha y año
    ventas_diarias = (
        df.group_by(['Fecha', 'Año'])
        .agg([
            pl.col('Sales').sum().alias('Sales')
        ])
        .sort(['Fecha'])
    )
    
    # Obtener lista de años únicos
    years = sorted(df['Año'].unique().to_list())
    
    # Preparar datos por año
    data_by_year = {}
    for year in years:
        year_data = ventas_diarias.filter(pl.col('Año') == year)
        data_by_year[year] = {
            'dates': year_data['Fecha'].cast(pl.Utf8).to_list(),
            'sales': year_data['Sales'].to_list()
        }
    
    return {
        'years': years,
        'data_by_year': data_by_year
    }
