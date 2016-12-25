#!/usr/bin/python

#  Copyright (C) 2015, Samsung Electronics, Co., Ltd. All Rights Reserved.
#  #  Written by System S/W 2 Group, S/W Platform R&D Team,
#  #  Mobile Communication Division.
#  ##
#
#  ##
#  # Project Name : abget
#  #
#  # Project Description :
#  #
#  # Comments : tabstop = 8, shiftwidth = 8 noexpandtab
#  ##
#
#  ##
#  # File Name : abget.py
#  #
#  # File Description :
#  #
#  # Author : Byeong Jun Mun(bjun.mun@samsung.com)
#  # Dept : System S/W R&D Team Grp.2
#  # Created Date : 09-June-2015
#  # Last Update: 1-Sep-2015
#  ##

VERSION = "0.953"

from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import os
import wx.lib.agw.ultimatelistctrl as ULC
import wx
import abget
import pyodin
import time
import threading
import commands
import sys
import webbrowser
import signal
import ConfigParser

EVT_RESULT_ID = wx.NewId()
def EVT_RESULT(win, func):
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class LoginDialog(wx.Dialog):
    """
    Class to define login dialog
    """
    #----------------------------------------------------------------------
    def __init__(self, qb, config, username = '', password = ''):

        """Constructor"""
        wx.Dialog.__init__(self, None, title="Quick Build Login",\
                size = (260, 170))
        self.logged_in = False
        self.qb = qb
        self.config = config

        # user info
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)

        user_lbl = wx.StaticText(self, label="Username:")
        user_sizer.Add(user_lbl, 0, wx.ALL|wx.CENTER, 5)
        self.user = wx.TextCtrl(self, size = (-1, 25))
        self.user.SetValue(username)
        user_sizer.Add(self.user, 1, wx.ALL|wx.EXPAND, 5)

        # pass info
        p_sizer = wx.BoxSizer(wx.HORIZONTAL)
        p_lbl = wx.StaticText(self, label="Password:")
        p_sizer.Add(p_lbl, 0, wx.ALL|wx.CENTER, 5)
        self.password = wx.TextCtrl(self, size = (-1, 25), style=wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)
        self.password.SetValue(password)
        self.password.Bind(wx.EVT_TEXT_ENTER, self.onLogin)
        p_sizer.Add(self.password, 1, wx.ALL|wx.EXPAND, 5)

        self.messageLabel = wx.StaticText(self, -1, label = "")
        self.messageLabel.SetForegroundColour((255,0,0))

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(user_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(p_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.messageLabel, 1, wx.ALL | wx.EXPAND, 5)

        btn = wx.Button(self, label="Login")
        btn.Bind(wx.EVT_BUTTON, self.onLogin)
        main_sizer.Add(btn, 1, wx.ALL|wx.CENTER, 5)

        self.SetSizer(main_sizer)

    #----------------------------------------------------------------------
    def onLogin(self, event):
        """
        Check credentials and login
        """
        if self.logginInQb() == True:
            self.Close()

    def logginInQb(self):
        username = self.user.GetValue()
        password = self.password.GetValue()
        if self.qb.login(username, password, self.config) is True:
            print "You are now logged in!"
            self.logged_in = True
            return True
        else:
            print "Username or password is incorrect!"
            self.messageLabel.SetLabel("Username or password is incorrect!")
            return False

class OdinBinaryListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, size=(200, 200), style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

        self.InsertColumn(0, 'Path', width=300)
        self.InsertColumn(1, 'File name', width=100)
        self.index = 0
        self.binary_list = []
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnClickItem, self)

    def OnClickItem(self, event):
        idx = event.m_itemIndex
        if self.IsChecked(idx) == True:
            self.CheckItem(idx, False)
        else:
            self.CheckItem(idx)

    def addItem(self, name):
        file_name = os.path.basename(name)
        dir_name = os.path.dirname(name)

        self.InsertStringItem(self.index, dir_name)
        self.SetStringItem(self.index, 1, file_name)
        self.index += 1

    def addItems(self, items):
        self.binary_list += items
        for item in items:
            self.addItem(item)

    def getBinaryList(self):
        return self.binary_list

    def resetList(self):
        self.DeleteAllItems()
        del self.binary_list[:]
        self.index = 0

class OdinOptionsCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, size=(300, 200), style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

        self.InsertColumn(0, 'Options', width=200)
        self.index = 0
        self.addItem('Auto Reboot')
        self.addItem('Re-Partition')
        self.addItem('F.Reset Time')
        self.addItem('DeviceInfo')
        self.addItem('Nand Erase All')
        self.addItem('Flash Lock')
        self.addItem('TFlash')
        self.addItem('Phone EFS Clear')
        self.addItem('Phone Bootloader Update')
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnClickItem, self)

    def OnClickItem(self, event):
        idx = event.m_itemIndex
        if self.IsChecked(idx) == True:
            self.CheckItem(idx, False)
        else:
            self.CheckItem(idx)

    def addItem(self, name):
        self.InsertStringItem(self.index, name)
        self.index += 1


class ProjectListCtrl(wx.ListCtrl):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, size=(200, -1), style=wx.LC_REPORT | wx.SUNKEN_BORDER)

        self.InsertColumn(0, 'Project', width=200)
        self.index = 0

    def addProjectItem(self, project_name):
        self.InsertStringItem(self.index, project_name)
        self.index += 1

class BinaryListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, id, size=(200, 200), style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

        self.InsertColumn(0, 'Download Binary', width=200)
        self.index = 0
        self.addItem('pit')
        self.addItem('BL')
        self.addItem('AP')
        self.addItem('CP')
        self.addItem('CSC')
        self.addItem('DEBUG_KERNEL')

        self.selectAll()
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnClickItem, self)

    def addItem(self, name):
#        self.build_list_ctrl.InsertStringItem(self.load_num, build_id)
#        self.build_list_ctrl.SetStringItem(self.load_num, 1, mode)

        self.InsertStringItem(self.index, name)
        self.index += 1

    def selectAll(self):
        num = self.GetItemCount()
        for i in xrange(num):
            self.CheckItem(i)

    def OnClickItem(self, event):
        idx = event.m_itemIndex
        if self.IsChecked(idx) == True:
            self.CheckItem(idx, False)
        else:
            self.CheckItem(idx)

    def getItemStatus(self):

        pit = self.IsChecked(0)
        bl = self.IsChecked(1)
        ap = self.IsChecked(2)
        cp = self.IsChecked(3)
        csc = self.IsChecked(4)
        debug = self.IsChecked(4)

        return pit, bl, ap, cp, csc, debug

    def isPitChecked(self):
        return self.IsChecked(0)

    def isBlChecked(self):
        return self.IsChecked(1)

    def isApChecked(self):
        return self.IsChecked(2)

    def isCpChecked(self):
        return self.IsChecked(3)

    def isCscChecked(self):
        return self.IsChecked(4)

    def isDebugChecked(self):
        return self.IsChecked(5)

    def setCheckPit(self, val):
        self.CheckItem(0, val)

    def setCheckBl(self, val):
        self.CheckItem(1, val)

    def setCheckAp(self, val):
        self.CheckItem(2, val)

    def setCheckCp(self, val):
        self.CheckItem(3, val)

    def setCheckCsc(self, val):
        self.CheckItem(4, val)

    def setCheckDebug(self, val):
        self.CheckItem(5, val)

