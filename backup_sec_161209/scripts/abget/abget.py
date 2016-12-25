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
#  # Version : 0.953
#  ##
#
from bs4 import BeautifulSoup
import urllib, urllib2, cookielib
import mechanize
import re
import sys, getopt
import os
import ConfigParser
import getpass
import base64
import time
import wx
import subprocess

qb_main_url="http://android.qb.sec.samsung.net"
login_url = qb_main_url + "/signin"
history_url = qb_main_url + "/history"
overview_url = qb_main_url + "/overview"

def httpsToHttp(url):
    if url[:5] == 'https':
       url = 'http' + url[5:]
    return url

class BuildInfo():
    def __init__(self, build_id, url, mode, date, status, hw_rev, \
            version, build_cl, duration, triggered_by = ""):
        self.build_id = build_id
        self.url = url
        self.mode = mode
        self.date = date
        self.status = status
        self.hw_rev = hw_rev
        self.version = version
        self.build_cl = build_cl
        self.triggered_by = triggered_by
        self.duration = duration

class ABGetConfigParser():
    def __init__(self, project_name, build_cfg):
        self.config, config_path = self.openConfig('abget.cfg')
        self.download_path = self.config.get("PATH", "DOWNLOAD_PATH");

        if self.download_path[:1] == '.':
            self.download_path = os.path.dirname(os.path.abspath( __file__ )) + \
            self.download_path[1:]
        elif self.download_path[:1] != '/':
            self.download_path = os.path.dirname(os.path.abspath( __file__ )) + \
            self.download_path

        if self.download_path[-1:] != '/':
            self.download_path += '/'

        if build_cfg == None:
            build_cfg = "RBS"

        if project_name is not None:
            self.project_url = httpsToHttp(self.config.get(project_name, build_cfg))
            self.pbs_url = httpsToHttp(self.config.get(project_name, "PBS"))
            self.rbs_url = httpsToHttp(self.config.get(project_name, "RBS"))

        self.login_config, self.login_cfg_path = self.openConfig('.login.cfg')

        if self.login_config is not None:
            self.username = self.login_config.get("LOGIN_INFO","ID")
            self.password = self.login_config.get("LOGIN_INFO", "PW")
        else:
            self.username = ""
            self.password = ""

    def openConfig(self, filename):
        isExist = False
        config = ConfigParser.RawConfigParser()
        config_path = os.path.dirname(os.path.abspath( __file__ )) + '/' + filename
        if os.path.isfile(config_path):
            config.read(config_path)
            isExist = True
        else:
            env_path = os.environ['PATH']
            env_pathes = env_path.split(":")
            for path in env_pathes:
                _path = path + '/' + filename
                if os.path.isfile(_path):
                    config_path = _path
                    config.read(config_path)
                    isExist = True

        if isExist is True:
            return config, config_path
        else:
            return None, config_path

    def getProjects(self):
        return self.config.sections()

    def getProjectPages(self, project_name):
        return self.config.options(project_name)

    def getUserName(self):
        return self.username

    def getPassword(self):
        return base64.b64decode(self.password)

    def saveLoginInfo(self, username, password):

        Config = ConfigParser.ConfigParser()
        Config.add_section("LOGIN_INFO")
        Config.set("LOGIN_INFO", "ID", username)
        Config.set("LOGIN_INFO", "PW", base64.b64encode(password))

        cfgfile = open(self.login_cfg_path, 'w')

        Config.write(cfgfile)
        cfgfile.close()

    def close(self):
        self.config.close()

    def getPrjIndex(self, prj_name):
        idx = 0
        print "find project : " + prj_name

        for prj in self.projects:
            if (prj == prj_name):
                return idx
            idx += 1
            print prj

        return -1

    def getProjectUrl(self, project_name, build_cfg):
        self.project_url = httpsToHttp(self.config.get(project_name, build_cfg))
        return self.project_url

    def getPbsUrl(self):
        return self.pbs_url

    def getRbsUrl(self):
        return self.rbs_url

    def getDownloadPath(self):
        return self.download_path

