# Bot Agendar Citas en Mi Cuenta Infonavit ------
# Lee el Excel de personas pendientes de citas y persona por persona inicia sesión y espera a que haya citas libres para agendar. 

## Instalación

### 1. Instalar dependencias

pip install -r requirements.txt

### 2. Instalar Chromium

playwright install chromium

### 3. Configurar variables de entorno

Copiar `.env.example` como `.env` y completar los valores necesarios.

### 4. Ejecutar

python main.py