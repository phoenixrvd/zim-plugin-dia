import gtk
import hashlib
import os

from zim.actions import action
from zim.applications import Application
from zim.fs import UnixFile, File
from zim.gui import FileDialog
from zim.plugins import PluginClass, WindowExtension, extends


class Dia(PluginClass):
    plugin_info = {
        'name': _('Dia'),  # T: plugin name
        'description': _('Allow to insert a diagram from  `Dia Diagram Editor <http://dia-installer.de/>`_ as image with link to original file.'),  # T: plugin description
        'author': 'Viacheslav Wolf',
        'help': 'Plugins:Dia',
    }

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

        dialog = FileDialog(self.window, _('Select File')) # T: dialog title

        # Set file filter for Dia-Types
        filter = gtk.FileFilter()
        filter.set_name(_('Dia'))
        # T: Filter in open file dialog, shows image files only
        filter.add_pixbuf_formats()
        filter.add_pattern('*.dia') # allow only .dia extension
        dialog.filechooser.add_filter(filter)
        dialog.filechooser.set_filter(filter)

        file = dialog.run()
        if file:
            # TODO review

            src_path = file.path

            m = hashlib.md5()
            m.update(src_path)

            page = self.window.ui.page
            dir = self.window.ui.notebook.get_attachments_dir(page)
            # Create dir if not exists
            dir.touch()
            dest_filenname = m.hexdigest()
            dest_path = os.path.join(dir.path, dest_filenname + ".png")

            # TODO get from config
            dot = Application( ('dia') )

            # dia -t png --nosplash -e foo.png Diagramm1.dia
            # TODO error handling and logging
            dot.run( ('-t', 'png', '--nosplash',  '-e', dest_path, file.path ) )

            file = File(dest_path)

            attrib = {
                'href': src_path,

                # TODO Relative path to image @see pageview.py L.6332
                'src': dest_path
            }

            # Insert imge as link to local *.dia file
            buffer = self.window.pageview.view.get_buffer()
            buffer.insert_at_cursor('\n')
            buffer.insert_image_at_cursor(file, **attrib)
            buffer.insert_at_cursor('\n')