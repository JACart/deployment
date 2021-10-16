import sys
import subprocess
import os
import json

f = open(PACKAGE_PATH, "r")
datafile = json.load(f)

keys = datafile["keys"]

apt = open("/etc/apt/sources.list.d/ros-latest.list", "a")
for i in keys:
    apt.write(i + "\n")
    print("Adding" + i)


apt.close()