class EnvData():
    def __init__(self, config):
        self.gui_config, self.gui_cfg_path = config.openConfig('.pyodin_gui.cfg')
        if self.gui_config is not None:
            self.pitChecked = self.gui_config.getboolean("LAST_DATA","PIT")
            self.blChecked = self.gui_config.getboolean("LAST_DATA","BL")
            self.apChecked = self.gui_config.getboolean("LAST_DATA","AP")
            self.cpChecked = self.gui_config.getboolean("LAST_DATA","CP")
            self.cscChecked = self.gui_config.getboolean("LAST_DATA","CSC")
            self.lastSelectProject = self.gui_config.get("LAST_DATA","PROJECT")
            self.lastSelectCfg = self.gui_config.get("LAST_DATA","CFG")

            if self.isExist("debug") is True:
                self.debugChecked = self.gui_config.getboolean("LAST_DATA","DEBUG")
            else:
                self.debugChecked = True

            if self.isExist("auto_down") is True:
                self.autoDownChecked = self.gui_config.getboolean("LAST_DATA","auto_down")
            else:
                self.autoDownChecked = False

            if self.isExist("file_path") is True:
                self.lastFilePath = self.gui_config.get("LAST_DATA","file_path")
            else:
                self.lastFilePath = os.getcwd()

        else:
            self.pitChecked = True
            self.blChecked = True
            self.apChecked = True
            self.cpChecked = True
            self.cscChecked = True
            self.debugChecked = True
            self.autoDownChecked = False
            self.lastFilePath = os.getcwd()
            self.lastSelectProject = ""
            self.lastSelectCfg = ""

    def isExist(self, keyname):
        for key in self.gui_config.items("LAST_DATA"):
            if key[0] == keyname:
                return True
        return False

    def saveLastData(self, pit, bl, ap, cp, csc, debug, auto, path, project, cfg):
        Config = ConfigParser.ConfigParser()
        Config.add_section("LAST_DATA")
        Config.set("LAST_DATA", "PIT", pit)
        Config.set("LAST_DATA", "BL", bl)
        Config.set("LAST_DATA", "AP", ap)
        Config.set("LAST_DATA", "CP", cp)
        Config.set("LAST_DATA", "CSC", csc)
        Config.set("LAST_DATA", "DEBUG", debug)
        Config.set("LAST_DATA", "AUTO_DOWN", auto)
        Config.set("LAST_DATA", "file_path", path)
        Config.set("LAST_DATA", "PROJECT", project)
        Config.set("LAST_DATA", "CFG", cfg)

        cfgfile = open(self.gui_cfg_path, 'w')
        Config.write(cfgfile)
        cfgfile.close()

class AbgetTabPanel(wx.Panel):
    ID_POPMENU_OPEN_WEB = 301

    def __init__(self, parent, config, qb, downloadMethod = None):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.config = config
        self.qb = qb
        self.downloadMethod = downloadMethod

        self.show_build_enabled = False
        self.show_build_thread = None

        font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        boldfont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        boldfont.SetWeight(wx.BOLD)
        boldfont.SetPointSize(12)

        self.build_list_ctrl = ULC.UltimateListCtrl(self, wx.ID_ANY,\
                   agwStyle=wx.LC_REPORT|wx.LC_VRULES|wx.LC_HRULES|wx.LC_SINGLE_SEL|\
                  ULC.ULC_HAS_VARIABLE_ROW_HEIGHT )

        self.build_list_ctrl.InsertColumn(0, 'ID', width=100)
        self.build_list_ctrl.InsertColumn(1, 'Mode', width=50)
        self.build_list_ctrl.InsertColumn(2, 'Begin Date', width=160)
        self.build_list_ctrl.InsertColumn(3, 'Status', width=125)
        self.build_list_ctrl.InsertColumn(4, 'HW rev', width=50)
        self.build_list_ctrl.InsertColumn(5, 'Version', width=260)
        self.build_list_ctrl.InsertColumn(6, 'Triggered by', width=200)
        self.build_list_ctrl.InsertColumn(7, 'Duration', width=200)
        self.load_num = 0
        self.build_list = []
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectBuild,\
                        self.build_list_ctrl)

        self.popupmenu = wx.Menu()
        popup_handler = [
                [ "Open build page", self.OnOpenBuildPage, \
                            self.ID_POPMENU_OPEN_WEB ],
        ]

        for text, func, m_id in popup_handler:
            if func is not None:
                item = self.popupmenu.Append(m_id, text)
                self.build_list_ctrl.Bind(wx.EVT_MENU, func, item)
            else:
                self.popupmenu.AppendSeparator()

        self.build_list_ctrl.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,\
                        self.OnMouseRightDownHandler)

        self.project_list_ctrl = ProjectListCtrl(self, -1)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectProject,\
                        self.project_list_ctrl)

        self.binary_list_ctrl = BinaryListCtrl(self, -1)

        # Adding build list to build_list_ctrl
        self.project_name = "DEGASVELTE_LTN"
        self.build_cfg = "RBS"

        self.combo = wx.ComboBox(self, style=wx.CB_READONLY)
        self.updateBuildCfgBox()
        self.combo.Bind(wx.EVT_COMBOBOX, self.OnPbsRbsSelect)
        self.combo.SetSelection(0)
        '''
        self.project_add_btn = wx.Button(self, label="+", size = (100, 30))
        self.project_del_btn = wx.Button(self, label="-", size = (100, 30))
        
        project_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        project_btn_sizer.Add(self.project_add_btn, 0, wx.ALL|wx.CENTER, 0)
        project_btn_sizer.Add(self.project_del_btn, 0, wx.ALL|wx.CENTER, 0)
        '''

        self.reload_btn = wx.Button(self, \
                label="Reload", size = (100, 30))
        self.reload_btn.Bind(wx.EVT_BUTTON, self.onReload)
        self.reload_btn.Disable()

        self.download_btn = wx.Button(self, label="Download", size = (100, 30))
        self.download_btn.Bind(wx.EVT_BUTTON, self.onDownloadAll)
        self.download_btn.Disable()

        self.qb_download_status = wx.TextCtrl(self, \
                -1, '', size = (120, 25), style=wx.TE_LEFT|wx.TE_READONLY)
        self.qb_download_progress = wx.Gauge(self, -1, 100, size = (200, 20))

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.reload_btn, 0, wx.ALL|wx.CENTER, 5)
        button_sizer.Add(self.download_btn, 0, wx.ALL|wx.CENTER, 5)

        self.AutoDownloadCheckBox = \
                wx.CheckBox(self, wx.ID_ANY, "Auto downloading")

        ver_sizer = wx.BoxSizer(wx.VERTICAL)
        ver_sizer.Add(self.AutoDownloadCheckBox, 0, wx.ALL, 5)
        ver_sizer.Add(self.qb_download_status, 0, wx.ALL|wx.EXPAND, 5)
        ver_sizer.Add(self.qb_download_progress, 0, wx.ALL|wx.EXPAND, 5)
        ver_sizer.Add(self.build_list_ctrl, 1, wx.ALL|wx.EXPAND, 5)
        ver_sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 5)

        ver_set_sizer = wx.BoxSizer(wx.VERTICAL)
        ver_set_sizer.Add(self.combo, 0, wx.ALL | wx.EXPAND, 5)
        ver_set_sizer.Add(self.project_list_ctrl, 1, wx.ALL|wx.EXPAND, 5)
