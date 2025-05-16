# Archivo para app en Streamlit: "formateador_blackboard_ultra.py"
import re
import streamlit as st
import os
from zipfile import ZipFile
import datetime
import streamlit.components.v1 as components

# Selector de modo
modo = st.sidebar.selectbox("Selecciona una acción:", ["Formatear preguntas (TXT)", "Crear Banco de Preguntas (ZIP)"])
with st.sidebar:
    st.markdown("""
        <style>
        div.stButton{
         margin-left:15px;
        }
        div.stButton > button {
            background: none;
            border: none;
            color: #0066cc;
            padding: 0px;
            font-size: 12px;
            text-align: left;
            text-decoration: none;
            margin:0px;
        }
        div.stButton > button:hover {
            text-decoration: none;
            color: #1f618d;
            background: none;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("#### 🎓 Tutoriales")
    preg_archivo_video = st.button(" 🔹 Cargar preguntas desde Archivo")
    banco_archivo_video = st.button(" 🔹 Cargar Banco de Preguntas")



# opción tutoriales: preguntas desde archivo
if preg_archivo_video:
    st.header("🎓 ¿Como Cargar preguntas desde Archivo?")
    st.write("""
        ✅ Descubre cómo cargar masivamente preguntas desde un archivo TXT a Blackboard Ultra con formato específico.
        
           En este video aprenderás cómo estructurar correctamente el archivo, importar rápidamente grandes cantidades de preguntas, y optimizar tu tiempo en la creación de evaluaciones.       
        """)
    components.html(
        """
        <iframe id="kaltura_player"
            src='https://cdnapisec.kaltura.com/p/3457153/embedPlaykitJs/uiconf_id/55955072?iframeembed=true&amp;entry_id=1_1qgsuv3i&amp;config%5Bprovider%5D=%7B%22widgetId%22%3A%221_h0xctz5d%22%7D&amp;config%5Bplayback%5D=%7B%22startTime%22%3A0%7D'
            style="width: 100%; height: 400px; border: 0;"
            allowfullscreen
            webkitallowfullscreen
            mozAllowFullScreen
            allow="autoplay *; fullscreen *; encrypted-media *"
            sandbox="allow-scripts allow-same-origin allow-presentation allow-popups"
            title="Tutorial en Kaltura">
        </iframe>
        """,
        height=400
    )    
# opción tutoriales: banco de preguntas
elif banco_archivo_video:
    st.header("🎓 ¿Como Cargar Banco de Preguntas?")
    st.write("""
        ✅ Aprende a cargar fácilmente bancos de preguntas en Blackboard Ultra utilizando la herramienta automática de formato
        
           En este video aprenderás cómo estructurar correctamente el archivo, importar rápidamente grandes cantidades de preguntas, y optimizar tu tiempo en la creación de evaluaciones.
        """)
    components.html(
        """
        <iframe id="kaltura_player" src='https://cdnapisec.kaltura.com/p/3457153/embedPlaykitJs/uiconf_id/55955072?iframeembed=true&amp;entry_id=1_vxitjkr2&amp;config%5Bprovider%5D=%7B%22widgetId%22%3A%221_0e4rn77n%22%7D&amp;config%5Bplayback%5D=%7B%22startTime%22%3A0%7D'  
            style="width: 640px;height: 360px;border: 0;" 
            allowfullscreen 
            webkitallowfullscreen 
            mozAllowFullScreen 
            allow="autoplay *; fullscreen *; encrypted-media *" 
            sandbox="allow-downloads allow-forms allow-same-origin allow-scripts allow-top-navigation allow-pointer-lock allow-popups allow-modals allow-orientation-lock allow-popups-to-escape-sandbox allow-presentation allow-top-navigation-by-user-activation" 
            title="Cargar banco de preguntas">
        </iframe>
        """,
        height=400
    )   

else:
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
    
        titulo_banco = st.text_input("Título del Banco de Preguntas", placeholder="Ejemplo: Evaluación AWS - Módulo 1")
        contenido_total = st.text_area("📋 Pega aquí las preguntas y justificaciones:", height=600)
    
        if st.button("🎯 Procesar y Descargar"):
            if not contenido_total.strip():
                st.warning("⚠️ Debes pegar contenido para continuar.")
                st.stop()
    
            if not titulo_banco.strip():
                st.warning("⚠️ Debes ingresar un título para el banco de preguntas antes de continuar.")
                st.stop()
    
            try:
                # Separar preguntas por número con formato flexible: 1, 1., 1.-, 1-
                preguntas_dict = {}
                for bloque in re.split(r'(?m)(?=^\d+(?:\.\-?|\-|\.)?\s)', contenido_total.split("Justificación de claves pregunta")[0].strip()):
                    match = re.match(r'^(\d+)(?:\.\-?|\-|\.)?\s', bloque)
                    if match:
                        numero = int(match.group(1))
                        preguntas_dict[numero] = bloque.strip()
    
                # Separar y mapear justificaciones
                justificaciones_dict = {}
                for match in re.finditer(r'Justificación de claves pregunta (\d+):(.*?)(?=Justificación de claves pregunta \d+:|$)', contenido_total, re.DOTALL):
                    numero = int(match.group(1))
                    contenido = match.group(2).strip()
                    justificaciones_dict[numero] = contenido
    
                preguntas = []
                for numero in sorted(preguntas_dict):
                    bloque = preguntas_dict[numero]
                    lineas = [l.strip() for l in bloque.strip().split('\n') if l.strip()]
                    if not lineas or len(lineas) < 5:
                        continue
    
                    pregunta_texto = re.sub(r'^\d+(?:\.\-?|\-|\.)?\s*', '', lineas[0]).strip()
                    opciones = []
                    correcta = None
                    for linea in lineas[1:]:
                        if not linea: continue
                        if re.match(r'^\*\s*[a-eA-E]\)', linea):
                            correcta = re.sub(r'^\*\s*[a-eA-E]\)\s*', '', linea).strip()
                            opciones.append(correcta)
                        else:
                            opcion = re.sub(r'^[a-eA-E]\)\s*', '', linea).strip()
                            opciones.append(opcion)
    
                    if not correcta:
                        st.error(f"❌ Pregunta {numero} no tiene alternativa correcta marcada (usa * antes de la letra)")
                        st.stop()
    
                    comentario = justificaciones_dict.get(numero, "Sin justificación.")
                    comentario = comentario.replace('\r\n', '\n').replace('\r', '\n')
                    comentario = re.sub(r'(?:\n\s*)?[•\-*]\s*[a-eA-E]\)\s*', r'<br/>&bull; ', comentario)
                    comentario = re.sub(r'\n\s*\n+', '<br/>', comentario)
                    comentario = re.sub(r'(?<!\n)\n(?!\n)', '<br/><br/>', comentario.strip())
    
                    preguntas.append({
                        "pregunta": pregunta_texto,
                        "opciones": opciones,
                        "correcta": correcta,
                        "comentario": comentario
                    })
    
                if len(preguntas) != len(justificaciones_dict):
                    st.error(f"❗ Error: Se encontraron {len(preguntas)} preguntas pero {len(justificaciones_dict)} justificaciones.")
                    st.stop()
    
                st.success(f"✅ Validación exitosa: {len(preguntas)} preguntas con sus justificaciones correspondientes.")
    
                fecha_actual = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
                res = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
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
                    comentario = p.get('comentario', '').strip()
                    res += f"""    <GRADABLE>
          <FEEDBACK_WHEN_CORRECT><![CDATA[{comentario}]]></FEEDBACK_WHEN_CORRECT>
          <FEEDBACK_WHEN_INCORRECT><![CDATA[{comentario}]]></FEEDBACK_WHEN_INCORRECT>
          <CORRECTANSWER answer_id="q{i}_a{idx_correcta}" />
        </GRADABLE>
      </QUESTION_MULTIPLECHOICE>
    """
    
                res += "</POOL>"
    
                # Generar archivos ZIP
                zip_name = f"banco_{titulo_banco.replace(' ', '_')}.zip" if titulo_banco else "banco_blackboard.zip"
                with ZipFile(zip_name, "w") as zipf:
                    zipf.writestr("res00001.dat", res)
                    zipf.writestr("imsmanifest.xml", """<?xml version="1.0" encoding="UTF-8"?>
    <manifest identifier="man00001">
      <organization default="toc00001">
        <tableofcontents identifier="toc00001"/>
      </organization>
      <resources>
        <resource baseurl="res00001" file="res00001.dat" identifier="res00001" type="assessment/x-bb-pool"/>
      </resources>
    </manifest>""")
                
                with open(zip_name, "rb") as f:
                    st.download_button(
                        label="📥 Descargar banco de preguntas",
                        data=f,
                        file_name=zip_name,
                        mime="application/zip"
                    )
                
                st.success("✅ ¡Banco de preguntas generado correctamente!")
    
            except Exception as e:
                st.error(f"❗ Error: {str(e)}")
                st.error("🔍 Revise el formato del texto ingresado según las instrucciones.")
