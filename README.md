# Service Interconnect to enable workload migration

[website]: https://skupper.io/

#### Contents

* [Overview](#overview)
* [Prerequisites](#prerequisites)
* [Step 2: Access your Kubernetes cluster](#step-2-access-your-kubernetes-cluster)
* [Step 3: Set up your Kubernetes namespace](#step-3-set-up-your-kubernetes-namespace)
* [Step 4: Install Skupper in your Kubernetes namespace](#step-4-install-skupper-in-your-kubernetes-namespace)
* [Step 5: Install the Skupper gateway](#step-5-install-the-skupper-gateway)
* [Step 6: Deploy the frontend and backend services](#step-6-deploy-the-frontend-and-backend-services)
* [Step 7: Expose the backend service](#step-7-expose-the-backend-service)
* [Step 8: Expose the frontend service](#step-8-expose-the-frontend-service)
* [Step 9: Test the application](#step-9-test-the-application)
* [Accessing the web console](#accessing-the-web-console)
* [Cleaning up](#cleaning-up)
* [About this example](#about-this-example)

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


## Step 1: Start backend and frontend on the VM

For this example, we are initially running both the backend and the frontend as a local system process.
Run the following command in sepatate tabb.

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

In the Tab1 you will be able to check the logs of the backen, and per each greeting sent by the frontend (running in Tab2) you will see a log in the backend.


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


## Step @: Install RHSI in your Openshift namespace

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


