import gtk
import hashlib
import os

from zim.actions import action
from zim.applications import Application
from zim.fs import File
from zim.gui import FileDialog, GtkInterface
from zim.plugins import PluginClass, WindowExtension, extends


class Dia(PluginClass):
    plugin_info = {
        'name': _('Dia'),  # T: plugin name
        'description': _('Allow to insert a diagram from  `Dia Diagram Editor <http://dia-installer.de/>`_ as image with link to original file.'),  # T: plugin description
        'author': 'Viacheslav Wolf',
        'help': 'Plugins:Dia',
    }

    # TODO check_dependencies is dia installed ??? Windows ???

    # TODO plugin_preferences for dia binary path configuration


@extends('MainWindow')
class MainWindowExtension(WindowExtension):
    uimanager_xml = '''
        <ui>
            <menubar name='menubar'>
                <menu action='insert_menu'>
                    <placeholder name='plugin_items'>
                        <menuitem action='insert'/>
                    </placeholder>
                </menu>
            </menubar>
        </ui>
    '''

    @action(
            _('Dia File'),
            readonly=True,
    )  # T: menu item
    def insert(self):

        file = DiaFileDialog(self.window).run()
        if file:

            src_file, dest_file = DiaToSvg('dia', file, self.window.ui).convert()

            # TODO use relative path to image for src @see pageview.py L.6332
            attrib = {
                'href': src_file.path,
                'src': dest_file.path
            }

            # Insert image as link to local *.dia file
            buffer = self.window.pageview.view.get_buffer()
            buffer.insert_at_cursor('\n')
            buffer.insert_image_at_cursor(dest_file, **attrib)
            buffer.insert_at_cursor('\n')


class DiaFileDialog(FileDialog):

    def __init__(self, window):
        FileDialog.__init__(self, window, _('Select File')) # T: dialog title
        self.add_filter(_('Dia'), '*.dia')

    def add_filter(self, title, pattern):

        file_type_filter = gtk.FileFilter()
        file_type_filter.set_name(title)
        file_type_filter.add_pattern(pattern)

        self.filechooser.add_filter(file_type_filter)


class DiaToSvg(Application):

    image_type = 'svg'

    def __init__(self, binary_path, src_file, ui):
        """
        :type binary_path: str
        :type src_file: File
        :type ui: GtkInterface
        """

        Application.__init__(self, binary_path)

        self.ui = ui
        self.src_file = src_file
        self.dest_file = self.get_dest_file()

    def get_dest_file(self):
        """:rtype File"""

        ui = self.ui
        page = ui.page
        dest_dir = ui.notebook.get_attachments_dir(page)
        # Create dir if not exists
        dest_dir.touch()

        # image name is md5 from source path
        m = hashlib.md5()
        m.update(self.src_file.path)
        dest_filenname = m.hexdigest() + "." + self.image_type

        dest_path = os.path.join(dest_dir.path, dest_filenname)
        dest_file = File(dest_path)
        return dest_file

    def convert(self):
        src_file = self.src_file
        dest_file = self.dest_file

        args = (
            '-t',
            self.image_type,
            '--nosplash',
            '-e',
            dest_file.path,
            src_file.path,
        )

        # TODO throw error of not possible
        self.run(args)
        return src_file, dest_file
