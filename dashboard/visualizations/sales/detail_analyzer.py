"""
Analizador detallado de ventas por día.
Genera información completa, comparaciones e insights automáticos para un día específico.
"""
import polars as pl
from datetime import datetime, timedelta
from dashboard.visualizations.shared.data_loader import load_online_retail_data
from dashboard.visualizations.sales.data_processor import detectar_outliers_iqr


def get_daily_sales_detail(date_str, country=None, customer_profile=None, start_date=None, end_date=None):
    """
    Obtiene análisis detallado de ventas para un día específico.

    Args:
        date_str: Fecha en formato 'YYYY-MM-DD'
        country: País para filtrar (opcional)
        customer_profile: Perfil de cliente para filtrar (opcional)
        start_date: Fecha de inicio del rango general en formato YYYY-MM (opcional)
        end_date: Fecha de fin del rango general en formato YYYY-MM (opcional)

    Returns:
        dict con análisis completo del día
    """
    df = load_online_retail_data()

    if df.is_empty():
        return None

    # Convertir InvoiceDate a datetime
    df = df.with_columns([
        pl.col('InvoiceDate').str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").alias('InvoiceDate')
    ])

    # Aplicar filtros generales (país, fechas)
    if country:
        df = df.filter(pl.col('Country') == country)

    if start_date:
        start_datetime = pl.lit(start_date + "-01").str.strptime(pl.Datetime, "%Y-%m-%d")
        df = df.filter(pl.col('InvoiceDate') >= start_datetime)

    if end_date:
        import datetime as dt
        year, month = map(int, end_date.split('-'))
        if month == 12:
            next_month = dt.datetime(year + 1, 1, 1)
        else:
            next_month = dt.datetime(year, month + 1, 1)
        last_day = next_month - dt.timedelta(days=1)
        end_datetime = pl.lit(last_day.strftime("%Y-%m-%d") + " 23:59:59").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S")
        df = df.filter(pl.col('InvoiceDate') <= end_datetime)

    # Aplicar filtro de perfil si se especifica
    if customer_profile:
        if 'Total' not in df.columns:
            df = df.with_columns(
                (pl.col('Quantity') * pl.col('UnitPrice')).alias('Total')
            )

        total_lower, total_upper = detectar_outliers_iqr(df, 'Total')
        price_lower, price_upper = detectar_outliers_iqr(df, 'UnitPrice')

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

        df = df.filter(pl.col('Perfil') == customer_profile)

    # Calcular Sales si no existe
    if 'Sales' not in df.columns:
        df = df.with_columns([
            (pl.col('Quantity') * pl.col('UnitPrice')).alias('Sales')
        ])

    # Extraer fecha
    df = df.with_columns([
        pl.col('InvoiceDate').dt.date().alias('Fecha')
    ])

    # Parsear la fecha seleccionada
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    # Filtrar datos del día seleccionado
    df_day = df.filter(pl.col('Fecha') == target_date)

    if df_day.is_empty():
        return None

    # ===== SECCIÓN 1: RESUMEN DEL DÍA =====
    summary = _calculate_day_summary(df_day)

    # ===== SECCIÓN 2: ANÁLISIS COMPARATIVO =====
    comparisons = _calculate_comparisons(df, target_date, df_day)

    # ===== SECCIÓN 3: TOP 5 PRODUCTOS =====
    top_products = _get_top_products(df_day)

    # ===== SECCIÓN 4: TOP 5 CLIENTES =====
    top_customers = _get_top_customers(df_day)

    # ===== SECCIÓN 5: INSIGHTS AUTOMÁTICOS =====
    insights = _generate_insights(summary, comparisons, top_products, top_customers, target_date)

    return {
        'date': date_str,
        'summary': summary,
        'comparisons': comparisons,
        'top_products': top_products,
        'top_customers': top_customers,
        'insights': insights
    }


def _calculate_day_summary(df_day):
    """Calcula resumen básico del día"""
    total_sales = df_day['Sales'].sum()
    total_transactions = df_day['InvoiceNo'].n_unique()
    unique_customers = df_day['CustomerID'].n_unique()
    unique_products = df_day['StockCode'].n_unique()
    total_quantity = df_day['Quantity'].sum()

    return {
        'total_sales': float(total_sales) if total_sales else 0,
        'transactions': int(total_transactions) if total_transactions else 0,
        'unique_customers': int(unique_customers) if unique_customers else 0,
        'unique_products': int(unique_products) if unique_products else 0,
        'total_quantity': int(total_quantity) if total_quantity else 0,
        'avg_transaction_value': float(total_sales / total_transactions) if total_transactions > 0 else 0
    }


