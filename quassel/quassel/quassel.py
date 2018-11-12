# -*- coding: utf-8 -*-
# Copyright Hannah von Reth <vonreth@kde.org>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import info
from CraftOS.osutils import OsUtils
from Package.CMakePackageBase import *


class subinfo(info.infoclass):
    def setTargets(self):
        self.svnTargets["master"] = "https://github.com/quassel/quassel.git"
        for ver in ["0.12.0", "0.12.2", "0.12.4"]:
            self.targets[ver] = f"http://quassel-irc.org/pub/quassel-{ver}.tar.bz2"
            self.targetInstSrc[ver] = f"quassel-{ver}"
        self.targetDigests["0.12.2"] = "12e9a88597f724498c40a1548b5f788e7c40858c"
        self.patchToApply["0.11.0"] = ("quassel-0.11.0-20141002.diff", 1)

        self.webpage = "http://quassel-irc.org"
        self.description = "a distributed IRC client"
        self.defaultTarget = "0.12.4"

    def setDependencies(self):
        if CraftCore.compiler.isWindows:
            self.runtimeDependencies["qt-libs/snorenotify"] = None
        self.runtimeDependencies["libs/boost/boost-headers"] = None
        self.runtimeDependencies["libs/zlib"] = None
        self.runtimeDependencies["libs/openssl"] = None
        # self.runtimeDependencies["kdesupport/qca"] = None
        self.runtimeDependencies["dev-utils/pkg-config"] = None
        self.runtimeDependencies["libs/qt5/qtbase"] = None
        self.runtimeDependencies["libs/qt5/qtwebengine"] = None
        self.runtimeDependencies["libs/qt5/qtscript"] = None
        self.buildDependencies["libs/qt5/qttools"] = None
        self.runtimeDependencies["kde/frameworks/tier1/sonnet"] = None


class Package(CMakePackageBase):
    def __init__(self, **args):
        CMakePackageBase.__init__(self)
        self.supportsNinja = self.subinfo.buildTarget == "master" or CraftVersion(self.subinfo.buildTarget) > "0.12.4"
        self.subinfo.options.configure.args = " -DUSE_QT5=ON"
        if OsUtils.isWin():
            self.subinfo.options.configure.args += (" -DCMAKE_INSTALL_BINDIR=bin"
                                                    " -DCMAKE_INSTALL_LIBDIR=bin"
                                                   )

    def install(self):
        return CMakePackageBase.install(self)

    def preArchive(self):
        return utils.mergeTree(os.path.join(self.archiveDir(), "bin"), self.archiveDir())

    def createPackage(self):
        self.blacklist_file.append(os.path.join(self.packageDir(), "blacklist.txt"))
        self.defines["caption"] = self.binaryArchiveName(fileType=None).capitalize()
        self.defines["productname"] = "Quassel IRC"
        self.defines["company"] = "Quassel IRC"
        self.defines["icon"] = os.path.join(self.sourceDir(), "pics", "quassel.ico")
        self.defines["nsis_include"] = f"!include {self.packageDir()}\\SnoreNotify.nsh"
        self.defines["preInstallHook"] = r"""
        ReadRegStr $R0 HKLM "Software\KDE\Quassel" "Install_Dir"
        ${IfNot} $R0 == ""
            ExecWait '"$R0\uninstall.exe" /S _?=$R0'
        ${EndIf}
        """

        self.defines["sections"] = r"""
!define MyApp_AppUserModelId  QuasselProject.QuasselIRC
!define SnoreToastExe "$INSTDIR\SnoreToast.exe"

Section "Quassel"  QUASSEL_ALL_IN_ONE
    SectionIn 1
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
        !insertmacro SnoreShortcut "$SMPROGRAMS\$StartMenuFolder\Quassel.lnk" "$INSTDIR\quassel.exe" "${MyApp_AppUserModelId}"
    !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section "QuasselClient"  QUASSEL_CLIENT
    SectionIn 1
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
        !insertmacro SnoreShortcut "$SMPROGRAMS\$StartMenuFolder\Quassel Client.lnk" "$INSTDIR\quasselclient.exe" "${MyApp_AppUserModelId}"
    !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section "QuasselCore"  QUASSEL_CORE
    SectionIn 1
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
        CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Quassel Core.lnk" "$INSTDIR\quasselcore.exe"
    !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd"""


        self.ignoredPackages.append("binary/mysql")
        self.ignoredPackages.append("libs/dbus")


        return TypePackager.createPackage(self)
