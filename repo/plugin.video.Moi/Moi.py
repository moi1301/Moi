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

class DependencyManager:
    """Clase encargada de gestionar las descargas e instalación de librerías externas."""
    def __init__(self, addon_path):
        self.libraries_zip_url = "https://moi1301.github.io/Moi/bibliotecas.zip"
        self.libraries_zip_path = os.path.join(addon_path, 'bibliotecas.zip')
        self.libraries_path = os.path.join(addon_path, 'lib')
        self.first_run_file = os.path.join(addon_path, "first_run.txt")

    def _check_and_install_libraries(self):
        """Descarga y extrae el archivo zip de librerías si la carpeta 'lib' no existe."""
        if not os.path.exists(self.libraries_path):
            xbmcgui.Dialog().notification("Instalando bibliotecas", "Descargando bibliotecas necesarias...", xbmcgui.NOTIFICATION_INFO)
            try:
                urllib.request.urlretrieve(self.libraries_zip_url, self.libraries_zip_path)
                with zipfile.ZipFile(self.libraries_zip_path, "r") as zip_ref:
                    zip_ref.extractall(self.libraries_path)
                os.remove(self.libraries_zip_path)
                xbmcgui.Dialog().notification("Addon", "Bibliotecas instaladas correctamente", xbmcgui.NOTIFICATION_INFO)
            except Exception as e:
                xbmcgui.Dialog().notification("Error", f"Error al instalar las bibliotecas: {str(e)}", xbmcgui.NOTIFICATION_ERROR)
                sys.exit()

    def verificar_primer_inicio(self):
        """Valida si es la primera ejecución y añade la ruta de librerías al sys.path."""
        if not os.path.exists(self.first_run_file):
            self._check_and_install_libraries()
            with open(self.first_run_file, "w") as f:
                f.write("Primer inicio completado")
        
        # Insertar siempre el directorio 'lib' en el path del sistema
        sys.path.insert(0, self.libraries_path)


