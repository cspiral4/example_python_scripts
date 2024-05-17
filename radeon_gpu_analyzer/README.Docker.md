### Building and running RadeonGPUAnalyzerGUI

These docker files configure an Ubuntu 22.04 build of RGA master branch.

The container requires an X Server process to connect to in order to install Qt
and run RadeonGPUAnalyzerGUI.  

"apt-get install -y qtcreator" fails, even with DISPLAY defined, because 
the install assumes a TTY interface, not a script.  Downloading
and installing via the ".run" file works, but now requires
having a Qt account login.  The latest version of Qt is 6.x.  RGA may not 
work with this version.

On Ubuntu docker server hosts, if the system comes with an X Server, you just 
need to update the DISPLAY environment variable in Dockerfile with the host 
IP address.

On Windows docker server hosts, you need to install something like XMing 
or VcXsrv and then use your host IP address for the DISPLAY environment 
variable.

Example, in the Dockerfile: export DISPLAY="10.0.0.100:0.0"

Alternatively, installing and running a VNC server will provide
the container with an X Server without requiring one on the host machine.


Currently, pre_build.py fails to find Qt - I am using the 5.15.3 version 
that comes with Ubuntu, installed with apt-get.  This also configures the 
system with the latest Vulkan SDK.

### Deploying your application to the cloud

First, build your image, e.g.: `docker build -t myapp .`.
If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t myapp .`.

Then, push it to your registry, e.g. `docker push myregistry.com/myapp`.

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.