#!/usr/bin/env python

from cleo import Application
from commands import admin


application = Application()

# admin
application.add(admin.CreatePackage())
application.add(admin.ConfigureClient())
application.add(admin.SetValue())
application.add(admin.AddValue())
application.add(admin.InstallCommand())
application.add(admin.BumpVersion())


if __name__ == '__main__':
    application.run()
