# -*- coding: utf-8 -*-
"""

    mslib.msui.mscolab
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Window to display authentication and project details for mscolab


    To better understand of the code, look at the 'ships' example from
    chapter 14/16 of 'Rapid GUI Programming with Python and Qt: The
    Definitive Guide to PyQt Programming' (Mark Summerfield).

    This file is part of mss.

    :copyright: Copyright 2019- Shivashis Padhi
    :license: APACHE-2.0, see LICENSE for details.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import json
import logging
import types
import fs
import requests
from fs import open_fs, path
from requests.auth import HTTPBasicAuth

from mslib.msui import MissionSupportSystemDefaultConfig as mss_default
from mslib.msui import flighttrack as ft
from mslib.msui import mscolab_admin_window as maw
from mslib.msui import mscolab_project as mp
from mslib.msui import mscolab_version_history as mvh
from mslib.msui import sideview, tableview, topview
from mslib.msui import socket_control as sc
from mslib.msui.mss_qt import QtCore, QtGui, QtWidgets, get_open_filename, get_save_filename
from mslib.msui.mss_qt import ui_add_project_dialog as add_project_ui
from mslib.msui.mss_qt import ui_add_user_dialog as add_user_ui
from mslib.msui.mss_qt import ui_mscolab_window as ui
from mslib.msui.mss_qt import ui_wms_password_dialog as ui_pw
from mslib.msui.mss_qt import ui_mscolab_merge_waypoints_dialog
from mslib.utils import config_loader
from mslib.utils import load_settings_qsettings, save_settings_qsettings, dropEvent, dragEnterEvent, show_popup

MSCOLAB_URL_LIST = QtGui.QStandardItemModel()


def add_mscolab_urls(combo_box, url_list):
    combo_box_urls = [combo_box.itemText(_i) for _i in range(combo_box.count())]
    for url in (_url for _url in url_list if _url not in combo_box_urls):
        combo_box.addItem(url)


class MSSMscolabWindow(QtWidgets.QMainWindow, ui.Ui_MSSMscolabWindow):
    """PyQt window implementing mscolab window
    """
    name = "Mscolab"
    identifier = None
    viewCloses = QtCore.pyqtSignal(name="viewCloses")

    def __init__(self, parent=None, data_dir=mss_default.mss_dir, mscolab_server_url=mss_default.mscolab_server_url):
        """Set up user interface
        """
        super(MSSMscolabWindow, self).__init__(parent)
        self.setupUi(self)
        self.loggedInWidget.hide()
        # if token is None, not authorized, else authorized
        self.token = None
        # User related signals
        self.connectMscolab.clicked.connect(self.connect_handler)
        self.addUser.clicked.connect(self.add_user_handler)
        self.loginButton.clicked.connect(self.authorize)
        self.logoutButton.clicked.connect(self.logout)
        self.deleteAccountButton.clicked.connect(self.delete_account)
        self.disconnectMscolab.clicked.connect(self.disconnect_handler)
        # Project related signals
        self.addProject.clicked.connect(self.add_project_handler)
        self.importBtn.clicked.connect(self.handle_import)
        self.exportBtn.clicked.connect(self.handle_export)
        self.workLocallyCheckBox.stateChanged.connect(self.handle_work_locally_toggle)
        self.save_ft.clicked.connect(self.save_wp_mscolab)
        self.fetch_ft.clicked.connect(self.fetch_wp_mscolab)
        self.chatWindowBtn.clicked.connect(self.open_chat_window)
        self.adminWindowBtn.clicked.connect(self.open_admin_window)
        self.versionHistoryBtn.clicked.connect(self.open_version_history_window)
        # View related signals
        self.topview.clicked.connect(self.open_topview)
        self.sideview.clicked.connect(self.open_sideview)
        self.tableview.clicked.connect(self.open_tableview)
        # int to store active pid
        self.active_pid = None
        # storing access_level to save network call
        self.access_level = None
        # storing project_name to save network call
        self.active_project_name = None
        # Storing project list to pass to admin window
        self.projects = None
        # store active_flight_path here as object
        self.waypoints_model = None
        # Store active project's file path
        self.local_ftml_file = None
        # store a reference of window in class
        self.open_windows_mscolab = []
        # connection object to interact with sockets
        self.conn = None
        # store window instances
        self.active_windows = []
        # assign ids to view-window
        self.id_count = 0
        # project window
        self.chat_window = None
        # Admin Window
        self.admin_window = None
        # Version History Window
        self.version_window = None
        # set data dir, uri
        self.data_dir = data_dir
        self.mscolab_server_url = None
        self.disable_action_buttons()
        # disabling login, add user button. they are enabled when url is connected
        self.loginButton.setEnabled(False)
        self.addUser.setEnabled(False)
        self.disconnectMscolab.setEnabled(False)

        self.url.setEditable(True)
        self.url.setModel(MSCOLAB_URL_LIST)
        # fill value of mscolab url from config
        default_MSCOLAB = config_loader(
            dataset="default_MSCOLAB", default=mss_default.default_MSCOLAB)
        add_mscolab_urls(self.url, default_MSCOLAB)

        self.emailid.setText(config_loader(dataset="MSCOLAB_mailid", default=""))
        self.password.setText(config_loader(dataset="MSCOLAB_password", default=""))

        # fill value of mscolab url if found in QSettings storage
        self.settings = load_settings_qsettings('mscolab', default_settings={'mscolab_url': None, 'auth': {}})
        if self.settings['mscolab_url'] is not None:
            add_mscolab_urls(self.url, [self.settings['mscolab_url']])

    def disconnect_handler(self):
        self.logout()
        # enable and disable right buttons
        self.disconnectMscolab.setEnabled(False)
        self.loginButton.setEnabled(False)
        self.addUser.setEnabled(False)
        self.connectMscolab.setEnabled(True)
        # set mscolab_server_url to None
        self.mscolab_server_url = None

    def show_info(self, text):
        self.error_dialog = QtWidgets.QErrorMessage()
        self.error_dialog.showMessage(text)

    def connect_handler(self):
        try:
            url = str(self.url.currentText())
            r = requests.get(url)
            if r.text == "Mscolab server":
                # delete mscolab http_auth settings for the url
                if self.mscolab_server_url in self.settings["auth"].keys():
                    del self.settings["auth"][self.mscolab_server_url]
                save_settings_qsettings('mscolab', self.settings)
                # assign new url to self.mscolab_server_url
                self.mscolab_server_url = url
                self.status.setText("Status: connected")
                # enable and disable right buttons
                self.loginButton.setEnabled(True)
                self.addUser.setEnabled(True)
                self.disconnectMscolab.setEnabled(True)
                self.connectMscolab.setEnabled(False)
                self.settings["mscolab_url"] = url
                save_settings_qsettings('mscolab', self.settings)
                return
        except requests.exceptions.ConnectionError:
            logging.debug("mscolab server isn't active")
        except requests.exceptions.InvalidSchema:
            logging.debug("invalid schema of url")
        except requests.exceptions.InvalidURL:
            logging.debug("invalid url")
        except Exception as e:
            logging.debug("Error %s", str(e))
        # inform user that url is invalid
        self.show_info("Invalid url, please try again!")

    def handle_import(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select a file", "", "Flight track (*.ftml)")
        if file_path == "":
            return
        dir_path, file_name = fs.path.split(file_path)
        with open_fs(dir_path) as file_dir:
            xml_content = file_dir.readtext(file_name)
        try:
            model = ft.WaypointsTableModel(xml_content=xml_content)
        except SyntaxError:
            show_popup(self, "Import Failed", f"The file - {file_name}, does not contain valid XML")
            return
        self.waypoints_model = model
        if self.workLocallyCheckBox.isChecked():
            self.waypoints_model.save_to_ftml(self.local_ftml_file)
            self.waypoints_model.dataChanged.connect(self.handle_local_data_changed)
        else:
            self.conn.save_file(self.token, self.active_pid, xml_content, comment=None)
            self.waypoints_model.dataChanged.connect(self.handle_mscolab_autosave)
        show_popup(self, "Import Success", f"The file - {file_name}, was imported successfully!", 1)

    def handle_export(self):
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Flight track", self.active_project_name,
                                                             f"Flight track (*.ftml)")
        if file_path == "":
            return
        xml_doc = self.waypoints_model.get_xml_doc()
        dir_path, file_name = fs.path.split(file_path)
        with open_fs(dir_path).open(file_name, 'w') as file:
            xml_doc.writexml(file, indent="  ", addindent="  ", newl="\n", encoding="utf-8")

    def disable_project_buttons(self):
        self.save_ft.setEnabled(False)
        self.fetch_ft.setEnabled(False)
        self.topview.setEnabled(False)
        self.sideview.setEnabled(False)
        self.tableview.setEnabled(False)
        self.workLocallyCheckBox.setEnabled(False)
        self.importBtn.setEnabled(False)
        self.exportBtn.setEnabled(False)
        self.chatWindowBtn.setEnabled(False)
        self.adminWindowBtn.setEnabled(False)
        self.versionHistoryBtn.setEnabled(False)

    def disable_action_buttons(self):
        # disable some buttons to be activated after successful login or project activate
        self.addProject.setEnabled(False)
        self.disable_project_buttons()

    def add_project_handler(self):
        if self.token is None:
            self.error_dialog = QtWidgets.QErrorMessage()
            self.error_dialog.showMessage('Please login to use this feature')
            return
        else:
            logging.debug(self.token)
        self.proj_diag = QtWidgets.QDialog()
        self.add_proj_dialog = add_project_ui.Ui_addProjectDialog()
        self.add_proj_dialog.setupUi(self.proj_diag)
        self.add_proj_dialog.f_content = None
        self.add_proj_dialog.buttonBox.accepted.connect(self.add_project)
        # enable accepted only if path and description are not none
        self.add_proj_dialog.buttonBox.setEnabled(False)
        self.add_proj_dialog.path.textChanged.connect(self.check_and_enable_project_accept)
        self.add_proj_dialog.description.textChanged.connect(self.check_and_enable_project_accept)
        self.add_proj_dialog.browse.clicked.connect(self.set_exported_file)
        self.proj_diag.show()

    def check_and_enable_project_accept(self):
        if self.add_proj_dialog.path.text() != "" and self.add_proj_dialog.description.toPlainText() != "":
            self.add_proj_dialog.buttonBox.setEnabled(True)

    def set_exported_file(self):
        file_path = get_open_filename(
            self, "Open ftml file", "", "Flight Track Files (*.ftml)")
        if file_path is not None:
            f_name = path.basename(file_path)
            f_dir = open_fs(path.dirname(file_path))
            f_content = f_dir.readtext(f_name)
            self.add_proj_dialog.f_content = f_content
            self.add_proj_dialog.selectedFile.setText(f_name)

    def add_project(self):
        path = self.add_proj_dialog.path.text()
        description = self.add_proj_dialog.description.toPlainText()
        # ToDo if path and description is null alert user
        if not path:
            self.error_dialog = QtWidgets.QErrorMessage()
            self.error_dialog.showMessage('Path can\'t be empty')
            return
        elif not description:
            self.error_dialog = QtWidgets.QErrorMessage()
            self.error_dialog.showMessage('Description can\'t be empty')
            return

        data = {
            "token": self.token,
            "path": path,
            "description": description
        }
        if self.add_proj_dialog.f_content is not None:
            data["content"] = self.add_proj_dialog.f_content
        r = requests.post('{}/create_project'.format(self.mscolab_server_url), data=data)
        if r.text == "True":
            self.error_dialog = QtWidgets.QErrorMessage()
            self.error_dialog.showMessage('Your project was created successfully')
            self.add_projects()
            p_id = self.get_recent_pid()
            self.conn.handle_new_room(p_id)
        else:
            self.error_dialog = QtWidgets.QErrorMessage()
            self.error_dialog.showMessage('The path already exists')

    def add_user_handler(self):
        self.user_diag = QtWidgets.QDialog()
        self.add_user_dialog = add_user_ui.Ui_addUserDialog()
        self.add_user_dialog.setupUi(self.user_diag)
        self.add_user_dialog.buttonBox.accepted.connect(self.add_user)
        self.user_diag.show()

    def add_user(self):
        emailid = self.add_user_dialog.emailid.text()
        password = self.add_user_dialog.password.text()
        re_password = self.add_user_dialog.rePassword.text()
        username = self.add_user_dialog.username.text()
        if password == re_password:
            data = {
                "email": emailid,
                "password": password,
                "username": username
            }
            r = requests.post('{}/register'.format(self.mscolab_server_url), data=data).json()
            if r["success"]:
                self.error_dialog = QtWidgets.QErrorMessage()
                self.error_dialog.showMessage('You are registered, you can now log in.')
            else:
                self.error_dialog = QtWidgets.QErrorMessage()
                self.error_dialog.showMessage(r["message"])
        else:
            self.error_dialog = QtWidgets.QErrorMessage()
            self.error_dialog.showMessage('Oh no, your passwords don\'t match')

    def open_chat_window(self):
        if self.active_pid is None:
            return

        if self.chat_window is not None:
            self.chat_window.raise_()
            self.chat_window.activateWindow()
            return

        self.chat_window = mp.MSColabProjectWindow(self.token, self.active_pid, self.user, self.active_project_name,
                                                   self.access_level, self.conn,
                                                   mscolab_server_url=self.mscolab_server_url)
        self.chat_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.chat_window.viewCloses.connect(self.close_chat_window)
        self.chat_window.reloadWindows.connect(self.reload_windows_slot)
        self.chat_window.show()

    def close_chat_window(self):
        self.chat_window = None

    def open_admin_window(self):
        if self.active_pid is None:
            return

        if self.admin_window is not None:
            self.admin_window.raise_()
            self.admin_window.activateWindow()
            return

        self.admin_window = maw.MSColabAdminWindow(self.token, self.active_pid, self.user,
                                                   self.active_project_name, self.projects, self.conn,
                                                   mscolab_server_url=self.mscolab_server_url)
        self.admin_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.admin_window.viewCloses.connect(self.close_admin_window)
        self.admin_window.show()

    def close_admin_window(self):
        self.admin_window = None

    def open_version_history_window(self):
        if self.active_pid is None:
            return

        if self.version_window is not None:
            self.version_window.raise_()
            self.version_window.activateWindow()
            return

        self.version_window = mvh.MSColabVersionHistory(self.token, self.active_pid, self.user,
                                                        self.active_project_name, self.conn,
                                                        mscolab_server_url=self.mscolab_server_url)
        self.version_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.version_window.viewCloses.connect(self.close_version_history_window)
        self.version_window.reloadWindows.connect(self.reload_windows_slot)
        self.version_window.show()

    def close_version_history_window(self):
        self.version_window = None

    def create_local_project_file(self):
        with open_fs(self.data_dir) as mss_dir:
            rel_file_path = path.join('local_mscolab_data', self.user['username'],
                                      self.active_project_name, 'mscolab_project.ftml')
            if mss_dir.exists(rel_file_path) is True:
                return
            mss_dir.makedirs(path.dirname(rel_file_path))
            server_data = self.waypoints_model.get_xml_content()
            mss_dir.writetext(rel_file_path, server_data)

    def handle_work_locally_toggle(self):
        if self.workLocallyCheckBox.isChecked():
            if self.version_window is not None:
                self.version_window.close()
            self.create_local_project_file()
            self.local_ftml_file = path.join(self.data_dir, 'local_mscolab_data',
                                             self.user['username'], self.active_project_name, 'mscolab_project.ftml')
            self.save_ft.setEnabled(True)
            self.fetch_ft.setEnabled(True)
            self.versionHistoryBtn.setEnabled(False)
            self.reload_local_wp()
        else:
            self.local_ftml_file = None
            self.save_ft.setEnabled(False)
            self.fetch_ft.setEnabled(False)
            if self.access_level == "admin" or self.access_level == "creator":
                self.versionHistoryBtn.setEnabled(True)
            self.waypoints_model = None
            self.load_wps_from_server()

    def authorize(self):
        auth = ('', '')
        self.settings = load_settings_qsettings('mscolab', default_settings={'auth': {}})
        if self.mscolab_server_url in self.settings["auth"].keys():
            auth = self.settings["auth"][self.mscolab_server_url]
        # get mscolab /token http auth credentials from cache
        emailid = self.emailid.text()
        password = self.password.text()
        data = {
            "email": emailid,
            "password": password
        }
        r = requests.post(self.mscolab_server_url + '/token', data=data, auth=HTTPBasicAuth(auth[0], auth[1]))
        if r.status_code == 401:
            dlg = MSCOLAB_AuthenticationDialog(parent=self)
            dlg.setModal(True)
            if dlg.exec_() == QtWidgets.QDialog.Accepted:
                username, password = dlg.getAuthInfo()
                self.settings["auth"][self.mscolab_server_url] = (username, password)
                # save to cache
                save_settings_qsettings('mscolab', self.settings)
        elif r.text == "False":
            # popup that has wrong credentials
            self.error_dialog = QtWidgets.QErrorMessage()
            self.error_dialog.showMessage('Oh no, your credentials were incorrect.')
            pass
        else:
            # remove the login modal and put text there
            _json = json.loads(r.text)
            self.token = _json["token"]
            self.user = _json["user"]
            self.label.setText("logged in as: " + _json["user"]["username"])
            self.loggedInWidget.show()
            self.loginWidget.hide()

            self.add_projects()

            # create socket connection here
            self.conn = sc.ConnectionManager(self.token, user=self.user, mscolab_server_url=self.mscolab_server_url)
            self.conn.signal_reload.connect(self.reload_window)
            self.conn.signal_new_permission.connect(self.render_new_permission)
            self.conn.signal_update_permission.connect(self.handle_update_permission)
            self.conn.signal_revoke_permission.connect(self.handle_revoke_permission)
            # activate add project button here
            self.addProject.setEnabled(True)

    def add_projects(self):
        # add projects
        data = {
            "token": self.token
        }
        r = requests.get(self.mscolab_server_url + '/projects', data=data)
        _json = json.loads(r.text)
        self.projects = _json["projects"]
        self.add_projects_to_ui(self.projects)

    def get_recent_pid(self):
        """
        get most recent project's p_id
        # ToDo can be merged with get_recent_project
        """
        data = {
            "token": self.token
        }
        r = requests.get(self.mscolab_server_url + '/projects', data=data)
        _json = json.loads(r.text)
        projects = _json["projects"]
        return projects[-1]["p_id"]

    def get_recent_project(self):
        """
        get most recent project
        """
        data = {
            "token": self.token
        }
        r = requests.get(self.mscolab_server_url + '/projects', data=data)
        _json = json.loads(r.text)
        projects = _json["projects"]
        return projects[-1]

    def add_projects_to_ui(self, projects):
        logging.debug("adding projects to ui")
        self.listProjects.clear()
        selectedProject = None
        for project in projects:
            project_desc = f'{project["path"]} - {project["access_level"]}'
            widgetItem = QtWidgets.QListWidgetItem(project_desc, parent=self.listProjects)
            widgetItem.p_id = project["p_id"]
            widgetItem.access_level = project["access_level"]
            if widgetItem.p_id == self.active_pid:
                selectedProject = widgetItem
            self.listProjects.addItem(widgetItem)
        if selectedProject is not None:
            self.listProjects.setCurrentItem(selectedProject)
            self.listProjects.itemActivated.emit(selectedProject)
        self.listProjects.itemActivated.connect(self.set_active_pid)

    def set_active_pid(self, item):
        if item.p_id == self.active_pid:
            return
            # close all hanging window
        for window in self.active_windows:
            window.close()
        if self.version_window is not None:
            self.version_window.close()
        if self.chat_window is not None:
            self.chat_window.close()
        if self.admin_window is not None:
            self.admin_window.close()
        # Turn off work locally toggle
        self.workLocallyCheckBox.blockSignals(True)
        self.workLocallyCheckBox.setChecked(False)
        self.workLocallyCheckBox.blockSignals(False)
        self.save_ft.setEnabled(False)
        self.fetch_ft.setEnabled(False)

        # set active_pid here
        self.active_pid = item.p_id
        self.access_level = item.access_level
        self.active_project_name = item.text().split("-")[0].strip()
        self.waypoints_model = None
        # set active flightpath here
        self.load_wps_from_server()
        # enable project specific buttons
        self.importBtn.setEnabled(True)
        self.exportBtn.setEnabled(True)
        self.topview.setEnabled(True)
        self.sideview.setEnabled(True)
        self.tableview.setEnabled(True)
        self.workLocallyCheckBox.setEnabled(True)

        if self.access_level == "viewer" or self.access_level == "collaborator":
            if self.access_level == "viewer":
                self.chatWindowBtn.setEnabled(False)
            else:
                self.chatWindowBtn.setEnabled(True)
            self.adminWindowBtn.setEnabled(False)
            self.versionHistoryBtn.setEnabled(False)
        else:
            self.adminWindowBtn.setEnabled(True)
            self.chatWindowBtn.setEnabled(True)
            self.versionHistoryBtn.setEnabled(True)

        # change font style for selected
        font = QtGui.QFont()
        for i in range(self.listProjects.count()):
            self.listProjects.item(i).setFont(font)
        font.setBold(True)
        item.setFont(font)

    def reload_wps_from_server(self):
        if self.active_pid is None:
            return
        self.load_wps_from_server()
        for window in self.active_windows:
            # set active flight track
            window.setFlightTrackModel(self.waypoints_model)
            # redraw figure *only for canvas based window, not tableview*
            if hasattr(window, 'mpl'):
                window.mpl.canvas.waypoints_interactor.redraw_figure()

    def request_wps_from_server(self):
        data = {
            "token": self.token,
            "p_id": self.active_pid
        }
        r = requests.get(self.mscolab_server_url + '/get_project', data=data)
        xml_content = json.loads(r.text)["content"]
        return xml_content

    def load_wps_from_server(self):
        if self.workLocallyCheckBox.isChecked():
            return
        xml_content = self.request_wps_from_server()
        self.waypoints_model = ft.WaypointsTableModel(xml_content=xml_content)
        self.waypoints_model.dataChanged.connect(self.handle_mscolab_autosave)

    def open_topview(self):
        # showing dummy info dialog
        if self.active_pid is None:
            return
        self.create_view_window("topview")

    def open_sideview(self):
        # showing dummy info dialog
        if self.active_pid is None:
            return
        self.create_view_window("sideview")

    def open_tableview(self):
        # showing dummy info dialog
        if self.active_pid is None:
            return
        self.create_view_window("tableview")

    def create_view_window(self, _type):
        view_window = None
        if _type == "topview":
            view_window = topview.MSSTopViewWindow(model=self.waypoints_model,
                                                   parent=self.listProjects,
                                                   _id=self.id_count)
            view_window.view_type = "topview"
        elif _type == "sideview":
            view_window = sideview.MSSSideViewWindow(model=self.waypoints_model,
                                                     parent=self.listProjects,
                                                     _id=self.id_count)
            view_window.view_type = "sideview"
        else:
            view_window = tableview.MSSTableViewWindow(model=self.waypoints_model,
                                                       parent=self.listProjects,
                                                       _id=self.id_count)
            view_window.view_type = "tableview"
        if self.access_level == "viewer":
            self.disable_navbar_action_buttons(_type, view_window)

        view_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        view_window.show()
        view_window.viewClosesId.connect(self.handle_view_close)
        self.active_windows.append(view_window)

        # increment id_count
        self.id_count += 1

    def disable_navbar_action_buttons(self, _type, view_window):
        """
        _type: view type (topview, sideview, tableview)
        view_window: PyQt view window

        function disables some control, used if access_level is not appropriate
        """
        if _type == "topview" or _type == "sideview":
            actions = view_window.mpl.navbar.actions()
            for action in actions:
                action_text = action.text()
                if action_text == "Ins WP" or action_text == "Del WP" or action_text == "Mv WP":
                    action.setEnabled(False)
        else:
            # _type == tableview
            view_window.btAddWayPointToFlightTrack.setEnabled(False)
            view_window.btCloneWaypoint.setEnabled(False)
            view_window.btDeleteWayPoint.setEnabled(False)
            view_window.btInvertDirection.setEnabled(False)

    def enable_navbar_action_buttons(self, _type, view_window):
        """
        _type: view type (topview, sideview, tableview)
        view_window: PyQt view window

        function enables some control, used if access_level is appropriate
        """
        if _type == "topview" or _type == "sideview":
            actions = view_window.mpl.navbar.actions()
            for action in actions:
                action_text = action.text()
                if action_text == "Ins WP" or action_text == "Del WP" or action_text == "Mv WP":
                    action.setEnabled(True)
        else:
            # _type == tableview
            view_window.btAddWayPointToFlightTrack.setEnabled(True)
            view_window.btCloneWaypoint.setEnabled(True)
            view_window.btDeleteWayPoint.setEnabled(True)
            view_window.btInvertDirection.setEnabled(True)

    def logout(self):
        self.clean_up_window()

    def delete_account(self):
        w = QtWidgets.QWidget()
        qm = QtWidgets.QMessageBox
        reply = qm.question(w, 'Continue?', 'You cannot undo this operation!', qm.Yes, qm.No)
        if reply == QtWidgets.QMessageBox.No:
            return
        data = {
            "token": self.token
        }
        requests.post(self.mscolab_server_url + '/delete_user', data=data)
        self.clean_up_window()

    def clean_up_window(self):
        # delete token and show login widget-items
        self.token = None
        # delete active-project-id
        self.active_pid = None
        # delete active access_level
        self.access_level = None
        # delete active project_name
        self.active_project_name = None
        # delete local file name
        self.local_ftml_file = None
        # clear projects list here
        self.loggedInWidget.hide()
        self.loginWidget.show()
        # clear project listing
        self.listProjects.clear()
        # disconnect socket
        if self.conn is not None:
            self.conn.disconnect()
            self.conn = None
        # close all hanging window
        for window in self.active_windows:
            window.close()
        # close project window if active
        if self.chat_window is not None:
            self.chat_window.close()
        # Close Admin Window if active
        if self.admin_window is not None:
            self.admin_window.close()
        if self.version_window is not None:
            self.version_window.close()
        self.disable_action_buttons()

        # delete mscolab http_auth settings for the url
        if self.mscolab_server_url in self.settings["auth"].keys():
            del self.settings["auth"][self.mscolab_server_url]
        save_settings_qsettings('mscolab', self.settings)

    def handle_mscolab_autosave(self, comment=None):
        xml_content = self.waypoints_model.get_xml_content()
        self.conn.save_file(self.token, self.active_pid, xml_content, comment=None)

    def save_wp_mscolab(self, comment=None):
        server_xml = self.request_wps_from_server()
        server_waypoints_model = ft.WaypointsTableModel(xml_content=server_xml)
        merge_waypoints_dialog = MscolabMergeWaypointsDialog(self.waypoints_model, server_waypoints_model, self)
        if merge_waypoints_dialog.exec_():
            xml_content = merge_waypoints_dialog.get_values()
            if xml_content is not None:
                self.conn.save_file(self.token, self.active_pid, xml_content, comment=comment)
                self.waypoints_model = ft.WaypointsTableModel(xml_content=xml_content)
                self.waypoints_model.save_to_ftml(self.local_ftml_file)
                self.waypoints_model.dataChanged.connect(self.handle_local_data_changed)

    def handle_local_data_changed(self):
        self.waypoints_model.save_to_ftml(self.local_ftml_file)

    def reload_local_wp(self):
        self.waypoints_model = ft.WaypointsTableModel(filename=self.local_ftml_file, data_dir=self.data_dir)
        self.waypoints_model.dataChanged.connect(self.handle_local_data_changed)
        for window in self.active_windows:
            window.setFlightTrackModel(self.waypoints_model)
            if hasattr(window, 'mpl'):
                window.mpl.canvas.waypoints_interactor.redraw_figure()

    def fetch_wp_mscolab(self):
        # Fetch the latest changes from the server
        xml_content = self.request_wps_from_server()
        # Over write the local file with the fetched data
        with open_fs(self.data_dir) as mss_dir:
            relative_file_path = path.relativefrom(self.data_dir, self.local_ftml_file)
            mss_dir.writetext(relative_file_path, xml_content)
            self.reload_local_wp()

    @QtCore.Slot(int, int, str)
    def handle_update_permission(self, p_id, u_id, access_level):
        """
        p_id: project id
        u_id: user id
        access_level: updated access level

        function updates existing permissions and related control availability
        """
        if u_id == self.user["id"]:
            # update table of projects
            for i in range(self.listProjects.count()):
                item = self.listProjects.item(i)
                if item.p_id == p_id:
                    desc = item.text().split(' - ')
                    desc[-1] = access_level
                    desc = ' - '.join(desc)
                    item.setText(desc)
                    item.p_id = p_id
                    item.access_level = access_level
            if p_id != self.active_pid:
                return
            self.access_level = access_level
            # Close mscolab windows based on new access_level and update their buttons
            if self.access_level == "collaborator" or self.access_level == "viewer":
                self.adminWindowBtn.setEnabled(True)
                self.versionHistoryBtn.setEnabled(True)
                if self.admin_window is not None:
                    self.admin_window.close()
                if self.version_window is not None:
                    self.version_window.close()
            else:
                self.adminWindowBtn.setEnabled(True)
                self.versionHistoryBtn.setEnabled(True)

            if self.access_level == "viewer":
                self.chatWindowBtn.setEnabled(False)
                if self.chat_window is not None:
                    self.chat_window.close()
            else:
                self.chatWindowBtn.setEnabled(True)
            # update view window nav elements if open
            for window in self.active_windows:
                _type = window.view_type
                if self.access_level == "viewer":
                    self.disable_navbar_action_buttons(_type, window)
                else:
                    self.enable_navbar_action_buttons(_type, window)
        # update project window if open
        if self.chat_window is not None:
            self.chat_window.load_users()

    @QtCore.Slot(int, int)
    def handle_revoke_permission(self, p_id, u_id):
        if u_id == self.user["id"]:
            # Check if the user has opened any windows of revoked project and close them
            if self.active_pid == p_id:
                for window in self.active_windows:
                    window.close()
                if self.chat_window is not None:
                    self.chat_window.close()
                if self.admin_window is not None:
                    self.admin_window.close()
                if self.version_window is not None:
                    self.version_window.close()
                self.active_pid = None
                self.access_level = None
                self.active_project_name = None
                self.disable_project_buttons()

            # Update project list
            remove_item = None
            for i in range(self.listProjects.count()):
                item = self.listProjects.item(i)
                if item.p_id == p_id:
                    remove_item = item
            if remove_item is not None:
                self.listProjects.takeItem(self.listProjects.row(remove_item))

    @QtCore.Slot()
    def reload_windows_slot(self):
        self.reload_window(self.active_pid)

    @QtCore.Slot(int, int)
    def render_new_permission(self, p_id, u_id):
        """
        p_id: project id
        u_id: user id

        to render new permission if added
        """
        data = {
            'token': self.token
        }
        r = requests.get(self.mscolab_server_url + '/user', data=data)
        _json = json.loads(r.text)
        if _json['user']['id'] == u_id:
            project = self.get_recent_project()
            project_desc = f'{project["path"]} - {project["access_level"]}'
            widgetItem = QtWidgets.QListWidgetItem(project_desc, parent=self.listProjects)
            widgetItem.p_id = project["p_id"]
            widgetItem.access_level = project["access_level"]
            self.listProjects.addItem(widgetItem)
        if self.chat_window is not None:
            self.chat_window.load_users()

    @QtCore.Slot(int)
    def reload_window(self, value):
        if self.active_pid != value or self.workLocallyCheckBox.isChecked():
            return
        self.reload_wps_from_server()

    @QtCore.Slot(int)
    def handle_view_close(self, value):
        logging.debug("removing stale window")
        for index, window in enumerate(self.active_windows):
            if window._id == value:
                del self.active_windows[index]

    def setIdentifier(self, identifier):
        self.identifier = identifier

    def closeEvent(self, event):
        if self.conn:
            self.conn.disconnect()
        self.viewCloses.emit()


class MSCOLAB_AuthenticationDialog(QtWidgets.QDialog, ui_pw.Ui_WMSAuthenticationDialog):
    """Dialog to ask the user for username/password should this be
       required by a WMS server.
    """

    def __init__(self, parent=None):
        """
        Arguments:
        parent -- Qt widget that is parent to this widget.
        """
        super(MSCOLAB_AuthenticationDialog, self).__init__(parent)
        self.setupUi(self)

    def getAuthInfo(self):
        """Return the entered username and password.
        """
        return (self.leUsername.text(),
                self.lePassword.text())


class MscolabMergeWaypointsDialog(QtWidgets.QDialog, ui_mscolab_merge_waypoints_dialog.Ui_MergeWaypointsDialog):
    def __init__(self, local_waypoints_model, server_waypoints_model, parent=None):
        super(MscolabMergeWaypointsDialog, self).__init__(parent)
        self.setupUi(self)

        self.local_waypoints_model = local_waypoints_model
        self.server_waypoints_model = server_waypoints_model
        self.merge_waypoints_model = ft.WaypointsTableModel()
        self.localWaypointsTable.setModel(self.local_waypoints_model)
        self.serverWaypointsTable.setModel(self.server_waypoints_model)
        self.mergedWaypointsTable.setModel(self.merge_waypoints_model)
        self.mergedWaypointsTable.dropEvent = types.MethodType(dropEvent, self.mergedWaypointsTable)
        self.mergedWaypointsTable.dragEnterEvent = types.MethodType(dragEnterEvent, self.mergedWaypointsTable)

        self.xml_content = None
        self.local_waypoints_dict = {}
        self.server_waypoints_dict = {}
        self.merge_waypoints_list = []

        # Event Listeners
        self.overwriteBtn.clicked.connect(lambda: self.save_waypoints(self.local_waypoints_model))
        self.keepServerBtn.clicked.connect(lambda: self.save_waypoints(self.server_waypoints_model))
        self.saveBtn.clicked.connect(lambda: self.save_waypoints(self.merge_waypoints_model))
        self.localWaypointsTable.selectionModel().selectionChanged.connect(
            lambda selected, deselected:
            self.handle_selection(selected, deselected, self.local_waypoints_model, self.local_waypoints_dict)
        )
        self.serverWaypointsTable.selectionModel().selectionChanged.connect(
            lambda selected, deselected:
            self.handle_selection(selected, deselected, self.server_waypoints_model, self.server_waypoints_dict)
        )

    def handle_selection(self, selected, deselected, wp_model, wp_dict):
        len_selected = len(selected.indexes())
        len_deselected = len(deselected.indexes())

        for index in range(0, len_selected, 15):
            row = selected.indexes()[index].row()
            waypoint = wp_model.waypoint_data(row)
            wp_dict[row] = waypoint
            self.merge_waypoints_list.append(waypoint)

        for index in range(0, len_deselected, 15):
            row = deselected.indexes()[index].row()
            delete_waypoint = wp_dict[row]
            self.merge_waypoints_list.remove(delete_waypoint)

        self.merge_waypoints_model = ft.WaypointsTableModel(waypoints=self.merge_waypoints_list)
        self.mergedWaypointsTable.setModel(self.merge_waypoints_model)

    def save_waypoints(self, waypoints_model):
        if waypoints_model.rowCount() == 0:
            return
        self.xml_content = waypoints_model.get_xml_content()
        self.accept()

    def get_values(self):
        return self.xml_content

