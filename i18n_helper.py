from gettext import gettext as _

import re, string
import gtk
import gedit

# Insert items in the Tools menu
ui_str = """<ui>
  <menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_2">
        <menuitem name="I18nHelper" action="I18nHelper"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""
class I18nWindowHelper:
    def __init__(self, plugin, window):
        self._window = window
        self._plugin = plugin

        # Insert menu items
        self._insert_menu()

    def deactivate(self):
        # Remove any installed menu items
        self._remove_menu()

        self._window = None
        self._plugin = None
        self._action_group = None

    def _insert_menu(self):
        # Get the GtkUIManager
        manager = self._window.get_ui_manager()

        # Create a new action group
        self._action_group = gtk.ActionGroup("ExamplePyPluginActions")
        self._action_group.add_actions([('I18nHelper', None, _('I18n-ize'),
                                         '<Control><Shift>i',
                                         _("Replace selected string with i18n version, generates and cuts en.yml string to clipboard."),
                                          self.i18nize)])

        # Insert the action group
        manager.insert_action_group(self._action_group, -1)

        # Merge the UI
        self._ui_id = manager.add_ui_from_string(ui_str)

    def _remove_menu(self):
        # Get the GtkUIManager
        manager = self._window.get_ui_manager()

        # Remove the ui
        manager.remove_ui(self._ui_id)

        # Remove the action group
        manager.remove_action_group(self._action_group)

        # Make sure the manager updates
        manager.ensure_update()

    def update_ui(self):
        self._action_group.set_sensitive(self._window.get_active_document() != None)

    # Menu activate handlers
    def i18nize(self, action):
        # Takes the current string, generates a i18n key.
        # Replaces the selection with the t('<<key>>'),
        # Adds the locale.yml string to clipboard (key: Original String)
        
        doc = self._window.get_active_document()
        if not doc:
            return

        selection = doc.get_selection_bounds()
        current_pos_mark = doc.get_insert()
        
        if not len(selection):
            return
        
        start, end = selection
        
        string = start.get_slice(end)
        i18n_key = re.sub(r'[\W]+', '', string.lower().strip().replace(' ', '_'))
        i18n_string = re.sub(r'[\'"]+', '', string.strip())
        
        locale_config = '{0}: {1}'.format(i18n_key, i18n_string)
            
        # If string is quoted, string is already being evaluated.
        # If not quoted, string needs the '=' evaluation added.
        if string.startswith("'") or string.startswith('"'):
            view_string = 't(".{0}")'.format(i18n_key)
        else:
            view_string = '= t(".{0}")'.format(i18n_key)
               
        doc.delete(start, end)
        doc.insert(start, view_string)
        
        cb = gtk.Clipboard()
        cb.set_text(locale_config)
        cb.store()
        

class I18nPlugin(gedit.Plugin):
    def __init__(self):
        gedit.Plugin.__init__(self)
        self._instances = {}

    def activate(self, window):
        self._instances[window] = I18nWindowHelper(self, window)

    def deactivate(self, window):
        self._instances[window].deactivate()
        del self._instances[window]

    def update_ui(self, window):
        self._instances[window].update_ui()



