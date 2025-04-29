# Archivo para app en Streamlit: "formateador_blackboard_ultra.py"
import re
import streamlit as st
import os
from zipfile import ZipFile
import datetime

# Selector de modo
modo = st.sidebar.selectbox("Selecciona una acción:", ["Formatear preguntas (TXT)", "Crear Banco de Preguntas (ZIP)"])

# ===========================================================
# MODO 1: FORMATEAR PREGUNTAS PARA BLACKBOARD ULTRA (TXT)
# ===========================================================
if modo == "Formatear preguntas (TXT)":
    st.header("📋 Formateador de Preguntas para Blackboard Ultra")

    st.write("""
    📋 **Instrucciones para pegar tus preguntas:**

    * La pregunta debe empezar con número seguido de punto (ej: 1.)
    * Cada alternativa debe comenzar con minúscula a), b), c), d)
    * Marca la respuesta correcta agregando un asterisco (*) **antes de la letra**, ejemplo: *d)
    """)

    # Área para pegar preguntas
    texto_usuario = st.text_area("Pega aquí tus preguntas:", height=300)

    # Botón para procesar
    if st.button("Procesar y validar"):
        if not texto_usuario.strip():
            st.warning("⚠️ Por favor pega las preguntas antes de procesar.")
        else:
            # Nuevo chequeo: ¿hay un texto de Justificación en el pegado?
            if re.search(r'Justificación de claves pregunta \d+:?', texto_usuario, re.IGNORECASE):
                st.error("❗ Error: Parece que has pegado una justificación. Solo debes pegar preguntas con alternativas (sin justificaciones).")
                st.stop()

            bloques = re.split(r'\n(?=\d+\.\s)', texto_usuario.strip())
            salida = []
            errores = []
            formato_invalido = False

            for idx, bloque in enumerate(bloques, start=1):
                lineas = bloque.strip().split('\n')
                if not lineas or len(lineas) < 5:
                    errores.append(f"❗ Pregunta {idx}: No tiene las 4 opciones requeridas o falta el formato correcto.")
                    formato_invalido = True
                    continue

                # Validar formato de la primera línea (número punto pregunta)
                if not re.match(r'^\d+\.\s*.*\?\]?', lineas[0]):
                    errores.append(f"❗ Pregunta {idx}: El enunciado debe comenzar con número punto y terminar con signo de pregunta.")
                    formato_invalido = True
                    continue

                # Validar alternativas
                alternativas = []
                tiene_correcta = False

                for linea in lineas[1:]:
                    linea = linea.strip()
                    if not re.match(r'^(\*?[a-d]\))\s', linea):
                        errores.append(f"❗ Pregunta {idx}: Alternativas deben comenzar con a), b), c) o d) (minúsculas).")
                        formato_invalido = True
                        break

                    correcta = False
                    if linea.startswith('*'):
                        correcta = True
                        tiene_correcta = True
                        linea = linea[1:].strip()

                    opcion_match = re.match(r'^[a-d]\)\s*(.*)', linea)
                    if opcion_match:
                        texto_opcion = opcion_match.group(1).strip()
                        estado = "Correct" if correcta else "Incorrect"
                        alternativas.append((texto_opcion, estado))
                    else:
                        errores.append(f"❗ Pregunta {idx}: Error procesando alternativas.")
                        formato_invalido = True

                if not tiene_correcta:
                    errores.append(f"❗ Pregunta {idx}: No tiene respuesta correcta marcada con '*'.")
                    formato_invalido = True

                if not formato_invalido:
                    pregunta_texto = re.sub(r'^\d+\.\s*', '', lineas[0]).strip()
                    fila = ["MC", pregunta_texto]
                    for texto_opcion, estado in alternativas:
                        fila.append(texto_opcion)
                        fila.append(estado)
                    salida.append("\t".join(fila))

            # Mostrar errores o resultado
            if errores:
                st.error("⚠️ Se encontraron errores en el formato:")
                for error in errores:
                    st.write(error)
                st.stop()
            
            contenido_final = "\n".join(salida)
            st.success("✅ Formateado exitosamente. Puedes revisar abajo y descargar.")
            st.text_area("Contenido generado:", value=contenido_final, height=300)

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
    st.header("📘 Generador de Banco Blackboard Ultra (.zip)")

    st.markdown("""
    ### 📝 Instrucciones
    1. Pega las preguntas y justificaciones en el formato correcto.
    2. Marca la alternativa correcta con un `*` antes de la letra.
    3. Las justificaciones deben comenzar con `Justificación de claves pregunta X:`
    """)
    
    titulo_banco = st.text_input("Título del Banco de Preguntas")
    contenido_total = st.text_area("📋 Pega aquí las preguntas y justificaciones:", height=600)
    
    if st.button("🎯 Procesar y Descargar"):
        if not contenido_total.strip():
            st.warning("⚠️ Debes pegar contenido para continuar.")
            st.stop()
    
        try:
            partes = contenido_total.split("Justificación de claves pregunta 1:")
            preguntas_texto = partes[0].strip()
            justificaciones_texto = "Justificación de claves pregunta 1:" + partes[1]
    
            preguntas_bloques = re.split(r'\n(?=\d+\.\s)', preguntas_texto)
            justificaciones_bloques = re.split(r'Justificación de claves pregunta \d+:', justificaciones_texto)[1:]
    
            preguntas = []
            for idx, bloque in enumerate(preguntas_bloques):
                lineas = bloque.strip().split('\n')
                if not lineas or len(lineas) < 5:
                    continue
    
                pregunta_texto = re.sub(r'^\d+\.\s*', '', lineas[0]).strip()
    
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
    
            # Asignar justificaciones formateadas
            for idx, justificacion_raw in enumerate(justificaciones_bloques):
                if idx < len(preguntas):
                    # Formatear justificación con saltos y viñetas
                    justificacion = justificacion_raw.strip()
                    justificacion = re.sub(r'\n\s*\n', '\n\n', justificacion)  # Espacios dobles
                    justificacion = re.sub(r'•\s*([a-d]\))', r'•\t\1', justificacion)
                    justificacion = re.sub(r'\s*•\s*([a-d]\))', r'•\t\1', justificacion)
                    preguntas[idx]["comentario"] = justificacion

            # ---------------------------------------------------------
            # 🚦 Validación de integridad de preguntas y justificaciones
            # ---------------------------------------------------------            
            cantidad_preguntas = len(preguntas)
            cantidad_justificaciones = len(justificaciones_bloques)
            
            st.info(f"🔎 Detectadas {cantidad_preguntas} preguntas y {cantidad_justificaciones} justificaciones.")
            
            if cantidad_preguntas != cantidad_justificaciones:
                st.error(f"❗ Error: El número de preguntas ({cantidad_preguntas}) no coincide con el número de justificaciones ({cantidad_justificaciones}).")
                st.stop()
            else:
                st.success("✅ Validación exitosa: Todas las preguntas tienen su justificación correspondiente.")
            
            # Crear XML Blackboard
            fecha_actual = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
            res = f"""<?xml version="1.0" encoding="utf-8"?>
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
    
            for i in range(1, len(preguntas)+1):
                res += f'    <QUESTION id="q{i}" class="QUESTION_MULTIPLECHOICE" />\n'
            res += "  </QUESTIONLIST>\n"
    
            for i, p in enumerate(preguntas, 1):
                res += f"""  <QUESTION_MULTIPLECHOICE id="q{i}">
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
                for j, opcion in enumerate(p['opciones'], 1):
                    res += f"""    <ANSWER id="q{i}_a{j}" position="{j}">
          <DATES>
            <CREATED value="{fecha_actual}" />
            <UPDATED value="{fecha_actual}" />
          </DATES>
          <TEXT>{opcion}</TEXT>
        </ANSWER>
    """
                idx_correcta = p['opciones'].index(p['correcta']) + 1
                comentario = p['comentario'].strip()
                res += f"""    <GRADABLE>
          <FEEDBACK_WHEN_CORRECT>{comentario}</FEEDBACK_WHEN_CORRECT>
          <FEEDBACK_WHEN_INCORRECT>{comentario}</FEEDBACK_WHEN_INCORRECT>
          <CORRECTANSWER answer_id="q{i}_a{idx_correcta}" />
        </GRADABLE>
      </QUESTION_MULTIPLECHOICE>
    """
    
            res += "</POOL>"
    
            manifest = f"""<?xml version="1.0" encoding="UTF-8"?>
    <manifest identifier="man00001">
      <organization default="toc00001">
        <tableofcontents identifier="toc00001"/>
      </organization>
      <resources>
        <resource baseurl="res00001" file="res00001.dat" identifier="res00001" type="assessment/x-bb-pool"/>
      </resources>
    </manifest>"""
    
            with open("res00001.dat", "w", encoding="utf-8") as f:
                f.write(res)
            with open("imsmanifest.xml", "w", encoding="utf-8") as f:
                f.write(manifest)
    
            zip_name = "banco_blackboard.zip"
            with ZipFile(zip_name, "w") as zipf:
                zipf.write("res00001.dat")
                zipf.write("imsmanifest.xml")
    
            with open(zip_name, "rb") as f:
                st.download_button(
                    label="📥 Descargar banco de preguntas Blackboard",
                    data=f,
                    file_name=zip_name,
                    mime="application/zip"
                )
            st.success("✅ ¡Banco de preguntas generado correctamente!")
        except Exception as e:
            st.error(f"❗ Error al procesar: {e}")
