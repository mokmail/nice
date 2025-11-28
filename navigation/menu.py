from nicegui import ui

class Navigation:
    
    def create_nav(self):
        with ui.fab('navigation' ,label= 'Navigation' , direction='up' , color='teal' ).classes('fixed bottom-4 right-8 w-48 ') as nav:   
            ui.fab_action('home' , label='Home' , color='teal' , on_click=lambda: ui.navigate.to('/')).classes('w-48 h-12 ')
            ui.fab_action('map' , label='GEOSPATIAL' , color='red' , on_click=lambda: ui.navigate.to('/maps') ).classes('w-48 h-12 ')
            ui.fab_action('info' , label='Info' , color='blue' , on_click=lambda: ui.notify('The information page is not yet implemented' , color='red' )   ).classes('w-48 h-12 ')
            ui.fab_action('style' , label='About CIO' , color='orange' , on_click=lambda: ui.navigate.to('/about') ).classes('w-48 h-12 ')
            ui.fab_action('style' , label='PMO' , color='green' , on_click=lambda: ui.notify('The PMO page is not yet implemented' , color='green' ) ).classes('w-48 h-12 ')
            ui.fab_action('auto_awesome' , label='Art. Intelligence' , color='pink' , on_click=lambda: ui.navigate.to('/ai') ).classes('w-48 h-12 ')
         