class QbuildParser():
    br = mechanize.Browser()

    def __init__(self, prj_name, get_debug = False):
        self.br.set_handle_robots(False) # ignore robots
        self.prj_name = prj_name
        self.get_debug = get_debug
        self.build_status = ""
        self.progress = None
        self.statusText = None
        self.currentHistoryUrl = None
        self.get_ap = True
        self.get_bl = True
        self.get_pit = True
        self.get_csc = True
        self.get_cp = True

    def setStatusText(self, text):
        self.statusText = text

    def setProgress(self, progress):
        self.progress = progress

    def setProject(self, prj_name, url):
        self.prj_name = prj_name
        self.prj_url = url
        self.currentHistoryUrl = self.getAllHistroyUrl()

    def setPrjUrl(self, url):
        self.prj_url = url

    def login(self, userid, passwd, config):
        self.br.open(login_url)
        self.br.form = list(self.br.forms())[0]
        control = self.br.form.find_control("userName")
        control.value = userid
        control = self.br.form.find_control("password")
        control.value = passwd
        res = self.br.submit()
        content = res.read()
        if content.find("Login to QuickBuild") >= 0:
            print "Can not login to QuickBuild. Please check your id / pw"
            return False
        else:
            config.saveLoginInfo(userid, passwd)
            print "Quick Build login success"

        return True

    def downloadBuildBinFromSelect(self, ver):
        build_url = self.getAllBuildFromAllHistory(ver)

        if build_url == None:
            return None

        return self.downloadAll(build_url)

    def downloadReleaseBinAll(self, ver, download_path):
        build_url = self.getBuildFromRecommeded(ver)

        if build_url == None:
            return None

        return self.downloadAll(build_url, download_path)

    def downloadBuildBinAll(self, ver, download_path):
        build_url = self.getBuildFromAllHistory(ver)

        if build_url == None:
            return None

        return self.downloadAll(build_url, download_path)

    def waitForBuild(self, build_url):
        build_status = 'Running'
        while build_status == 'Running':
            resp = self.br.open(build_url)
            soup = BeautifulSoup(resp.read())
            summary = soup.find('div', {'class': re.compile(r'build-summary*')})
            summary_head = summary.find('thead').findAll('td')

            cnt = 0
            for tag in summary_head:
                if tag.text.find('Status') >= 0:
                    break
                cnt += 1

            summary_data = summary.find('tbody').findAll('td')
            build_status = summary_data[cnt].text

            progress = soup.find('div', {'class':re.compile(r'progress-percentage')})

            if progress is not None:
                print "build status : " + build_status + "(" + progress.text + ")"
                if self.statusText is not None:
                    wx.CallAfter(self.statusText.SetValue, \
                            "build status : " + build_status + "(" + progress.text + ")")

                if progress.text == '100%':
                    time.sleep(10)
                else:
                    time.sleep(120)

    def setDownloadFile(self, pit, bl, ap, cp, csc, debug):
        self.get_pit = pit
        self.get_ap = ap
        self.get_bl = bl
        self.get_cp = cp
        self.get_csc = csc
        self.get_debug = debug
        print pit

    def downloadAll(self, build_url, download_path):
        print "build url : " + build_url