#        ver_set_sizer.Add(project_btn_sizer, 0, wx.ALL|wx.RIGHT, 5)
        ver_set_sizer.Add(self.binary_list_ctrl, 0, wx.ALL|wx.EXPAND, 5)

        hor_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hor_sizer.Add(ver_set_sizer, 0, wx.ALL|wx.EXPAND, 5)
        hor_sizer.Add(ver_sizer, 1, wx.ALL | wx.EXPAND, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(hor_sizer, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(main_sizer)

        self.projects = self.config.getProjects()
        self.projects.remove('PATH')
        for prj in self.projects:
            self.project_list_ctrl.addProjectItem(prj)

        self.isListUpdating = False

    def OnSelectBuild(self, event):
        self.download_btn.Enable()
        item_idx = event.m_itemIndex
        self.build_url = self.getBuildUrl(item_idx)
        self.build_version = self.getBuildVersion(item_idx)
        self.build_cl = self.getBuildCl(item_idx)
        self.build_mode = self.getBuildMode(item_idx)

    def OnOpenBuildPage(self, event):
        item_idx = self.right_item
        webbrowser.open_new(self.getBuildUrl(item_idx))

    def OnMouseRightDownHandler(self, event):
        pos = event.GetPoint()

        self.right_item = event.m_itemIndex
        self.build_list_ctrl.PopupMenu(self.popupmenu, pos)
        event.Skip()

    def OnSelectProject(self, event):
        self.download_btn.Disable()
        self.reload_btn.Enable()
        item_idx = event.m_itemIndex

        if self.project_name is not self.projects[item_idx]:
            self.project_name = self.projects[item_idx]
            self.updateBuildCfgBox()
            self.reloadBuilds()

    def updateBuildCfgBox(self):
        self.combo.Clear()
        pages = self.config.getProjectPages(self.project_name)

        for page in pages:
            self.combo.Append(page.upper())

        self.combo.SetSelection(0)
        self.build_cfg = self.combo.GetValue()

    def OnPbsRbsSelect(self, event):
        self.download_btn.Disable()
        self.reload_btn.Enable()
        self.build_cfg = event.GetString()
        self.reloadBuilds()

    def onReload(self, event):
        self.reloadBuilds()

    def onDownloadAll(self, event):
        global auto_download

        if auto_download is True:
            self.download_btn.SetLabel("Download")
            auto_download = False
        else:
            download_thread = threading.Thread(target=self.downloadThread)
            download_thread.start()

    def disableControlAll(self):
        self.binary_list_ctrl.Disable()
        self.build_list_ctrl.Disable()
        self.project_list_ctrl.Disable()
        self.combo.Disable()
        self.reload_btn.Disable()
        self.download_btn.Disable()

    def enableControlAll(self):
        self.binary_list_ctrl.Enable()
        self.build_list_ctrl.Enable()
        self.project_list_ctrl.Enable()
        self.combo.Enable()
        self.download_btn.Enable()

    def downloadThread(self):
        global auto_download
        global auto_download_files

        download_path = self.config.getDownloadPath() + \
                        self.project_name + "/"

        if self.build_version != "":
            versions = self.build_version.split(" ")
            if len(versions) > 0:
                version = versions[0]
            download_path += version[-3:] + "_"
        else:
            version = self.build_cl.split(" ")[0]
            download_path += version + "_"

        download_path += self.build_mode + "_"

        self.qb.setDownloadFile(self.binary_list_ctrl.isPitChecked(), \
                self.binary_list_ctrl.isBlChecked(), \
                self.binary_list_ctrl.isApChecked(), \
                self.binary_list_ctrl.isCpChecked(), \
                self.binary_list_ctrl.isCscChecked(), \
                self.binary_list_ctrl.isDebugChecked())
        wx.CallAfter(self.disableControlAll)
        files = self.qb.downloadAll(self.build_url, download_path)
        wx.CallAfter(self.enableControlAll)

        auto_download = self.AutoDownloadCheckBox.GetValue()
        if auto_download is True:
            self.download_btn.SetLabel("Stop")
            auto_download_files = files[:]

        if self.downloadMethod != None:
            wx.CallAfter(self.qb_download_status.SetValue, \
                                "Launching Pyodin...");
            wx.CallAfter(self.downloadMethod, files)

    def reloadBuilds(self):
        wx.BeginBusyCursor()
        if self.show_build_thread is not None:
            if self.show_build_thread.isAlive() is True:
                self.show_build_enabled = False
                self.show_build_thread.join()

        self.deleteAll()
        self.show_build_enabled = True
        self.show_build_thread = threading.Thread(target=self.showBuildThread)
        self.show_build_thread.start()

    def showBuildList(self, build_list):
        if build_list is not None:
            self.addBuilds(build_list)
        wx.EndBusyCursor()

    def updateBuildList(self):
        list_total  = self.build_list_ctrl.GetItemCount()
        list_top    = self.build_list_ctrl.GetTopItem()
        list_pp     = self.build_list_ctrl.GetCountPerPage()
        list_bottom = min(list_top + list_pp, list_total)

        if list_total is list_bottom and self.isListUpdating is False:
            wx.BeginBusyCursor()
            if self.show_build_thread is not None:
                if self.show_build_thread.isAlive() is True:
                    self.show_build_thread.join()

            self.show_build_thread = threading.Thread(target=self.showNextBuildThread)
            self.show_build_thread.start()

    def addBuildItem(self, build_id, mode, date, status, hw_rev, \
            version, cl, by, duration):
        self.build_list_ctrl.InsertStringItem(self.load_num, build_id)
        self.build_list_ctrl.SetStringItem(self.load_num, 1, mode)
        self.build_list_ctrl.SetStringItem(self.load_num, 2, date)
        self.build_list_ctrl.SetStringItem(self.load_num, 3, status)
        self.build_list_ctrl.SetStringItem(self.load_num, 4, hw_rev)
        self.build_list_ctrl.SetStringItem(\
                self.load_num, 5, version + ' ' + cl)
        self.build_list_ctrl.SetStringItem(self.load_num, 6, by)
        self.build_list_ctrl.SetStringItem(self.load_num, 7, duration)

#        if (status == 'recommended'):
#            self.build_list_ctrl.SetItemBackgroundColour(self.load_num, '#c1e9f2')
        self.load_num += 1

    def addBuilds(self, build_list):
        self.build_list += build_list
        for build in build_list:
            self.addBuild(build)

    def addBuild(self, build):
        self.addBuildItem(build.build_id, build.mode, build.date,\
                build.status,build.hw_rev, build.version, \
                build.build_cl, build.triggered_by, build.duration)

    def deleteAll(self):
        self.build_list_ctrl.DeleteAllItems()
        del self.build_list[:]
        self.load_num = 0

    def getBuildUrl(self, idx):
        return self.build_list[idx].url

    def getBuildVersion(self, idx):
        return self.build_list[idx].version

    def getBuildCl(self, idx):
        return self.build_list[idx].build_cl

    def getBuildMode(self, idx):
        return self.build_list[idx].mode

    def showBuildThread(self):
        self.isListUpdating = True
        url = self.config.getProjectUrl(self.project_name, self.build_cfg)
        self.qb.setProject(self.project_name, url)
        recommend_build_list = self.qb.getRecommendedList()
        if recommend_build_list is not None:
            build_list = recommend_build_list
        else:
            build_list = []

        build_list += self.qb.getRecentList()
        self.isListUpdating = False

        if self.show_build_enabled is True:
            wx.CallAfter(self.showBuildList, build_list)

    def showNextBuildThread(self):
        self.isListUpdating = True
        build_list = self.qb.getRecentList()
        self.isListUpdating = False
        wx.CallAfter(self.showBuildList, build_list)

class PyodinTabPanel(wx.Panel):
    def __init__(self, parent, downloadMethod):
        self.donwnloadMethod = downloadMethod

        wx.Panel.__init__(self, parent=parent)

        self.last_path = None

        self.binary_list_ctrl = OdinBinaryListCtrl(self, -1)
        downloadBtn = wx.Button(self, label="Download")
        downloadBtn.Bind(wx.EVT_BUTTON, self.onDownloadStart)

        addBtn = wx.Button(self, label="Add")
        addBtn.Bind(wx.EVT_BUTTON, self.onAddBinary)

#        deleteBtn = wx.Button(self, label="Delete")
        resetBtn = wx.Button(self, label="Reset")
        resetBtn.Bind(wx.EVT_BUTTON, self.onReset)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(addBtn, 0, wx.ALL, 10)
#        buttonSizer.Add(deleteBtn, 0, wx.ALL, 10)
        buttonSizer.Add(resetBtn, 0, wx.ALL, 10)
        buttonSizer.Add(downloadBtn, 0, wx.ALL, 10)

        listSizer = wx.BoxSizer(wx.VERTICAL)
        listSizer.Add(self.binary_list_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        listSizer.Add(buttonSizer, 0, wx.ALL, 0)


#        self.odin_option_ctrl = OdinOptionsCtrl(self, -1)
        self.odin_log_text = wx.TextCtrl(self, \
                -1, '', size = (300, 25), \
                style=wx.TE_LEFT|wx.TE_MULTILINE|wx.TE_READONLY)

        optionSizer = wx.BoxSizer(wx.VERTICAL)
#        optionSizer.Add(self.odin_option_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        optionSizer.Add(self.odin_log_text, 1, wx.ALL | wx.EXPAND, 10)


        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(optionSizer, 0, wx.ALL | wx.EXPAND, 10)
        mainSizer.Add(listSizer, 1, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(mainSizer)

    def onReset(self, event):
        self.binary_list_ctrl.resetList()

    def onAddBinary(self, event):
        dlg = wx.FileDialog(self, "Choose a file", self.last_path, "", \
                "binaries(*.pit,*.md5,*.tar)|*.pit;*.md5;*.tar", \
                    wx.OPEN | wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
#            mypath = os.path.basename(path)
            print ("You selected: %s" % paths)
            self.last_path = os.path.dirname(paths[0])
            self.binary_list_ctrl.addItems(paths)
        dlg.Destroy()

    def onDownloadStart(self, event):
        binary_list = self.binary_list_ctrl.getBinaryList()[:]
        print binary_list
        self.donwnloadMethod(binary_list)

class Device():
    def __init__(self, text, progress):
        self.devicePath = None
        self.statusText = text
        self.progress = progress

    def attached(self, path):
        self.statusText.SetValue(path)
        self.devicePath = path

    def detached(self):
        self.statusText.SetValue("")
        self.devicePath = None

    def isAttached(self):
        if self.devicePath is None:
            return False
        else:
            return True

class MainWindow(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size = (1000,500))

        self.SetMinSize((1200, 700))
        panel = wx.Panel(self, wx.ID_ANY)

        '''
        isNeedUpdate = self.checkUpdate()
        if isNeedUpdate is True:
            dialog = wx.MessageDialog(parent, \
                    message = "New Pyodin is available.\n"+\
                    "Do you want to download new Pyodin?",\
                    caption = "Pyodin", style = wx.YES_NO | \
                    wx.ICON_INFORMATION, pos = wx.DefaultPosition)
            response = dialog.ShowModal()

            if (response == wx.ID_YES):
                self.proceedUpdate()
        '''

        self.contiDown = False
        self.project_name = "DEGASVELTE_LTN"
        self.build_cfg = "RBS"
        get_debug_files = False
        self.config = abget.ABGetConfigParser(self.project_name, self.build_cfg)
        self.qb = abget.QbuildParser(self.project_name, get_debug_files)

        username = self.config.getUserName()
        password = self.config.getPassword()

        if username == "" and password == "":
            self.showLoginDialog(username, password)
        else:
            if self.qb.login(username, password, self.config) is True:
                print "You are now logged in!"
                self.logged_in = True
            else:
                self.showLoginDialog(username, password)

        notebook = wx.Notebook(panel)
        self.abgetPanel = AbgetTabPanel(notebook, self.config,\
                self.qb, self.odinDownloadAllDevice)
        notebook.AddPage(self.abgetPanel, "Abget")

        self.pyodinPanel = PyodinTabPanel(notebook, self.odinDownloadAllDevice)
        notebook.AddPage(self.pyodinPanel, "Pyodin")

        self.devices = []
        self.download_status = []
        self.download_progress = []
        download_sizer = wx.BoxSizer(wx.HORIZONTAL)
        device_sizer = []

        self.deviceToCtrl = []
        self.deviceCtrl = []

        for i in xrange(0, 8):
            self.download_status.append(wx.TextCtrl(panel, -1, '', \
                        size = (-1, 25), style=wx.TE_CENTER|wx.TE_READONLY))
            self.download_progress.append(wx.Gauge(panel, -1, 100, \
                        size = (-1, 25)))
            device_sizer.append(wx.BoxSizer(wx.VERTICAL))
            device_sizer[i].Add(self.download_status[i], 1, \
                        wx.ALL|wx.EXPAND, 5)
            device_sizer[i].Add(self.download_progress[i], 1, \
                        wx.ALL|wx.EXPAND, 5)
            download_sizer.Add(device_sizer[i], 1,\
                        wx.ALL | wx.EXPAND, 5)

            self.deviceCtrl.append(Device(self.download_status[i], self.download_progress[i]))

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(download_sizer, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(main_sizer)

        self.statusbar = self.CreateStatusBar()
        self.Centre()

        self.Show(True)

        self.lastData = EnvData(self.config)
        self.updateGui(self.lastData)

        self.qb.setProgress(self.abgetPanel.qb_download_progress)
        self.qb.setStatusText(self.abgetPanel.qb_download_status)

        self.dev_dector = threading.Thread(target=self.deviceDetectThread)
        self.dev_dector.start()

        self.Bind(wx.EVT_CLOSE, self.OnCloseFrame)
        EVT_RESULT(self,self.OnResult)

    def showLoginDialog(self, username, password):
        dlg = LoginDialog(self.qb, self.config, username, password)
        dlg.ShowModal()
        if dlg.logged_in is False:
            self.OnExitApp()

    def OnResult(self, event):
        if event.data[0] == "s":
            self.poppid = int(event.data[1:])

    def checkUpdate(self):
        updater_path = os.path.dirname(os.path.abspath( __file__ )) + '/updater.sh'
        isOldVersion = os.system(updater_path + " -c")
        if isOldVersion != 0:
            return True

        return False

    def proceedUpdate(self):
        updater_path = os.path.dirname(os.path.abspath( __file__ )) + '/updater.sh'
        os.system(updater_path + " -u")
        os.execv(__file__, sys.argv)
        sys.exit(0)

    def updateGui(self, env):
        self.abgetPanel.binary_list_ctrl.setCheckPit(env.pitChecked)
        self.abgetPanel.binary_list_ctrl.setCheckBl(env.blChecked)
        self.abgetPanel.binary_list_ctrl.setCheckAp(env.apChecked)
        self.abgetPanel.binary_list_ctrl.setCheckCp(env.cpChecked)
        self.abgetPanel.binary_list_ctrl.setCheckCsc(env.cscChecked)
        self.abgetPanel.binary_list_ctrl.setCheckDebug(env.debugChecked)
        self.abgetPanel.AutoDownloadCheckBox.SetValue(env.autoDownChecked)
        self.pyodinPanel.last_path = env.lastFilePath
        self.project_name = env.lastSelectProject
        self.build_cfg = env.lastSelectCfg

    def OnCloseFrame(self, event):
        pit = self.abgetPanel.binary_list_ctrl.isPitChecked()
        bl = self.abgetPanel.binary_list_ctrl.isBlChecked()
        ap = self.abgetPanel.binary_list_ctrl.isApChecked()
        cp = self.abgetPanel.binary_list_ctrl.isCpChecked()
        csc = self.abgetPanel.binary_list_ctrl.isCscChecked()
        debug = self.abgetPanel.binary_list_ctrl.isDebugChecked()
        auto = self.abgetPanel.AutoDownloadCheckBox.GetValue()
        path = self.pyodinPanel.last_path;

        self.lastData.saveLastData(pit, bl, ap, cp, csc, debug, \
                    auto, path, self.project_name, self.build_cfg)
        self.OnExitApp()

    def odinDownloadAllDevice(self, files):
        cnt = 0
        devices = self.devices[:]
        for dev in devices:
            self.odinDownload(dev, files, self.deviceToCtrl[cnt])
            cnt += 1

    def odinDownload(self, dev, files, deviceCtrl):
        self.__odinDownload(dev, files, deviceCtrl.progress, \
                deviceCtrl.statusText)

    def __odinDownload(self, dev, files, progress, text):
        copy_files = files[:]
        t = pyodin.PyodinThread(dev, copy_files)
        t.setProgressBar(progress)
        t.setStatusText(text)
        t.start()

    def OnExitApp(self):
        self.Destroy()
        os.kill(os.getpid(), signal.SIGINT)

    def getDevices(self):
        return self.devices

    def addDevice(self, dev):
        for ctrl in self.deviceCtrl:
            if ctrl.isAttached() is False:
                ctrl.attached(dev)
                return ctrl
        return None


    def getDevicePathes(self):
        status, output = commands.getstatusoutput("ls /dev/ttyACM*")
        dev_pathes = output.split("\n")

        if output.find('cannot access') > 0:
            return None

        return dev_pathes

    def deviceDetectThread(self):
        global auto_download
        global auto_download_files

        time.sleep(1)
#       try:
        while(True):
            wx.CallAfter(self.abgetPanel.updateBuildList)
            devices = self.getDevicePathes()
            if devices is None:
                if len(self.devices) > 0:
                    print "Detached " + self.devices[0]
                    print "Waiting for the new device."
                    self.deviceToCtrl[0].detached()
                    del self.devices[:]
                    del self.deviceToCtrl[:]

                time.sleep(0.5)
                continue

            time.sleep(0.5)

            for dev in devices:
                cnt = 0
                for current_dev in self.devices:
                    if dev.find(current_dev) >= 0:
                        break
                    cnt += 1

                if cnt is len(self.devices):
                    print "Attached " + dev
                    self.devices.append(dev)
                    self.deviceToCtrl.append(self.addDevice(dev))
                    if auto_download is True:
                        self.odinDownload(dev, auto_download_files, \
                                self.deviceToCtrl[cnt])

            if len(self.devices) > 0:
                cur_cnt = 0
                for cur_dev in self.devices:
                    cnt = 0
                    for dev in devices:
                        if dev.find(cur_dev) >= 0:
                            break
                        cnt += 1

                    if cnt is len(devices):
                        print "Detached " + cur_dev
                        self.deviceToCtrl[cur_cnt].detached()
                        del self.deviceToCtrl[cur_cnt]
                        del self.devices[cur_cnt]
                    cur_cnt += 1
#        except:
#            sys.exit(0)

auto_download = False
auto_download_files = []

app = wx.App(False)
frame = MainWindow(None, "PYODIN-GUI Ver " + VERSION)
app.MainLoop()