def _calculate_comparisons(df, target_date, df_day):
    """Calcula comparaciones con períodos anteriores"""
    comparisons = {}
    day_sales = df_day['Sales'].sum()

    # 1. Comparación con día anterior
    previous_date = target_date - timedelta(days=1)
    df_previous = df.filter(pl.col('Fecha') == previous_date)
    if not df_previous.is_empty():
        prev_sales = df_previous['Sales'].sum()
        comparisons['vs_previous_day'] = _calculate_change(day_sales, prev_sales)
    else:
        comparisons['vs_previous_day'] = None

    # 2. Comparación con promedio del mes
    month_start = target_date.replace(day=1)
    df_month = df.filter(
        (pl.col('Fecha') >= month_start) &
        (pl.col('Fecha') < target_date)
    )
    if not df_month.is_empty():
        month_daily_avg = df_month.group_by('Fecha').agg([
            pl.col('Sales').sum()
        ])['Sales'].mean()
        comparisons['vs_month_avg'] = _calculate_change(day_sales, month_daily_avg)
    else:
        comparisons['vs_month_avg'] = None

    # 3. Comparación con mismo día semana anterior
    week_before_date = target_date - timedelta(days=7)
    df_week_before = df.filter(pl.col('Fecha') == week_before_date)
    if not df_week_before.is_empty():
        week_before_sales = df_week_before['Sales'].sum()
        comparisons['vs_week_before'] = _calculate_change(day_sales, week_before_sales)
    else:
        comparisons['vs_week_before'] = None

    # 4. Comparación con mismo día año anterior
    year_before_date = target_date.replace(year=target_date.year - 1)
    df_year_before = df.filter(pl.col('Fecha') == year_before_date)
    if not df_year_before.is_empty():
        year_before_sales = df_year_before['Sales'].sum()
        comparisons['vs_year_before'] = _calculate_change(day_sales, year_before_sales)
    else:
        comparisons['vs_year_before'] = None

    return comparisons


def _calculate_change(current, previous):
    """Calcula cambio porcentual y absoluto"""
    if previous == 0 or previous is None:
        return None

    change_abs = float(current - previous)
    change_pct = float((current - previous) / previous * 100)
    direction = 'up' if change_abs > 0 else 'down' if change_abs < 0 else 'neutral'

    return {
        'current': float(current),
        'previous': float(previous),
        'change_abs': change_abs,
        'change_pct': change_pct,
        'direction': direction
    }


def _get_top_products(df_day):
    """Obtiene top 5 productos del día"""
    if df_day.is_empty():
        return []

    products = (
        df_day.group_by(['StockCode', 'Description'])
        .agg([
            pl.col('Quantity').sum().alias('total_quantity'),
            pl.col('Sales').sum().alias('total_sales'),
        ])
        .sort('total_sales', descending=True)
        .head(5)
    )

    total_day_sales = df_day['Sales'].sum()

    result = []
    for row in products.iter_rows(named=True):
        contribution_pct = (row['total_sales'] / total_day_sales * 100) if total_day_sales > 0 else 0
        result.append({
            'stock_code': row['StockCode'],
            'description': row['Description'] if row['Description'] else 'Sin descripción',
            'quantity': int(row['total_quantity']),
            'sales': float(row['total_sales']),
            'contribution_pct': float(contribution_pct)
        })

    return result


def _get_top_customers(df_day):
    """Obtiene top 5 clientes del día con sus perfiles"""
    if df_day.is_empty():
        return []

    # Asegurar que tenemos columna Total y Perfil
    if 'Total' not in df_day.columns:
        df_day = df_day.with_columns(
            (pl.col('Quantity') * pl.col('UnitPrice')).alias('Total')
        )

    if 'Perfil' not in df_day.columns:
        total_lower, total_upper = detectar_outliers_iqr(df_day, 'Total')
        price_lower, price_upper = detectar_outliers_iqr(df_day, 'UnitPrice')

        df_day = df_day.with_columns(
            pl.when((pl.col('Total') > total_upper) & (pl.col('UnitPrice') <= price_upper))
            .then(pl.lit('Mayorista Estándar'))
            .when((pl.col('Total') <= total_upper) & (pl.col('UnitPrice') > price_upper))
            .then(pl.lit('Minorista Lujo'))
            .when((pl.col('Total') > total_upper) & (pl.col('UnitPrice') > price_upper))
            .then(pl.lit('Mayorista Lujo'))
            .otherwise(pl.lit('Minorista Estándar'))
            .alias('Perfil')
        )

    customers = (
        df_day.group_by(['CustomerID', 'Perfil'])
        .agg([
            pl.col('Sales').sum().alias('total_spent'),
            pl.col('InvoiceNo').n_unique().alias('num_transactions')
        ])
        .sort('total_spent', descending=True)
        .head(5)
    )

    total_day_sales = df_day['Sales'].sum()

    result = []
    for row in customers.iter_rows(named=True):
        contribution_pct = (row['total_spent'] / total_day_sales * 100) if total_day_sales > 0 else 0
        result.append({
            'customer_id': str(row['CustomerID']) if row['CustomerID'] else 'Desconocido',
            'profile': row['Perfil'],
            'total_spent': float(row['total_spent']),
            'transactions': int(row['num_transactions']),
            'contribution_pct': float(contribution_pct)
        })

    return result


