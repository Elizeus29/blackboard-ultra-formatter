# Archivo para app en Streamlit: "formateador_blackboard_ultra.py"
import re
import streamlit as st
import os
from zipfile import ZipFile
import datetime

st.title("📝 Herramienta Blackboard Ultra: Formatear o Crear Banco de Preguntas")

# Selector de modo
modo = st.sidebar.selectbox("Selecciona una acción:", ["Formatear preguntas (TXT)", "Crear Banco de Preguntas (ZIP)"])

# ===========================================================
# MODO 1: FORMATEAR PREGUNTAS PARA BLACKBOARD ULTRA (TXT)
# ===========================================================
if modo == "Formatear preguntas (TXT)":
    st.header("📋 Formateador de Preguntas para Blackboard Ultra")

    st.write("""
    📋 **Instrucciones para pegar tus preguntas:**

    * Pega tus preguntas en el área de texto a continuación
    * Las alternativas deben comenzar con letras minúsculas a), b), c), d)
    * Marca la respuesta correcta agregando un asterisco (*) **antes de la letra** correspondiente, por ejemplo: *c)
    """)

    # Área para pegar preguntas
    texto_usuario = st.text_area("Preguntas:", height=300)

    # Botón para procesar
    if st.button("Procesar y validar"):
        if not texto_usuario.strip():
            st.warning("⚠️ Por favor pega las preguntas antes de procesar.")
        else:
            bloques = re.split(r'\n\s*\n', texto_usuario.strip())
            salida = []
            errores = []
            for idx, bloque in enumerate(bloques, start=1):
                lineas = bloque.strip().split('\n')
                if not lineas:
                    continue

                # Primera línea contiene el número y la pregunta
                primera_linea = lineas[0]
                pregunta_match = re.match(r'^\d+\.\s*(.*)', primera_linea)
                if not pregunta_match:
                    continue
                pregunta = pregunta_match.group(1).strip()

                alternativas = []
                tiene_correcta = False

                for linea in lineas[1:]:
                    linea = linea.strip()
                    correcta = False
                    if linea.startswith('*'):
                        correcta = True
                        tiene_correcta = True
                        linea = linea[1:].strip()

                    opcion_match = re.match(r'^[a-d]\)\s*(.*)', linea, re.IGNORECASE)
                    if opcion_match:
                        texto_opcion = opcion_match.group(1).strip()
                        estado = "Correct" if correcta else "Incorrect"
                        alternativas.append((texto_opcion, estado))

                if not tiene_correcta:
                    errores.append(f"❗ Pregunta {idx}: No tiene ninguna respuesta marcada como Correct.")

                # Crear la fila solo si tiene alternativas
                if alternativas:
                    fila = ["MC", pregunta]
                    for texto_opcion, estado in alternativas:
                        fila.append(texto_opcion)
                        fila.append(estado)
                    salida.append("\t".join(fila))

            if errores:
                st.error("Se encontraron errores en las preguntas:")
                for error in errores:
                    st.write(error)
                st.stop()
            
            # Mostrar el contenido formateado
            contenido_final = "\n".join(salida)
            st.success("✅ Formateado exitosamente. Puedes revisar abajo y descargar.")
            st.text_area("Contenido generado:", value=contenido_final, height=300)

            # Permitir descargar
            st.download_button(
                label="📥 Descargar preguntas formateadas",
                data=contenido_final,
                file_name='preguntas_blackboard_ultra.txt',
                mime='text/plain'
            )

