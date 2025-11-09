"""
Procesador de datos para la visualización de Top 5 productos más vendidos.
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


def get_top_products_data(country=None, customer_profile=None):
    """
    Obtiene los datos del Top 5 de productos más vendidos.
    
    Args:
        country: País para filtrar (opcional)
        customer_profile: Perfil de cliente para filtrar (opcional)
    
    Returns:
        dict con datos de productos más vendidos
    """
    print(f"DEBUG - get_top_products_data: country={country}, profile={customer_profile}")
    
    df = load_online_retail_data()
    
    if df is None or df.height == 0:
        print("DEBUG - DataFrame vacío o None")
        return None
    
    print(f"DEBUG - DataFrame inicial: {df.height} filas")
    
    # Filtrar por país si se especifica
    if country:
        df = df.filter(pl.col('Country') == country)
        print(f"DEBUG - Después de filtrar por país {country}: {df.height} filas")
    
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
    
    # Calcular ventas totales por producto
    if 'Sales' not in df.columns:
        df = df.with_columns([
            (pl.col('Quantity') * pl.col('UnitPrice')).alias('Sales')
        ])
    
    # Agrupar por descripción del producto
    productos_ventas = (
        df.group_by('Description')
        .agg([
            pl.col('Sales').sum().alias('TotalSales'),
            pl.col('Quantity').sum().alias('TotalQuantity')
        ])
        .sort('TotalSales', descending=True)
        .head(5)  # Top 5
    )
    
    print(f"DEBUG - Productos encontrados: {productos_ventas.height}")
    
    # Convertir a listas para el gráfico
    products = productos_ventas['Description'].to_list()
    sales = productos_ventas['TotalSales'].to_list()
    quantities = productos_ventas['TotalQuantity'].to_list()
    
    print(f"DEBUG - Top 5 productos: {products}")
    print(f"DEBUG - Ventas: {sales}")
    
    # Invertir para que el producto #1 aparezca arriba en el gráfico horizontal
    products.reverse()
    sales.reverse()
    quantities.reverse()
    
    result = {
        'products': products,
        'sales': sales,
        'quantities': quantities,
        'total_products': len(products)
    }
    
    print(f"DEBUG - Retornando: {result}")
    
    return result
