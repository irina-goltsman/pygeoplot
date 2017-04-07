"""
Map plotter interface.
"""

from IPython.display import HTML, display

from .display import map_to_html, standalone_html

__all__ = ['Map', 'GeoPoint']


class GeoPoint(object):
    def __init__(self, lat, lon, weight=None):
        self.lat = lat
        self.lon = lon
        self.weight = weight

    @staticmethod
    def parse(obj):
        if isinstance(obj, GeoPoint):
            return obj  # FIXME: why doesnt work?

        elif (isinstance(obj, list) or isinstance(obj, tuple)) and len(obj) in [2, 3]:
            return GeoPoint(*obj)

        elif isinstance(obj, str):
            parts = obj.strip().split(',')
            return GeoPoint(*map(float, parts))

        else:
            raise ValueError('Cannot convert "%s" to GeoPoint' % repr(obj))

    def to_coord(self):
        return self.lat, self.lon


def _coordinates(point):
    geo_point = GeoPoint.parse(point)
    if geo_point.weight:
            return {
                "type": 'Feature',
                "geometry": {
                    "type": 'Point',
                    "coordinates": geo_point.to_coord()
                },
                "properties": {
                    "weight": geo_point.weight
                }
            }
    else:
        return geo_point.to_coord()


def _coordinates_many(points):
    coordinates = [_coordinates(point) for point in points]
    if len(coordinates) > 0 and isinstance(coordinates[0], dict):
        return {
            "type": 'FeatureCollection',
            "features": coordinates
        }

    return coordinates


class Map(object):
    """
    Canvas for visualizing data on the interactive map.
    """

    def __init__(self, show_click_coords=False):
        self.show_click_coords = show_click_coords
        self.center = [55.76, 37.64]
        self.zoom = 8
        self.objects = []

    def set_state(self, center, zoom):
        self.center = center
        self.zoom = zoom

    def add_object(self, obj):
        self.objects.append(obj)

    def add_placemark(self, point, hint=None, content=None, preset='islands#icon', icon_color=None):
        obj = {
            'type': 'Placemark',
            'point': _coordinates(point),
            'hint': hint,
            'content': content
        }

        if icon_color:
            obj['iconColor'] = icon_color

        if preset:
            obj['preset'] = preset

        self.add_object(obj)

    def add_line(self, points, hint=None, content=None, color='#000000', width=4, opacity=0.5):
        self.add_object({
            'type': 'Line',
            'points': _coordinates_many(points),
            'hint': hint,
            'content': content,
            'color': color,
            'width': width,
            'opacity': opacity,
        })

    def add_heatmap(self, points, intensity_of_midpoint=0.2, radius=10, dissipating=False):
        self.add_object({
            'type': 'Heatmap',
            'points': _coordinates_many(points),
            "intensityOfMidpoint": intensity_of_midpoint,
            "radius": radius,
            "dissipating": dissipating
        })

    def to_dict(self):
        """
        Outputs JSON-serializable dictionary representation of the map plot.
        """
        return {
            'state': {
                'center': self.center,
                'zoom': self.zoom,
            },
            'objects': self.objects,
            'showClickCoords': self.show_click_coords
        }

    def to_html(self, *args, **kwargs):
        return map_to_html(self, *args, **kwargs)

    def display(self, *args, **kwargs):
        display(HTML(self.to_html(*args, **kwargs)))

    def save_html(self, file, *args, **kwargs):
        if isinstance(file, str):
            with open(file, 'w') as f:
                self.save_html(f, *args, **kwargs)
        else:
            file.write(standalone_html(self.to_html(*args, **kwargs)))
