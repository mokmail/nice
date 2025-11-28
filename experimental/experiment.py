from nicegui import ui
import json 
import requests
import time
from ollama import chat
from ollama import ChatResponse
import asyncio
from stac.bevcatalog import Bevstac
import os

import rasterio
import io



class Experiment:
    def __init__(self):
        self.response = ''
        self.output_label = ui.markdown()
    

        with  ui.expansion('Response', icon='info' , value = True).classes('overflow-y-auto w-full h-6/12 margin-0 p-4 '):
            self.output_label = ui.markdown('Response comes here').classes('w-full h-124')

    async def ask_AI(self, prompt):
        self.response = ''
        response = chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in response:  # normal generator
            if hasattr(chunk, 'message') and chunk.message and chunk.message.content:
                self.response += chunk.message.content
                self.output_label.set_content(self.response)
                await asyncio.sleep(0)  # yield control to event loop

    async def handle_upload(self, e):
        with ui.dialog() as dialog:
            
            if e.file.content_type == 'image/tiff':
                await e.file.save(os.path.join('temp' , e.file.name))
                bevstac = Bevstac(filename=e.file.name, geotiff_url=os.path.join('temp' , e.file.name))
            

 
                
                
                result = bevstac.create_stac_from_geotiff_url()
                ui.json_editor({"content":{"json": result[0].to_dict()}}).classes('w-full h-96 margin-auto p-4 border-2 border-blue-500 bg-blue-200')
                ui.json_editor({"content":{"json": result[1].to_dict()}}).classes('w-full h-96 margin-auto p-4 border-2 border-blue-500 bg-blue-200')
                ui.json_editor({"content":{"json": result[2].to_dict()}}).classes('w-full h-96 margin-auto p-4 border-2 border-blue-500 bg-blue-200')
                dialog.open()
            
            else:
                ui.notify('Please upload a GeoTIFF file')
                dialog.open()
    
    def create_ui(self) -> None:
        with ui.row().classes('flex gap-2  w-full h-96 margin-0 p-4 items-center justify-center'):
            geotiff = ui.upload(on_upload=lambda e : self.handle_upload(e) , label='Upload GeoTIFF').classes('w-2/12 h-48 shadow-xl border-1 border-blue-50')
            geotiff.props('accept="image/tiff"')
            prompt_text = ui.textarea('Please type your prompt here').classes('h-48 w-9/12 items-center justify-center margin-0 shadow-xl  border-1 border-blue-50 p-4')
        
                
            
            
            ui.button('Submit', on_click=lambda: asyncio.create_task(self.ask_AI(prompt_text.value))).classes('w-full') 
