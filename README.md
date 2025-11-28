# Sistema de Visualización y Análisis de Datos de Retail Online
## Inteligencia de Negocios y Minería de Datos

<div align="center">
<table>
    <thead>
        <tr>
            <th>
                <img src="https://github.com/RodrigoStranger/imagenes-la-salle/blob/main/logo_secundario_color.png?raw=true" width="150"/>
            </th>
            <th>
                <span style="font-weight:bold;">UNIVERSIDAD LA SALLE DE AREQUIPA</span><br />
                <span style="font-weight:bold;">FACULTAD DE INGENIERÍAS Y ARQUITECTURA</span><br />
                <span style="font-weight:bold;">DEPARTAMENTO ACADEMICO DE INGENIERÍA Y MATEMÁTICAS</span><br />
                <span style="font-weight:bold;">CARRERA PROFESIONAL DE INGENIERÍA DE SOFTWARE</span>
            </th>
        </tr>
    </thead>
</table>
</div>

<div align="center">
<table>
    <thead>
        <tr>
            <th><strong>Semestre</strong></th>
            <th><strong>Profesor</strong></th>
            <th><strong>Créditos</strong></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td align="center">2025 II</td>
            <td align="center">Ana María Cuadros Valdivia</td>
            <td align="center">3</td>
        </tr>
    </tbody>
</table>
</div>

