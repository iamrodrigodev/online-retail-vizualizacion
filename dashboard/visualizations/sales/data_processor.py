"""
Procesador de datos para la visualización de tendencias de ventas diarias.
"""
import polars as pl
from dashboard.visualizations.shared.data_loader import load_online_retail_data


def get_sales_trend_data(country=None, customer_profile=None):
    """
    Obtiene los datos de tendencia de ventas diarias.
    
    Args:
        country: País para filtrar (opcional)
        customer_profile: Perfil de cliente para filtrar (opcional)
    
    Returns:
        dict con datos de ventas por fecha y año
    """
    df = load_online_retail_data()
    
    if df is None or df.height == 0:
        return None
    
    # Filtrar por país si se especifica
    if country:
        df = df.filter(pl.col('Country') == country)
    
    # Filtrar por perfil de cliente si se especifica
    if customer_profile:
        # Cargar la clasificación de perfiles
        from dashboard.visualizations.customer_profiles.data_processor import classify_customer_profiles
        df = classify_customer_profiles(df)
        df = df.filter(pl.col('perfil') == customer_profile)
    
    # Asegurar que InvoiceDate sea datetime
    df = df.with_columns([
        pl.col('InvoiceDate').str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").alias('InvoiceDate')
    ])
    
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
