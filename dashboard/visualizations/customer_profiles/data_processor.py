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


def get_customer_profiles_data(country=None):
    """
    Obtiene los datos de perfiles de cliente.
    Si se proporciona un país, filtra por ese país.
    """
    df = load_online_retail_data()
    
    if df.is_empty():
        return {}
    
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
    
    # Convertir a diccionario
    result = {
        'perfiles': perfil_counts['Perfil'].to_list(),
        'counts': perfil_counts['count'].to_list(),
        'percentages': perfil_counts['percentage'].to_list(),
        'total_transacciones': total_transacciones
    }
    
    return result
