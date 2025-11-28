import os
from nicegui import ui
import pystac
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
import datetime

class StacViewer:
    def __init__(self):
        self.map = None
        self.catalog_path_input = None
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

    def get_stac_items_static(self, path):
        """
        Parses a local or remote STAC Catalog/Collection and returns all items.
        """
        try:
            # Load the catalog/collection
            catalog = pystac.read_file(path)
            
            ui.notify(f"Reading catalog: {catalog.id}...", type='info')
            
            # Pystac 1.0+ helper to get all items recursively
            # This works for both Catalogs and Collections
            items = list(catalog.get_all_items())
            return items
        except Exception as e:
            ui.notify(f"Error loading STAC: {str(e)}", type='negative')
            print(f"Error: {e}")
            return []

    def load_demo_data(self):
        """
        Generates a dummy STAC Item for demonstration purposes.
        """
        geom = {
            "type": "Polygon",
            "coordinates": [[
                [16.30, 48.15],
                [16.45, 48.15],
                [16.45, 48.25],
                [16.30, 48.25],
                [16.30, 48.15]
            ]]
        }
        
        item = pystac.Item(
            id="demo_item_vienna",
            geometry=geom,
            bbox=[16.30, 48.15, 16.45, 48.25],
            datetime=datetime.datetime.now(),
            properties={"title": "Demo Area"}
        )
        
        self.render_items([item])
        ui.notify("Loaded demo data")

    def load_map_data(self):
        """
        Triggered by the UI button to load from the input path.
        """
        stac_path = self.catalog_path_input.value
        
        if not stac_path:
            ui.notify("Please enter a valid path or URL", type='warning')
            return

        items = self.get_stac_items_static(stac_path)
        
        if not items:
            ui.notify("No items found or path is invalid.", type='warning')
            return

        self.render_items(items)

    def render_items(self, items):
        """
        Logic to draw items on the map and fit bounds.
        """
        # Clear existing layers
        self.map.clear_layers()
        self.map.tile_layer(
            url_template=r'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        )

        geometries = []
        features = []

        for item in items:
            if not item.geometry:
                continue
                
            # Collect geometry for bounds
            geometries.append(shape(item.geometry))
            # Collect feature for the map layer
            features.append(item.to_dict())

        if not features:
            ui.notify("No items with geometry found.", type='warning')
            return

        # 1. Create FeatureCollection
        feature_collection = {
            "type": "FeatureCollection",
            "features": features
        }

        # 2. Add GeoJSON Layer (The detailed polygons)
        # We pass simple style options directly.
        self.map.generic_layer(name='GeoJSON', args=[
            feature_collection, 
            {'style': {'color': 'blue', 'weight': 2}}
        ])

        ui.notify(f'Loaded {len(features)} items onto the map.')

        # 3. Calculate Bounds and Zoom
        if geometries:
            combined_geom = unary_union(geometries)
            minx, miny, maxx, maxy = combined_geom.bounds
            
            # Leaflet bounds are [[lat1, lon1], [lat2, lon2]]
            # shapely bounds are (minx/lon, miny/lat, maxx/lon, maxy/lat)
            south_west = [miny, minx]
            north_east = [maxy, maxx]
            bounds = [south_west, north_east]

            # 4. Debug Layer: Draw a simple Rectangle around the bounds
            # If the GeoJSON fails to render, this RED BOX will definitively show up
            # allowing us to verify the camera location is correct.
            self.map.generic_layer(name='Rectangle', args=[
                bounds,
                {'color': 'red', 'weight': 1, 'fill': False, 'dashArray': '5, 5'}
            ])
            
            # Fit the map view to these bounds
            self.map.run_map_method('fitBounds', bounds)
            
            ui.notify(f"Zoomed to bounds: {bounds}")

    def stac_viewer_frontend(self):
        with ui.column().classes('w-full items-center gap-4 p-4'):
            ui.label('STAC Catalog Viewer').classes('text-h4 font-bold text-slate-700')

            with ui.row().classes('w-full max-w-4xl gap-2'):
                self.catalog_path_input = ui.input(
                    'STAC Catalog Path (File or URL)', 
                    value='../fastme/stac_catalog/catalog.json'
                ).classes('w-full flex-grow')
                
                ui.button(icon='folder_open', on_click=self.load_map_data).props('flat round')

            with ui.row():
                ui.button('Load from Path', on_click=self.load_map_data)
                ui.button('Load Demo Data', on_click=self.load_demo_data).props('outline')

            # Map component
            # Changed h-[600px] to explicit style to ensure height is respected
            self.map = ui.leaflet(center=(48.2081, 16.3713), zoom=8) \
                .classes('w-full shadow-lg rounded-lg') \
                .style('height: 600px')
    def stac_viewer_maplibre(self):
        with ui.column().classes('w-full items-center gap-4 p-4'):
            ui.label('STAC Catalog Viewer').classes('text-h4 font-bold text-slate-700')

            with ui.row().classes('w-full max-w-4xl gap-2'):
                self.catalog_path_input = ui.input(
                    'STAC Catalog Path (File or URL)', 
                    value='../fastme/stac_catalog/catalog.json'
                ).classes('w-full flex-grow')
                
                ui.button(icon='folder_open', on_click=self.load_map_data).props('flat round')

            with ui.row():
                ui.button('Load from Path', on_click=self.load_map_data)
                ui.button('Load Demo Data', on_click=self.load_demo_data).props('outline')

            # Map component
            # Changed h-[600px] to explicit style to ensure height is respected
            self.map = self.init_map(
                style=        {'name':'Dark', 'value':'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json' , 'description':'Dark background map'},
                
                zoom=8,
                
            )
# Instantiate and run
