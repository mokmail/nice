from nicegui import ui
from navigation.menu import Navigation

menu= Navigation()


class AI:
    def create_ai(self):
        menu.create_nav()
        with ui.row().classes('w-full h-full margin-0 items-center justify-center flex flex-col items-center justify-center  margin-auto'):
            ui.label('AI Page').classes('flex text-9xl font-thin p-24') 
            ui.separator()
            ui.markdown('### AI functions will be added soon')
            with ui.row().classes('w-full h-full margin-0 items-center justify-center flex  items-center justify-center  margin-auto'):
                ui.button('chatbot', on_click=lambda: ui.notify('We are working on it'))
                ui.button('Rag', on_click=lambda: ui.notify('We are working on it'))
                
