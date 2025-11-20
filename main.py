from nicegui import ui
from navigation.menu import Navigation
import asyncio
from pages.about import About
from pages.geo import Geo
from pages.ai import AI
# (Assuming stac import is valid or placeholder)
# from stac.bevcatalog import create_stac_from_geotiff_url as create_stac_catalog


menu= Navigation()

@ui.page('/')
def start():
    menu.create_nav()    
    with ui.row().classes('items-center w-full justify-center h-screen flex flex-col items-center justify-center   '):
        ui.label('CIO GATE').classes('text-9xl').style('background-image: linear-gradient(to right, #007bff, #6f42c1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;')
      
        
@ui.page('/maps')
def maps():
    geo = Geo()
    geo.create_geo()


@ui.page('/about')
def about():
    about = About()
    about.create_about()
@ui.page('/ai')
def ai():
    ai = AI()
    ai.create_ai()
    


ui.run(title='CIO GATE' , fastapi_docs=True , native=False)
