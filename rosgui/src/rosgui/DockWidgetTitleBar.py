# Copyright (c) 2011, Dirk Thomas, Dorian Scholz, TU Darmstadt
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#   * Neither the name of the TU Darmstadt nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os

from QtBindingHelper import loadUi
from QtCore import qDebug, QEvent, QObject, Qt, Slot
from QtGui import QDockWidget, QIcon, QWidget

class DockWidgetTitleBar(QWidget):

    def __init__(self, dock_widget, hide_close_button=False):
        super(DockWidgetTitleBar, self).__init__(dock_widget)
        self._hide_close_button_flag = hide_close_button

        ui_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'DockWidgetTitleBar.ui')
        loadUi(ui_file, self)
        self._extra_buttons = {
            'settings': self.settings_button,
            'reload': self.reload_button,
            'help': self.help_button,
            'close': self.close_button,
        }

        self.settings_button.setIcon(QIcon.fromTheme('emblem-system'))
        self.settings_button.setText("")
        self.reload_button.setIcon(QIcon.fromTheme('view-refresh'))
        self.reload_button.setText("")
        self.help_button.setIcon(QIcon.fromTheme('help-browser'))
        self.help_button.setText("")

        self.close_button.setIcon(QIcon.fromTheme('window-close'))
        self.close_button.setText("")

        self.float_button.clicked.connect(self.toggle_floating)
        self.dockable_button.clicked.connect(self.toggle_dockable)

        dock_widget.featuresChanged.connect(self.features_changed)
        self.features_changed(0)

        self.update_title()

        self._event_callbacks = {
            QEvent.WindowTitleChange: self.update_title,
        }
        dock_widget.installEventFilter(self)


    def connect_button(self, button_id, callback):
        button = self._extra_buttons.get(button_id, None)
        if button is None:
            qDebug('DockWidgetTitleBar.connect_button(): unknown button_id: %s' % button_id)
            return
        button.clicked.connect(callback)


    def show_button(self, button_id, visibility=True):
        button = self._extra_buttons.get(button_id, None)
        if button is None:
            qDebug('DockWidgetTitleBar.show_button(): unknown button_id: %s' % button_id)
            return
        button.setVisible(visibility)


    def hide_button(self, button_id):
        self.show_button(button_id, False)


    def eventFilter(self, obj, event):
        if event.type() in self._event_callbacks:
            ret_val = self._event_callbacks[event.type()](obj, event)
            if ret_val is not None:
                return ret_val
        return QObject.eventFilter(self, obj, event)


    def update_title(self, *args):
        self.title_label.setText(self.parentWidget().windowTitle())


    @Slot(bool)
    def toggle_dockable(self, enabled):
        dock_widget = self.parentWidget()
        if enabled:
            dock_widget.setAllowedAreas(Qt.AllDockWidgetAreas)
        else:
            dock_widget.setAllowedAreas(Qt.NoDockWidgetArea)


    @Slot()
    def toggle_floating(self):
        dock_widget = self.parentWidget()
        dock_widget.setFloating(not dock_widget.isFloating())


    def features_changed(self, _features):
        features = self.parentWidget().features()
        self.close_button.setVisible((not self._hide_close_button_flag) and bool(features & QDockWidget.DockWidgetClosable))
        self.float_button.setVisible(bool(features & QDockWidget.DockWidgetFloatable))


    def save_settings(self, perspective_settings):
        perspective_settings.set_value('dockable', self.dockable_button.isChecked())


    def restore_settings(self, perspective_settings):
        self.dockable_button.setChecked(perspective_settings.value('dockable', True) in [True, 'true'])
        self.toggle_dockable(self.dockable_button.isChecked())


if __name__ == '__main__':
    import sys
    from QtGui import QApplication, QMainWindow

    app = QApplication(sys.argv)

    win = QMainWindow()

    dock1 = QDockWidget('dockwidget1', win)
    win.addDockWidget(Qt.LeftDockWidgetArea, dock1)
    title_bar = DockWidgetTitleBar(dock1)
    dock1.setTitleBarWidget(title_bar)

    dock2 = QDockWidget('dockwidget2')
    win.addDockWidget(Qt.RightDockWidgetArea, dock2)
    title_bar = DockWidgetTitleBar(dock2)
    dock2.setTitleBarWidget(title_bar)

    win.resize(640, 480)
    win.show()

    app.exec_()
