from navigation.menu import Navigation
from nicegui import ui

menu= Navigation()

class About:
    def create_about(self):
        with ui.row().classes('items-center w-full justify-center h-screen flex flex-col items-center justify-center   '):
            ui.label('CIO GATE').classes('text-9xl').style('background-image: linear-gradient(to right, red, purple); -webkit-background-clip: text; -webkit-text-fill-color: transparent;')
            with     ui.row().classes("w-1/4 items-center justify-center flex  items-center justify-center "):
                ui.chip('AI', color='red', icon='auto_awesome').classes('m-2 text-white text-xl')
                ui.chip('Strategies', color='blue', icon='switch_access_shortcut').classes('m-2 text-white text-xl')
                ui.chip('Data', color='green', icon='dataset').classes('m-2 text-white text-xl')
                ui.chip('Knowledge', color='orange', icon='auto_stories').classes('m-2 text-white text-xl')
                ui.chip('IT', color='purple', icon='terminal').classes('m-2 text-white text-xl')
                ui.chip('Security', color='purple', icon='security').classes('m-2 text-white text-xl')
                ui.chip('Governance', color='green', icon='local_police').classes('m-2 text-white text-xl') 
                ui.chip('ESP', color='pink', icon='api').classes('m-2 text-white text-xl')   

                
               

        menu.create_nav()