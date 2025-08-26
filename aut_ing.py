import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

# -------------------------------
# CONFIGURACIÓN DEL DRIVER REMOTO
# -------------------------------
# Usa un servicio de Selenium remoto (Browserless, etc.)
REMOTE_WEBDRIVER_URL = "https://<API_KEY>@chrome.browserless.io/webdriver"

options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")  # Headless para la nube
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# -------------------------------
# FUNCIONES
# -------------------------------
def seleccionar_dropdown_autocomplete(driver, wait, xpath_input, valor="2025"):
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
        opciones = driver.find_elements(By.XPATH, "//div[@class='ui-select-choices-row']//div")
        print(f"📊 Opciones encontradas: {len(opciones)}")
        for opcion in opciones:
            print(f"   - {opcion.text}")
    except Exception as e:
        print(f"❌ Error en debug: {e}")

def formatear_rut(rut):
    if pd.isna(rut):
        return ""
    rut_str = str(int(rut))
    if len(rut_str) == 8:
        return f"{rut_str[:2]}.{rut_str[2:5]}.{rut_str[5:]}"
    elif len(rut_str) == 7:
        return f"{rut_str[:1]}.{rut_str[1:4]}.{rut_str[4:]}"
    else:
        return rut_str

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

if submitted:
    if not excel_file:
        st.error("Por favor, sube un archivo Excel antes de continuar.")
    else:
        try:
            df = pd.read_excel(excel_file)
            st.success("Archivo Excel cargado correctamente.")
            st.dataframe(df.head())

            # Inicializar navegador remoto SOLO cuando se ejecute
            driver = webdriver.Remote(command_executor=REMOTE_WEBDRIVER_URL, options=options)
            wait = WebDriverWait(driver, 15)
            actions = ActionChains(driver)

            # Procesar Excel
            df['RUT_completo'] = df.apply(lambda x: formatear_rut(x['RUT']) + ('-' + str(x['DV']) if not pd.isna(x['DV']) else ''), axis=1)
            df['Fecha Nacimiento'] = pd.to_datetime(df['Fecha Nacimiento (Formato: dd-mm-aaaa)'], dayfirst=True, errors='coerce')
            df['Fecha Nacimiento Formato'] = df['Fecha Nacimiento'].dt.strftime('%d-%m-%Y')
            df['Fecha Ingreso'] = pd.to_datetime(df['Fecha Ingreso (Formato: dd-mm-aaaa)'], dayfirst=True, errors='coerce')
            df['Fecha Ingreso Formato'] = df['Fecha Ingreso'].dt.strftime('%d-%m-%Y')

            # LOGIN
            driver.get("https://vidasana.minsal.cl/login#!/login")
            usuario_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="login-form"]/div[2]/div/input')))
            clave_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="login-form"]/div[3]/div/input')))
            boton_login = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login-form"]/div[4]/div/button')))
            usuario_input.send_keys(usuario.strip())
            clave_input.send_keys(clave.strip())
            boton_login.click()
            time.sleep(5)
            st.success("✅ Login ejecutado correctamente")

            # Acceso al módulo
            enlace = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div[1]/div/a')))
            enlace.click()
            time.sleep(3)
            st.info("✅ Acceso al módulo realizado")

            # Bucle de ingresos (ejemplo: primer registro)
            for i in range(1):  # Cambiar a range(len(df)) para procesar todos
                try:
                    # Año
                    boton_presiona = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[1]/div/div/div/span')))
                    boton_presiona.click()
                    xpath_ano = '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[1]/div/div/input[1]'
                    seleccionar_dropdown_autocomplete(driver, wait, xpath_ano, "2025")
                    
                    # Primer ingreso
                    boton_presiona2 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[2]/div/div/div/span')))
                    boton_presiona2.click()
                    xpath_ingreso = '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[2]/div/div/input[1]'
                    seleccionar_dropdown_autocomplete(driver, wait, xpath_ingreso, "Primer ingreso")
                    
                    # Llenar datos personales
                    campos = {
                        'RUT_completo': '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[6]/div/input',
                        'Nombre': '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[8]/div/input',
                        'Apellido Paterno': '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[9]/div/input',
                        'Apellido Materno': '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[10]/div/input',
                        'Fecha Nacimiento Formato': '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[12]/div/datepicker/input',
                        'Fecha Ingreso Formato': '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[13]/div/datepicker/input',
                    }
                    for col, xpath in campos.items():
                        elem = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
                        elem.send_keys(str(df[col][i]))

                except Exception as e:
                    st.error(f"❌ Error en la fila {i}: {e}")

        except Exception as e:
            st.error(f"Error general: {e}")

        finally:
            driver.quit()
