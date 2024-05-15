### Building and running RadeonGPUAnalyzerGUI

These docker files configure an Ubuntu 22.04 build of RGA master branch.  
Currently, pre_build.py fails to find Qt - I am using the 5.15.3 version 
that comes with Ubuntu, installed with apt-get.  This also configures the 
system with the latest Vulkan SDK.

### Building

`mv rga.dockerignore .dockerignore`

`docker build -t myrga .`

### Deploying your application to the cloud

First, build your image, e.g.: `docker build -t myapp .`.
If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t myapp .`.

Then, push it to your registry, e.g. `docker push myregistry.com/myapp`.

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.
