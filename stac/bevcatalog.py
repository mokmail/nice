import pystac
import rasterio
from rasterio.io import MemoryFile
from shapely.geometry import box
from datetime import datetime
import os
import requests

def create_stac_from_geotiff_url(geotiff_url: str, catalog_id: str = "my-geotiff-catalog", collection_id: str = "geotiff-collection", item_id: str = None, output_dir: str = "stac_catalog"):
    """
    Creates a STAC Catalog, Collection, Item, and Asset from a web link to a GeoTIFF file.

    Args:
        geotiff_url (str): The URL to the GeoTIFF file.
        catalog_id (str): The ID for the STAC Catalog.
        collection_id (str): The ID for the STAC Collection.
        item_id (str, optional): The ID for the STAC Item. If None, derived from the GeoTIFF filename.
        output_dir (str): The directory where the STAC catalog will be saved.

    Returns:
        pystac.Catalog: The created STAC Catalog object.
    """
    # 1. Create a root STAC Catalog
    catalog = pystac.Catalog(id=catalog_id, description="A STAC Catalog generated from a GeoTIFF URL.")

    # 2. Create a STAC Collection
    collection = pystac.Collection(
        id=collection_id,
        description="A collection of GeoTIFF items.",
        extent=pystac.Extent(
            spatial=pystac.SpatialExtent([[-180, -90, 180, 90]]), # Placeholder, will be updated by item
            temporal=pystac.TemporalExtent([[datetime(1970, 1, 1), None]]) # Placeholder, will be updated by item
        )
    )
    catalog.add_child(collection)

    # 3. Read GeoTIFF metadata from URL
    try:
        # Use requests to get the header and a small chunk for rasterio to inspect
        # For large files, it's better to stream or use rasterio's virtual file system
        # For simplicity, we'll download a small part or rely on rasterio's URL handling
        with rasterio.open(geotiff_url) as src:
            bounds = src.bounds
            crs = src.crs.to_string()
            transform = src.transform
            width = src.width
            height = src.height

            # Extract datetime from metadata if available, otherwise use a default
            # This is a simplification; real-world scenarios might parse filename or specific tags
            item_datetime = datetime.utcnow()
            if 'TIFFTAG_DATETIME' in src.tags():
                try:
                    item_datetime = datetime.strptime(src.tags()['TIFFTAG_DATETIME'], '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    pass # Fallback to utcnow()

            # Create a shapely geometry from bounds
            geometry = box(bounds.left, bounds.bottom, bounds.right, bounds.top)

            # If item_id is not provided, derive from filename
            if item_id is None:
                item_id = os.path.splitext(os.path.basename(geotiff_url))[0]

            # 4. Create a STAC Item
            item = pystac.Item(
                id=item_id,
                geometry=geometry.__geo_interface__,
                bbox=list(geometry.bounds),
                datetime=item_datetime,
                properties={
                    "proj:epsg": src.crs.to_epsg() if src.crs.to_epsg() else None,
                    "proj:shape": [height, width],
                    "proj:transform": list(transform)
                }
            )

            # 5. Add the GeoTIFF as an Asset to the Item
            item.add_asset(
                key="data",
                asset=pystac.Asset(
                    href=geotiff_url,
                    media_type=pystac.MediaType.GEOTIFF,
                    roles=["data", "source"]
                )
            )

            # 6. Add the Item to the Collection
            collection.add_item(item)

    except Exception as e:
        print(f"Error processing GeoTIFF from {geotiff_url}: {e}")
        raise

    # 7. Save the STAC Catalog to disk
    catalog.normalize_hrefs(os.path.abspath(output_dir))
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED, dest_href=output_dir)

    return catalog
