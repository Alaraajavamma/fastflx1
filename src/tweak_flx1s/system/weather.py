import requests
import urllib.parse
from gi.repository import Gio, GLib
from tweak_flx1s.utils import logger, run_command

class WeatherManager:
    def __init__(self):
        # We try to use the schema source for org.gnome.Weather
        # Note: If running in a flatpak sandbox or if schema is missing, this might fail.
        # But we are running on host (deb package).
        self.schema_id = "org.gnome.Weather"
        self.settings = None
        try:
            self.settings = Gio.Settings.new(self.schema_id)
        except Exception as e:
            logger.warning(f"Could not load GSettings for {self.schema_id}: {e}")

    def search_location(self, query):
        if not query:
            return None
        encoded = urllib.parse.quote(query.replace(" ", "+"))
        url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=1"
        try:
            resp = requests.get(url, headers={"User-Agent": "FastFLX1/1.0"})
            if resp.status_code != 200:
                logger.error(f"Weather API error: {resp.status_code}")
                return None
            data = resp.json()
            if not data:
                return None
            return data[0]
        except Exception as e:
            logger.error(f"Error fetching weather location: {e}")
            return None

    def add_location(self, location_data):
        if not self.settings:
            logger.error("GSettings not initialized")
            return False

        try:
            name = location_data.get('display_name', '').split(',')[0]
            lat = float(location_data.get('lat'))
            lon = float(location_data.get('lon'))

            # Radians conversion as per original script
            lat_rad = lat / (180 / 3.141592654)
            lon_rad = lon / (180 / 3.141592654)

            # GVariant text format construction
            # location="<(uint32 2, <('$name', '', false, [($lat, $lon)], @a(dd) [])>)>"
            # Note: The original script used < ... > for variant

            variant_str = f"<(uint32 2, <('{name}', '', false, [({lat_rad}, {lon_rad})], @a(dd) [])>)>"

            logger.info(f"Parsing variant string: {variant_str}")

            # Parse the variant string. Signature for 'locations' is 'av'.
            # The string represents one item (a variant 'v').
            new_location_variant = GLib.Variant.parse(GLib.VariantType("v"), variant_str, None)

            # Get current list
            current_value = self.settings.get_value("locations")

            # Create a new builder for the array
            builder = GLib.VariantBuilder(GLib.VariantType("av"))

            # Add existing items
            if current_value:
                iter_ = current_value.iter()
                while True:
                    child = iter_.next_value()
                    if not child:
                        break
                    builder.add_value(child)

            # Add new item
            builder.add_value(new_location_variant)

            new_array = builder.end()
            self.settings.set_value("locations", new_array)
            logger.info(f"Added location: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to add location: {e}")
            return False
