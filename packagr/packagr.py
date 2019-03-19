#!/usr/bin/env python3

from cleo import Application
from packagr.commands import admin, packaging


application = Application()

# admin
application.add(admin.CreatePackage())
application.add(admin.ConfigureClient())
application.add(admin.SetValue())
application.add(admin.AddValue())
application.add(admin.RemoveValue())
application.add(admin.InstallCommand())
application.add(admin.UninstallCommand())
application.add(admin.BumpVersion())

# package
application.add(packaging.CreatePackage())
application.add(packaging.UploadPackage())


def run():
    application.run()
