import logging
import os
import re

from PySide6.QtCore import QObject, QStringListModel, QUrl, Signal, Property, Slot, QAbstractItemModel

from library.deepzoom.deepzoom_server import DeepZoomServer


class DeepZoomViewer(QObject):
    def __init__(self, server: DeepZoomServer):
        QObject.__init__(self)
        self._selected_file_url = ""
        self._selected_file_name = ""
        self._selected_file_folder = ""
        self._selected_file_thumbnail_url = ""
        self._last_selected_file_folder = ""
        self._selected_file_siblings = QStringListModel(self)
        self._supported_file_extensions = ""
        self._server = server
        self._dzi_levels = tuple()
        self._dzi_dimensions = tuple()
        self._dzi_min_zoom_level = 0
        self._dzi_max_zoom_level = 0
        self._dzi_meters_per_pixel = 0.0
        self._dzi_pixels_per_meter = 0.0
        self.set_supported_file_extensions()

    def get_selected_file(self):
        return self._selected_file_url

    def get_selected_file_siblings(self):
        return self._selected_file_siblings

    def set_selected_file(self, file):
        if isinstance(file, QUrl):
            if file.isLocalFile():
                self._selected_file_path = file.toLocalFile()
            else:
                file_name = file.toString().split('/')[3]
                self._selected_file_path = os.path.join(self._selected_file_folder, file_name)
        elif isinstance(file, str):
            self._selected_file_path = file
        else:
            return
        self._selected_file_name = os.path.basename(self._selected_file_path)
        self._selected_file_folder = os.path.dirname(self._selected_file_path)
        self._server.set_base_dir(self._selected_file_folder)
        self._set_dzi_info()
        self._selected_file_url = self._server.get_slide_url(self._selected_file_name)
        self.on_selected_file.emit()
        self.reload.emit()
        self.set_selected_file_thumbnail()
        self._detect_selected_file_siblings()
        logging.debug("DeepZoomViewer - Selected file: %s", self._selected_file_url)
        logging.debug("DeepZoomViewer - Selected file folder: %s", self._selected_file_folder)

    @Slot(list)
    def set_selected_file_siblings(self, files):
        self._selected_file_siblings.setStringList(files)
        self.on_selected_file_siblings.emit()

    def _detect_selected_file_siblings(self):
        if self._selected_file_folder != self._last_selected_file_folder:
            self._last_selected_file_folder = self._selected_file_folder
            temp_siblings = []
            with os.scandir(self._selected_file_folder) as d:
                for entry in d:
                    supported_file_extensions_re = re.compile('.' + '$|.'.join(self._supported_file_extensions) + '$')
                    if entry.is_file() and re.search(supported_file_extensions_re, entry.name):
                        slide_path = self._server.get_thumbnail_url(entry.name)
                        temp_siblings.append(slide_path)
            temp_siblings = sorted(temp_siblings)
            self.set_selected_file_siblings(temp_siblings)

    def _set_dzi_info(self):
        self._dzi_levels = self._server.get_level_tiles(self._selected_file_name)
        self._dzi_dimensions = self._server.get_level_dimensions(self._selected_file_name)
        self._dzi_meters_per_pixel = self._server.get_meters_per_pixel(self._selected_file_name)
        logging.debug("DeepZoomViewer - Image levels: %s", self._dzi_levels)
        logging.debug("DeepZoomViewer - Image dimensions: %s", self._dzi_dimensions)
        logging.debug("DeepZoomViewer - Image mpp: %s", self._dzi_meters_per_pixel)
        self.set_dzi_min_zoom_level()
        self.set_dzi_max_zoom_level()
        self.set_dzi_pixels_per_meter()

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

    def get_dzi_pixels_per_meter(self):
        return self._dzi_pixels_per_meter

    def set_dzi_pixels_per_meter(self):
        self._dzi_pixels_per_meter = 1e6 / self._dzi_meters_per_pixel if self._dzi_meters_per_pixel > 0 else 0
        logging.debug("DeepZoomViewer - Set image mpp:  %s", self._dzi_pixels_per_meter)
        self.on_dzi_pixels_per_meter.emit()

    def get_supported_file_extensions(self):
        return "(*." + " *.".join(self._supported_file_extensions) + ")"

    def set_supported_file_extensions(self):
        self._supported_file_extensions = self._server.get_supported_file_types()
        self.on_supported_file_extensions.emit()

    def get_tile_size(self):
        return self._server.get_tile_dimensions()[0]

    reload = Signal()
    on_tile_size = Signal()
    on_dzi_max_width = Signal()
    on_dzi_max_height = Signal()
    on_dzi_min_zoom_level = Signal()
    on_dzi_max_zoom_level = Signal()
    on_dzi_pixels_per_meter = Signal()

    on_selected_file = Signal()
    on_selected_file_thumbnail = Signal()
    on_selected_file_siblings = Signal()
    on_supported_file_extensions = Signal()

    dzi_tile_size = Property(int, get_tile_size, notify=on_tile_size)
    dzi_max_width = Property(int, get_dzi_max_width, notify=on_dzi_max_width)
    dzi_max_height = Property(int, get_dzi_max_height, notify=on_dzi_max_height)
    dzi_min_zoom_level = Property(int, get_dzi_min_zoom_level, set_dzi_min_zoom_level, notify=on_dzi_min_zoom_level)
    dzi_max_zoom_level = Property(int, get_dzi_max_zoom_level, set_dzi_max_zoom_level, notify=on_dzi_max_zoom_level)
    dzi_pixels_per_meter = Property(float, get_dzi_pixels_per_meter, set_dzi_pixels_per_meter, notify=on_dzi_pixels_per_meter)

    selected_file = Property(QUrl, get_selected_file, set_selected_file, notify=on_selected_file)
    selected_file_thumbnail = Property(QUrl, get_selected_file_thumbnail, set_selected_file_thumbnail, notify=on_selected_file_thumbnail)
    selected_file_siblings = Property(QAbstractItemModel, get_selected_file_siblings, set_selected_file_siblings, notify=on_selected_file_siblings)
    supported_file_extensions = Property(str, get_supported_file_extensions, notify=on_supported_file_extensions)
