import sys
import subprocess
import os
import json
import getpass

PACKAGE_PATH = "packages.json"
PATH = os.path.expanduser("~")
USER = getpass.getuser()

#if os.geteuid() != 0:
#    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

subprocess.run(["sudo", "apt-get", "update"])
subprocess.run(["sudo", "apt-get", "upgrade", "-y"])

os.chmod('catkin_src.sh', 0o770)
os.chmod('vcs.sh', 0o770)

f = open(PACKAGE_PATH, "r")
datafile = json.load(f)

aptpackages = datafile["apt"]
pippackages = datafile["pip"]
keys = datafile["keys"]
github = datafile["github"]
public_keys = datafile["public_keys"]

print("Running keys")

for i in public_keys:
    subprocess.run(["sudo", "apt-key", "adv", "--keyserver",
                   "keyserver.ubuntu.com", "--recv-key", i])



subprocess.run(["sudo", "touch", "/etc/apt/sources.list.d/ros-latest.list"])

subprocess.run(["sudo", "python", "keys.py"])

subprocess.run(["wget", "https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.0.130-1_amd64.deb"])

subprocess.run(["sudo", "dpkg", "-i", "cuda-repo-ubuntu1804_10.0.130-1_amd64.deb"])

subprocess.run(["sudo", "apt-key", "adv", "--fetch-keys", "https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub"])

print("Updating local repo...")
subprocess.run(["sudo", "apt-get", "update"])

print("Installing apt packages")
for i in aptpackages:
    subprocess.run(["sudo", "apt-get", "install", i, "-y"])
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

os.chdir(PATH)
subprocess.run(
    ["wget", "https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz"])
os.mkdir('eigen')
subprocess.run(["tar", "--strip-components=1",
               "-xzvf", "eigen-3.4.0.tar.gz", "-C", "eigen"])
os.chdir('eigen')
os.mkdir('build')
os.chdir('build')
subprocess.run(["sudo", "cmake", ".."])
subprocess.run(["sudo", "make"])
subprocess.run(["sudo", "make", "install"])
os.chdir(PATH)
subprocess.run(["sudo", "rm", "-rf", "eigen-3.4.0.tar.gz"])
subprocess.run(["sudo", "rm", "-rf", "eigen"])

print("Building autoware")
os.mkdir('autoware.ai')
os.chdir('autoware.ai')
os.mkdir('src')
os.chdir(PATH)
os.chdir('autoware.ai')

subprocess.run(["sudo", "rosdep", "init"])

subprocess.run(["wget", "-O", "autoware.ai.repos",
               "https://gitlab.com/autowarefoundation/autoware.ai/autoware/raw/1.12.0/autoware.ai.repos?inline=false"])
subprocess.run(["../deployment/vcs.sh"], shell=True)
subprocess.run(["rosdep", "update"])
subprocess.run(["rosdep", "install", "-y", "--from-paths", "src", "--ignore-src", "--rosdistro=melodic", "--os=ubuntu:bionic"])
subprocess.run(["AUTOWARE_COMPILE_WITH_CUDA=1", "colcon", "build", "--cmake-args", "-DCMAKE_BUILD_TYPE=Release"], shell=True)


os.chdir(PATH)
os.mkdir('catkin_ws')
os.chdir('catkin_ws')
os.mkdir('src')
os.chdir('src')

for i in github:
    subprocess.run(["git", "clone", "https://github.com/" + i])

os.chdir(PATH)
os.chdir('catkin_ws')

subprocess.run(["../deployment/catkin_src.sh"])

subprocess.run(["catkin_make"])

os.chdir(PATH)
os.chmod('catkin_ws/src/ai-navigation/run.sh', 0o770)

os.mkdir('AVData')
subprocess.run(["cp catkin_ws/src/ai-navigation/speedBoiMap.pcd", "AVData"])
subprocess.run(["sudo cp catkin_ws/src/ai-navigation/99-usb-serial.rules" "/etc/udev/rules.d/"])
subprocess.run(["sudo", "chown", USER + ":", "/dev/ttyUSB9"])
subprocess.run(["sudo", "chmod", "777", "/dev/ttyUSB9"])

