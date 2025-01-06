import gzip
import test
import base64
import requests
import json
import pyodbc
import time
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select


from bs4 import BeautifulSoup, Tag

casosPrueba = []
driver = None
base64_image=""
response=""
headers=""
json_response=""
options = Options()
api_key=""
height = ""
elementos = ""
tipoCaso=""


def obtieneCasodePrueba():
    global casosPrueba
    with open('itau.txt', 'r') as f:
        # Loop through each line in the file
        for line in f:
            print(line.strip())
            casosPrueba.append(line.strip())  # strip() is used to remove the newline character at the end of the line
    

def SeteaConfiguracionSelenium():
    global driver, height
 

    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    #options.add_argument(f"--window-size=1920,{height}")
    #options.add_argument("--hide-scrollbars")
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    
    driver = webdriver.Chrome(executable_path=r'chromedriver', options=options)
    #driver = webdriver.Chrome(service=Service('chromedriver.exe'), options=options)

 
def SeteaConfiguracionIA():
    global api_key, headers
    api_key = ""
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

def extraerImagen():
    global base64_image
    base64_image=driver.get_screenshot_as_base64()


def extraccionFuentes():
    global contenido
    contenido = driver.page_source

    soup = BeautifulSoup(contenido, 'html.parser')
    # Find and remove all script and style tags
    # Find and remove all script and style tags
    for tag in soup(["script", "style", "link", "meta", "header", "head", "footer", "template", "svg", "img", "noscript"]):
        tag.decompose()

    # The variable 'contenido' now holds the HTML content without script and style tags
    contenido = str(soup)
    # Let's assume 'contenido' is your HTML
    
    with open('output.txt', 'w', encoding='utf-8') as f:
        # Write the content of the variable to the file
        f.write(contenido)    




def ObtenerPasosARealizar(caso):
    global base64_image, response, json_response, elementos, tipoCaso, api_key
    base64_image=driver.get_screenshot_as_base64()
    # Decodifica la cadena en base64 a bytes
    image_bytes = base64.b64decode(base64_image)

    # Escribe los bytes en un archivo
    with open('screenshot.png', 'wb') as file:
        file.write(image_bytes)

    unique_id = str(uuid.uuid4())
    print ("Caso de Prueba : " + caso)
    estructura = "{'actions':[{'elemento':'','tipo_elemento':'','identificador':{'tipo':'','valor':''},'accion':'','valor':''}]}"
    
    estructura2 = {
    "casoDePrueba": "Nombre del Caso de Prueba",
    "actions": [
        {
        "elemento": "Descripción del Elemento",
        "tipo_elemento": "tipo de elemento HTML",
        "identificadores": [
            {
            "tipo": "tipo de identificador",
            "valor": "valor del identificador"
            },
            {
            "tipo": "tipo de identificador",
            "valor": "valor del identificador"
            },
            {
            "tipo": "tipo de identificador",
            "valor": "valor del identificador"
            }
        ],
        "alternativos": [
            {
            "tipo": "tipo de identificador alternativo",
            "valor": "valor del identificador alternativo"
            },
            {
            "tipo": "tipo de identificador alternativo",
            "valor": "valor del identificador alternativo"
            },
            {
            "tipo": "tipo de identificador alternativo",
            "valor": "valor del identificador alternativo"
            }
        ],
        "accion": "tipo de acción (e.g., click, escribir, validar)",
        "valor": "valor asociado a la acción, si aplica"
        },
    ]
    }

    validacion={
    "Validacion": "Resultado de simulacion de credito",
    "Elementos": [
        {
        "elemento": "[elemento que se debe validar]",
        "ValorEsperado": "[Valor que se espera]",
        "valorActual": "[Valor actual del elemento]",
        "Resultado": "[OK o NO OK]"
        }]
    }
    
    palabrasValidaciones = ["valida", "validar", "valide"]

    if any(palabra in caso for palabra in palabrasValidaciones):
        prompCustomizado= f" favor respondeme con esta estructura de ejemplo: {validacion}, y para los valores esperados, utiliza validaciones generales. y analiza solo los campos que se muestran en la pagina web referente a lo requerido en la etapa de la prueba"
        tipoCaso="validacion"
        temperature = 1
    else:
        prompCustomizado= f"para ello necesito que me indiques cuales son los elementos que necesito interactuar para cumplir esta etapa de la prueba, de preferencia por su ID, que esten visibles y habilitados la respuesta que me des, favor con esta estructura si son acciones a realizar:{estructura2}, en el tag Alternativo dame otras opciones para llegar al elemento por selenium, ademas si el input es del tipo radio el tipo_elemento que sea el label que este referenciando el radio, incluye tambien la opcion de llegar al elemento por el placeholder. Para ello te comparto la imagen de la pagina web que estoy probando y su codigo fuente para que me des el id del elemento : {contenido}"
        tipoCaso="accion"
        temperature = 0.2

    payload = {
    "model": "gpt-4o-mini", #gpt-4o  gpt-4-turbo #gpt-4o-mini 
    "messages": [
        {
        "role": "system", 
        "content": "eres un programa en python que esta en ejecucion siguiendo una flujo de prueba de un usuario para el sitio web y con selenium esta interactuando con esta pagina, favor tus respuestas que sean solo en formato json indicando el elemento tipo de elemento que necesito interactuar su identificador para selenium (id, name, xpath, etc) y la accion o validacion a realizar, todo esto en orden de las acciones o validaciones que se requieran realizar "
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": f"soy un flujo de prueba, en esta etapa necesito: {caso}, {prompCustomizado} "
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "low"
            }
            }
        ]
        }
    ],
    "max_tokens": 4096,
    "temperature": temperature
    }

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "Unique-ID": unique_id
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    json_response = response.json()
    #print(json_response)
    print("----")
    respuestaContent=json_response["choices"][0]["message"]["content"]
    respuestaContent = respuestaContent.replace('json', '').replace('\n', '').replace('`', '')
    
    #respuestaContent = '{  "actions": [    {      "elemento": "Botón",      "tipo_elemento": "button",      "identificador": {        "tipo": "id",        "valor": "btn-ir-simulador"      },      "accion": "click",      "valor": ""    }  ]}  '
    print(respuestaContent)

    elementos = json.loads(respuestaContent)

    


def EjecutaTestIA():
    driver.get("https://ww2.itau.cl/personas/creditos/credito-hipotecario-itau")

    print("----")
    for caso in casosPrueba:
        extraccionFuentes()
        extraerImagen()
        ObtenerPasosARealizar(caso)
        
        #ObtenerResultados()
        print("----")
        time.sleep(15)




if __name__ == "__main__":
    SeteaConfiguracionSelenium()
    SeteaConfiguracionIA()
    obtieneCasodePrueba()
    EjecutaTestIA()