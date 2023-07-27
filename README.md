# Service Interconnect to enable workload migration

[website]: https://skupper.io/

#### Contents

* [Overview](#overview)
* [Prerequisites](#prerequisites)
* [Step 1: Start the backend and the frontend on the local system](#step-1-start-the-backend-and-the-frontend-on-the-local-system)
* [Step 2: Access your Openshift cluster](#step-2-access-your-openshift-cluster)
* [Step 3: Set up your Openshift namespace](#step-3-set-up-your-openshift-namespace)
* [Step 4: Install RHSI in your Openshift namespace](#step-4-isstall-rhsi-in-your-openshift-namespace)
* [Step 5: Install the Skupper gateway]
* [Step 6: Build the backend image]
* [Step 7: Deploy the backend on Openshift]
* [Step 8: Switch the backend running locally with the one running on Openshift]


(Step-5-Install the Skupper gateway)
(Step-6-uild the backend image)
(Step-7-Deploy the backend on Openshift)
(Step-8-Switch the backend running locally with the one running on Openshift)

* [Cleaning up](#cleaning-up)

## Overview

This example is a basic multi-service HTTP application deployed
across a Kubernetes cluster and a bare-metal host or VM.

It contains two services:

* A backend service that exposes an `/api/greet` endpoint.  It
  returns greetings of the form `Hi, <your-name>.

* A frontend service that sends greetings to the backend and
  fetches new greetings in response.

Both the frontend and the backend run initially on your local
machine. 

We are going to show how the backend can be moved to Openshift and use RHSI to enable the frontend to connect to the backend
using a dedicated service network, withoind need of reconfiguring the frontend.

<!-- <img src="images/entities.svg" width="640"/> -->

## Prerequisites

* A working installation of Podman ([installation guide][install-podman])

* The `oc` command-line tool, version 4.12 or later
  ([installation guide][install-oc-cli])

* The `skupper` command-line tool, version 1.4 or later
  ([installation guide][skupper-cli])

* Access to an Openshift cluster

* The `requests` and `Flask` Python modules.  This is required to
  run the services locally.  To install the modules, run `pip
  install requests Flask`

[install-podman]: https://podman.io/getting-started/installation
[install-oc-cli]: https://docs.openshift.com/container-platform/4.12/cli_reference/openshift_cli/getting-started-cli.html#installing-openshift-cli
[skupper-cli]: https://access.redhat.com/documentation/en-us/red_hat_service_interconnect/1.4/html-single/installation/index#installing-skupper-cli
[ocp-providers]: https://skupper.io/start/openshift.html

## Step 1: Start the backend and the frontend on the local system

For this example, we are initially running both the backend and the frontend as a local system process.
Run the following commands in sepatate tabs.

_**Console for rhsi-demo:**_

~~~ shell
# in Tab1
(cd backend && python main.py)
# in Tab2
(cd frontend && python main.py)
~~~

_Sample output:_

~~~ console
# in Tab1
$ (cd backend && python main.py)
 * Serving Flask app 'api'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:6000
 * Running on http://10.128.0.90:6000
Press CTRL+C to quit
10.128.0.85 - - [26/Jul/2023 13:58:48] "GET /api/greet?name=name1 HTTP/1.1" 200 -
...

# in Tab2
$ (cd frontend && python main.py)
Hello, 1!
Hello, 2!
Hello, 3!
...
~~~

In the Tab1 you will be able to check the logs of the backend, and per each greeting sent by the frontend (running in Tab2) you will see a log in the backend.

## Step 2: Access your Openshift cluster

[Find the instructions][ocp-providers] and use them to authenticate and
configure access.

## Step 3: Set up your Openshift namespace

Use `oc create namespace` to create the namespace you wish
to use (or use an existing namespace).  Use `oc config
set-context` to set the current namespace for your session.

_**Console for rhsi-demo:**_

~~~ shell
oc create namespace rhsi-demo
oc config set-context --current --namespace rhsi-demo
~~~

_Sample output:_

~~~ console
$ oc create namespace rhsi-demo
namespace/rhsi-demo created

$ oc config set-context --current --namespace rhsi-demo
Context "rhsi-demo..." modified.
~~~

## Step 4: Install RHSI in your Openshift namespace

The `skupper init` command installs the Skupper router and service
controller in the current namespace.

_**Console for rhsi-demo:**_

~~~ shell
skupper init
~~~

_Sample output:_

~~~ console
$ skupper init
Skupper is now installed in namespace 'rhsi-demo'.  Use 'skupper status' to get more information.
~~~

## Step 5: Install the Skupper gateway

The `skupper gateway init` command starts a Skupper router on
your local system and links it to the Skupper router in the
current Kubernetes namespace.

_**Console for rhsi-demo:**_

~~~ shell
skupper gateway init --type podman
~~~

_Sample output:_

~~~ console
$ skupper gateway init --type podman
Skupper gateway: ... Use 'skupper gateway status' to get more information.
~~~

The `--type podman` option runs the router as a Podman
container.  You can also run it as a Docker container (`--type
docker`) or as a systemd service (`--type service`).


## Step 6: Build the backend image

Replace the <backend_image_url> with the url of the your image in your image regitry

_**Console for rhsi-demo:**_

~~~ shell
podman build backend/ -t <backend_image_url>
~~~

_Sample output:_

~~~ console
$ podman build backend/ -t <backend_image_url>
Successfully tagged <backend_image_url>:latest
~~~

## Step 7: Deploy the backend on Openshift

_**Console for rhsi-demo:**_

~~~ shell
oc new-app <backend_image_url>
~~~

_Sample output:_

~~~ console
$ oc new-app <backend_image_url> --name backend
--> ...Success...
    Run 'oc status' to view your app.
~~~

## Step 8: Switch the backend running locally with the one running on Openshift

_**Console for rhsi-demo:**_

We are now going to switch the two backends, so that we can decommission the one running on the local system.
To do that, we are first going to expose the backend on the VAN, and then create a forward rule on port 6000 on the local system (through the skupper
gateway) to forwart all incomong requests to the backend VAN service.

Before running the following commands, stop the backend, by pressing CTRL+C on the Tab1.
The frontend has been developed sa that it will try to reconnect if the backend goes down, so when you stop the backend on the local system,
you will see some error messages in the Tab2. Once we will perform the switch to the backend on Openshift, the client will automatically reconnect,
but this time it will connect to the backend running on Openshift.

~~~ shell
skupper service create backend 6000
skupper service bind backend deployment/backend
skupper gateway forward backend 6000
~~~

_Sample output:_

~~~ console
$ skupper service create backend 6000
$ skupper service bind backend deployment/backend
$ skupper gateway forward backend 6000
2023/07/27 12:32:22 CREATE io.skupper.router.tcpListener backend:6000 map[address:backend:6000 name:backend:6000 port:6000 siteId:e06dd6a1-7d36-44bf-88bf-8c50fcdfbcd1]
~~~

Observe the logs in Tab2, you should see that the client has managed to reconnec and continue from ther it stopped.
On Openshift, you can see the logs from the backend pod logs.

## Cleaning up

To remove Skupper and the other resources from this exercise, use
the following commands.

_**Console for hello-world:**_

~~~ shell
kill $(ps -ef | grep 'python main\.py' | awk '{print $2}') 2> /dev/null
skupper gateway delete
skupper delete
oc delete service/backend
oc delete deployment/backend
~~~