#        if self.build_status == 'running':
        self.waitForBuild(build_url)

        dest_array = []
        type_array = []

        soup, build_id = self.openBuildPage(build_url)

        download_path += build_id
        if self.get_pit is True:
            pit_url = self.getBinaryURL(soup, ".pit")
            if (pit_url is not None):
                dest_array.append(self.getBinaryFromURL(pit_url, download_path))

        if self.get_ap is True:
            ap_url = self.getBinaryURL(soup, "AP_")
            if (ap_url is not None):
                dest_array.append(self.getBinaryFromURL(ap_url, download_path))

        if self.get_bl is True:
            bl_url = self.getBinaryURL(soup, "BL_")
            if (bl_url != None):
                dest_array.append(self.getBinaryFromURL(bl_url, download_path))

        if self.get_cp is True:
            cp_url = self.getBinaryURL(soup, "CP_")
            if (cp_url is not None):
                dest_array.append(self.getBinaryFromURL(cp_url, download_path))

        if self.get_csc is True:
            csc_url = self.getBinaryURL(soup, "CSC_")
            if (csc_url is not None):
                dest_array.append(self.getBinaryFromURL(csc_url, download_path))

        kernel_url = self.getBinaryURL2(soup, {"KERNEL_", ".md5"})
        if (kernel_url is not None):
            self.getBinaryFromURL(kernel_url, download_path)


        if self.get_debug == True:
            file_url = self.getBinaryURL(soup, "DEBUG_KERNEL")
            if file_url != None:
                self.getBinaryFromURL(file_url, download_path)

        return dest_array

    def findBuildsFromPage(self, soup, bin_ver):
        builds = soup.findAll('a', {'class': re.compile(r'build-status.*')})

        for tag in builds:
            bin_str = ''
            text_list = tag.text.splitlines()
            for t in text_list:
                bin_str += t

            cnt = 0
            for info in bin_ver:
                if (bin_str.find(info) >= 0):
                    cnt += 1
                else:
                    break

            if cnt == len(bin_ver):
                self.build_status = tag['class'][1]
                return qb_main_url + tag['href']

        return None

    def getBuildsFromBuildId(self, soup, build_id):
        builds = soup.findAll('tr', {'class':'even'})
        for tag in builds:
            if tag.text.find(build_id) >= 0:
                build_tag = tag.find('a', {'class':re.compile(r'build-status.*')})
                self.build_status = build_tag['class'][1]
                build_url = qb_main_url + build_tag['href']
                return build_url

        builds = soup.findAll('tr', {'class':'odd'})
        for tag in builds:
            if tag.text.find(build_id) >= 0:
                build_tag = tag.find('a', {'class':re.compile(r'build-status.*')})
                self.build_status = build_tag['class'][1]
                build_url = qb_main_url + build_tag['href']
                return build_url

        return None

    def getAllBuildFromAllHistory(self, bin_ver):
        history_url = self.getAllHistroyUrl()
        return self.getAllBuildsFromHistory(history_url, bin_ver)


    def getBuildFromAllHistory(self, bin_ver):
        history_url = self.getAllHistroyUrl()
        return self.getBuildFromHistory(history_url, bin_ver)

    def getBuildFromRecommeded(self, bin_ver):
        build_url = self.getRecommendedMoreUrl()

        if build_url is None:
            return None

        resp = self.br.open(build_url)
        soup = BeautifulSoup(resp.read())

        build_url = self.findBuildsFromPage(soup, bin_ver)
        if build_url is not None:
            return build_url

        build_url = self.getBuildsFromBuildId(soup, bin_ver[1])
        if build_url is not None:
            return build_url

        return None

    def getAllBuildsFromHistory(self, history_url, bin_ver):
        cnt = 0
        url = history_url
        while url is not None:
            resp = self.br.open(url)
            soup = BeautifulSoup(resp.read())

            build_ver, build_url = self.findAllBuildsFromPage(soup, bin_ver)

            for i in range(0, len(build_ver)):
                cnt += 1
                print "Build Id %d" % cnt
                print build_ver[i]

            url = self.getNextPage(soup)
        return None

    def getBuildsFromHistory(self, history_url, bin_ver):
        url = history_url
        while url is not None:
            resp = self.br.open(url)
            soup = BeautifulSoup(resp.read())

            build_url = self.findBuildsFromPage(soup, bin_ver)
            if build_url is not None:
                return build_url

            build_url = self.getBuildsFromBuildId(soup, bin_ver[1])
            if build_url is not None:
                return build_url

            url = self.getNextPage(soup)
        return None


    def getBuildFromHistory(self, history_url, bin_ver):
        url = history_url
        while url is not None:
            resp = self.br.open(url)
            soup = BeautifulSoup(resp.read())

            build_url = self.findBuildsFromPage(soup, bin_ver)
            if build_url is not None:
                return build_url

            build_url = self.getBuildsFromBuildId(soup, bin_ver[1])
            if build_url is not None:
                return build_url

            url = self.getNextPage(soup)
        return None

    def getNextPage(self, soup):
        Pages = soup.findAll('a', {'title': re.compile(r'Go.*')})

        for tag in Pages:
            if (tag.text == '>'):
                next_url = history_url + tag['href'].split("..")[-1]
                return next_url

        return None

    def openBuildPage(self, url):
        resp = self.br.open(url)
        soup = BeautifulSoup(resp.read())
        summary = soup.find('div', {'class': re.compile(r'build-summary*')})
        summary_head = summary.find('thead').findAll('td')

        cnt = 0
        for tag in summary_head:
            if tag.text.find('Id') >= 0:
                break
            cnt += 1

        summary_data = summary.find('tbody').findAll('td')
        build_id = summary_data[cnt].text
        return soup, build_id

    def getBinaryURL(self, soup, binary_name):
        binaries = soup.findAll('a', {'title': re.compile(r'Download.*|\w{32}')})

        for tag in binaries:
            if tag.text.find(binary_name) >= 0:
                return qb_main_url + tag['href']

        return None

    def getBinaryURL2(self, soup, binary_names):
        binaries = soup.findAll('a', {'title': re.compile(r'Download.*|\w{32}')})

        for tag in binaries:
            isFind = True
            for bin_name in binary_names:
                if (tag.text.find(bin_name) < 0):
                    isFind = False
                    break

            if isFind is True:
                return qb_main_url + tag['href']

        return None

    def openUrl(self, url):
        resp = self.br.open(url)
        soup = BeautifulSoup(resp.read())
        builds = soup.findAll('h1')
        for tag in builds:
            if tag.text.find("Login") >= 0:
                print "error : cannot login"
                return None

        return soup

    def getRecommendedMoreUrl(self):
        soup = self.openUrl(self.prj_url)

        if soup is None:
            return None

        builds = soup.findAll('div', {'class':'head'})

        for tag in builds:
            if tag.text.find("Recommended") >= 0:
                more_url = overview_url + tag.find('a', {'title':'More'})['href'].split("..")[-1]
                return more_url

    def getAllHistroyUrl(self):
        soup = self.openUrl(self.prj_url)

        if soup is None:
            return None

        builds = soup.findAll('a', {'title':"All builds in history"})

        for tag in builds:
            history_url = qb_main_url + tag['href'].split("..")[-1]
            print history_url
            return history_url

    def getBinaryFromURL(self, url, download_path):

        print "download url : " + url
        file_name = url.split('filename=')[1].split('&')[0]
        #dir_name = "./bin/" + "QB" + file_name.split('QB')[1].split('_')[0] + "/"

        dir_name = download_path + "/"
        if not os.path.isdir(dir_name):
            os.system("mkdir -p " + dir_name)

        u = self.br.open(url)
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])

        full_name = dir_name + file_name
        if os.path.isfile(full_name):
            exist_size = os.path.getsize(full_name)
            print "file_size : %d exist_size : %d" % (file_size, exist_size)
            if file_size == exist_size:
                if self.statusText is not None:
                    wx.CallAfter(self.statusText.SetValue, 'exist ' + full_name)

                return full_name

        download_msg = "Downloading: %s Bytes: %s" % (file_name, file_size)
        print download_msg
        if self.statusText is not None:
            wx.CallAfter(self.statusText.SetValue, download_msg)

        f = open(full_name, 'wb')
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,

            if self.progress is not None:
                wx.CallAfter(self.progress.SetValue, file_size_dl * 100. / file_size)

        print ""
        f.close()

        return full_name

    def showBuildList(self):

