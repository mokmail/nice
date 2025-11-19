from nicegui import ui

class Navigation:
    
    def create_nav(self):
        with ui.fab('navigation' ,label= 'Navigation' , direction='up' , color='teal' ).classes('fixed bottom-4 right-4') as nav:   
            ui.fab_action('home' , label='Home' , color='teal' , on_click=lambda: ui.navigate.to('/'))
            ui.fab_action('map' , label='GEOSPATIAL' , color='red' , on_click=lambda: ui.navigate.to('/maps') )
            ui.fab_action('info' , label='Info' , color='blue' , on_click=lambda: ui.notify('The information page is not yet implemented' , color='red' )   )
            ui.fab_action('style' , label='About CIO' , color='orange' , on_click=lambda: ui.navigate.to('/about') )
            ui.fab_action('style' , label='PMO' , color='green' , on_click=lambda: ui.notify('The PMO page is not yet implemented' , color='green' ) )
            ui.fab_action('auto_awesome' , label='Art. Intelligence' , color='pink' , on_click=lambda: ui.notify('The AI page is not yet implemented' , color='green' ) )
         


