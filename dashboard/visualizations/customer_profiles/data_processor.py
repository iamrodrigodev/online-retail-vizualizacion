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


def get_customer_profiles_data(country=None, start_date=None, end_date=None):
    """
    Obtiene los datos de perfiles de cliente.
    Si se proporciona un país, filtra por ese país.
    Si se proporcionan fechas, filtra por rango de fechas.
    """
    df = load_online_retail_data()
    
    if df.is_empty():
        return {}
    
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
    
    # Crear columna Total si no existe
    if 'Total' not in df.columns:
        df = df.with_columns(
            (pl.col('Quantity') * pl.col('UnitPrice')).alias('Total')
        )
    
    # Filtrar por país si se proporciona
    if country:
        df = df.filter(pl.col('Country') == country)
        
        if df.is_empty():
            return {}
    
    # Detectar outliers en Total y UnitPrice
    total_lower, total_upper = detectar_outliers_iqr(df, 'Total')
    price_lower, price_upper = detectar_outliers_iqr(df, 'UnitPrice')
    
    # Clasificar cada transacción usando when-then-otherwise
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
    
    # Contar perfiles
    perfil_counts = df.group_by('Perfil').agg(pl.count().alias('count'))
    total_transacciones = len(df)
    
    # Calcular porcentajes
    perfil_counts = perfil_counts.with_columns(
        ((pl.col('count') / total_transacciones) * 100).alias('percentage')
    )
    
    # Ordenar por porcentaje de menor a mayor
    perfil_counts = perfil_counts.sort('percentage')
    
    # Convertir a diccionario
    result = {
        'perfiles': perfil_counts['Perfil'].to_list(),
        'counts': perfil_counts['count'].to_list(),
        'percentages': perfil_counts['percentage'].to_list(),
        'total_transacciones': total_transacciones
    }
    
    return result
