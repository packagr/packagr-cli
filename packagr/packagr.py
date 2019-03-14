#!/usr/bin/env python

from cleo import Application
from commands import admin, packaging


application = Application()

# admin
application.add(admin.CreatePackage())
application.add(admin.ConfigureClient())
application.add(admin.SetValue())
application.add(admin.AddValue())
application.add(admin.InstallCommand())
application.add(admin.BumpVersion())

# package
application.add(packaging.CreatePackage())
application.add(packaging.UploadPackage())


if __name__ == '__main__':
    application.run()