def _generate_insights(summary, comparisons, top_products, top_customers, target_date):
    """Genera insights automáticos basados en reglas de negocio"""
    insights = []

    # Insight 1: Día excepcional vs promedio mes
    if comparisons.get('vs_month_avg') and comparisons['vs_month_avg']['change_pct'] > 50:
        insights.append({
            'icon': '🔥',
            'type': 'success',
            'message': f"Día excepcional: Las ventas superaron en {comparisons['vs_month_avg']['change_pct']:.1f}% el promedio mensual"
        })

    # Insight 2: Alerta de bajo rendimiento
    if comparisons.get('vs_month_avg') and comparisons['vs_month_avg']['change_pct'] < -50:
        insights.append({
            'icon': '⚠️',
            'type': 'warning',
            'message': f"Alerta: Ventas {abs(comparisons['vs_month_avg']['change_pct']):.1f}% por debajo del promedio mensual"
        })

    # Insight 3: Patrón de fin de semana
    day_of_week = target_date.weekday()
    if day_of_week >= 5 and comparisons.get('vs_month_avg') and comparisons['vs_month_avg']['change_pct'] > 20:
        insights.append({
            'icon': '📈',
            'type': 'info',
            'message': "Patrón detectado: Alto rendimiento en fin de semana"
        })

    # Insight 4: Concentración de ventas en un cliente
    if top_customers and top_customers[0]['contribution_pct'] > 30:
        insights.append({
            'icon': '👤',
            'type': 'warning',
            'message': f"Concentración de ventas: Un solo cliente ({top_customers[0]['customer_id']}) representa el {top_customers[0]['contribution_pct']:.1f}% del día"
        })

    # Insight 5: Análisis de perfiles de clientes
    if top_customers:
        luxury_count = sum(1 for c in top_customers if 'Lujo' in c['profile'])
        if luxury_count >= 3:
            insights.append({
                'icon': '💎',
                'type': 'success',
                'message': f"Día premium: {luxury_count} de los top 5 clientes son de segmento Lujo"
            })

        wholesale_count = sum(1 for c in top_customers if 'Mayorista' in c['profile'])
        if wholesale_count >= 4:
            insights.append({
                'icon': '📦',
                'type': 'info',
                'message': f"Actividad mayorista: {wholesale_count} de los top 5 clientes son mayoristas"
            })

    # Insight 6: Tendencia creciente/decreciente
    if comparisons.get('vs_previous_day') and comparisons.get('vs_week_before'):
        if (comparisons['vs_previous_day']['direction'] == 'up' and
            comparisons['vs_week_before']['direction'] == 'up'):
            insights.append({
                'icon': '📊',
                'type': 'success',
                'message': "Tendencia alcista: Crecimiento constante respecto a día anterior y semana pasada"
            })
        elif (comparisons['vs_previous_day']['direction'] == 'down' and
              comparisons['vs_week_before']['direction'] == 'down'):
            insights.append({
                'icon': '📉',
                'type': 'warning',
                'message': "Tendencia bajista: Caída respecto a día anterior y semana pasada"
            })

    # Insight 7: Alto número de transacciones pero bajo ticket promedio
    if summary['avg_transaction_value'] < 50 and summary['transactions'] > 100:
        insights.append({
            'icon': '💰',
            'type': 'info',
            'message': f"Alto volumen de transacciones ({summary['transactions']}) pero ticket promedio bajo (£{summary['avg_transaction_value']:.2f})"
        })

    # Insight 8: Crecimiento interanual
    if comparisons.get('vs_year_before') and comparisons['vs_year_before']['change_pct'] > 100:
        insights.append({
            'icon': '🚀',
            'type': 'success',
            'message': f"Crecimiento interanual excepcional: +{comparisons['vs_year_before']['change_pct']:.1f}% vs mismo día del año anterior"
        })

    # Si no hay insights, agregar uno neutral
    if not insights:
        insights.append({
            'icon': 'ℹ️',
            'type': 'info',
            'message': "Día con comportamiento dentro de parámetros normales"
        })

    return insights
