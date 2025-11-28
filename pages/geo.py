
from navigation.menu import Navigation
from nicegui import ui
import asyncio
from stac.bevcatalog import Bevstac
import pystac_client
import pystac
from shapely.geometry import shape
from stac.stacviewer import StacViewer

menu= Navigation()



class Geo:
    def __init__(self):
        self.catalog  = None
        self.collection = None

        
    
        self.map_styles = [
        {'name':'Dark', 'value':'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json' , 'description':'Dark background map'},
        {'name':'Light', 'value':'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json', 'description':'Light background map'},
        {'name':'Voyager', 'value':'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json', 'description':'Voyager background map'},
        {'name':'Demo', 'value':'https://demotiles.maplibre.org/style.json', 'description':'Demo background map'},
    ]
    

    def create_geo(self) :
        with ui.tabs().classes('w-full h-full') as tabs:
            maps = ui.tab('Map' )
            info = ui.tab('Info')
            stac = ui.tab(' Stac')
        with ui.tab_panels(tabs , value=info ).classes('w-full h-full'):
            with ui.tab_panel(maps).classes('w-full h-full'):
                self.create_ui()    
            with ui.tab_panel(info).classes('w-full h-full'):
                self.info_panel()
                # this function will be implemented later 
            with ui.tab_panel(stac):
                with ui.expansion('Stac Viewer', icon='map' , value = True).classes('w-full '):
                    viewer = StacViewer()
                    viewer.stac_viewer_maplibre()
                with ui.expansion('Stac Genarator', icon='map' , value = True).classes('w-full '):
                    self.stac_generator_frontend()     
            
               
                
        menu.create_nav()
        # 1. Load MapLibre resources
        ui.add_head_html('<link href="https://unpkg.com/maplibre-gl/dist/maplibre-gl.css" rel="stylesheet" />')
        ui.add_head_html('<script src="https://unpkg.com/maplibre-gl/dist/maplibre-gl.js"></script>')
 

       
    # 3. Define the JS initialization logic
    
            
    async def init_map(self, style , zoom=8):
            #style = map_styles['Light']
            await ui.run_javascript(f'''
                    const map = new maplibregl.Map({{
                        container: 'map',
                        style: '{style['value']}',
                        center: [  16.3713 , 48.2081],
                        zoom: {zoom},
                        maxZoom: 18,
                        
                    }});

                    map.on('load', () => {{
                        map.addSource('dgm', {{
                            type: 'raster',
                            tiles: 'https://data.bev.gv.at/download/DGM/Hoehenraster/DGM_R500.tif',
                            tileSize: 512
                        }});
                        map.addLayer({{ 
                            id: 'dgm',
                            type: 'raster',
                            source: 'dgm',
                        
                            maxzoom: 18
                        }});
                    }}); 
                ''')

            # 4. Trigger the logic only after the UI is built and client connects
            # A timer of 0.1s ensures the DOM 'map' div exists before JS tries to find it
            
    def create_ui(self ):
        with ui.card().classes('w-full h-full margin-0'):
            
            image = ui.image('https://data.bev.gv.at/geonetwork/images/logos/fef865d2-c0d2-4c3c-bff9-884e60f1e975.png?random1763546621077')
            image.style('max-width: 200px; max-height: 200px;')
            ui.separator()
            # 2. Create the container
            ui.element('div').props('id="map" style="width: 100%; height:450px;"').classes('w-full h-full')

            with ui.dropdown_button('Select Style'  ).classes('w-full h-full'):
                with ui.row().classes('p-4 items-center w-full  '):  
                    slider =ui.slider( min=1 , max=18 , step=1 , value = 5 ).props('label-always').classes('p-12 ')          
                    for style in self.map_styles:    
                        with ui.card().classes('w-2/12 h-full items-center justify-center flex flex-col items-center justify-center '):
                            ui.label(style['description'])
                            ui.separator()
                            with ui.row().classes('p-4 items-center w-full')    :
                                    ui.chip(style['name'] , color='blue', icon='style')
                                    ui.chip('style' , color='red' , icon='style')
                                    ui.chip('information' , color='green' , removable=True , on_click=lambda: print('removed'))
                            ui.image('https://data.bev.gv.at/geonetwork/images/logos/fef865d2-c0d2-4c3c-bff9-884e60f1e975.png?random1763546621077')
                            ui.separator()
                        
            
                            ui.button(style['name'], on_click=lambda style=style: self.init_map(style , zoom=slider.value))
                                
    def info_panel(self):
        from experimental.experiment import Experiment
        ex = Experiment()
        ex.create_ui()
    
    def generate_stac(self , value):
        bevstac = Bevstac(collection_id='geotiff-collection33')
        try:
            result = bevstac.create_stac_from_geotiff_url(value)
            with ui.row().classes("w-full h-full") : 
                self.catalog = ui.json_editor({"content":{"json": result[0].to_dict()}} )
                self.collection = ui.json_editor({"content":{"json": result[1].to_dict()}})
                self.item = ui.json_editor({"content":{"json": result[2].to_dict()}})
        except Exception as e: 
            ui.notify(e)
  
        
    def stac_generator_frontend(self):

        with ui.card().classes('w-full h-fit margin-0'):
            ui.markdown('### Welcome to the STAC Generator')
            ui.markdown('Please enter the URL of the GeoTIFF file you want to convert to a STAC catalog')
            url = ui.input('URL').classes('w-full h-full')
          
            

            ui.button('Stac Generator', on_click=lambda: self.generate_stac(url.value) , color='green').classes('w-full')
    def get_stac_items_static(self , catalog_path_or_url):
    # Use pystac.Catalog.open() for static files/URLs, 
    # not pystac_client.Client.open() which expects an API.
        try:
            catalog = pystac.Catalog.from_file(catalog_path_or_url)
            # Iterate through all items recursively linked in the catalog
            items = list(catalog.get_all_items())
            return items
        except Exception as e:
            ui.notify(f"Error opening catalog: {e}", type='negative')
            return []


            
    

