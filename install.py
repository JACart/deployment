import sys
import subprocess
import os
import json

PACKAGE_PATH = "packages.json"
PATH = os.path.expanduser("~")

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
public_keys = datafile["public_keys"]

print("Running keys")

for i in public_keys:
    subprocess.run(["apt-key", "adv", "--keyserver",
                   "keyserver.ubuntu.com", "--recv-key", i])

subprocess.run(["touch", "/etc/apt/sources.list.d/ros-latest.list"])

apt = open("/etc/apt/sources.list.d/ros-latest.list", "a")
for i in keys:
    apt.write(i + "\n")
    print("Adding" + i)

apt.close()

print("Updating local repo...")
subprocess.run(["apt-get", "update"])

print("Installing apt packages")
for i in aptpackages:
    subprocess.run(["apt-get", "install", i, "-y"])
    print("Installing " + i)

subprocess.run(["apt", "--fix-broken", "install", "-y"])

print("Installing pip packages")
for i in pippackages:
    subprocess.run(["pip", "install", "-U", i])
    print("Installing " + i)

print("Installing pip3 packages")
for i in pippackages:
    subprocess.run(["pip3", "install", "-U", i])
    print("Installing " + i)

print("Installing Autoware v1.12.0")

os.chdir(PATH)
subprocess.run(
    ["wget", "https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz"])
os.mkdir('eigen')
subprocess.run(["tar", "--strip-components=1",
               "-xzvf", "eigen-3.4.0.tar.gz", "-C", "eigen"])
os.chdir('eigen')
os.mkdir('build')
os.chdir('build')
subprocess.run(["cmake", ".."])
subprocess.run(["make"])
subprocess.run(["make", "install"])
os.chdir(PATH)
subprocess.run(["rm", "-rf", "eigen-3.4.0.tar.gz"])
subprocess.run(["rm", "-rf", "eigen"])

print("Building autoware")
os.mkdir('autoware.ai')
os.chdir('autoware.ai')
os.mkdir('src')
os.chdir(PATH)
os.chdir('autoware.ai')
subprocess.run(["wget", "-O", "autoware.ai.repos",
               "\"https://raw.githubusercontent.com/Autoware-AI/autoware.ai/1.12.0/autoware.ai.repos\""])
subprocess.run(["vcs", "import", "src", "<", "autoware.ai.repos"])
subprocess.run(["rosdep", "update"])
subprocess.run(["rosdep", "install", "-y", "--from-paths",
               "src", "--ignore-src", "--rosdistro melodic", "--os=ubuntu:bionic"])
subprocess.run("AUTOWARE_COMPILE_WITH_CUDA=1", "colcon", "build",
               "--cmake-args", "-DCMAKE_BUILD_TYPE=Release")


os.chdir(PATH)
os.mkdir('catkin_ws')
os.chdir(PATH)
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

os.chdir(PATH)
os.chmod('catkin_ws/src/ai-navigation/run.sh', 0o770)