#        build_url = self.getRecommendedMoreUrl()
        build_url = self.prj_url
        if build_url is None:
            return None

        resp = self.br.open(build_url)
        soup = BeautifulSoup(resp.read())

        recommended_list = None
        recent_list = None
        print build_url
#        builds = soup.findAll('a', {'class': re.compile(r'build-status.*')})

        print "Show Build List"
        print "==========================================================================="
        print "RECOMMENDED BUILDS"
        recommendedSoup = soup.findAll('div', {'class':re.compile(".*blue.*")})
        if len(recommendedSoup) > 0:
            recommended = recommendedSoup[0]
            bodies = recommended.findAll('tbody')
            recommended_list = self.showBuildListEachTable(bodies, False)
        else:
            print "---------------------------------------------------------------------------"
            print "No build"

        print "==========================================================================="
        print "RECENT BUILDS"
        recentSoup = soup.findAll('div', {'class':re.compile('.*build-history.*')})
        if len(recentSoup) > 0:
            recentBuild = recentSoup[0]
            bodies = recentBuild.findAll('tbody')
            recent_list = self.showBuildListEachTable(bodies, True)

        print "==========================================================================="

        if recommended_list is not None:
            return recommended_list + recent_list
        else:
            return recent_list

    def getRecommendedList(self):
        build_url = self.prj_url
        if build_url is None:
            return None

        resp = self.br.open(build_url)
        soup = BeautifulSoup(resp.read())

        print "Show Build List"
        print "==========================================================================="
        print "RECOMMENDED BUILDS"
        recommendedSoup = soup.findAll('div', {'class':re.compile(".*blue.*")})
        if len(recommendedSoup) > 0:
            recommended = recommendedSoup[0]
            bodies = recommended.findAll('tbody')
            build_list = (self.showBuildListEachTable(bodies, False))
            return build_list
        else:
            print "---------------------------------------------------------------------------"
            print "No build"
            return None

    def getRecentList(self):