class KodiSportsAddon:
    """Clase principal que controla la interfaz de usuario, navegación y lógica del Addon."""
    def __init__(self):
        # Variables de entorno de Kodi
        self.addon_handle = int(sys.argv[1])
        self.base_url = sys.argv[0]
        self.addon = xbmcaddon.Addon()
        self.addon_path = self.addon.getAddonInfo('path')
        self.resources_path = os.path.join(self.addon_path, 'resources')
        
        # Colecciones de datos
        self.categories = self._inicializar_categorias()
        self.acestream_channels = self._inicializar_canales_acestream()
        self.html5_channels = []  # Mantenido según estructura original

    def _inicializar_categorias(self):
        return [
            {"name": "AGENDA", "subcategories": [], "icon": f"{self.resources_path}/agenda.png"},
            {"name": "DEPORTES", "subcategories": [], "icon": f"{self.resources_path}/deportes.png"},
            {"name": "FÚTBOL", "subcategories": [], "icon": f"{self.resources_path}/futbol.png"},
            {"name": "CHAMPIONS", "subcategories": [], "icon": f"{self.resources_path}/champions.png"},
            {"name": "GOLF", "subcategories": [], "icon": f"{self.resources_path}/golf.png"},
            {"name": "DAZN", "subcategories": [], "icon": f"{self.resources_path}/dazn.png"},
            {"name": "F1", "subcategories": [], "icon": f"{self.resources_path}/f1.png"},
            {"name": "BALONCESTO", "subcategories": [], "icon": f"{self.resources_path}/baloncesto.png"},
        ]

    def _inicializar_canales_acestream(self):
        return [
            {"name": "F1 | DAZN F1 1080", "url": "acestream://d6281d4e6310269b416180442a470d23a4a99dc9"},
            # Agrega más canales AceStream según sea necesario
        ]

    def build_url(self, query):
        """Genera URLs internas para el enrutamiento de Kodi."""
        return self.base_url + '?' + urlencode(query)

    def buscar_enlace_por_nombre(self, nombre):
        """Busca una coincidencia de canal AceStream."""
        nombre_min = nombre.lower()
        for canal in self.acestream_channels:
            if nombre_min in canal["name"].lower():
                return canal["url"]
        return None

    def list_categories(self):
        """Muestra el menú de categorías raíz en la interfaz."""
        for category in self.categories:
            list_item = xbmcgui.ListItem(label=category["name"])
            list_item.setArt({"icon": category["icon"]})
            url = self.build_url({"action": "list_channels", "category": category["name"]})
            xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=list_item, isFolder=True)
        xbmcplugin.endOfDirectory(self.addon_handle)

    def list_channels(self, category):
        """Filtra y muestra los canales estáticos que correspondan a la categoría."""
        selected_category = next((cat for cat in self.categories if cat["name"] == category), None)
        if not selected_category:
            xbmcgui.Dialog().notification("Error", "Categoría no encontrada", xbmcgui.NOTIFICATION_ERROR)
            return

        if category == "AGENDA":
            self.list_agenda_events()
            return

        for channel in self.acestream_channels:
            if channel["name"].upper().startswith(category.upper()):
                list_item = xbmcgui.ListItem(label=channel["name"])
                url = self.build_url({"action": "play_acestream", "url": channel["url"]})
                list_item.setInfo("video", {"title": channel["name"]})
                xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=list_item, isFolder=False)
        xbmcplugin.endOfDirectory(self.addon_handle)

    def obtener_eventos_desde_html(self):
        """Hace scraping a la web externa para parsear los eventos deportivos."""
        url = "http://mistreamt.duckdns.org:8091/eventos/"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        headers = {"User-Agent": user_agent}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            eventos = []
            tabla_eventos = soup.find('body')
            
            if not tabla_eventos:
                return []

            for fila in tabla_eventos.find_all('tr')[1:]:
                columnas = fila.find_all('td')
                if len(columnas) >= 4:
                    hora = columnas[1].text.strip()
                    categoria = columnas[2].text.strip()
                    equipo_1 = columnas[3].text.strip()
                    equipo_2 = columnas[4].text.strip()
                    enlaces = [{"name": enlace.text.strip(), "url": enlace['href']} for enlace in columnas[5].find_all('a')]
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

    def list_agenda_events(self):
        """Muestra la lista de eventos raspados de la Agenda."""
        eventos = self.obtener_eventos_desde_html()
        if not eventos:
            xbmcgui.Dialog().notification("Agenda", "No hay eventos disponibles", xbmcgui.NOTIFICATION_INFO)
            return
        for evento in eventos:
            titulo = f"{evento['hora']} | {evento['categoria']} | {evento['evento']}"
            list_item = xbmcgui.ListItem(label=titulo)
            url = self.build_url({"action": "mostrar_enlaces_evento", "enlaces": json.dumps(evento["enlaces"])})
            xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=list_item, isFolder=True)
        xbmcplugin.endOfDirectory(self.addon_handle)

    def mostrar_enlaces_evento(self, enlaces_json):
        """Desglosa y genera los enlaces de reproducción asignados a un evento específico."""
        enlaces = json.loads(enlaces_json)
        for enlace in enlaces:
            list_item = xbmcgui.ListItem(label=enlace["name"])
            url = self.build_url({"action": "play_acestream", "url": enlace["url"]})
            xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=list_item, isFolder=False)
        xbmcplugin.endOfDirectory(self.addon_handle)

    def play_html5(self, url):
        """Reproduce flujos HTML5 nativos."""
        try:
            xbmc.Player().play(url)
        except Exception as e:
            xbmcgui.Dialog().notification("Error", str(e), xbmcgui.NOTIFICATION_ERROR)

    def play_acestream(self, url):
        """Pasa el ID de AceStream de forma controlada hacia el addon de Horus."""
        try:
            acestream_id = url.replace("acestream://", "")
            horus_url = f"plugin://script.module.horus/?action=play&id={acestream_id}"
            xbmc.Player().play(horus_url)
        except Exception as e:
            xbmcgui.Dialog().notification("Error", f"Error al reproducir: {e}", xbmcgui.NOTIFICATION_ERROR)

    def run(self):
        """Enrutador de acciones primarias basándose en los argumentos de Kodi."""
        args = dict(parse_qsl(sys.argv[2][1:]))
        action = args.get("action")

        if action == "list_channels":
            category = args.get("category")
            if category == "AGENDA":
                self.list_agenda_events()
            else:
                self.list_channels(category)
        elif action == "mostrar_enlaces_evento":
            self.mostrar_enlaces_evento(args["enlaces"])
        elif action == "play_html5":
            self.play_html5(args["url"])
        elif action == "play_acestream":
            self.play_acestream(args["url"])
        else:
            self.list_categories()


if __name__ == '__main__':
    # 1. Obtener ruta base del addon para instanciar el gestor
    addon_base_path = xbmcaddon.Addon().getAddonInfo('path')
    
    # 2. Comprobar e instalar librerías comprimidas en el primer inicio
    manager = DependencyManager(addon_base_path)
    manager.verificar_primer_inicio()

    # 3. Intentar importación de librerías inyectadas de manera segura
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as error:
        xbmcgui.Dialog().notification("Error", f"No se pudieron importar los módulos: {error}", xbmcgui.NOTIFICATION_ERROR)
        sys.exit()

    # 4. Iniciar la aplicación orientada a objetos
    addon_instance = KodiSportsAddon()
    addon_instance.run()