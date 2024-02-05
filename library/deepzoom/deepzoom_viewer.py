from PySide2.QtCore import Signal, Property, Slot

from library.base.viewer import Viewer
from library.deepzoom.deepzoom_server import DeepZoomServer


class DeepZoomViewer(Viewer):
    def __init__(self, server: DeepZoomServer):
        super().__init__()
        self._server = server
        self._dzi_levels = tuple()
        self._dzi_dimensions = tuple()
        self._dzi_min_zoom_level = 0
        self._dzi_max_zoom_level = 0
        self.set_supported_file_extensions()

    def set_selected_file(self, file):
        self._set_selected_file(file)
        self._server.set_base_dir(self._selected_file_folder)
        self._set_dzi_info()
        self._selected_file_url = self._server.get_slide_url(self._selected_file_name)
        self.on_selected_file.emit()
        self.reload.emit()
        self.set_selected_file_thumbnail()
        siblings = [self._server.get_thumbnail_url(a) for a in self._scan_working_dir()]
        self.set_selected_file_siblings(siblings)
        print("Selected file: ", self._selected_file_url)
        print("Selected file folder: ", self._selected_file_folder)

    @Slot(list)
    def set_selected_file_siblings(self, files):
        self._selected_file_siblings.setStringList(files)
        self.on_selected_file_siblings.emit()

    def _set_dzi_info(self):
        self._dzi_levels = self._server.get_level_tiles(self._selected_file_name)
        self._dzi_dimensions = self._server.get_level_dimensions(self._selected_file_name)
        print(self._dzi_levels)
        print(self._dzi_dimensions)
        self.set_dzi_min_zoom_level()
        self.set_dzi_max_zoom_level()

    def get_selected_file_thumbnail(self):
        return self._selected_file_thumbnail_url

    def set_selected_file_thumbnail(self):
        self._selected_file_thumbnail_url = self._server.get_thumbnail_url(self._selected_file_name)
        self.on_selected_file_thumbnail.emit()

    def get_dzi_max_width(self):
        return self._dzi_dimensions[-1][0]

    def get_dzi_max_height(self):
        return self._dzi_dimensions[-1][1]

    def get_dzi_min_zoom_level(self):
        return self._dzi_min_zoom_level

    def set_dzi_min_zoom_level(self):
        self._dzi_min_zoom_level = next(x[0] for x in enumerate(self._dzi_levels) if max(x[1]) > 2)
        self.on_dzi_min_zoom_level.emit()

    def get_dzi_max_zoom_level(self):
        return self._dzi_max_zoom_level

    def set_dzi_max_zoom_level(self):
        self._dzi_max_zoom_level = len(self._dzi_levels) - 1
        self.on_dzi_max_zoom_level.emit()

    def get_supported_file_extensions(self):
        return "(*." + " *.".join(self._supported_file_extensions) + ")"

    def set_supported_file_extensions(self):
        self._supported_file_extensions = self._server.get_supported_file_types()
        self.on_supported_file_extensions.emit()

    def get_tile_size(self):
        return self._server.get_tile_dimensions()[0]

    on_tile_size = Signal()
    on_dzi_max_width = Signal()
    on_dzi_max_height = Signal()
    on_dzi_min_zoom_level = Signal()
    on_dzi_max_zoom_level = Signal()

    dzi_tile_size = Property(int, get_tile_size, notify=on_tile_size)
    dzi_max_width = Property(int, get_dzi_max_width, notify=on_dzi_max_width)
    dzi_max_height = Property(int, get_dzi_max_height, notify=on_dzi_max_height)
    dzi_min_zoom_level = Property(int, get_dzi_min_zoom_level, set_dzi_min_zoom_level, notify=on_dzi_min_zoom_level)
    dzi_max_zoom_level = Property(int, get_dzi_max_zoom_level, set_dzi_max_zoom_level, notify=on_dzi_max_zoom_level)
