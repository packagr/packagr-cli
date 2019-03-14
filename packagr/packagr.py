#!/usr/bin/env python

from cleo import Application
from commands import admin


application = Application()
application.add(admin.CreatePackage())
application.add(admin.ConfigureClient())


if __name__ == '__main__':
    application.run()
