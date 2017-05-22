"""
Routines for generating HTML that shows Map object.
"""

import random
import json
import re

import jinja2

__all__ = ['map_to_html', 'standalone_html']

JS_CODE = """
draw_functions = {

    "Placemark": function(map, obj) {
        properties = {
            hintContent: obj.hint,
            balloonContent: obj.content
        };
        options = {};
        if ('preset' in obj) {
            options['preset'] = obj.preset;
        }
        if ('iconColor' in obj) {
            options['iconColor'] = obj.iconColor
        }
        map.geoObjects.add(
            new ymaps.Placemark(obj.point, properties, options)
        );
    },

    "Line": function(map, obj) {
        properties = {
            hintContent: obj.hint,
            balloonContent: obj.content
        };
        options = {
            strokeColor: obj.color,
            strokeWidth: obj.width,
            strokeOpacity: obj.opacity
        };
        map.geoObjects.add(
            new ymaps.Polyline(obj.points, properties, options)
        );
    },

    "Heatmap": function(map, obj) {
        options = {
            radius: obj.radius,
            intensityOfMidpoint: obj.intensityOfMidpoint,
            dissipating: obj.dissipating,
            gradient: obj.gradient
        };
        ymaps.modules.require(['Heatmap'], function (Heatmap) {
            var heatmap = new Heatmap(obj.points, options);
            heatmap.setMap(map);
        });
    }

}

function show_map(id, map_data) {
    ymaps.ready(init);

    var yaMap;
    function init() {

        yaMap = new ymaps.Map(id, map_data.state);

        if (map_data.showClickCoords) {
            yaMap.events.add('click', function (e) {
                console.log(e);
                if (!yaMap.balloon.isOpen()) {
                    var coords = e.get('coordPosition');
                    yaMap.balloon.open(coords, {
                        contentBody:[
                            coords[0].toPrecision(9),
                            coords[1].toPrecision(9)
                        ].join(', ')
                    });
                }
                else {
                    yaMap.balloon.close();
                }
            });
        }

        map_data.objects.forEach(
            function(obj) {
                draw_func = draw_functions[obj.type];
                if (draw_func) {
                    draw_func(yaMap, obj);
                } else {
                    console.error("Bad object type: "+obj.type);
                }
            }
        );

    }
}
"""


TEMPLATE_HTML = jinja2.Template("""
<div id="{{ container_id }}" style="width: {{ width }}px; height: {{ height }}px"></div>
<script src="https://api-maps.yandex.ru/2.1/?lang=ru_RU" type="text/javascript"></script>
<script src="https://cdn.rawgit.com/yandex/mapsapi-heatmap/master/build/heatmap.min.js" type="text/javascript"></script>
<script type="text/javascript">
    {{ js_code }}

    show_map("{{ container_id }}", {{ map_json }});

    {% if resizeable %}
    $(function() {
        $("#{{ container_id }}").resizable();
        $("#{{ container_id }}").on("resize", function() { myMap.container.fitToViewport(); })
    });
    {% endif %}

</script>
""")


TEMPLATE_STANDALONE_HTML = jinja2.Template("""
<html>
<head>
    <script type="text/javascript" src="http://cdnjs.cloudflare.com/ajax/libs/require.js/2.1.15/require.min.js"></script>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
    <script src="https://api-maps.yandex.ru/2.1/?lang=ru_RU" type="text/javascript"></script>
    <script src="https://cdn.rawgit.com/yandex/mapsapi-heatmap/master/build/heatmap.min.js" type="text/javascript"></script>
</head>
<body>
    {{ body }}
</body>
""")


def map_to_html(map, width=640, height=480, resizeable=False, container_id=None):
    if container_id is None:
        container_id = 'map_' + str(int(random.random() * 1E10))
    elif re.search('\s', container_id):
        raise ValueError("container_id must not contain spaces")

    map_dict = map.to_dict()

    html = TEMPLATE_HTML.render(
        container_id=container_id,
        width=width,
        height=height,
        resizeable=resizeable,
        map_json=json.dumps(map_dict),
        js_code=JS_CODE,
    )

    return html


def standalone_html(body):
    return TEMPLATE_STANDALONE_HTML.render(body=body)
