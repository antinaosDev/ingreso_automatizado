import streamlit as st
import pandas as pd
import time
from playwright.sync_api import sync_playwright

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
# FUNCIONES AUXILIARES
# -------------------------------
def formatear_rut(rut, dv=None):
    """Formatea RUT chileno."""
    if pd.isna(rut):
        return ""
    rut_str = str(int(rut))
    if len(rut_str) == 8:
        rut_formateado = f"{rut_str[:2]}.{rut_str[2:5]}.{rut_str[5:]}"
    elif len(rut_str) == 7:
        rut_formateado = f"{rut_str[:1]}.{rut_str[1:4]}.{rut_str[4:]}"
    else:
        rut_formateado = rut_str
    if dv and not pd.isna(dv):
        rut_formateado += f"-{dv}"
    return rut_formateado

def seleccionar_dropdown(page, selector_input, valor):
    """Selecciona un valor en un input con autocomplete"""
    try:
        input_el = page.locator(selector_input)
        input_el.fill(valor)
        input_el.press("Enter")
        time.sleep(0.5)
        return True
    except Exception as e:
        st.warning(f"❌ No se pudo seleccionar '{valor}': {e}")
        return False

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

            # Preprocesar Excel
            df['RUT_completo'] = df.apply(lambda x: formatear_rut(x['RUT'], x['DV']), axis=1)
            df['Fecha Nacimiento'] = pd.to_datetime(df['Fecha Nacimiento (Formato: dd-mm-aaaa)'], dayfirst=True, errors='coerce')
            df['Fecha Nacimiento Formato'] = df['Fecha Nacimiento'].dt.strftime('%d-%m-%Y')
            df['Fecha Ingreso'] = pd.to_datetime(df['Fecha Ingreso (Formato: dd-mm-aaaa)'], dayfirst=True, errors='coerce')
            df['Fecha Ingreso Formato'] = df['Fecha Ingreso'].dt.strftime('%d-%m-%Y')

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Login
                page.goto("https://vidasana.minsal.cl/login#!/login")
                page.fill('xpath=//*[@id="login-form"]/div[2]/div/input', usuario.strip())
                page.fill('xpath=//*[@id="login-form"]/div[3]/div/input', clave.strip())
                page.click('xpath=//*[@id="login-form"]/div[4]/div/button')
                time.sleep(5)
                st.success("✅ Login ejecutado correctamente")

                # Acceder al módulo
                page.click('xpath=//*[@id="page-wrapper"]/div/div/ui-view/div[1]/div/a')
                time.sleep(3)
                st.info("✅ Acceso al módulo realizado")

                # Bucle de ingreso (ejemplo con la primera fila)
                for i in range(1):  # Cambiar a range(len(df)) para todas las filas
                    # Año
                    seleccionar_dropdown(page, 'xpath=//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[1]/div/div/input[1]', "2025")
                    # Ingreso
                    seleccionar_dropdown(page, 'xpath=//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[2]/div/div/input[1]', "Primer ingreso")
                    # Derivado por
                    seleccionar_dropdown(page, 'xpath=//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[3]/div/div/input[1]', df['Derivado por'][i])
                    # Nacionalidad
                    seleccionar_dropdown(page, 'xpath=//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[5]/div/div/input[1]', df['Nacionalidad'][i])
                    # RUT y nombre
                    page.fill('xpath=//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[6]/div/input', df['RUT_completo'][i])
                    page.fill('xpath=//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[8]/div/input', df['Nombre'][i])
                    page.fill('xpath=//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[9]/div/input', df['Apellido Paterno'][i])
                    page.fill('xpath=//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[10]/div/input', df['Apellido Materno'][i])
                    # Sexo
                    seleccionar_dropdown(page, 'xpath=//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[11]/div/div/input[1]', df['Sexo'][i])
                    # Fecha Nacimiento
                    page.fill('xpath=//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[12]/div/datepicker/input', df['Fecha Nacimiento Formato'][i])
                    # Fecha Ingreso
                    page.fill('xpath=//*[@id="page-wrapper"]/div/div/ui-view/div/div/div[2]/form/div[13]/div/datepicker/input', df['Fecha Ingreso Formato'][i])

                st.success("🎉 Datos ingresados correctamente")
                browser.close()

        except Exception as e:
            st.error(f"Error general: {e}")
            import traceback
            traceback.print_exc()