#        build_url = self.prj_url
#        build_url = self.getAllHistroyUrl()
        build_url = self.currentHistoryUrl
        if build_url is None:
            return None

        resp = self.br.open(build_url)
        soup = BeautifulSoup(resp.read())
        self.currentHistoryUrl = self.getNextPage(soup)

        print "==========================================================================="
        print "RECENT BUILDS"
        recent_list = self.getBuildList(soup, True)
        return recent_list
        print "==========================================================================="

    def buildListParser(self, builds, showBy):
        build_list = []
        for build in builds:
#                print build
            tags = build.findAll('a', {'class': re.compile(r'build-status.*')})

            if len(tags) < 1:
                continue

            tag = tags[0]
#            print tag
            build_ver_full = tag.text
            build_url = qb_main_url + tag['href']
#                print build_url
            str_build_info = ''
            text_list = tag.text.splitlines()
            for t in text_list:
                str_build_info += t


            if str_build_info.find(self.prj_name) < 0:
                continue

            build_status = tag['class'][1]
            if build_status == 'cancelled' or build_status == 'failed':
                continue

            build_ver_split = str_build_info.split('-i ')
            if len(build_ver_split) > 1:
                str_build_ver = build_ver_split[1].split(' -j')[0]
            else:
                str_build_ver = ""

            if str_build_info.find('eng') >= 0:
                str_build_mode = "eng"
            else:
                str_build_mode = "user"

            str_build_cl = 'AP' + str_build_info.split('AP')[1].split('OPT')[0]

            str_hw_rev = ''
            hw_opt_idx = str_build_info.find('-w ')
            if hw_opt_idx >= 0:
                hw_opt_idx += 3
                str_hw_rev = str_build_info[hw_opt_idx:hw_opt_idx+2]

            tag = build.findAll('span')
            if tag[0].text == "":
                str_build_id = tag[1].text
            else:
                str_build_id = tag[0].text

            duration = ''
            for t in tag:
                # find begin date
                if t.text.find("201") >= 0 and t.text[4:5] == '-'\
                    and t.text[7:8] == '-' :
                    begin_date =  t.text

                # find duration
                if (t.text.find("m:") >= 0) or \
                    (t.text.find("minutes") >= 0 and t.text.find("seconds") >= 0):
                    duration = t.text
#print "duration : " + duration

            if showBy is True:
                str_triggered_by = tag[-1].text[1:-1]

                print '| ' + str_build_id + ' | ' + \
                    str_build_mode.ljust(4, ' ') + ' | ' + \
                    begin_date + ' | ' + \
                    build_status.ljust(11, ' ') + ' | ' + \
                    str_build_ver + ' ' + str_build_cl + "[ by " + str_triggered_by + "]"
                build_list.append(BuildInfo(str_build_id, build_url, \
                            str_build_mode, begin_date, build_status, \
                            str_hw_rev, str_build_ver, \
                            str_build_cl, duration, str_triggered_by ))


            else:
                print '| ' + str_build_id + ' | ' + \
                        str_build_mode.ljust(4, ' ') + ' | ' + \
                        begin_date + ' | ' + \
                        build_status.ljust(11, ' ') + ' | ' + \
                        str_build_ver + ' '  + str_build_cl
                build_list.append(BuildInfo(str_build_id, build_url, \
                            str_build_mode, begin_date, build_status, \
                            str_hw_rev, str_build_ver, \
                            str_build_cl, duration))
        return build_list

    def getBuildList(self, body, showBy):
        print "---------------------------------------------------------------------------"
        print "| ID      | Mode | Begin Date          | Status      | Version"
        print "---------------------------------------------------------------------------"
        builds = body.findAll('tr', {'class':re.compile('')})
        return self.buildListParser(builds, showBy)

    def showBuildListEachTable(self, bodies, showBy):
        print "---------------------------------------------------------------------------"
        print "| ID      | Mode | Begin Date          | Status      | Version"
        print "---------------------------------------------------------------------------"
        build_list = []

        for body in bodies:
            builds = body.findAll('tr', {'class':re.compile('')})
            build_list += self.buildListParser(builds, showBy)

        return build_list

