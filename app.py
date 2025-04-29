# archivo: app.py
import streamlit as st
import re

def procesar_preguntas_ultra(texto):
    bloques = re.split(r'\n\s*\n', texto.strip())
    salida = []
    for bloque in bloques:
        lineas = bloque.strip().split('\n')
        if not lineas:
            continue
        
        primera_linea = lineas[0]
        pregunta_match = re.match(r'^\d+\.\s*(.*)', primera_linea)
        if not pregunta_match:
            continue
        pregunta = pregunta_match.group(1).strip()
        
        alternativas = []
        
        for linea in lineas[1:]:
            linea = linea.strip()
            correcta = False
            if linea.startswith('*'):
                correcta = True
                linea = linea[1:].strip()
            
            opcion_match = re.match(r'^[a-d]\)\s*(.*)', linea, re.IGNORECASE)
            if opcion_match:
                texto_opcion = opcion_match.group(1).strip()
                estado = "Correct" if correcta else "Incorrect"
                alternativas.append((texto_opcion, estado))

        fila = ["MC", pregunta]
        for texto_opcion, estado in alternativas:
            fila.append(texto_opcion)
            fila.append(estado)
        
        salida.append("\t".join(fila))
    return "\n".join(salida)

# ---- Interfaz Streamlit ----

st.title("📄 Formateador de Preguntas para Blackboard Ultra")

st.markdown("""
Pega aquí tus preguntas siguiendo el formato:
- Pregunta numerada
- Opciones a), b), c), d)
- Marca la respuesta correcta con un *
""")

texto_usuario = st.text_area("Pega aquí tus preguntas", height=300)

if st.button("Procesar"):
    if texto_usuario.strip() == "":
        st.warning("⚠️ Por favor pega las preguntas primero.")
    else:
        contenido_formateado = procesar_preguntas_ultra(texto_usuario)
        st.success("✅ Preguntas procesadas correctamente.")
        
        # Mostrar vista previa
        st.text_area("Vista previa del archivo generado:", value=contenido_formateado, height=300)
        
        # Generar archivo para descargar
        st.download_button(
            label="📥 Descargar archivo TXT",
            data=contenido_formateado,
            file_name="preguntas_blackboard_ultra.txt",
            mime="text/plain"
        )
