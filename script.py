import asyncio
import os
import random
import pandas as pd
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page

# CAMBIO AQUÍ: Importar stealth_async desde el submódulo correcto
from playwright_stealth import Stealth

# SYSTEM CONSTANTS  -------------------------------------
load_dotenv()
LOAD_EXCELL_PATH = os.getenv("LOAD_EXCELL_PATH")
URL_INFONAVIT = "https://micuenta.infonavit.org.mx/"


# SYSTEM FLOW -------------------------------------------
async def setup_infonavit_page(page: Page, url: str):
    print(f"Navegando a: {url}")
    await page.goto(url, wait_until="domcontentloaded")
    print("Página cargada correctamente.")

    await asyncio.sleep(random.uniform(1.5, 3.0))

    print("Descartando modal inicial...")
    await page.mouse.click(15, 15)
    await asyncio.sleep(random.uniform(0.5, 1.2))


def get_excell_first_record(path):

    # Nota: Esta función es sincrónica ya que pandas no requiere 'await'.

    if not path or not os.path.exists(path):
        print(f"Error: La ruta del Excel no existe: {path}")
        return None

    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()

    if "Fecha" not in df.columns:
        df["Fecha"] = None

    pendientes = df[df["Fecha"].isna() | (df["Fecha"].astype(str).str.strip() == "")]

    if not pendientes.empty:
        primer_pendiente = pendientes.iloc[0]
        indice_original = primer_pendiente.name

        nombre = str(primer_pendiente["Nombre"]).strip()
        nss = str(primer_pendiente["Nss"]).strip()
        password = str(primer_pendiente["Contraseña"]).strip()

        print(f"\n[EXCEL] Procesando fila número {indice_original + 1}:")
        print(f"  Nombre: {nombre}")
        print(f"  NSS: {nss}")

        return indice_original, nombre, nss, password
    else:
        print("\n[EXCEL] ¡No hay registros pendientes por procesar!")
        return None


async def login(page: Page, nss: str, password: str):
    print(f"\n[LOGIN] Iniciando sesión para el NSS: {nss}...")

    input_nss = page.locator('input[id*="nss"], input[name*="nss"], #nss').first
    input_password = page.locator('input[type="password"], #password').first
    btn_ingresar = page.locator('button[type="submit"], input[type="submit"]').first

    await input_nss.wait_for(state="visible", timeout=10000)

    # Clic en el campo antes de escribir
    await input_nss.click()
    await asyncio.sleep(random.uniform(0.3, 0.7))

    print("[LOGIN] Llenando campo NSS...")
    # Usar .type() con un pequeño retraso entre pulsaciones de teclas
    await input_nss.type(nss, delay=random.randint(80, 150))

    await asyncio.sleep(random.uniform(0.5, 1.0))

    print("[LOGIN] Llenando campo Contraseña...")
    await input_password.click()
    await input_password.type(password, delay=random.randint(80, 150))

    await asyncio.sleep(random.uniform(0.8, 1.5))

    print("[LOGIN] Presionando botón de ingreso...")
    await btn_ingresar.click()

    await asyncio.sleep(2)


# EXECUTE METHOD --------------------------------------
async def main():
    record = get_excell_first_record(LOAD_EXCELL_PATH)

    if not record:
        print("Fin de la ejecución: No hay datos que procesar.")
        return

    indice, nombre, nss, password = record

    async with async_playwright() as p:
        # Argumentos para evitar banderas típicas de automatización en Chromium
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
            ],
        )

        # Crear contexto con dimensiones y User-Agent reales
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="es-MX",
            timezone_id="America/Mexico_City",
        )

        # APLICAR STEALTH AL CONTEXTO AQUÍ
        stealth = Stealth()
        await stealth.apply_stealth_async(context)

        page = await context.new_page()

        try:
            await setup_infonavit_page(page, URL_INFONAVIT)
            await login(page, nss, password)

            print("\nManteniendo navegador abierto para pruebas. Presiona Ctrl+C para salir.")
            await asyncio.Future()

        except Exception as e:
            print(f"Ocurrió un error durante la ejecución: {e}")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())