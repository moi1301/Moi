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
    {"name": "F1 | DAZN F1 1080", "url": "acestream://b08e158ea3f5c72084f5ff8e3c30ca2e4d1ff6d1"},
    {"name": "F1 | DAZN F1 1080 | OPCION 2", "url": "acestream://bcf9dc38f92e90a71b87bd54b3bac91b76d09a69"},
    {"name": "F1 | DAZN F1 1080 | OPCION 3", "url": "acestream://fd53cfa7055fe458d4f5c0ff59a06cd43723be55"},
    {"name": "F1 | DAZN F1 720", "url": "acestream://ed6188dcbb491efeb2092c1a6199226c27f61727"},
    {"name": "FÚTBOL | M. LA LIGA 1080", "url": "acestream://00c9bc9c5d7d87680a5a6bed349edfa775a89947"},
    {"name": "FÚTBOL | M. LA LIGA 1080 | OPCION 2", "url": "acestream://07f2b92762cfff99bba785c2f5260c7934ca6034"},
    {"name": "FÚTBOL | M. LA LIGA 1080 | MULTIAUDIO", "url": "acestream://c9321006921967d6258df6945f1d598a5c0cbf1e"},
    {"name": "FÚTBOL | M. LA LIGA 1080 | MULTIAUDIO 2", "url": "acestream://4b528d10eaad747ddf52251206177573ee3e9f74"},
    {"name": "FÚTBOL | M. LA LIGA 720", "url": "acestream://14b6cd8769cd485f2cffdca64be9698d9bfeac58"},
    {"name": "FÚTBOL | M. LA LIGA 2 1080", "url": "acestream://51b363b1c4d42724e05240ad068ad219df8042ec"},
    {"name": "FÚTBOL | M. LA LIGA 2 720", "url": "acestream://ad42faa399df66dcd62a1cbc9d1c99ed4512d3b8"},
    {"name": "FÚTBOL | M. LA LIGA 3 1080", "url": "acestream://7ad14386deef2f45ffe17d30a631dbf79b6a1a87"},
    {"name": "FÚTBOL | M. LA LIGA 4 1080", "url":"acestream://382b14499e3d76e557d449d2e5bbc4e4bd63bd39"},
    #{"name": "FÚTBOL | M. LA LIGA 5 1080", "url":"acestream://382b14499e3d76e557d449d2e5bbc4e4bd63bd39"},
    #{"name": "FÚTBOL | M. LA LIGA 6 1080", "url":"acestream://382b14499e3d76e557d449d2e5bbc4e4bd63bd39"},   
    #{"name": "FÚTBOL | LA LIGA BAR 1080", "url": "acestream://608b0faf7d3d25f6fe5dba13d5e4b4142949990e"},
    #{"name": "FÚTBOL | LA LIGA BAR 1080 | OPCION 2", "url": "acestream://94d34491106e00394835c8cb68aa94481339b53f"},
    {"name": "FÚTBOL | DAZN LaLiga 1080", "url": "acestream://e2b8a4aba2f4ea3dd68992fcdb65c9e62d910b05"},
    {"name": "FÚTBOL | DAZN LaLiga 1080 | OPCION 2", "url": "acestream://f8d5e39a49b9da0215bbd3d9efb8fb3d06b76892"},
    {"name": "FÚTBOL | DAZN LaLiga 1080 | OPCION 3", "url": "acestream://520950d296c952e1864a08e15af9f89f1ab514ec"},
    {"name": "FÚTBOL | DAZN LaLiga 720", "url": "acestream://4e6d9cf7d177366045d33cd8311d8b1d7f4bed1f"},
    {"name": "FÚTBOL | DAZN LaLiga 2 1080", "url": "acestream://a231b2fa1f7754433efeb8bb8d69d7b9096dcba8"},
    {"name": "FÚTBOL | DAZN LaLiga 2 720", "url": "acestream://c976c7b37964322752db562b4ad65515509c8d36"},
    {"name": "FÚTBOL | LaLiga Smartbank 1080", "url": "acestream://87bb542f974b6b9e89d0f2e20ed6dc93426f4be0"},
    {"name": "FÚTBOL | LaLiga Smartbank 720", "url": "acestream://a4f072c9b614323ac1258a175f868a909ea3c8cd"},
    {"name": "FÚTBOL | LaLiga Smartbank 2 1080", "url": "acestream://709075831bf5c41ed0a20dfbd640aab6c28971f8"},
    #{"name": "FÚTBOL | LaLiga Smartbank 2 720", "url": "acestream://0a335406bad0b658aeddb2d38f8c0614b2e5623a"},
    {"name": "FÚTBOL | LaLiga Smartbank 3", "url": "acestream://778d2f60bb7207addedcca0b9aed98f41529724e"},  
    {"name": "DEPORTES | M.Plus 1080", "url": "acestream://1ab443f5b4beb6d586f19e8b25b9f9646cf2ab78"},   
    {"name": "FÚTBOL | Copa 1080", "url": "acestream://f6beccbc4eea4bc0cda43b3e8ac14790a98b61b4"},
    {"name": "FÚTBOL | Copa 720", "url": "acestream://b51f2d9a15b6956a44385b6be531bcabeb099d9d"},    
    {"name": "DEPORTES | #VAMOS 1080", "url": "acestream://c7c81acdd1a03ecc418c94c2f28e2adb0556c40b"},
    {"name": "DEPORTES| #VAMOS 720", "url": "acestream://0e5d8c9724fa9163f49096b70484e315251eb785"},
    {"name": "FÚTBOL | #ELLAS 1080", "url": "acestream://d8c2ed470e847154a88f011137cc206319f6bed5"},
    {"name": "DEPORTES | M. DEPORTES 1080", "url": "acestream://ebca4a63ce3bfda7b272964a1acc5227218184a4"},
    {"name": "DEPORTES | M. DEPORTES 720", "url": "acestream://2f3cfd199a49819cbd129689a840dc3d23ab93aa"},
    {"name": "DEPORTES | M. DEPORTES 2 1080", "url": "acestream://f0ee7a2b43c1df5ea9e4fac5bf876d5bef4372b0"},
    {"name": "DEPORTES | M. DEPORTES 2 720", "url": "acestream://bfa01c11c5c6b7a616a516de4f2c769a89d26b25"},
    {"name": "DEPORTES | M. DEPORTES 3 1080", "url": "acestream://799c6b5ee1cf41af077d14e3f9c45a32697eb903"},
    {"name": "DEPORTES | M. DEPORTES 4 1080", "url": "acestream://b40e1de2dcbd7c665f54877b14c830ed67b32a96"},
    {"name": "DEPORTES | M. DEPORTES 5 1080", "url": "acestream://7b361369a40046ad3011086f9d4ae2982fb4d5aa"},
    #{"name": "DEPORTES | M. DEPORTES 6 1080", "url": "acestream://cc5782d37ae6b6e0bab396dd64074982d0879046"},
    #{"name": "DEPORTES | M. DEPORTES 7 1080", "url": "acestream://070f82d6443a52962d6a2ed9954c979b29404932"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 1080 MULTIAUDIO", "url": "acestream://97df5b7824948972d041d8ca2a4d29c90b641bc9"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 1080 MULTIAUDIO", "url": "acestream://2b51710cee513e8939785fa3e7980f32d4e0415f"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 1080 2", "url": "acestream://9db029dff6a9c637d1f670e78dbc1a479b9b406e"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 720", "url": "acestream://b028202ff335911db3118bceac027df3e8ef6c32"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 2 1080", "url":"acestream://74ab4e4ec7e2da001f473ca40893b7307b8029c5"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 2 720", "url": "acestream://38f7b2044e549df2039ff26cefa6f9a60c854d5e"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 3 1080", "url": "acestream://4416843c96b7f7a1bc55c476091a60fff0922bc7"},
    {"name": "CHAMPIONS | M.L. CAMPEONES 3 720", "url": "acestream://cfc371890bfb502737a26de5215e50929c52d0f9"},
    #{"name": "CHAMPIONS | M.L. CAMPEONES 4 1080", "url": "acestream://65a18a6bd83918a9586b673fec12405aaf4e9f7d"},
    #{"name": "CHAMPIONS | M.L. CAMPEONES 5 1080", "url": "acestream://11744c25a594e17d587ed0871fe40ff21b4bd1e0"},
    #{"name": "CHAMPIONS | M.L. CAMPEONES 6 1080", "url": "acestream://fdda1f0dd8c33fbdc5a66ab98e291f570cae67cd"},
    #{"name": "CHAMPIONS | M.L. CAMPEONES 7 1080", "url": "acestream://b7f47db93dced60f54e8f89e2366ed061b534049"},
    #{"name": "CHAMPIONS | M.L. CAMPEONES 8 1080", "url": "acestream://d298c6e5c8be71f5995b45289c6388b225318b3c"},
    #{"name": "CHAMPIONS | M.L. CAMPEONES 9 SD", "url": "acestream://2d7c4cfb3987b652a779afc894cca2fccbbacf21"},
    #{"name": "CHAMPIONS | M.L. CAMPEONES 10 SD", "url": "acestream://c056f9e180cd7d40963129a17ff54f4ee8259353"},
    #{"name": "CHAMPIONS | M.L. CAMPEONES 11 SD", "url": "acestream://a12a16f74cf12799d4475ae867dc61eb60e1ba2e"},
    #{"name": "CHAMPIONS | M.L. CAMPEONES 12 SD", "url": "acestream://df7d145fcaf0566db4098d2f10236185d92bc9fd"},
    #{"name": "CHAMPIO#NS | M.L. CAMPEONES 13 SD", "url": "acestream://bdfe9ebe62d690c1b13eef4346d72e618cfbe804"},
    {"name": "GOLF | M. GOLF 1080", "url": "acestream://76a69812c66bfc4899e89df498220588a56e6064"},
    #{"name": "GOLF | M. GOLF2 1080", "url": "acestream://e258e75e0e802afa5fcc53d46b47d8801a254ad5"},
    {"name": "DAZN 1 1080", "url": "acestream://eb6ffec065b26259ad3d1811e0bbb0a5332ed276"},
    #{"name": "DAZN 1 720", "url": "acestream://35c7f0c966ecde3390f4510bb4caded40018c07a"},
    {"name": "DAZN 2 1080", "url": "acestream://ae68a0835039fab28fd2314108fabd4fab33b8ab"},
    {"name": "DAZN 2 720", "url": "acestream://a929eeec1268d69d1556a2e3ace793b2577d8810"},
    {"name": "DAZN 3 1080", "url": "acestream://19cd05c7ae26f22737ae5728b571ca36abd8a2e8"},

    {"name": "DAZN 4 1080", "url": "acestream://4e83f23945ab3e43982045f88ec31daaa4683102"},
    {"name": "DEPORTES | EUROSPORT 1 1080", "url": "acestream://c3da6c4f91d9d10ade00318a869435e19f204d0e"},
    {"name": "DEPORTES | EUROSPORT 1 720", "url": "acestream://d830c1dc3b74e74f79cbb823804cf2037857e78a"},
    {"name": "DEPORTES | EUROSPORT 2 1080", "url": "acestream://0585e09bb8ac9720e4c11934f1b184e309291551"},
    {"name": "DEPORTES | EUROSPORT 2 720", "url": "acestream://5c910d614894635153a7d42de98cc2e4a958a53f"},
    {"name": "DEPORTES | REAL MADRID TV 1080", "url": "acestream://0ec3f3786318acd8dca2588f74c3759cda76cd11"},
    {"name": "DEPORTES | REAL MADRID TV 720", "url": "acestream://0827cf7d290967985892965c6e61244a479d6dcd"},
    {"name": "DEPORTES | WIMBLEDON UHD", "url": "acestream://78aa81aedb1e2b6a9ba178398148940857155f6a"},
    {"name": "DEPORTES | MUNDO TORO HD", "url": "acestream://f763ab71f6f646e6c993f37e237be97baf2143ef"},
    {"name": "DEPORTES | RED BULL TV", "url": "acestream://6994af284ecab2996f9b140ef44b8da8bfee0006"},
    {"name": "DEPORTES | UFC CHANNEL", "url": "acestream://7cf437be950f3525e735be57c63f7824cab822c9"},
    {"name": "DEPORTES | FOX SPORTS 2", "url": "acestream://ad6f4e8e329d6a97c7e7d7b0b8e5d04d8dd0bb48"},
    {"name": "BALONCESTO | NBA", "url": "acestream://e72d03fb9694164317260f684470be9ab781ed95"},
    {"name": "BALONCESTO | NBA USA 1", "url": "acestream://39db49bc89dcc3c8797566231f869dca57f1a47e"},
    {"name": "BALONCESTO | NBA USA 2", "url": "acestream://f1c84ec8ea0c0bfff8a24272b66c64354a522110"},
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
    url = "https://ciriaco-liart.vercel.app/"
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
                hora = columnas[0].text.strip()
                categoria = columnas[1].text.strip()
                equipo_1 = columnas[2].text.strip()
                equipo_2 = columnas[3].text.strip()
                enlaces = [{"name": enlace.text.strip(), "url": enlace['href']} for enlace in columnas[4].find_all('a')]
                if enlaces:
                    eventos.append({
                        'hora': hora,
                        'categoria': categoria,
                        'evento': f"{equipo_1} vs {equipo_2}",
                        'enlaces': enlaces
                        })
        return eventos
    
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().notification("Error", f"Error al obtener eventos: {e}", xbmcgui.NOTIFICATION_ERROR)
        return []

def list_agenda_events():
    eventos = obtener_eventos_desde_html()
    if not eventos:
        xbmcgui.Dialog().notification("Agenda", "No hay eventos disponibles", xbmcgui.NOTIFICATION_INFO)
        return
    for evento in eventos:
        titulo = f"{evento['hora']} | {evento['categoria']} | {evento['evento']}"
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