#@title 📝 Pegado de Preguntas para Formato Blackboard Ultra (con verificación de respuesta correcta)
import re
import ipywidgets as widgets
from IPython.display import display

# Crear el área de texto
text_area = widgets.Textarea(
    value='Pega aquí tus preguntas...',
    placeholder='Pega aquí tus preguntas',
    description='Preguntas:',
    layout=widgets.Layout(width='100%', height='300px')
)

# Botón para procesar
boton_procesar = widgets.Button(description="Procesar y generar TXT")

# Área de salida de mensajes
output = widgets.Output()

display(text_area, boton_procesar, output)

def procesar_preguntas_ultra(texto):
    bloques = re.split(r'\n\s*\n', texto.strip())
    salida = []
    errores = []
    
    for bloque_num, bloque in enumerate(bloques, start=1):
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
        hay_correcta = False
        
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
                if correcta:
                    hay_correcta = True
        
        # Verificar si hay al menos una respuesta correcta
        if not hay_correcta:
            errores.append(f"⚠️ Pregunta {bloque_num}: \"{pregunta}\" NO tiene respuesta marcada como correcta.")

        # Generar fila de salida
        fila = ["MC", pregunta]
        for texto_opcion, estado in alternativas:
            fila.append(texto_opcion)
            fila.append(estado)
        salida.append("\t".join(fila))
    
    return "\n".join(salida), errores

def on_button_clicked(b):
    output.clear_output()
    texto_usuario = text_area.value
    contenido_formateado, errores = procesar_preguntas_ultra(texto_usuario)
    
    with output:
        if errores:
            for error in errores:
                print(error)
            print("\n🚫 Corrige los errores antes de generar el archivo.\nNo se descargará ningún archivo hasta que estén corregidos.")
        else:
            with open('preguntas_blackboard_ultra.txt', 'w', encoding='utf-8') as f:
                f.write(contenido_formateado)
            print("✅ Archivo 'preguntas_blackboard_ultra.txt' generado correctamente.")
            from google.colab import files
            files.download('preguntas_blackboard_ultra.txt')

# Conectar botón a función
boton_procesar.on_click(on_button_clicked)
