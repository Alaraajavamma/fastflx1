import requests
import urllib.parse
from gi.repository import Gio
from fastflx1.utils import logger

class WeatherManager:
    def __init__(self):
        self.settings = Gio.Settings.new("org.gnome.Weather")
        self.flatpak_id = "org.gnome.Weather"

    def search_location(self, query):
        encoded = urllib.parse.quote(query.replace(" ", "+"))
        url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=1"
        try:
            resp = requests.get(url, headers={"User-Agent": "FastFLX1/1.0"})
            data = resp.json()
            if not data:
                return None
            return data[0]
        except Exception as e:
            logger.error(f"Error fetching weather location: {e}")
            return None

    def add_location(self, location_data):
        # We need to construct a GVariant compatible with org.gnome.Weather locations
        # The schema is usually `av` (array of variants).
        # Inside, it's a specific structure.
        # Original script:
        # location="<(uint32 2, <('$name', '', false, [($lat, $lon)], @a(dd) [])>)>"
        # gsettings set org.gnome.Weather locations "[...]"

        name = location_data.get('display_name', '').split(',')[0] # Simplify name
        lat = float(location_data.get('lat'))
        lon = float(location_data.get('lon'))

        # Radians conversion
        lat_rad = lat / (180 / 3.141592654)
        lon_rad = lon / (180 / 3.141592654)

        logger.info(f"Adding location: {name} ({lat}, {lon})")

        # Constructing GVariant in Python is cleaner
        # The signature for a location seems to be `(u(sbsa(dd)a(dd)))` roughly?
        # Actually the script output: `<(uint32 2, <('$name', '', false, [($lat, $lon)], @a(dd) [])>)>`
        # This looks like `v`. The variant contains a tuple.
        # The tuple is `(uint32, Variant)`.
        # The inner Variant is `(string, string, boolean, array of (double, double), array of (double, double))`?

        # Let's try to fetch current value and see format.
        current_locs = self.settings.get_value("locations")

        # Creating the new location variant
        # We can construct it using GLib.Variant.parse if we have the signature.
        # Or build it with GLib.Variant constructors.

        # Let's stringify it like the bash script did, it might be easier to pass to Variant.parse
        # location_str = f"<(uint32 2, <('{name}', '', false, [({lat_rad}, {lon_rad})], @a(dd) [])>)>"
        # Actually constructing the variant object is better.

        # Inner struct: (name, code, is_current, coordinates, ???)
        # coords = [(lat_rad, lon_rad)]

        inner_variant_val = GLib.Variant("(sbsa(dd)a(dd))", (
            name,
            "",
            False,
            [(lat_rad, lon_rad)],
            []
        ))

        outer_variant = GLib.Variant("(uv)", (2, inner_variant_val))

        # Variant wrapper around that?
        # The setting is `av` (array of variants).
        location_variant = GLib.Variant("v", outer_variant)

        # Build new list
        new_list = []
        if current_locs:
            for i in range(current_locs.n_children()):
                new_list.append(current_locs.get_child_value(i))

        new_list.append(location_variant)

        new_value = GLib.Variant("av", new_list)
        self.settings.set_value("locations", new_value)

        # TODO: Handle flatpak logic if needed (via flatpak run --command=gsettings)
        # But native is preferred.

from gi.repository import GLib
