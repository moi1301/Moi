import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import sys
import os
import urllib.request
import zipfile
import json
from urllib.parse import urlencode, parse_qsl

# Configuración para la gestión de dependencias
LIBRARIES_ZIP_URL = "https://moi1301.github.io/Moi/bibliotecas.zip"
LIBRARIES_ZIP_PATH = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'bibliotecas.zip')
LIBRARIES_PATH = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'lib')
FIRST_RUN_FILE = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), "first_run.txt")

# Define el handle del addon
addon_handle = int(sys.argv[1])
BASE_URL = sys.argv[0]

# Obtener el addon y la ruta del addon
addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')
RESOURCES_PATH = os.path.join(addon_path, 'resources')

# Verificar si las bibliotecas ya están instaladas
def check_and_install_libraries():
    if not os.path.exists(LIBRARIES_PATH):
        xbmcgui.Dialog().notification("Instalando bibliotecas", "Descargando bibliotecas necesarias...", xbmcgui.NOTIFICATION_INFO)
        try:
            urllib.request.urlretrieve(LIBRARIES_ZIP_URL, LIBRARIES_ZIP_PATH)
            with zipfile.ZipFile(LIBRARIES_ZIP_PATH, "r") as zip_ref:
                zip_ref.extractall(LIBRARIES_PATH)
            os.remove(LIBRARIES_ZIP_PATH)
            xbmcgui.Dialog().notification("Addon", "Bibliotecas instaladas correctamente", xbmcgui.NOTIFICATION_INFO)
        except Exception as e:
            xbmcgui.Dialog().notification("Error", f"Error al instalar las bibliotecas: {str(e)}", xbmcgui.NOTIFICATION_ERROR)
            sys.exit()

# Verificar si es la primera ejecución e instalar bibliotecas
def verificar_prime_inicio():
    if not os.path.exists(FIRST_RUN_FILE):
        check_and_install_libraries()
        with open(FIRST_RUN_FILE, "w") as f:
            f.write("Primer inicio completado")

# Llamar a la función de verificación
verificar_prime_inicio()

# Agregar las bibliotecas a sys.path
sys.path.insert(0, LIBRARIES_PATH)

# Intentar importar los módulos requeridos
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    xbmcgui.Dialog().notification("Error", f"No se pudieron importar los módulos: {e}", xbmcgui.NOTIFICATION_ERROR)
    sys.exit()

# Función para construir URLs
def build_url(query):
    return BASE_URL + '?' + urlencode(query)

# Define categories with automatic icon path
CATEGORIES = [
    {"name": "AGENDA", "subcategories": [], "icon": f"{RESOURCES_PATH}/agenda.png"},
    {"name": "DEPORTES", "subcategories": [], "icon": f"{RESOURCES_PATH}/deportes.png"},
    {"name": "FÚTBOL", "subcategories": [], "icon": f"{RESOURCES_PATH}/futbol.png"},
    {"name": "CHAMPIONS", "subcategories": [], "icon": f"{RESOURCES_PATH}/champions.png"},
    {"name": "GOLF", "subcategories": [], "icon": f"{RESOURCES_PATH}/golf.png"},
    {"name": "DAZN", "subcategories": [], "icon": f"{RESOURCES_PATH}/dazn.png"},
    {"name": "F1", "subcategories": [], "icon": f"{RESOURCES_PATH}/f1.png"},
    {"name": "BALONCESTO", "subcategories": [], "icon": f"{RESOURCES_PATH}/baloncesto.png"},
]

# Define AceStream channels
ACESTREAM_CHANNELS = [
    # ... your existing AceStream channel definitions here ...
{"name": "F1 | DAZN F1 1080", "url": "acestream://d6281d4e6310269b416180442a470d23a4a99dc9"},
    
]

# Define HTML5 channels
HTML5_CHANNELS = [
    # ... add more HTML5 channels here ...
]

# Función para construir URLs
def build_url(query):
    return BASE_URL + '?' + urlencode(query)

# Buscar enlace AceStream por nombre
def buscar_enlace_por_nombre(nombre):
    nombre = nombre.lower()
    for canal in ACESTREAM_CHANNELS:
        if nombre in canal["name"].lower():
            return canal["url"]
    return None

def list_categories():
    for category in CATEGORIES:
        list_item = xbmcgui.ListItem(label=category["name"])
        list_item.setArt({"icon": category["icon"]})
        url = build_url({"action": "list_channels", "category": category["name"]})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=list_item, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

