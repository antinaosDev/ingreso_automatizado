from csv import excel
import streamlit as st
import time
import os
import pandas as pd
import traceback

# Selenium con undetected_chromedriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

# -------------------------------
# FUNCIONES SELENIUM
# -------------------------------
def seleccionar_dropdown_autocomplete(driver, xpath_input, valor="2025"):
    """Selecciona un valor en un dropdown con autocomplete"""
    try:
        input_autocomplete = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_input)))
        input_autocomplete.clear()
        input_autocomplete.send_keys(valor)
        time.sleep(0.5)
        input_autocomplete.send_keys(Keys.ENTER)
        time.sleep(1)
        print(f"✅ Valor '{valor}' seleccionado correctamente en autocomplete")
        return True
    except Exception as e:
        print(f"❌ Error al seleccionar autocomplete: {e}")
        return False

def debug_dropdown_estado(driver):
    """Debug del estado del dropdown"""
    try:
        print("🐛 Estado actual del dropdown:")
        try:
            opciones = driver.find_elements(By.XPATH, "//div[@class='ui-select-choices-row']//div")
            print(f"📊 Opciones encontradas: {len(opciones)}")
            for opcion in opciones:
                print(f"   - {opcion.text}")
        except:
            print("📊 No se pudieron leer las opciones")
    except Exception as e:
        print(f"❌ Error en debug: {e}")

def formatear_rut(rut, dv=None):
    """Formatea RUT chileno"""
    if pd.isna(rut):
        return ""
    rut_str = str(int(rut))
    if len(rut_str) == 8:
        rut_formateado = f"{rut_str[:2]}.{rut_str[2:5]}.{rut_str[5:]}"
    elif len(rut_str) == 7:
        rut_formateado = f"{rut_str[:1]}.{rut_str[1:4]}.{rut_str[4:]}"
    else:
        rut_formateado = rut_str
    if dv:
        return f"{rut_formateado}-{dv}"
    return rut_formateado

# -------------------------------
# INTERFAZ STREAMLIT
# -------------------------------
st.set_page_config(page_title="Automatización de Ingresos", page_icon=":robot_face:", layout="wide")
st.title("Automatización de Ingresos - Vidasana Minsal ✍🏽")

column1, column2 = st.columns([2, 4])
with column1:
    st.image("https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDl4aWk2bTI1endoNGNoN3M4bWg1ZndjbWMxbnU4YjMyeXd1Njh4ZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/eltkEbq0Zl4aGQHisf/giphy.gif")
with column2:
    with st.form("formulario"):
        st.write("Por favor, ingresa los siguientes datos:")
        usuario = st.text_input("Usuario", value="tu_usuario")
        clave = st.text_input("Clave", value="tu_clave", type="password")
        excel_file = st.file_uploader("Sube el archivo Excel con los datos", type=["xlsx"])
        submitted = st.form_submit_button("Iniciar Automatización")

# -------------------------------
# EJECUCIÓN
# -------------------------------
if submitted:
    if not excel_file:
        st.error("Por favor, sube un archivo Excel antes de continuar.")
    else:
        try:
            df = pd.read_excel(excel_file)
            st.success("Archivo Excel cargado correctamente.")
            st.dataframe(df.head())

            # Formatear RUT y fechas
            df['RUT_completo'] = df.apply(lambda x: formatear_rut(x['RUT'], x['DV'] if 'DV' in df.columns else None), axis=1)
            df['Fecha Nacimiento'] = pd.to_datetime(df['Fecha Nacimiento (Formato: dd-mm-aaaa)'], dayfirst=True, errors='coerce')
            df['Fecha Nacimiento Formato'] = df['Fecha Nacimiento'].dt.strftime('%d-%m-%Y')
            df['Fecha Ingreso'] = pd.to_datetime(df['Fecha Ingreso (Formato: dd-mm-aaaa)'], dayfirst=True, errors='coerce')
            df['Fecha Ingreso Formato'] = df['Fecha Ingreso'].dt.strftime('%d-%m-%Y')

            st.write(f"📊 Cantidad de registros: {len(df)}")

            # -------------------------------
            # INICIALIZAR NAVEGADOR
            # -------------------------------
            options = uc.ChromeOptions()
            options.headless = True  # ejecutar sin GUI
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = uc.Chrome(options=options)
            wait = WebDriverWait(driver, 15)
            actions = ActionChains(driver)

            # -------------------------------
            # LOGIN
            # -------------------------------
            driver.get("https://vidasana.minsal.cl/login#!/login")
            usuario_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="login-form"]/div[2]/div/input')))
            clave_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="login-form"]/div[3]/div/input')))
            boton_login = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login-form"]/div[4]/div/button')))
            usuario_input.send_keys(usuario.strip())
            clave_input.send_keys(clave.strip())
            boton_login.click()
            time.sleep(5)
            st.success("✅ Login ejecutado correctamente")

            # Acceso a módulo
            enlace = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div[1]/div/a')))
            enlace.click()
            time.sleep(3)
            st.info("✅ Acceso al módulo realizado")

            # -------------------------------
            # BUCLE DE INGRESOS
            # -------------------------------
            for i in range(len(df)):
                try:
                    # Aquí puedes replicar todos los pasos de tu dropdown/inputs
                    # Ejemplo mínimo:
                    boton_presiona = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[1]/div/div/div/span')))
                    boton_presiona.click()
                    xpath_ano = '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[1]/div/div/input[1]'
                    seleccionar_dropdown_autocomplete(driver, xpath_ano, "2025")

                    # Completa RUT
                    usuario_rut = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[6]/div/input')))
                    usuario_rut.send_keys(df['RUT_completo'][i])

                    # Completa nombre
                    usuario_nom = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[8]/div/input')))
                    usuario_nom.send_keys(df['Nombre'][i])

                    st.write(f"✅ Fila {i+1} procesada")

                except Exception as e:
                    st.error(f"❌ Error en la fila {i}: {e}")
                    traceback.print_exc()

            st.success("🎉 Automatización finalizada")
        except Exception as e:
            st.error(f"Error general: {e}")
            traceback.print_exc()
        finally:
            driver.quit()
