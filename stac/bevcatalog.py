import pystac
import rasterio
from pystac import Catalog, Collection, Item, Link , MediaType  , Extent , SpatialExtent , TemporalExtent
from rasterio.io import MemoryFile
from rasterio.warp import transform_bounds # Required for coordinate transformation
from shapely.geometry import box, mapping
from datetime import datetime
from nicegui import ui
import os

class Bevstac:
    def __init__(self, geotiff_url: str,filename: str, catalog_id: str = "BevStacCatalog", collection_id: str = "BevStacCollection",  output_dir: str = "fastme/stac_catalog"):
        self.geotiff_url = geotiff_url
        self.catalog_id = catalog_id
        self.collection_id = collection_id
        self.output_dir = output_dir
        self.filename = filename
        self.current_collection_exists = False
        self.catalog_path = os.path.join(self.output_dir, "catalog.json")
        self.collection_path = os.path.join(self.output_dir, self.collection_id , f"{self.collection_id}.json")
        self.item_path = os.path.join(self.output_dir, self.collection_id , self.filename.split('.')[0] + ".json")
        self.asset_path = os.path.join(self.output_dir, self.collection_id , self.filename.split('.')[0] , "asset.json")

        self.catalog = self.check_if_catalog_exists(self.catalog_path)
        self.collection = self.check_if_collection_exists(self.collection_path)
        self.item = self.check_if_item_exists(self.item_path)
      
        
        
    def check_if_catalog_exists(self , catalog):   
        if os.path.exists(self.catalog_path):
            catalog = pystac.Catalog.from_file(self.catalog_path)
            #print('catalog already exists')
        else:
            catalog = pystac.Catalog(id=self.catalog_id, description="A STAC Catalog generated from a GeoTIFF URL.")
        return catalog
        
    def check_if_collection_exists(self , collection_path ):
            if os.path.exists(collection_path):
                collection = Collection.from_file(collection_path)
                #print('collection already exists')
             

            else:
                collection = Collection(id=self.collection_id,description="A collection of GeoTIFF items.",href=self.collection_path, 
            extent=Extent(
                spatial=SpatialExtent([[0,0,0,0]]),
                temporal=TemporalExtent([[datetime(1970, 1, 1), None]])
            ))
            #self.catalog.add_child(collection)
            return collection
    def check_if_item_exists(self , item_path):
            if os.path.exists(item_path):
                item = pystac.Item.from_file(item_path)
            else:
                with rasterio.open(self.geotiff_url) as src:
                    # --- FIX STARTS HERE ---

                    # 1. Identify Source CRS
                    # If the file has a CRS, use it. If not, assume the user's request of 31254.
                    source_crs = src.crs if src.crs else "EPSG:31254"

                    # 2. Reproject bounds to EPSG:4326 (WGS84) for the STAC Item Geometry
                    # STAC requires the main geometry to be in Lat/Lon
                    left, bottom, right, top = transform_bounds(source_crs, "EPSG:4326", *src.bounds)
                    bbox_4326 = [left, bottom, right, top]
                    geometry_4326 = box(left, bottom, right, top)

                    # 3. Prepare Projection Extension Properties
                    # This tells the user what the *actual* data projection is (EPSG:31254)
                    epsg_code = src.crs.to_epsg() if src.crs else 31254

                    properties = {
                        # Standard STAC Projection Extension fields
                        "proj:epsg": epsg_code, 
                        "proj:shape": [src.height, src.width],
                        "proj:transform": list(src.transform),
                        # Store the original native bounds here if needed
                        "proj:bbox": bbox_4326, 
                    }

                    if src.crs and src.crs.to_wkt():
                        properties["proj:wkt2"] = src.crs.to_wkt()

                    # --- FIX ENDS HERE ---

                    # Extract datetime
                    item_datetime = datetime.utcnow()
                    if 'TIFFTAG_DATETIME' in src.tags():
                        try:
                            item_datetime = datetime.strptime(src.tags()['TIFFTAG_DATETIME'], '%Y:%m:%d %H:%M:%S')
                        except ValueError:
                            pass

                    if self.filename is None:
                        self.filename = os.path.splitext(os.path.basename(self.geotiff_url))[0]

                    # 4. Create a STAC Item
                    item = pystac.Item(
                        id=self.filename,
                        geometry=mapping(geometry_4326), # Use the 4326 geometry
                        bbox=bbox_4326,                  # Use the 4326 bbox
                        datetime=item_datetime,
                        properties=properties            # Contains the EPSG:31254 info
                    )

                    # Enable the projection extension explicitly
                    #pystac.extensions.projection.ProjectionExtension.add_to(item)

                    # 5. Add Asset
                    item.add_asset(
                        key="data",
                        asset=pystac.Asset(
                            href=self.geotiff_url,
                            media_type=pystac.MediaType.GEOTIFF,
                            roles=["data", "source"]
                        )
                    )

                    # 6. Add Item to Collection

                    #self.collection.add_item(self.item)

                    # Update collection extent based on this new item
                    #self.collection.update_extent_from_items()
                #self.collection.add_item(item)
                #self.collection.update_extent_from_items()   ### WARNING
            return item
            
        
  
        
       
        
    def add_item_to_collection(self):

        self.collection.add_item(self.item)
        self.collection.update_extent_from_items()
        self.collection.validate_all()

    def create_stac_from_geotiff_url(self):
        """
        Creates a STAC Catalog, Collection, Item, and Asset from a web link to a GeoTIFF file.
        Ensures Item geometry is EPSG:4326 while preserving native projection in properties.
        """
        

        # 2. Create a STAC Collection

        #print(self.catalog.get_all_collections())    

        print('Creating catalog')
        collections  = list(self.catalog.get_all_collections())
        print(collections)
        self.add_item_to_collection()
        if len(collections) > 0:
          for collection in collections:
            if collection.id == self.collection_id:
                
                self.catalog.remove_child(self.collection_id)
                ui.notify(f'collection {collection.id} already exists')
                self.catalog.add_child(self.collection)

                
              
            else:
                ui.notify(f'collection {collection.id} does not exist')
            
                self.catalog.add_child(collection)
        else:
            ui.notify(f'collection {self.collection_id} does not exist')
            
            self.catalog.add_child(self.collection)

    
           
            

        
        
        

        # 3. Read GeoTIFF metadata
        
       
    
            
        # 7. Save
        
        self.catalog.normalize_hrefs(self.output_dir)
        self.catalog.save(dest_href=self.output_dir)
        return self.catalog, self.collection, self.item
