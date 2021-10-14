import sys
import subprocess
import os
import json

PACKAGE_PATH = "packages.json"

if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

subprocess.run(["apt-get", "update"])
subprocess.run(["apt-get", "upgrade", "-y"])

f = open(PACKAGE_PATH, "r")
datafile = json.load(f)

aptpackages = datafile["apt"]
pippackages = datafile["pip"]
keys = datafile["keys"]
github = datafile["github"]

print("Running keys")

for i in keys:
    subprocess.run(["sudo", "sh", "-c", "'echo \"deb " + i +
                   "\" > /etc/apt/sources.list.d/ros-latest.list'"])
    print("Adding" + i)

print("Updating local repo...")
subprocess.run(["apt-get", "update"])

print("Installing apt packages")
for i in aptpackages:
    subprocess.run(["apt-get", "install", i, "-y"])
    print("Installing " + i)

print("Installing pip packages")
for i in pippackages:
    subprocess.run(["pip", "install", "-U", i])
    print("Installing " + i)

print("Installing pip3 packages")
for i in pippackages:
    subprocess.run(["pip3", "install", "-U", i])
    print("Installing " + i)

print("Installing Autoware v1.12.0")

os.chdir('~')
subprocess.run(["wget", "http://bitbucket.org/eigen/eigen/get/3.3.7.tar.gz"])
os.mkdir('eigen')
subprocess.run(["tar", "--strip-components=1",
               "-xzvf", "3.3.7.tar.gz", "-C", "eigen"])
os.chdir('eigen')
os.mkdir('build')
os.chdir('build')
subprocess.run(["cmake", ".."])
subprocess.run(["make"])
subprocess.run(["make", "install"])
os.chdir('~')
subprocess.run(["rm", "-rf", "3.3.7.tar.gz"])
os.rmdir('eigen')

print("Building autoware")
os.mkdir('autoware.ai/src')
os.chdir('autoware.ai')
subprocess.run(["wget", "-O", "autoware.ai.repos",
               "\"https://raw.githubusercontent.com/Autoware-AI/autoware.ai/1.12.0/autoware.ai.repos\""])
subprocess.run(["vcs", "import", "src", "<", "autoware.ai.repos"])
subprocess.run(["rosdep", "update"])
subprocess.run(["rosdep", "install", "-y", "--from-paths",
               "src", "--ignore-src", "--rosdistro melodic", "--os=ubuntu:bionic"])
subprocess.run("AUTOWARE_COMPILE_WITH_CUDA=1", "colcon", "build",
               "--cmake-args", "-DCMAKE_BUILD_TYPE=Release")


os.chdir('~')
os.mkdir('catkin_ws')
os.chdir('~')
os.mkdir('src')
os.chdir('src')

for i in github:
    subprocess.run(["git", "clone", "https://github.com/" + i])

os.chdir('..')
subprocess.run(["catkin-make"])

subprocess.run(
    ["echo", "\"source ~/catkin_ws/devel/setup.bash\"", ">>", "~/.bashrc"])
subprocess.run(
    ["echo", "\"source ~/autoware.ai/install/setup.bash\"", ">>", "~/.bashrc"])
subprocess.run(["source", "~/.bashrc"])

os.chdir('~')
os.chmod('catkin_ws/src/ai-navigation/run.sh', 0o770)
