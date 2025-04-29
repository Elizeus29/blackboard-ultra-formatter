# Archivo para app en Streamlit: "formateador_blackboard_ultra.py"
import re
import streamlit as st

st.title("📝 Formateador de Preguntas para Blackboard Ultra")
st.write("""
📋 **Instrucciones para pegar tus preguntas:**

* Pega tus preguntas en el área de texto a continuación.
* Las alternativas deben comenzar con letras minúsculas (a), b), c), d)).
* Marca la respuesta correcta agregando un asterisco (*) **antes de la letra** correspondiente (por ejemplo: *c)).
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