def list_channels(category):
    selected_category = next((cat for cat in CATEGORIES if cat["name"] == category), None)
    if not selected_category:
        xbmcgui.Dialog().notification("Error", "Categoría no encontrada", xbmcgui.NOTIFICATION_ERROR)
        return
    if category == "AGENDA":
        list_agenda_events()
        return
    for channel in ACESTREAM_CHANNELS:
        if channel["name"].upper().startswith(category.upper()):
            list_item = xbmcgui.ListItem(label=channel["name"])
            url = build_url({"action": "play_acestream", "url": channel["url"]})
            list_item.setInfo("video", {"title": channel["name"]})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=list_item, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle)

def obtener_eventos_desde_html():
    url = "https://share.google/RDzloEUnaERau3s8I"
    user_agent = "Mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/58.0.3029.110 safari/537.3"
    headers = {"User-Agent": user_agent}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        eventos = []
        tabla_eventos = soup.find('body')
        for fila in tabla_eventos.find_all('tr')[1:]:
            columnas = fila.find_all('td')
            if len(columnas) >= 4:
                hora = columnas[1].text.strip()
                categoria = columnas[2].text.strip()
                competicion = columnas[3].text.strip()
                equipos = columnas[4].text.strip()
                enlaces = [{"name": enlace.text.strip(), "url": enlace['href']} for enlace in columnas[5].find_all('a')]
                if enlaces:
                    eventos.append({
                        'hora': hora,
                        'categoria': categoria,
                        'competicion': competicion,
                        'evento': equipos,
                        'enlaces': enlaces
                        })
        return eventos
    
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().notification("Error", f"Error al obtener eventos: {e}", xbmcgui.NOTIFICATION_ERROR)
        return []

import json

def list_agenda_events():
    eventos = obtener_eventos_desde_html()
    if not eventos:
        xbmcgui.Dialog().notification("Agenda", "No hay eventos disponibles", xbmcgui.NOTIFICATION_INFO)
        return

    for evento in eventos:
        
        # 1. Separamos los equipos si tienen un guion y lo volvemos a unir con un "vs" o espacio
        if '-' in evento['evento']:  
            partes = evento['evento'].split('-')
            texto_evento = f"{partes[0].strip()} vs {partes[1].strip()}"
            evento['evento'] = texto_evento
        else:
            texto_evento = evento['evento']

        # 2. Comprobamos si juegan tus equipos favoritos para cambiar el color
        if "GRANADA" in texto_evento.upper() or "REAL MADRID" in texto_evento.upper():
            color = "blue"
        else:
            color = "white"

        # 3. Creamos el ítem para Kodi
        titulo = f"[COLOR {color}]{evento['hora']} | {evento['categoria']} | {evento['competicion']} | {texto_evento}[/COLOR]"
        list_item = xbmcgui.ListItem(label=titulo)
        
        url = build_url({"action": "mostrar_enlaces_evento", "enlaces": json.dumps(evento["enlaces"])})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=list_item, isFolder=True)
        
    xbmcplugin.endOfDirectory(addon_handle)


def mostrar_enlaces_evento(enlaces):
    enlaces = json.loads(enlaces)
    for enlace in enlaces:
        list_item = xbmcgui.ListItem(label=enlace["name"])
        url = build_url({"action": "play_acestream", "url": enlace["url"]})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=list_item, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle)

def play_html5(url):
    try:
        xbmc.Player().play(url)
    except Exception as e:
        xbmcgui.Dialog().notification("Error", str(e), xbmcgui.NOTIFICATION_ERROR)

# Reproducir enlace AceStream
def play_acestream(url):
    """
    Reproduce un enlace AceStream utilizando el addon Horus.
    """
    try:
        # Extraer solo el ID del enlace AceStream (eliminar 'acestream://')
        acestream_id = url.replace("acestream://", "")
        
        # Construir la URL para el addon Horus
        horus_url = f"plugin://script.module.horus/?action=play&id={acestream_id}"
        
        # Reproducir utilizando Horus
        xbmc.Player().play(horus_url)
    except Exception as e:
        xbmcgui.Dialog().notification("Error", f"Error al reproducir: {e}", xbmcgui.NOTIFICATION_ERROR)

if __name__ == '__main__':
    args = dict(parse_qsl(sys.argv[2][1:]))
    action = args.get("action")
    if action == "list_channels":
        category = args.get("category")
        if category == "AGENDA":
            list_agenda_events()
        else:
            list_channels(category)
    elif action == "mostrar_enlaces_evento":
        mostrar_enlaces_evento(args["enlaces"])
    elif action == "play_html5":
        play_html5(args["url"])
    elif action == "play_acestream":
        play_acestream(args["url"])
    else:
        list_categories()