---

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Marco Teórico](#marco-teórico)
3. [Pipeline de Procesamiento y Análisis](#pipeline-de-procesamiento-y-análisis)
4. [Modelos y Algoritmos Implementados](#modelos-y-algoritmos-implementados)
5. [Arquitectura del Sistema](#arquitectura-del-sistema)
6. [Comparación con Enfoques Existentes](#comparación-con-enfoques-existentes)
7. [Instalación y Uso](#instalación-y-uso)

---

## Descripción General

Este proyecto es una aplicación web de inteligencia de negocios que implementa un **pipeline completo de minería de datos** para el análisis de transacciones de retail online. El sistema combina técnicas avanzadas de aprendizaje automático, análisis estadístico y visualización interactiva para extraer insights de negocio accionables.

### Objetivo Principal

Desarrollar un sistema integral de Business Intelligence que permita:
- Segmentación automática de clientes basada en comportamiento de compra
- Análisis de similitud entre clientes usando algoritmos de Machine Learning
- Visualización interactiva de patrones de compra y tendencias de ventas
- Identificación de productos estrella por segmento de cliente
- Análisis geográfico de ventas y comportamiento de mercado

---

## Marco Teórico

### 1. Análisis RFM (Recency, Frequency, Monetary)

El análisis RFM es una técnica de marketing cuantitativo que segmenta clientes según tres dimensiones clave:

#### 1.1 Fundamento Teórico

**Recency (R)**: Tiempo transcurrido desde la última compra del cliente.
- **Base teórica**: Los clientes que compraron recientemente tienen mayor probabilidad de volver a comprar (teoría de comportamiento del consumidor).
- **Fórmula**: `R = Fecha_Referencia - Última_Fecha_Compra` (en días)
- **Interpretación**: Valores bajos de R indican clientes activos.

**Frequency (F)**: Número de transacciones realizadas por el cliente.
- **Base teórica**: La frecuencia de compra está correlacionada con la lealtad del cliente.
- **Fórmula**: `F = Conteo de transacciones únicas (InvoiceNo)`
- **Interpretación**: Valores altos de F indican clientes leales y comprometidos.

**Monetary (M)**: Valor total de las compras del cliente.
- **Base teórica**: El valor monetario indica el potencial de ingresos del cliente (Customer Lifetime Value).
- **Fórmula**: `M = Suma(Quantity × UnitPrice)` para todas las transacciones
- **Interpretación**: Valores altos de M identifican clientes de alto valor.

#### 1.2 Métricas Complementarias

Además del RFM tradicional, nuestro modelo incluye:

- **TotalQuantity**: Volumen total de productos comprados (distingue entre compradores mayoristas y minoristas)
- **AvgUnitPrice**: Precio promedio de productos comprados (identifica segmentos de lujo vs. estándar)
- **AvgOrderValue**: Valor promedio por transacción (AOV = Monetary / Frequency)
- **UniqueProducts**: Diversidad de productos comprados (indica amplitud del interés del cliente)

**Justificación**: Estas métricas adicionales capturan dimensiones del comportamiento del cliente que el RFM tradicional no contempla, permitiendo una segmentación más granular y precisa.

### 2. Detección de Outliers mediante IQR (Interquartile Range)

#### 2.1 Fundamento Matemático

El método IQR es una técnica estadística robusta para identificar valores atípicos basada en cuartiles:

**Definiciones**:
- Q1 (Primer Cuartil): Valor que divide el 25% inferior de los datos
- Q3 (Tercer Cuartil): Valor que divide el 75% inferior de los datos
- IQR = Q3 - Q1 (Rango intercuartílico)

**Límites de Detección**:
```
Límite_Inferior = Q1 - 1.5 × IQR
Límite_Superior = Q3 + 1.5 × IQR
```

#### 2.2 Aplicación en Segmentación de Clientes

En nuestro modelo, aplicamos IQR en dos dimensiones:

1. **Total de Transacción**: Identifica compras mayoristas vs. minoristas
2. **Precio Unitario**: Identifica productos de lujo vs. estándar

**Clasificación de Perfiles** (4 segmentos):

| Perfil | Condición Total | Condición UnitPrice | Interpretación de Negocio |
|--------|-----------------|---------------------|---------------------------|
| Minorista Estándar | ≤ Q3_Total | ≤ Q3_UnitPrice | Cliente casual, productos masivos |
| Mayorista Estándar | > Q3_Total | ≤ Q3_UnitPrice | Revendedor, compras en volumen |
| Minorista Lujo | ≤ Q3_Total | > Q3_UnitPrice | Cliente premium, productos selectos |
| Mayorista Lujo | > Q3_Total | > Q3_UnitPrice | Distribuidor de alta gama |

**Ventaja sobre métodos paramétricos**: IQR no asume distribución normal de los datos, siendo robusto ante asimetría (común en datos de retail).

**Implementación en código** (`customer_profiles/data_processor.py:detectar_outliers_iqr`):
```python
def detectar_outliers_iqr(df, columna):
    Q1 = df[columna].quantile(0.25)
    Q3 = df[columna].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return lower_bound, upper_bound
```

### 3. Normalización de Datos

La normalización es crucial antes de aplicar algoritmos de distancia y clustering. Implementamos dos métodos:

#### 3.1 Z-Score (Estandarización)

**Fórmula**:
```
X_normalized = (X - μ) / σ
```
Donde:
- μ = media de la característica
- σ = desviación estándar

**Propiedades**:
- Transforma datos a distribución con μ=0 y σ=1
- Preserva la forma de la distribución original
- Mantiene información sobre outliers

**Cuándo usar**:
- Para algoritmos basados en distancias (KNN, K-Means)
- Cuando las características tienen escalas muy diferentes (ej: Recency en días vs. Monetary en dólares)
- Para visualización de clustering (mejor separación visual)

#### 3.2 Min-Max (Escalado a [0,1])

**Fórmula**:
```
X_normalized = (X - X_min) / (X_max - X_min)
```

**Propiedades**:
- Escala todos los valores al rango [0, 1]
- Preserva la forma de la distribución
- Sensible a outliers (pueden comprimir la distribución)

**Cuándo usar**:
- Para algoritmos que requieren rangos acotados
- Cuando se necesita interpretabilidad directa (porcentajes)

**Recomendación del sistema**: Usar **Z-Score por defecto** para mejores resultados de clustering y visualización.

### 4. Métricas de Distancia

Las métricas de distancia cuantifican la similitud entre clientes en el espacio de características RFM.

#### 4.1 Distancia Euclidiana

**Fórmula**:
```
d(x, y) = √(Σᵢ (xᵢ - yᵢ)²)
```

**Interpretación Geométrica**: Distancia en línea recta en el espacio n-dimensional.

**Propiedades**:
- Métrica más intuitiva y común
- Sensible a la magnitud absoluta de las diferencias
- Asume que todas las dimensiones son igualmente importantes

**Ventajas**:
- Computacionalmente eficiente: O(n²·m) donde n=clientes, m=características
- Fácil de interpretar
- Funciona bien cuando las características están normalizadas

**Aplicación**: Útil para encontrar clientes con patrones de compra **cuantitativamente similares**.

#### 4.2 Distancia Coseno

**Fórmula**:
```
similarity(x, y) = (x · y) / (||x|| · ||y||)
distance(x, y) = 1 - similarity(x, y)
```

**Interpretación Geométrica**: Mide el ángulo entre vectores (0° = idénticos, 90° = ortogonales).

**Propiedades**:
- Invariante a la magnitud (solo considera dirección)
- Rango: [0, 2] (0 = idénticos, 2 = opuestos)
- Popular en sistemas de recomendación

**Ventajas**:
- Captura similitud de **patrones relativos** (proporciones)
- Un cliente que gasta $1000 con patrón RFM similar a otro que gasta $100 serán considerados similares

**Aplicación**: Ideal para identificar clientes con **comportamientos proporcionales** independientemente de la escala.

#### 4.3 Distancia de Pearson

**Fórmula**:
```
correlation(x, y) = Σᵢ((xᵢ - x̄)(yᵢ - ȳ)) / (n · σₓ · σᵧ)
distance(x, y) = 1 - correlation(x, y)
```

**Interpretación**: Basada en la correlación de Pearson (-1 a 1, transformada a distancia).

**Propiedades**:
- Mide correlación lineal entre características
- Normaliza por media y desviación estándar
- Rango: [0, 2] (0 = correlación perfecta positiva)

**Ventajas**:
- Captura relaciones lineales entre características
- Robusto ante transformaciones lineales (escala y traslación)

**Aplicación**: Útil para identificar clientes con **tendencias correlacionadas** en su comportamiento.

**Comparación práctica**:

| Métrica | Sensibilidad a Magnitud | Interpretación | Mejor Para |
|---------|-------------------------|----------------|------------|
| Euclidiana | Alta | Diferencias absolutas | Valores cuantitativos |
| Coseno | Nula | Similitud de patrones | Comportamientos proporcionales |
| Pearson | Baja | Correlación lineal | Tendencias y relaciones |

### 5. K-Nearest Neighbors (KNN)

#### 5.1 Algoritmo

KNN es un método de aprendizaje supervisado (en clasificación) y no supervisado (en grafos de similitud).

**Funcionamiento**:
1. Calcular matriz de distancias D entre todos los pares de clientes: O(n²·m)
2. Para cada cliente i, ordenar distancias: O(n log n)
3. Seleccionar los k clientes más cercanos (menores distancias)
4. Crear aristas (edges) entre cliente i y sus k vecinos

**Complejidad temporal**: O(n²·m + n²·log n) ≈ O(n²·m) para n clientes y m características.

#### 5.2 Parámetro k

La elección de k es crítica:

- **k pequeño** (k=3-5): Alta sensibilidad a ruido, grafos dispersos
- **k medio** (k=10-20): Balance entre sensibilidad y robustez (recomendado)
- **k grande** (k>50): Grafos densos, pierde especificidad

**Selección adaptativa en el sistema**: k configurable entre 1 y 500.

#### 5.3 Construcción del Grafo de Similitud

El grafo resultante G = (V, E) tiene:
- **Vértices (V)**: Clientes
- **Aristas (E)**: Conexiones entre cliente y sus k vecinos más cercanos
- **Propiedades**: Dirigido (puede que j ∈ KNN(i) pero i ∉ KNN(j))

**Aplicación en BI**:
- Identificar "clientes semilla" para campañas de marketing
- Recomendaciones de productos basadas en vecinos similares
- Detección de micro-segmentos dentro de perfiles RFM

### 6. PCA (Principal Component Analysis)

#### 6.1 Fundamento Matemático

PCA es una técnica de reducción dimensional que proyecta datos de alta dimensión a un subespacio de menor dimensión maximizando la varianza preservada.

**Objetivo**: Encontrar direcciones (componentes principales) que capturan la mayor variabilidad de los datos.

**Algoritmo** (via SVD - Singular Value Decomposition):

1. **Centrar datos**: X_centered = X - mean(X)
2. **Calcular matriz de covarianza**: C = (1/n) · X_centered^T · X_centered
3. **Descomposición en valores singulares**: X_centered = U · Σ · V^T
4. **Componentes principales**: PC = V (vectores propios de C)
5. **Proyección**: X_reduced = X_centered · PC[:, :k]

#### 6.2 Varianza Explicada

**Métrica clave**: Proporción de varianza explicada por cada componente.

```
Varianza_explicada_i = λᵢ / Σⱼ λⱼ
```

Donde λᵢ son los valores propios de la matriz de covarianza.

**Interpretación**:
- PC1 (30-40%): Captura la dirección de máxima variabilidad (usualmente dominada por Monetary)
- PC2 (20-30%): Segunda dirección ortogonal (usualmente Frequency o Recency)
- Total 2 componentes: ~60-70% de información preservada

#### 6.3 Loadings (Pesos de Características)

Los **loadings** indican la contribución de cada característica original a cada componente principal.

**Fórmula**:
```
Loading_ij = correlación(Feature_i, PC_j)
```

**Interpretación** en nuestro sistema:

Por ejemplo, si PC1 tiene loadings:
- Monetary: 0.85 (contribución alta positiva)
- AvgOrderValue: 0.75
- Frequency: 0.45
- Recency: -0.30 (contribución negativa)

**Significado**: PC1 representa principalmente el "valor del cliente" (combinación de gasto total y frecuencia, inversamente relacionado con recencia).

#### 6.4 Visualización 2D

**Reducción a 2D** (de 7 dimensiones originales):
- Permite visualización humana de patrones complejos
- Preserva relaciones de similitud aproximadas
- Facilita identificación de clusters y outliers

**Trade-off**:
- ✅ Ganancia: Interpretabilidad visual
- ⚠️ Pérdida: ~30-40% de información (varianza no capturada por PC1 y PC2)

**Optimización implementada**:
- Uso de **randomized SVD** (más rápido para datasets grandes)
- Tipo de dato **float32** (ahorra 50% de memoria vs float64)

### 7. K-Means Clustering

#### 7.1 Algoritmo

K-Means es un algoritmo de clustering particional que agrupa datos en k clusters minimizando la varianza intra-cluster.

**Algoritmo de Lloyd** (implementación estándar):

```
1. Inicialización: Seleccionar k centroides aleatorios (k-means++)
2. Asignación: Asignar cada punto al centroide más cercano
   cluster(x) = argmin_j ||x - μⱼ||²
3. Actualización: Recalcular centroides como promedio de puntos asignados
   μⱼ = (1/|Cⱼ|) · Σ_{x ∈ Cⱼ} x
4. Repetir pasos 2-3 hasta convergencia (cambio < ε) o max_iter
```

**Complejidad**: O(n · k · m · t) donde t = número de iteraciones (típicamente 10-50).

#### 7.2 Función Objetivo

K-Means minimiza la **suma de cuadrados intra-cluster** (Within-Cluster Sum of Squares, WCSS):

```
WCSS = Σⱼ Σ_{x ∈ Cⱼ} ||x - μⱼ||²
```

**Interpretación**: Busca clusters compactos (puntos cercanos a su centroide).

#### 7.3 Selección de k

En nuestro sistema, **k=4 clusters** se elige estratégicamente para:

1. **Alineación con perfiles de negocio**: 4 clusters corresponden a los 4 perfiles RFM (Minorista/Mayorista × Estándar/Lujo)
2. **Interpretabilidad**: Número manejable de segmentos para estrategias de marketing
3. **Validación empírica**: El método Elbow y Silhouette Score sugieren k=4-5 como óptimo para este dataset

#### 7.4 Optimizaciones Implementadas

- **Algoritmo Elkan**: Más eficiente que Lloyd estándar, evita cálculos redundantes
- **n_init=5**: Múltiples inicializaciones aleatorias (evita mínimos locales)
- **max_iter=50**: Límite de iteraciones (balance entre convergencia y velocidad)
- **float32**: Reduce uso de memoria crítico en producción

#### 7.5 Diferencia con Clasificación RFM

**Punto clave**: Los 4 clusters de K-Means NO son idénticos a los 4 perfiles RFM:

| Aspecto | Perfiles RFM (IQR) | Clusters K-Means |
|---------|-------------------|------------------|
| Método | Reglas determinísticas (outliers IQR) | Optimización iterativa (WCSS) |
| Dimensiones usadas | 2 (Total, UnitPrice) | 7 (RFM + 4 métricas) |
| Fronteras | Lineales (cuartiles) | No lineales (distancias euclidianas) |
| Interpretación | Tipos de cliente (negocio) | Grupos de comportamiento (datos) |

**Sinergia**:
- **Perfiles RFM**: Segmentación de negocio (tooltip, validación)
- **Clusters K-Means**: Segmentación analítica (visualización, colores)

### 8. Detección de Outliers Estadísticos

#### 8.1 Método Z-Score

**Fórmula**:
```
z_score(x) = |x - μ| / σ
Outlier si max(z_score(x)) > threshold (default: 3)
```

**Regla empírica** (distribución normal):
- 68% de datos dentro de 1σ
- 95% dentro de 2σ
- 99.7% dentro de 3σ

**Threshold=3**: Marca como outliers el ~0.3% más extremo (altamente atípicos).

#### 8.2 Aplicación Multidimensional

En nuestro sistema:
```python
outlier(cliente) = True si CUALQUIER característica tiene |z_score| > 3
```

**Interpretación**:
- Clientes con comportamiento extremo en al menos una dimensión RFM
- Ejemplos: Compra única masiva (Frequency=1, Monetary muy alto), Cliente VIP (todas métricas extremas)

#### 8.3 Visualización

**Outliers en gráfico**:
- Símbolo: Diamante (vs. círculo para normales)
- Tamaño: Más grande (10 vs. 8 pixels)
- Borde: Negro grueso (mayor contraste)

**Propósito en BI**: Identificar casos especiales que requieren análisis manual o estrategias personalizadas.

---

## Pipeline de Procesamiento y Análisis

El sistema implementa un pipeline ETL (Extract, Transform, Load) modular y escalable:

### Pipeline General

```
┌─────────────────────────────────────────────────────────────────────┐
│                      1. EXTRACCIÓN DE DATOS                         │
│  GitHub CSV → Polars DataFrame (cached) → Validación y Limpieza    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    2. TRANSFORMACIÓN DE DATOS                       │
│  ┌──────────────────┐   ┌──────────────────┐   ┌─────────────────┐ │
│  │ Filtros Globales │ → │ Feature Engineer │ → │ Segmentación    │ │
│  │ • País           │   │ • Cálculo Total  │   │ • Detección IQR │ │
│  │ • Fechas         │   │ • Parse dates    │   │ • 4 Perfiles    │ │
│  └──────────────────┘   └──────────────────┘   └─────────────────┘ │
└────────────────────────────┬────────────────────────────────────────┘
                             │
              ┌──────────────┴───────────────┐
              │                              │
              ↓                              ↓
┌──────────────────────────┐    ┌───────────────────────────────────┐
│  3A. VISUALIZACIONES     │    │  3B. ANÁLISIS DE SIMILITUD        │
│      BÁSICAS             │    │      (Pipeline Avanzado)          │
│                          │    │                                   │
│  • Mapa Mundial          │    │  Ver sección detallada abajo      │
│  • Perfiles de Cliente   │    │                                   │
│  • Tendencia de Ventas   │    │                                   │
│  • Top Productos         │    │                                   │
└──────────────┬───────────┘    └────────────────┬──────────────────┘
               │                                 │
               ↓                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│               4. VISUALIZACIÓN INTERACTIVA (Plotly.js)              │
│  • Gráficos responsivos  • Filtros dinámicos  • Tooltips enriquecidos│
└─────────────────────────────────────────────────────────────────────┘
```

### Pipeline de Análisis de Similitud de Clientes (Detallado)

Este es el **componente más complejo y distintivo** del sistema:

```
PASO 1: PREPARACIÓN DE CARACTERÍSTICAS RFM
├── Filtrar por país y fechas (si se especifica)
├── Calcular fecha de referencia: max(InvoiceDate) + 1 día
├── Agregar por CustomerID:
│   ├── Recency = Días desde última compra
│   ├── Frequency = COUNT(DISTINCT InvoiceNo)
│   ├── Monetary = SUM(Quantity × UnitPrice)
│   ├── TotalQuantity = SUM(Quantity)
│   ├── AvgUnitPrice = MEAN(UnitPrice)
│   ├── AvgOrderValue = Monetary / Frequency
│   └── UniqueProducts = COUNT(DISTINCT StockCode)
├── Clasificar CustomerType usando IQR (4 perfiles)
└── Output: (customer_ids, feature_matrix[n×7], customer_info{})

PASO 2: NORMALIZACIÓN
├── Opción A: Z-Score → X' = (X-μ)/σ
├── Opción B: Min-Max → X' = (X-min)/(max-min)
├── Validación: Detectar NaN/Inf → Reemplazar
└── Output: features_normalized[n×7] (float32)

PASO 3: CÁLCULO DE MATRIZ DE DISTANCIAS
├── Opción A: Euclidiana → d = √Σ(xᵢ-yᵢ)²
├── Opción B: Coseno → d = 1 - cos(θ)
├── Opción C: Pearson → d = 1 - corr(x,y)
├── Optimizaciones: Broadcasting, operaciones in-place, gc
└── Output: distance_matrix[n×n] (float32, simétrica)

PASO 4: BÚSQUEDA K-NEAREST NEIGHBORS
├── Para cliente seleccionado:
│   ├── Extraer fila de distancias
│   ├── Establecer distancia a sí mismo = ∞
│   ├── Ordenar distancias
│   └── Tomar primeros k índices
├── Crear aristas del grafo: source → target
├── OPTIMIZACIÓN: Liberar distance_matrix
└── Output: neighbor_indices[k], neighbor_distances[k], edges[]

PASO 5: REDUCCIÓN DIMENSIONAL
├── Opción A: PCA (por defecto)
│   ├── Centrar datos
│   ├── SVD randomized
│   ├── Proyectar a 2D
│   ├── Calcular varianza explicada
│   └── Identificar top features por componente
└── Opción B: Ejes directos (x_axis, y_axis)
└── Output: embedding_2d[n×2], pca_variance{} o axis_info{}

PASO 6: CLUSTERING K-MEANS
├── K-Means con k=4 (alineado a perfiles RFM)
├── Inicialización k-means++
├── Algoritmo Elkan (optimizado)
└── Output: cluster_labels[n] (int32, valores 0-3)

PASO 7: DETECCIÓN DE OUTLIERS
├── Calcular Z-scores multidimensional
├── Marcar outlier si any(z > 3)
└── Output: outlier_mask[n] (boolean)

PASO 8: PREPARACIÓN PARA VISUALIZACIÓN
├── embedding_data[]: {id, x, y, cluster, outlier, customer_type, ...}
├── neighbors_data[]: {id, distance, rank}
├── edges_data[]: {source, target}
└── Output: JSON serializable para frontend

PASO 9: GENERACIÓN DE GRÁFICO PLOTLY
├── Capas (orden):
│   ├── 1. Aristas (líneas grises)
│   ├── 2. Puntos normales (círculos, por cluster)
│   ├── 3. Outliers (diamantes)
│   ├── 4. Vecinos (borde amarillo)
│   └── 5. Cliente seleccionado (estrella roja)
├── Paleta de 4 colores para clusters
├── Leyenda: "Cluster X: Tipo (Y%)"
└── Output: Plotly Figure (JSON)

PASO 10: RENDERIZADO WEB
├── Backend: Serializar con PlotlyJSONEncoder
├── Frontend: Parsear y renderizar con Plotly.newPlot()
└── Métricas: n=1000 → 2-3s, n=5000 → 8-12s
```

### Optimizaciones de Performance Implementadas

El sistema está optimizado para despliegue en **Railway** (recursos limitados):

1. **Gestión de Memoria**:
   - Uso de `float32` en vez de `float64` (50% menos memoria)
   - Liberación agresiva con `gc.collect()` después de operaciones pesadas
   - Operaciones numpy in-place (`out=` parameter)

2. **Algoritmos Eficientes**:
   - PCA con `svd_solver='randomized'` (más rápido para n>1000)
   - K-Means con `algorithm='elkan'` (evita cálculos redundantes)
   - Reducción de iteraciones: `max_iter=50`, `n_init=5`

3. **Caché**:
   - Carga de datos con `@lru_cache` (evita descargas repetidas del CSV)
   - Reutilización de DataFrames entre visualizaciones

4. **Procesamiento Vectorizado**:
   - Uso intensivo de operaciones numpy/polars vectorizadas
   - Evitar loops de Python cuando sea posible

---

## Modelos y Algoritmos Implementados

### 1. Modelo de Segmentación RFM con IQR

**Descripción**: Sistema de clasificación de clientes en 4 perfiles de negocio.

**Entrenamiento**: No requiere entrenamiento (método basado en reglas estadísticas).

**Componentes**:
- Detección de outliers en dimensión `Total` (Q1, Q3, IQR)
- Detección de outliers en dimensión `UnitPrice`
- Lógica combinatoria para asignar perfil

**Diferenciación**:
- Métodos tradicionales usan percentiles fijos (ej: top 20% = VIP)
- Nuestro modelo usa IQR **adaptativo** que se ajusta a la distribución real de cada dataset/país/período
- Captura outliers en 2 dimensiones complementarias (volumen vs. precio)

**Ventajas**:
- ✅ Robusto ante cambios en distribución de datos
- ✅ Interpretabilidad de negocio directa
- ✅ No requiere datos históricos (funciona con snapshot)

**Limitaciones**:
- ⚠️ Asume independencia entre Total y UnitPrice (puede haber correlación)
- ⚠️ Fronteras rígidas (no captura gradientes suaves)

### 2. Modelo de Similitud de Clientes (Graph-based KNN)

**Descripción**: Sistema de aprendizaje no supervisado que construye un grafo de similitud entre clientes basado en comportamiento RFM.

**Arquitectura del Modelo**:

```
Input (7 dimensiones RFM)
         ↓
Normalización (Z-Score/MinMax)
         ↓
Espacio Métrico (Euclidean/Cosine/Pearson)
         ↓
Grafo KNN (k vecinos más cercanos)
         ↓
Proyección 2D (PCA)
         ↓
Clusters (K-Means, k=4)
         ↓
Output (Visualización interactiva)
```

**Entrenamiento**:
- **K-Means**: Algoritmo de Lloyd con inicialización k-means++
- **PCA**: Descomposición en valores singulares (SVD)
- **Ambos son "unsupervised"**: No requieren etiquetas, descubren patrones inherentes

**Inferencia**:
- Para nuevo cliente: Calcular características RFM → Normalizar → Encontrar k vecinos en grafo → Asignar cluster más cercano

**Diferenciación de Modelos Existentes**:

| Aspecto | Sistemas Tradicionales | Nuestro Modelo |
|---------|------------------------|----------------|
| Dimensionalidad | RFM básico (3D) | RFM extendido (7D) |
| Métrica | Solo Euclidiana | 3 métricas configurables |
| Visualización | 3D estático o 2D simple | 2D con PCA interpretable |
| Clustering | K-Means standalone | K-Means + validación con perfiles IQR |
| Outliers | Ignorados o removidos | Detectados y visualizados (valiosos) |
| Interactividad | Tablas/dashboards estáticos | Filtros dinámicos + drill-down |
| Escalabilidad | Problemas con n>10k | Optimizado para Railway (float32, SVD randomized) |

**Ejemplo de Caso de Uso**:

Imaginemos un cliente `12345` clasificado como "Minorista Lujo":
1. Sistema calcula sus k=10 vecinos más cercanos
2. Encuentra que 7/10 también son "Minorista Lujo", 2 "Mayorista Lujo", 1 "Minorista Estándar"
3. **Insight de negocio**: Este cliente tiene potencial de upgrade a "Mayorista Lujo" (2 vecinos similares ya lo son)
4. **Acción**: Ofrecerle descuentos por volumen o membresía mayorista
5. **Recomendación de productos**: Analizar top productos de sus 10 vecinos → productos que aún no ha comprado

### 3. Integración de Modelos

**Punto clave**: Los dos modelos (RFM-IQR y KNN-Clustering) se **complementan**, no compiten:

- **RFM-IQR**: Da interpretación de negocio (qué tipo de cliente es)
- **KNN-Clustering**: Da contexto analítico (con qué otros clientes se comporta similar)

**Validación cruzada**:
- Esperamos que clusters tengan composición predominante de ciertos perfiles RFM
- Si Cluster 2 es 80% "Mayorista Estándar" → confirma que el clustering captura patrones reales de negocio
- Si clusters tienen mezcla uniforme → indica que las 7 dimensiones RFM capturan información ortogonal a Total/UnitPrice

---

## Arquitectura del Sistema

### Stack Tecnológico

**Backend**:
- Django 5.2.8 (Framework web MVC)
- Polars (DataFrame library, más rápido que Pandas para datasets grandes)
- NumPy, SciPy (Computación numérica)
- scikit-learn (Algoritmos de ML: PCA, K-Means)
- Plotly (Generación de gráficos)

**Frontend**:
- HTML5/CSS3
- JavaScript (ES6+)
- Plotly.js (Renderizado interactivo de gráficos)

**Despliegue**:
- Gunicorn (WSGI server)
- WhiteNoise (Servir archivos estáticos)
- Railway (PaaS: PostgreSQL, auto-deploy desde Git)

**Datos**:
- Fuente: CSV en GitHub (público)
- Producción: PostgreSQL (Railway)
- Desarrollo: SQLite

### Estructura Modular

```
online-retail-vizualizacion/
├── core/                          # Configuración Django
│   ├── settings.py                # SQLite (dev), PostgreSQL (prod)
│   ├── urls.py                    # Rutas API
│   └── wsgi.py
├── dashboard/                     # Aplicación principal
│   ├── views.py                   # Orquestador HTTP (API endpoints)
│   ├── templates/index.html       # Single-page application
│   ├── static/visualizaciones/    # Frontend JS/CSS
│   └── visualizations/            # Módulos de procesamiento
│       ├── shared/
│       │   └── data_loader.py     # Carga CSV con caché
│       ├── world_map/
│       │   ├── data_processor.py
│       │   └── plot.py
│       ├── customer_profiles/
│       │   ├── data_processor.py  # Detección IQR
│       │   └── plot.py
│       ├── sales/
│       │   ├── data_processor.py
│       │   └── plot.py
│       ├── products/
│       │   ├── data_processor.py
│       │   └── plot.py
│       └── client_similarity/     # Pipeline complejo
│           ├── data_processor.py  # Orquestador principal
│           ├── preprocessing.py   # Normalización
│           ├── distances.py       # Matrices de distancia
│           ├── knn.py             # K-vecinos y grafo
│           ├── dimensionality.py  # PCA
│           ├── clustering.py      # K-Means, outliers
│           └── plot.py            # Visualización Plotly
├── manage.py
├── requirements.txt
├── Procfile                       # Railway deployment
└── README.md
```

---

## Comparación con Enfoques Existentes

### 1. Análisis RFM Tradicional

**Enfoque estándar**:
- División en quintiles (5 grupos) para R, F, M
- Asignación de score 1-5 a cada dimensión
- Concatenación: Cliente con R=5, F=4, M=5 → "545"
- 125 segmentos posibles (5³)

**Limitaciones**:
- ❌ Demasiados segmentos (dificulta acción)
- ❌ No considera distribución real (outliers mal manejados)
- ❌ Fronteras arbitrarias (quintiles pueden ser similares)

**Nuestro enfoque**:
- ✅ IQR adaptativo (se ajusta a distribución)
- ✅ 4 segmentos accionables (alineados con estrategias de negocio)
- ✅ Combina RFM con precio unitario (captura lujo vs. estándar)
- ✅ Validación con clustering no supervisado

### 2. Herramientas de BI Comerciales (Tableau, Power BI)

**Tableau/Power BI**:
- Drag-and-drop para crear visualizaciones
- Conectores a múltiples fuentes de datos
- Dashboards interactivos

**Limitaciones**:
- ❌ Algoritmos de ML limitados (requieren R/Python integrado)
- ❌ Costo (licencias por usuario)
- ❌ Menor control sobre pipeline de datos

**Nuestro enfoque**:
- ✅ Pipeline de ML completo en código (reproducible, versionable)
- ✅ Open-source (sin costos de licencia)
- ✅ Totalmente customizable (podemos agregar nuevos algoritmos)
- ✅ Integración nativa con Django (autenticación, permisos futuros)
- ⚠️ Requiere conocimientos técnicos (no drag-and-drop)

---

## Instalación y Uso

### Requisitos Previos

- Python 3.11+
- pip (gestor de paquetes)
- Git

### Instalación Local

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/online-retail-vizualizacion.git
cd online-retail-vizualizacion

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Aplicar migraciones
python manage.py migrate

# 6. Ejecutar servidor de desarrollo
python manage.py runserver

# 7. Abrir en navegador
# http://127.0.0.1:8000/
```

### Uso de la Aplicación

#### 1. Visualizaciones Básicas

Al cargar la página principal, verás 4 visualizaciones iniciales:

1. **Mapa Mundial**: Ventas por país (choropleth)
   - Click en país → Filtra todas las demás visualizaciones
   - Hover → Muestra ventas totales del país

2. **Perfiles de Cliente**: Barras horizontales con 4 segmentos
   - Click en barra → Filtra por perfil de cliente
   - Colores alineados con tipos de cliente

3. **Tendencia de Ventas**: Línea temporal
   - Muestra ventas mensuales
   - Se actualiza según filtros de país/perfil/fechas

4. **Top 5 Productos**: Barras horizontales
   - Productos más vendidos
   - Filtrable por categoría/subcategoría

#### 2. Análisis de Similitud de Clientes

**Panel de configuración**:

1. Seleccionar Customer ID (autocompletado con IDs disponibles)
2. Configurar parámetros:
   - **K vecinos**: Número de clientes similares a mostrar (1-500)
   - **Métrica de distancia**: Euclidiana (diferencias absolutas), Coseno (patrones), Pearson (correlaciones)
   - **Normalización**: Z-Score (recomendado), Min-Max
   - **Ejes**: PCA (automático) o Características directas (Recency, Frequency, etc.)
3. Aplicar filtros globales (opcional):
   - País
   - Rango de fechas
4. Click "Calcular Similitud"

**Interpretación del gráfico**:

- **Puntos**: Cada punto = 1 cliente
- **Colores**: 4 colores = 4 clusters (grupos de comportamiento similar)
- **Formas**:
  - Círculo: Cliente normal
  - Diamante: Outlier (comportamiento atípico)
  - Estrella roja: Cliente seleccionado
- **Líneas**: Conexiones entre cliente seleccionado y sus k vecinos
- **Ejes**:
  - Si PCA: "Característica_Principal (% varianza)"
  - Si directo: Nombre de la característica RFM

---

## Referencias

### Fundamentos Teóricos

1. **RFM Analysis**:
   - Bult, J. R., & Wansbeek, T. (1995). "Optimal Selection for Direct Mail." Marketing Science, 14(4), 378-394.
   - Fader, P. S., Hardie, B. G., & Lee, K. L. (2005). "RFM and CLV: Using Iso-Value Curves for Customer Base Analysis." Journal of Marketing Research, 42(4), 415-430.

2. **Outlier Detection (IQR)**:
   - Tukey, J. W. (1977). "Exploratory Data Analysis." Addison-Wesley.

3. **Distance Metrics**:
   - Deza, M. M., & Deza, E. (2009). "Encyclopedia of Distances." Springer.

4. **K-Nearest Neighbors**:
   - Cover, T., & Hart, P. (1967). "Nearest Neighbor Pattern Classification." IEEE Transactions on Information Theory, 13(1), 21-27.

5. **Principal Component Analysis**:
   - Jolliffe, I. T. (2002). "Principal Component Analysis." Springer Series in Statistics, 2nd Edition.
   - Halko, N., Martinsson, P. G., & Tropp, J. A. (2011). "Finding Structure with Randomness: Probabilistic Algorithms for Constructing Approximate Matrix Decompositions." SIAM Review, 53(2), 217-288.

6. **K-Means Clustering**:
   - MacQueen, J. (1967). "Some Methods for Classification and Analysis of Multivariate Observations." Proceedings of 5th Berkeley Symposium.
   - Arthur, D., & Vassilvitskii, S. (2007). "k-means++: The Advantages of Careful Seeding." SODA '07.

---

## Metadatos del Proyecto

**Curso**: Inteligencia de Negocios y Minería de Datos
**Institución**: Universidad La Salle de Arequipa
**Semestre**: 2025 II
**Profesora**: Ana María Cuadros Valdivia

**Dataset**:
- Fuente: UCI Machine Learning Repository - Online Retail Dataset
- URL: https://archive.ics.uci.edu/ml/datasets/Online+Retail
- Período: 01/12/2010 - 09/12/2011
- Registros: ~541,909 transacciones
- Clientes: ~4,372 únicos
- Países: 38

---

**Última actualización**: 28 de noviembre de 2025
