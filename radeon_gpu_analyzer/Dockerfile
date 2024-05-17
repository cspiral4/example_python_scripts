# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

################################################################################
# Pick a base image to serve as the foundation for the other build stages in
# this file.
#
# For illustrative purposes, the following FROM command
# is using the alpine image (see https://hub.docker.com/_/alpine).
# By specifying the "latest" tag, it will also use whatever happens to be the
# most recent version of that image when you build your Dockerfile.
# If reproducability is important, consider using a versioned tag
# (e.g., alpine:3.17.2) or SHA (e.g., alpine@sha256:c41ab5c992deb4fe7e5da09f67a8804a46bd0592bfdf0b1847dde0e0889d2bff).
FROM ubuntu:22.04 AS base

################################################################################
# Create a stage for building/compiling the application.
#
# The following commands will leverage the "base" stage above to generate
# a "hello world" script and make it executable, but for a real application, you
# would issue a RUN command for your application's build process to generate the
# executable. For language-specific examples, take a look at the Dockerfiles in
# the Awesome Compose repository: https://github.com/docker/awesome-compose
FROM base as build

RUN <<EOF
    set -e
    set -x
    export DISPLAY="10.0.0.101:0.0"
    apt-get update
    apt-get install -y apt-utils
    apt-get install -y perl
    apt-get upgrade -y
    apt-get install -y wget
    wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | tee /etc/apt/trusted.gpg.d/lunarg.asc
    wget -qO /etc/apt/sources.list.d/lunarg-vulkan-jammy.list https://packages.lunarg.com/vulkan/lunarg-vulkan-jammy.list
    apt-get update
    apt-get install -y build-essential
    apt-get install -y python3
    apt-get install -y python-is-python3
    apt-get install -y libboost-all-dev
    apt-get install -y gcc-multilib g++-multilib cmake git
    apt-get install -y libglu1-mesa-dev
    apt-get install -y mesa-common-dev
    apt-get install -y libgtk2.0-dev
    apt-get install -y zlib1g-dev libx11-dev
    apt-get install -y vulkan-sdk
    apt-get install -y libxcb1 libxcb1-dev
    apt-get install -y libxcb-xinerama0 libxcb-xinerama0-dev
    apt-get install -y xfce4 xfce4-goodies
    wget -qO /tmp/qt-installer.run https://d13lb3tujbc8s0.cloudfront.net/onlineinstallers/qt-online-installer-linux-x64-4.8.0.run
    chmod +x /tmp/qt-installer.run
    mkdir -p /opt/Qt
    # this installer is interactive, so we set DISPLAy to a valid X Server and use the --accept options to accept the license.
    /tmp/qt-installer.run -t /opt/Qt -p xcb --am --al -c --ao
    # Using apt-get to install QtCreator is not working.
    # echo "2\n" > ./qtcreator.txt
    # cat ./qtcreator.txt
    # export qtc_input=./qtcreator.txt
    # apt-get install -y qtcreator
    # apt-get install -y qtbase5-dev
    # apt-get install -y qtbase5-dev-tools
    # apt-get install -y qt5-qmake
EOF
RUN <<EOF2
    set -e
    set -x
    mkdir my_docker_test
    git clone https://github.com/GPUOpen-Tools/radeon_gpu_analyzer.git /my_docker_test/radeon_gpu_analyzer
    ls -l /opt/Qt
    # /bin/python /my_docker_test/radeon_gpu_analyzer/build/pre_build.py --qt 5.15.3 --qt-root /usr/bin --vk-include /usr/include/vulkan/ --vk-lib /usr/lib/x86_64-linux-gnu/vulkan/
    # try /usr/include/x86_64-linux-gnu/qt5/ as qt-root
    # cmake -B/my_docker_test/radeon_gpu_analyzer/build/release -DCMAKE_BUILD_TYPE=Release /my_docker_test/radeon_gpu_analyzer/
    # cd /my_docker_test/radeon_gpu_analyzer/build/release && make -j4
    # ls -R /my_docker_test/radeon_gpu_analyzer/build/linux
EOF2

################################################################################
# Create a final stage for running your application.
#
# The following commands tell
# the container runtime to execute RadeonGPUAnalyzerGUI when the image is run. 
# Ideally this stage
# contains the minimal runtime dependencies for the application as to produce
# the smallest image possible. This often means using a different and smaller
# image than the one used for building the application, but for illustrative
# purposes the "base" image is used here.
FROM base AS final

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser
USER appuser

# Copy the executable from the "build" stage.
COPY --from=build RadeonGPUAnalyzerGUI /bin/RadeonGPUAnalyzerGUI

# What the container should run when it is started.
ENTRYPOINT [ "/bin/RadeonGPUAnalyzerGUI" ]
