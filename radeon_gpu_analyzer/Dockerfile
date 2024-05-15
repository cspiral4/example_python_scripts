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
RUN apt-get update && apt-get install -y build-essential
RUN apt-get install -y wget python3
RUN apt-get install -y python-is-python3
RUN apt-get install -y libboost-all-dev
RUN apt-get install -y gcc-multilib g++-multilib cmake git
RUN apt-get install -y libglu1-mesa-dev
RUN apt-get install -y mesa-common-dev
RUN apt-get install -y libgtk2.0-dev
RUN apt-get install -y zlib1g-dev libx11-dev
RUN apt-get -q install -y qtbase5-dev
RUN apt-get -q install -y qtbase5-dev-tools
RUN apt-get -q install -y qt5-qmake
RUN wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | tee /etc/apt/trusted.gpg.d/lunarg.asc
RUN wget -qO /etc/apt/sources.list.d/lunarg-vulkan-jammy.list https://packages.lunarg.com/vulkan/lunarg-vulkan-jammy.list
RUN apt-get update && apt-get install -y vulkan-sdk
RUN mkdir my_docker_test
RUN git clone https://github.com/GPUOpen-Tools/radeon_gpu_analyzer.git /my_docker_test/radeon_gpu_analyzer
RUN ls -l /usr/bin/*qt* /usr/lib/qt5 /usr/lib/x86_64-linux-gnu/qt5/* /usr/include/x86_64-linux-gnu/qt5/*
RUN /bin/python /my_docker_test/radeon_gpu_analyzer/build/pre_build.py --qt 5.15.3 --qt-root /usr/bin --vk-include /usr/include/vulkan/ --vk-lib /usr/lib/x86_64-linux-gnu/vulkan/
# try /usr/include/x86_64-linux-gnu/qt5/ as qt-root
# RUN cmake -B/my_docker_test/radeon_gpu_analyzer/build/release -DCMAKE_BUILD_TYPE=Release /my_docker_test/radeon_gpu_analyzer/
# RUN cd /my_docker_test/radeon_gpu_analyzer/build/release && make -j4
# RUN ls -R /my_docker_test/radeon_gpu_analyzer/build/release

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
