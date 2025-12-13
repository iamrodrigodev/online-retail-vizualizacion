# Guía de Despliegue en Render

Esta guía te ayudará a desplegar la aplicación Django en Render.

## Requisitos Previos

1. Cuenta en [Render](https://render.com/)
2. Repositorio Git del proyecto (GitHub, GitLab, o Bitbucket)

## Pasos para el Despliegue

### 1. Crear una Base de Datos PostgreSQL

1. Ve a tu dashboard de Render
2. Haz clic en **New +** y selecciona **PostgreSQL**
3. Configura la base de datos:
   - **Name**: `online-retail-db` (o el nombre que prefieras)
   - **Database**: `online_retail`
   - **User**: (se genera automáticamente)
   - **Region**: Selecciona la región más cercana
   - **PostgreSQL Version**: 16 (o la más reciente)
   - **Plan**: Free (para desarrollo) o Starter/Pro (para producción)
4. Haz clic en **Create Database**
5. Guarda la **Internal Database URL** (la necesitarás más adelante)

### 2. Crear el Web Service

1. En el dashboard de Render, haz clic en **New +** y selecciona **Web Service**
2. Conecta tu repositorio de Git
3. Configura el servicio:
   - **Name**: `online-retail-visualization` (o el nombre que prefieras)
   - **Region**: La misma que la base de datos
   - **Branch**: `main`
   - **Root Directory**: (dejar vacío)
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn core.wsgi --log-file -`
   - **Plan**: Free (para desarrollo) o Starter/Pro (para producción)

### 3. Configurar Variables de Entorno

En la sección **Environment** del servicio web, agrega las siguientes variables:

```
RENDER=true
SECRET_KEY=tu-clave-secreta-super-segura-aqui
DATABASE_URL=[Internal Database URL de PostgreSQL]
PYTHON_VERSION=3.11.0
```

**Importante**:
- Genera una `SECRET_KEY` segura. Puedes usar: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- Copia la `DATABASE_URL` desde la base de datos PostgreSQL que creaste en el paso 1
- La variable `RENDER_EXTERNAL_HOSTNAME` se configura automáticamente por Render

### 4. Desplegar

1. Haz clic en **Create Web Service**
2. Render automáticamente:
   - Clonará tu repositorio
   - Ejecutará `build.sh` (instalará dependencias, migraciones, y archivos estáticos)
   - Iniciará el servidor con Gunicorn

3. Monitorea el progreso en la pestaña **Logs**

### 5. Verificar el Despliegue

Una vez completado el despliegue:
1. Haz clic en el URL generado (ej: `https://tu-app.onrender.com`)
2. Deberías ver la aplicación funcionando

## Configuración Adicional

### Crear Superusuario (Opcional)

Si necesitas acceso al admin de Django:

1. Ve a la pestaña **Shell** de tu servicio web en Render
2. Ejecuta:
   ```bash
   python manage.py createsuperuser
   ```
3. Sigue las instrucciones para crear el usuario

### Dominio Personalizado (Opcional)

1. Ve a **Settings** de tu servicio web
2. En la sección **Custom Domain**, haz clic en **Add Custom Domain**
3. Sigue las instrucciones para configurar tu dominio

## Actualizar la Aplicación

Render despliega automáticamente cuando haces push a la rama `main`. Para actualizar:

```bash
git add .
git commit -m "Descripción de cambios"
git push origin main
```

Render detectará los cambios y redespliegará automáticamente.

## Solución de Problemas

### Error: "Build failed"
- Verifica que `build.sh` sea ejecutable
- Revisa los logs de build en Render
- Asegúrate de que `requirements.txt` esté completo

### Error: "Database connection failed"
- Verifica que `DATABASE_URL` esté configurada correctamente
- Asegúrate de que la base de datos PostgreSQL esté activa

### Error: "Static files not loading"
- Verifica que WhiteNoise esté en `MIDDLEWARE` en `settings.py`
- Ejecuta `python manage.py collectstatic` en el build script

### La aplicación carga lentamente (Free tier)
- Los servicios gratuitos de Render se suspenden después de 15 minutos de inactividad
- La primera carga después de la suspensión puede tardar 30-60 segundos
- Considera actualizar a un plan de pago para evitar suspensiones

## Variables de Entorno Disponibles

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `RENDER` | Indica entorno de producción | Sí |
| `SECRET_KEY` | Clave secreta de Django | Sí |
| `DATABASE_URL` | URL de conexión PostgreSQL | Sí |
| `RENDER_EXTERNAL_HOSTNAME` | Hostname público (auto) | No |
| `PYTHON_VERSION` | Versión de Python a usar | Recomendada |

## Recursos

- [Documentación de Render](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Render Django Guide](https://render.com/docs/deploy-django)