# ===========================================================
# MODO 2: CREAR BANCO DE PREGUNTAS PARA BLACKBOARD ULTRA (ZIP)
# ===========================================================
else:
    st.header("🏛️ Crear Banco de Preguntas desde Pegado Masivo (ZIP)")

    st.write("""
    ✨ **Instrucciones:**
    - Pega todas tus preguntas + justificaciones.
    - Las alternativas deben comenzar con a), b), c), d).
    - Marca la respuesta correcta con un asterisco (*) antes de la letra.
    - Separa las preguntas de las justificaciones como en el ejemplo proporcionado.
    """)

    titulo_banco = st.text_input("Título del Banco de Preguntas:")

    contenido_total = st.text_area("📋 Pega aquí tus preguntas y justificaciones:", height=600)

    if st.button("🎯 Procesar Banco y Descargar"):
        if not contenido_total.strip():
            st.warning("⚠️ Por favor pega las preguntas y justificaciones.")
            st.stop()

        try:
            # Paso 1: Separar preguntas de justificaciones
            partes = contenido_total.split("Justificación de claves pregunta 1:")
            preguntas_texto = partes[0].strip()
            justificaciones_texto = "Justificación de claves pregunta 1:" + partes[1]

            preguntas_bloques = re.split(r'\n(?=\d+\.\s)', preguntas_texto)
            justificaciones_bloques = re.split(r'Justificación de claves pregunta \d+:', justificaciones_texto)[1:]

            preguntas = []
            for idx, bloque in enumerate(preguntas_bloques):
                lineas = bloque.strip().split('\n')
                if not lineas:
                    continue

                pregunta_linea = lineas[0]
                pregunta_texto = re.sub(r'^\d+\.\s*', '', pregunta_linea).strip()

                opciones = []
                correcta = None
                for linea in lineas[1:]:
                    linea = linea.strip()
                    if linea.startswith('*'):
                        correcta = re.sub(r'^\*\w\)\s*', '', linea)
                        opciones.append(correcta)
                    else:
                        opcion = re.sub(r'^\w\)\s*', '', linea)
                        opciones.append(opcion)

                preguntas.append({
                    "pregunta": pregunta_texto,
                    "opciones": opciones,
                    "correcta": correcta
                })

            # Asociar justificaciones
            for idx, justificacion in enumerate(justificaciones_bloques):
                if idx < len(preguntas):
                    preguntas[idx]['comentario'] = justificacion.strip()

            # Paso 2: Crear banco XML
            fecha_actual = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
            res00001_content = f"""<?xml version="1.0" encoding="utf-8"?>
<POOL>
  <COURSEID value="IMPORT" />
  <TITLE value="{titulo_banco}" />
  <DESCRIPTION>
    <TEXT></TEXT>
  </DESCRIPTION>
  <DATES>
    <CREATED value="{fecha_actual}" />
    <UPDATED value="{fecha_actual}" />
  </DATES>
  <QUESTIONLIST>
"""
            for idx, p in enumerate(preguntas, 1):
                res00001_content += f'    <QUESTION id="q{idx}" class="QUESTION_MULTIPLECHOICE" />\n'
            res00001_content += """  </QUESTIONLIST>\n"""

            for idx, p in enumerate(preguntas, 1):
                res00001_content += f"""  <QUESTION_MULTIPLECHOICE id="q{idx}">
    <DATES>
      <CREATED value="{fecha_actual}" />
      <UPDATED value="{fecha_actual}" />
    </DATES>
    <BODY>
      <TEXT>{p['pregunta']}</TEXT>
      <FLAGS value="true">
        <ISHTML value="true" />
        <ISNEWLINELITERAL />
      </FLAGS>
    </BODY>
"""
                for pos, opcion in enumerate(p['opciones'], 1):
                    res00001_content += f"""    <ANSWER id="q{idx}_a{pos}" position="{pos}">
      <DATES>
        <CREATED value="{fecha_actual}" />
        <UPDATED value="{fecha_actual}" />
      </DATES>
      <TEXT>{opcion}</TEXT>
    </ANSWER>
"""
                correcta_idx = p['opciones'].index(p['correcta']) + 1
                res00001_content += f"""    <GRADABLE>
      <FEEDBACK_WHEN_CORRECT>{p['comentario']}</FEEDBACK_WHEN_CORRECT>
      <FEEDBACK_WHEN_INCORRECT>{p['comentario']}</FEEDBACK_WHEN_INCORRECT>
      <CORRECTANSWER answer_id="q{idx}_a{correcta_idx}" />
    </GRADABLE>
  </QUESTION_MULTIPLECHOICE>
"""
            res00001_content += "</POOL>"

            imsmanifest_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="man00001">
  <organization default="toc00001">
    <tableofcontents identifier="toc00001"/>
  </organization>
  <resources>
    <resource baseurl="res00001" file="res00001.dat" identifier="res00001" type="assessment/x-bb-pool"/>
  </resources>
</manifest>"""

            # Guardar archivos
            with open("/tmp/res00001.dat", "w", encoding="utf-8") as f:
                f.write(res00001_content)
            with open("/tmp/imsmanifest.xml", "w", encoding="utf-8") as f:
                f.write(imsmanifest_content)

            # Crear ZIP
            zip_filename = "/tmp/banco_blackboard.zip"
            with ZipFile(zip_filename, 'w') as zipf:
                zipf.write("/tmp/res00001.dat", arcname="res00001.dat")
                zipf.write("/tmp/imsmanifest.xml", arcname="imsmanifest.xml")

            with open(zip_filename, "rb") as f:
                st.download_button(
                    label="📥 Descargar Banco de Preguntas (.zip)",
                    data=f,
                    file_name="banco_blackboard.zip",
                    mime="application/zip"
                )
            st.success("✅ Banco de preguntas generado exitosamente.")
        except Exception as e:
            st.error(f"❗ Error procesando las preguntas: {e}")
