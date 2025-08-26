from csv import excel
import streamlit as st
# Librerías selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
# Librerías generales
import time
import os
import math
# Librería pandas
import pandas as pd

# -------------------------------
# CONFIGURACIÓN DEL DRIVER
# -------------------------------
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--incognito")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Perfil temporal único
user_data_dir = os.path.join(os.getcwd(), "selenium_profile")
options.add_argument(f"--user-data-dir={user_data_dir}")

# -------------------------------
# FUNCIONES
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
        submitted = st.form_submit_button("Iniciar Automatización")
        excel_file = st.file_uploader("Sube el archivo Excel con los datos", type=["xlsx"])

if submitted:
    if not excel_file:
        st.error("Por favor, sube un archivo Excel antes de continuar.")
    else:
        try:
                df = pd.read_excel(excel_file)
                st.success("Archivo Excel cargado correctamente.")
                st.dataframe(df.head())

                # Inicializar navegador SOLO cuando se ejecute
                driver = webdriver.Chrome(options=options)
                wait = WebDriverWait(driver, 15)
                actions = ActionChains(driver)

                # --- Procesar Excel ---
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

                df['RUT_completo'] = df.apply(lambda x: formatear_rut(x['RUT']) + ('-' + str(x['DV']) if not pd.isna(x['DV']) else ''), axis=1)
                df['Fecha Nacimiento'] = pd.to_datetime(df['Fecha Nacimiento (Formato: dd-mm-aaaa)'], dayfirst=True, errors='coerce')
                df['Fecha Nacimiento Formato'] = df['Fecha Nacimiento'].dt.strftime('%d-%m-%Y')
                df['Fecha Ingreso'] = pd.to_datetime(df['Fecha Ingreso (Formato: dd-mm-aaaa)'], dayfirst=True, errors='coerce')
                df['Fecha Ingreso Formato'] = df['Fecha Ingreso'].dt.strftime('%d-%m-%Y')

                long = len(df['RUT_completo'])
                print("📊 Cantidad de registros:", long)

                # --- LOGIN ---
                driver.get("https://vidasana.minsal.cl/login#!/login")
                usuario_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="login-form"]/div[2]/div/input')))
                clave_input = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="login-form"]/div[3]/div/input')))
                boton_login = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login-form"]/div[4]/div/button')))
                usuario_input.send_keys(usuario.strip())
                clave_input.send_keys(clave.strip())
                boton_login.click()
                time.sleep(5)
                print("✅ Login ejecutado correctamente")

                # --- NAVEGAR ---
                enlace = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div[1]/div/a')))
                enlace.click()
                time.sleep(3)
                print("✅ Acceso al módulo realizado")

                # --- BUCLE DE INGRESOS ---
                for i in range(1):  # 🔹 cambia a range(len(df)) si quieres procesar todos
                    try:
                        # 6. Clic en "Presiona acá"
                        boton_presiona = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[1]/div/div/div/span')))
                        boton_presiona.click()
                        print("✅ Clic en 'Presiona acá' realizado")
                        time.sleep(1)

                        # 7. Seleccionar año con autocomplete
                        xpath_ano = '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[1]/div/div/input[1]'
                        if seleccionar_dropdown_autocomplete(driver, xpath_ano, "2025"):
                            print("🎉 Año procesado exitosamente")
                        else:
                            print("❌ No se pudo seleccionar el año")
                            debug_dropdown_estado(driver)

                        # 7. Clic en "Presiona acá" segundo drop
                        boton_presiona2 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[2]/div/div/div/span')))
                        boton_presiona2.click()
                        print("✅ Clic en 'Presiona acá' realizado")
                        time.sleep(1)

                        xpath_ingreso = '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[2]/div/div/input[1]'
                        if seleccionar_dropdown_autocomplete(driver, xpath_ingreso, "Primer ingreso"):
                            print("🎉 Ingreso exitoso")
                        else:
                            print("❌ No se pudo seleccionar el año")
                            debug_dropdown_estado(driver)
                        
                        # 7. Clic en "Presiona acá" segundo drop
                        boton_presiona3 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[3]/div/div/div/span')))
                        boton_presiona3.click()
                        print("✅ Clic en 'Presiona acá' realizado")
                        time.sleep(1)

                        xpath_derivacion = '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[3]/div/div/input[1]'
                        if seleccionar_dropdown_autocomplete(driver, xpath_derivacion, df['Derivado por'][i]):
                            print("🎉 Ingreso exitoso derivacion")
                        else:
                            print("❌ No se pudo seleccionar el año")
                            debug_dropdown_estado(driver)


                        # 7. Clic en "Presiona acá" segundo drop
                        boton_presiona4 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[5]/div/div/div/span')))
                        boton_presiona4.click()
                        print("✅ Clic en 'Presiona acá' realizado")
                        time.sleep(1)

                        xpath_pais = '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[5]/div/div/input[1]'
                        if seleccionar_dropdown_autocomplete(driver, xpath_pais, df['Nacionalidad'][i]):
                            print("🎉 Ingreso exitoso derivacion")
                        else:
                            print("❌ No se pudo seleccionar el año")
                            debug_dropdown_estado(driver)

                        usuario_rut = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[6]/div/input')))
                        usuario_rut.send_keys(df['RUT_completo'][i])

                        usuario_nom = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[8]/div/input')))
                        usuario_nom.send_keys(df['Nombre'][i])

                        usuario_ap = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[9]/div/input')))
                        usuario_ap.send_keys(df['Apellido Paterno'][i])

                        usuario_am = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[10]/div/input')))
                        usuario_am.send_keys(df['Apellido Materno'][i])

                        # 7. Clic en "Presiona acá" segundo drop
                        boton_presiona5 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[11]/div/div/div/span')))
                        boton_presiona5.click()
                        print("✅ Clic en 'Presiona acá' realizado")
                        time.sleep(1)

                        xpath_sexo = '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[11]/div/div/input[1]'
                        if seleccionar_dropdown_autocomplete(driver, xpath_sexo, df['Sexo'][i]):
                            print("🎉 Ingreso exitoso sexo")
                        else:
                            print("❌ No se pudo seleccionar el año")
                            debug_dropdown_estado(driver)

                        usuario_nac = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[12]/div/datepicker/input')))
                        usuario_nac.send_keys(df['Fecha Nacimiento Formato'][i])

                        usuario_ing = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[13]/div/datepicker/input')))
                        usuario_ing.send_keys(df['Fecha Ingreso Formato'][i])

                        # 7. Clic en "Presiona acá" segundo drop presiona a pesar del overlay
                        boton_presiona6 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[15]/div/div/div/span')))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton_presiona6)
                        time.sleep(0.3)
                        driver.execute_script("arguments[0].click();", boton_presiona6)


                        xpath_est = '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[15]/div/div/input[1]'
                        if seleccionar_dropdown_autocomplete(driver, xpath_est,'CESFAM Chol chol'):
                            print("🎉 Ingreso exitoso centro")
                        else:
                            print("❌ No se pudo seleccionar el año")
                            debug_dropdown_estado(driver)
                        
                        usuario_tel = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[17]/div/input')))
                        usuario_tel.send_keys(df['Telefono'][i])

                        usuario_tel_e = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[18]/div/input')))
                        usuario_tel_e.send_keys(df['Telefono Emergencia'][i])

                        usuario_dir = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[19]/div/input')))
                        usuario_dir.send_keys(df['Dirección'][i])

                        usuario_em = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[21]/div/input')))
                        usuario_em.send_keys(df['Correo'][i])

                    except Exception as e:
                        print("❌ Ocurrió un error en la fila", i, ":", e)
                        import traceback
                        traceback.print_exc()

        except Exception as e:
            st.error(f"Error general: {e}")
            import traceback
            traceback.print_exc()