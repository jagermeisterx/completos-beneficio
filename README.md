# Completada a Beneficio 🌭

Plataforma web para gestionar donaciones de la "Completada a Beneficio de la Tía Marcela".

## Stack

- **Backend:** FastAPI + a2wsgi (WSGI)
- **Frontend:** Bootstrap 5 + Vanilla JS
- **Base de datos:** SQLite
- **Hosting:** PythonAnywhere (gratuito)

## Deploy en PythonAnywhere

1. Crear cuenta en [pythonanywhere.com](https://www.pythonanywhere.com) (gratis, sin tarjeta)

2. Abrir consola Bash y clonar el repositorio:
```bash
git clone <url-del-repo> completada-beneficio
```

3. Crear virtualenv e instalar dependencias:
```bash
cd completada-beneficio
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Crear el directorio de datos:
```bash
mkdir -p data
```

5. Ir a la pestaña **Web** en PA y agregar nueva app:
   - **Manual configuration** → **Python 3.12**
   - **Source code:** `/home/<tu-user>/completada-beneficio`
   - **Working directory:** `/home/<tu-user>/completada-beneficio`
   - **WSGI config:** `/home/<tu-user>/completada-beneficio/wsgi.py`
   - **Virtualenv:** `/home/<tu-user>/completada-beneficio/venv`

6. En la sección **Static files**:
   - **URL:** `/static/`
   - **Directory:** `/home/<tu-user>/completada-beneficio/static`

7. Hacer clic en **Reload**

8. (Opcional) Cambiar contraseña admin en la pestaña **Web** → **Environment variables**:
   - `ADMIN_TOKEN` = `tu-clave-segura`

9. Tu app estará disponible en `https://<tu-user>.pythonanywhere.com`

## Admin

- **URL:** `/admin?token=admin123`
- Cambia la contraseña via variable de entorno `ADMIN_TOKEN`

## Desarrollo local

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
