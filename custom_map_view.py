from kivy_garden.mapview import MapView
from kivy.graphics import Mesh
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import Color
from kivy_garden.mapview import MapMarker, MapMarkerPopup

from GIS import gis

from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder


Builder.load_string('''
<ShapefileRenderer>
    canvas:
        Color
            rgba: 0.5,0.5,0.5,0.5
        Rectangle:
            pos: self.center_x, self.center_y
            size: 100, 100
''')

class ShapefileRenderer(FloatLayout):
    pass

class CustomMapView(MapView):
    def __init__(self, *args, **kwargs):
        super(CustomMapView, self).__init__(*args, **kwargs)
        gis.set_bbox(self.get_bbox())
        # self.add_bbox_map_makers()

        self.wid = Widget(pos=(0, 0), size=Window.size)
        self.wid.canvas.add(Color(0, 0, 0))
        gis.set_widget(self.wid)

        self.shapefileRenderer = ShapefileRenderer()
        self.add_widget(self.shapefileRenderer)

        self.render_mesh()
        gis.isInitialRender = False

        self.add_widget(self.wid)
        
        self.add_building_info_marker()

    def add_building_info_marker(self):
        m0 = MapMarkerPopup(lat=54.19216979440788, lon=9.105268718909326)  # Lille
        m0.add_widget(Button(text="building A"))
        self.add_marker(m0)

    def add_bbox_map_makers(self):
        m1 = MapMarker(lat=gis.bbox['lat_min'], lon=gis.bbox['lon_min'])  
        m2 = MapMarker(lat=gis.bbox['lat_max'], lon=gis.bbox['lon_max'])  
        self.add_marker(m1)
        self.add_marker(m2)
        
    def build_mesh(self, coords):
        vertices = []
        # vertices.extend([720, 480, 0, 0]) # shows where is the center of the widget
        indices = []

        for i, coord in enumerate(coords):
            x, y = gis.coords_to_point(coord[0], coord[1])
            vertices.extend([x, y, 0, 0])
            indices.append(i)

        self.temp_mesh = Mesh(vertices=vertices, indices=indices)
        self.temp_mesh.mode = 'triangle_fan' # 'points', 'line_strip', 'line_loop', 'lines', 'triangle_strip', 'triangle_fan'
        # print("$$$$$$$$$$$$$$MESH POS", self.mesh.pos)

    def render_mesh(self):
        with self.shapefileRenderer.canvas:
            Color(1, 0, 0, 0.3)
        # geom = gdf.loc[0, 'geometry']
            for polygon in gis.gdf['geometry']:
                self.build_mesh(polygon.exterior.coords)
        return
    
    def on_touch_down(self, touch): 
        # touch <MouseMotionEvent spos=(0.5798138869005011, 0.6323877068557919) pos=(1620.5798138869004, 1070.6323877068558)>
        self.last_pos_x = touch.pos[0]
        self.last_pos_y = touch.pos[1]
        if super().on_touch_down(touch):
            return True
        if not self.collide_point(touch.x, touch.y):
            return False
        return True

    def recreate_shapefileRenderer(self):
        self.remove_widget(self.shapefileRenderer)
        self.shapefileRenderer = ShapefileRenderer()
        self.add_widget(self.shapefileRenderer)

    def refresh_shapefile(self, *args): # clock gives some args so here it receives *args eventhough it's not needed in the function
        self.recreate_shapefileRenderer()
        # self.remove_widget(self.shapefileRenderer)
        gis.set_bbox(self.get_bbox())
        # self.add_bbox_map_makers()
        self.render_mesh()


    # fire only touch_down and touch_up event
    def on_touch_move(self, touch):
        print("!!!!!!!!ON TOUCH MOVE")
        self.refresh_shapefile()

        if super().on_touch_move(touch):
            return True
        if not self.collide_point(touch.x, touch.y):
            return False
        return

    def on_touch_up(self, touch):
        self.refresh_shapefile()
        if super().on_touch_up(touch):
            return True
        if not self.collide_point(touch.x, touch.y):
            return False
        return 
    
    def on_touch_down(self, touch):
        self.refresh_shapefile()
        if super().on_touch_down(touch):
            return True
        if not self.collide_point(touch.x, touch.y):
            return False
        return 

    def on_transform(self, *args):
        print("Hello!"); 
        if gis.isInitialRender == False:
            self.refresh_shapefile()
        super().on_transform(args); 


    