def print_help():
    print "help"
    print "Usage: " + sys.argv[0] + " <options>..."
    print "     -p <PROJECT>"
    print "     -v <VERSION>"
    print "     -c <CONFIGURATION>      PBS | RBS"
    print "     -t <TYPE>               user | eng"
    print "     -d                      download DEBUG_KERNEL file"
    print "     --url <BUILD URL>       download binary from <BUILD URL>"
    print "     --list                  show build list"
    print "     -r, --reset             reset login id / password"

def downloadPath(config):
    folder_name = build_info[0] + "/"

    for i in range(1, len(build_info)):
        folder_name += build_info[i] + "_"

    return config.getDownloadPath() + "/" + folder_name

def downloadFromRbs(config, qb):
    qb.setPrjUrl(config.getRbsUrl())
    download_path = downloadPath(config)
    files = qb.downloadReleaseBinAll(build_info, download_path)
    if files == None:
        files = qb.downloadBuildBinAll(build_info, download_path)
    return files

def downloadFromPbs(config, qb):
    qb.setPrjUrl(config.getPbsUrl())
    download_path = downloadPath(config)
    return qb.downloadBuildBinAll(build_info, download_path)

def showBuildList(build_cfg, config, qb):
    if build_cfg == "PBS":
        qb.setPrjUrl(config.getPbsUrl())
    else:
        qb.setPrjUrl(config.getRbsUrl())

    qb.showBuildList()

if __name__ == '__main__':

#    updater_path = os.path.dirname(os.path.abspath( __file__ )) + '/updater.sh'
#    isUpdate = os.system(updater_path)
#    if isUpdate != 0:
#        os.execv(__file__, sys.argv)
#        sys.exit(0)

    if len(sys.argv) == 1:
        print_help()
        sys.exit(0)

    project_name = None
    build_info = []
    build_version = None
    build_type = None

    opt = None
    build_cfg = None
    from_release = True
    from_select = False
    get_debug_files = False
    reset_login = False

    direct_download_url = None
    show_build_list = False
    opts, args = getopt.getopt(sys.argv[1:], "p:v:c:t:a:do:r",\
                    ["project=", "url=", "list", "reset"])

    for opt, arg in opts:
        if opt in ("-p", "--project"):
            project_name = arg
        elif opt == "-v":
            build_version = arg
        elif opt == "-c":
            build_cfg = arg
        elif opt == "-t":
            build_type = arg
        elif opt == "-d":
            get_debug_files = True
        elif opt == "--url":
            direct_download_url = httpsToHttp(arg)
        elif opt == "--list":
            show_build_list = True
        elif opt in ("-r", "--reset"):
            reset_login = True
        else:
            print "error : " + arg
            print_help()

    build_info.append(project_name)
    build_info.append(build_version)
    if build_type is not None:
        build_info.append(build_type)

    config = ABGetConfigParser(project_name, build_cfg)
    print "Quick Build Login"
    if (config.getUserName() == "" or reset_login is True):
        username = raw_input("id : ")
        password = getpass.getpass("pw : ")
    else:
        username = config.getUserName()
        password = config.getPassword()

    qb = QbuildParser(project_name, get_debug_files)
    qb.login(username, password, config)

    if show_build_list is True:
        showBuildList(build_cfg, config, qb)
        sys.exit(0)

    if direct_download_url is not None:
        download_path = config.getDownloadPath() + "/"
        print direct_download_url + " => " + download_path
        files = qb.downloadAll(direct_download_url, download_path);
    else:
        prj_url = config.getRbsUrl()
        print prj_url

        if build_cfg == "RBS":
            files = downloadFromRbs(config, qb)
        elif build_cfg == "PBS":
            files = downloadFromPbs(config, qb)
        else:
            files = downloadFromRbs(config, qb)
            if files  == None:
                files = downloadFromPbs(config, qb)

    if files == None:
        print "error : cannot find build : "
        print build_info
    else:
        odin_cmd = "./pyodin.py "
        for f in files:
            odin_cmd += f + " "

        print ""
        print "==========================================================================="
        print "Launching Pyodin..."
        print odin_cmd
        os.system(odin_cmd)
