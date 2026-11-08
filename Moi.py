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
            {"name": "F1 | DAZN F1 1080 | OPCION 2", "url": "acestream://2c6e4c897661e6b0257bfe931b66d20b2ec763b6"},
            {"name": "F1 | DAZN F1 1080 | OPCION 3", "url": "acestream://71eef80158aa8b37f3dc59f6793c6696df9a2dfa"},
            {"name": "F1 | DAZN F1 720", "url": "acestream://268289e7a3c5209960b53b4d43c8c65fab294b85"},
            {"name": "FÚTBOL | M. LA LIGA 1080", "url": "acestream://94d34491106e00394835c8cb68aa94481339b53f"},
            {"name": "FÚTBOL | M. LA LIGA 1080 | OPCION 2", "url": "acestream://d3de78aebe544611a2347f54d5796bd87f16c92d"},
            {"name": "FÚTBOL | M. LA LIGA 1080 | OPCION 3", "url": "acestream://6d05b31e5e8fdae312fbd57897363a7b10ddb163"},
            {"name": "FÚTBOL | M. LA LIGA 720", "url": "acestream://1bc437bce57b4b0450f6d1f8d818b7e97000745e"},
            {"name": "FÚTBOL | M. LA LIGA 2 1080", "url": "acestream://83c6c4942d69f4aa324aa746c5d7dbfd7d1572b3"},
            {"name": "FÚTBOL | M. LA LIGA 2 720", "url": "acestream://f31a586422c9244196c810c84b6c85da350318a5"},
            {"name": "FÚTBOL | M. LA LIGA 3 1080", "url": "acestream://ebe14f1edeb49f2253e3b355a8beeadc9b4f0bc4"},
            {"name": "FÚTBOL | LA LIGA BAR 1080", "url": "acestream://608b0faf7d3d25f6fe5dba13d5e4b4142949990e"},
            {"name": "FÚTBOL | LA LIGA BAR 1080 | OPCION 2", "url": "acestream://94d34491106e00394835c8cb68aa94481339b53f"},
            {"name": "FÚTBOL | DAZN LaLiga 1080", "url": "acestream://110d441ddc9713a7452588770d2bc85504672f47"},
            {"name": "FÚTBOL | DAZN LaLiga 1080 | OPCION 2", "url": "acestream://ec29289b0b14756e686c03a501bae1efa05be70c"},
            {"name": "FÚTBOL | DAZN LaLiga 1080 | OPCION 3", "url": "acestream://6de4794cd02f88f14354b5996823413a59a1de0f"},
            {"name": "FÚTBOL | DAZN LaLiga 720", "url": "acestream://8c8c1e047a1c5ed213ba74722a5345dc55c3c0eb"},
            {"name": "FÚTBOL | DAZN LaLiga 2 1080", "url": "acestream://97ba38d47680954be40e48bd8f43e17222fefecb"},
            {"name": "FÚTBOL | DAZN LaLiga 2 720", "url": "acestream://51dbbfb42f8091e4ea7a2186b566a40e780953d9"},
            {"name": "FÚTBOL | LaLiga Smartbank 1080", "url": "acestream://b2706a7ffbea236a3b398139a3a606ada664c0eb"},
            {"name": "FÚTBOL | LaLiga Smartbank 720", "url": "acestream://121f719ebb94193c6086ef92865cf9b197750980"},
            {"name": "FÚTBOL | LaLiga Smartbank 2 1080", "url": "acestream://0cfdfde1b70623b8c210b0f7301be2a87456481d"},
            {"name": "FÚTBOL | LaLiga Smartbank 2 720", "url": "acestream://0a335406bad0b658aeddb2d38f8c0614b2e5623a"},
            {"name": "FÚTBOL | LaLiga Smartbank 3", "url": "acestream://fefd45ed6ff415e05f1341b7d9da2988eacd13ea"},
            {"name": "DEPORTES | M.Plus 1080", "url": "acestream://56ac8e227d526e722624675ccdd91b0cc850582f"},
            {"name": "FÚTBOL | Copa 1080", "url": "acestream://f6beccbc4eea4bc0cda43b3e8ac14790a98b61b4"},
            {"name": "FÚTBOL | Copa 720", "url": "acestream://b51f2d9a15b6956a44385b6be531bcabeb099d9d"},
            {"name": "DEPORTES | #VAMOS 1080", "url": "acestream://d03c13b6723f66155d7a0df3692a3b073fe630f2"},
            {"name": "DEPORTES| #VAMOS 720", "url": "acestream://12ba546d229bc39f01c3c18988a034b215fe6adb"},
            {"name": "FÚTBOL | #ELLAS 1080", "url": "acestream://d8c2ed470e847154a88f011137cc206319f6bed5"},
            {"name": "DEPORTES | M. DEPORTES 1080", "url": "acestream://55d4602cb22b0d8a33c10c2c2f42dae64a9e8895"},
            {"name": "DEPORTES | M. DEPORTES 720", "url": "acestream://3a74d9869b13e763476800740c6625e715a39879"},
            {"name": "DEPORTES | M. DEPORTES 2 1080", "url": "acestream://639c561dd57fa3fc91fde715caeb696c5efb7ce7"},
            {"name": "DEPORTES | M. DEPORTES 3 1080", "url": "acestream://571bff4d12b1791eb99dbf20bec38e630693a6a3"},
            {"name": "DEPORTES | M. DEPORTES 4 1080", "url": "acestream://b4d1308a61e4caf8c06ac3d6ce89d165c015c2fb"},
            {"name": "DEPORTES | M. DEPORTES 5 1080", "url": "acestream://fcc0fd75bf1dba40b108fcf0d3514e0e549bfbac"},
            {"name": "DEPORTES | M. DEPORTES 6 1080", "url": "acestream://cc5782d37ae6b6e0bab396dd64074982d0879046"},
            {"name": "DEPORTES | M. DEPORTES 7 1080", "url": "acestream://070f82d6443a52962d6a2ed9954c979b29404932"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 1080 MULTIAUDIO", "url": "acestream://0a26e20f39845e928411e09a124374fccb6e1478"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 1080 MULTIAUDIO", "url": "acestream://775abd8697715c48a357906d40734ccd2a10513c"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 720", "url": "acestream://8edb264520569b2280c5e86b2dc734e120032903"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 2 1080", "url": "acestream://c070cdb701fc46bb79d17568d99fc64620443d63"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 2 720", "url": "acestream://abdf9058786a48623d0de51a3adb414ae10b6e72"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 3 1080", "url": "acestream://3618edda333dad5374ac2c801f5f14483934b97d"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 3 720", "url": "acestream://0b348cc1ae499e810729661878764a0fab88ab69"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 4 1080", "url": "acestream://65a18a6bd83918a9586b673fec12405aaf4e9f7d"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 5 1080", "url": "acestream://11744c25a594e17d587ed0871fe40ff21b4bd1e0"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 6 1080", "url": "acestream://fdda1f0dd8c33fbdc5a66ab98e291f570cae67cd"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 7 1080", "url": "acestream://b7f47db93dced60f54e8f89e2366ed061b534049"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 8 1080", "url": "acestream://d298c6e5c8be71f5995b45289c6388b225318b3c"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 9 SD", "url": "acestream://2d7c4cfb3987b652a779afc894cca2fccbbacf21"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 10 SD", "url": "acestream://c056f9e180cd7d40963129a17ff54f4ee8259353"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 11 SD", "url": "acestream://a12a16f74cf12799d4475ae867dc61eb60e1ba2e"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 12 SD", "url": "acestream://df7d145fcaf0566db4098d2f10236185d92bc9fd"},
            {"name": "CHAMPIONS | M.L. CAMPEONES 13 SD", "url": "acestream://bdfe9ebe62d690c1b13eef4346d72e618cfbe804"},
            {"name": "GOLF | M. GOLF 1080", "url": "acestream://f41f1096862767289620be5bd85727f946a434db"},
            {"name": "GOLF | M. GOLF2 1080", "url": "acestream://e258e75e0e802afa5fcc53d46b47d8801a254ad5"},
            {"name": "DAZN 1 1080", "url": "acestream://7cf0086fa7d478f51dbba952865c79e66cb9add5"},
            {"name": "DAZN 1 720", "url": "acestream://35c7f0c966ecde3390f4510bb4caded40018c07a"},
            {"name": "DAZN 2 1080", "url": "acestream://ca923c9873fd206a41c1e83ff8fc40e3cf323c9a"},
            {"name": "DAZN 2 720", "url": "acestream://a929eeec1268d69d1556a2e3ace793b2577d8810"},
            {"name": "DAZN 3 1080", "url": "acestream://19cd05c7ae26f22737ae5728b571ca36abd8a2e8"},
            {"name": "DAZN 4 1080", "url": "acestream://4e83f23945ab3e43982045f88ec31daaa4683102"},
            {"name": "DEPORTES | EUROSPORT 1 1080", "url": "acestream://16ffa1713f42aa27317ee039a2bd0cdbc89a1580"},
            {"name": "DEPORTES | EUROSPORT 2 1080", "url": "acestream://98784fa0714190de289f42eb5b84e405df7e685a"},
            {"name": "DEPORTES | REAL MADRID TV 1080", "url": "acestream://0ec3f3786318acd8dca2588f74c3759cda76cd11"},
            {"name": "DEPORTES | REAL MADRID TV 720", "url": "acestream://0827cf7d290967985892965c6e61244a479d6dcd"},
            {"name": "DEPORTES | WIMBLEDON UHD", "url": "acestream://78aa81aedb1e2b6a9ba178398148940857155f6a"},
            {"name": "DEPORTES | MUNDO TORO HD", "url": "acestream://f763ab71f6f646e6c993f37e237be97baf2143ef"},
            {"name": "BALONCESTO | NBA", "url": "acestream://e72d03fb9694164317260f684470be9ab781ed95"},
            {"name": "BALONCESTO | NBA USA 1", "url": "acestream://39db49bc89dcc3c8797566231f869dca57f1a47e"},
            {"name": "BALONCESTO | NBA USA 2", "url": "acestream://f1c84ec8ea0c0bfff8a24272b66c64354a522110"},
            {"name": "DEPORTES | RED BULL TV", "url": "acestream://6994af284ecab2996f9b140ef44b8da8bfee0006"},
            {"name": "DEPORTES | UFC CHANNEL", "url": "acestream://7cf437be950f3525e735be57c63f7824cab822c9"},
            {"name": "DEPORTES | FOX SPORTS 2", "url": "acestream://ad6f4e8e329d6a97c7e7d7b0b8e5d04d8dd0bb48"},
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