# Overview

This project contains all the source code for running the Pico Ws that
form the networking of the Halloween project. This project contains a
mixture of code that is Pico W hardware specific (```coordinator.py```
and ```endpoint.py``` for example) with the majority of the rest of the
code written as plain of Python so that it can be easily tested in on
a PC.

The networking uses a simple star like architecture. A single Coordinator
node is responsible for orchestrating all the other endpoint nodes in the
network. This architecture means changes in the orchestration across the
nodes only require changes to a single node on the network (the coordinator).

Under the circumstances that this project was envisaged, the network topology
is expected to consist of a single coordinator node and multiple endpoint
nodes, with each node being either a coordinator or an endpoint. The code
provide does allow for more complex scenarios. There is no technical reason
why a node could not be both an endpoint and a coordinator. This opens up
the possibility for multiple coordinators in a mesh style network topology.

# Endpoint nodes

The endpoint nodes provide all input sensors in the display and perform all
output display operations. Upon startup, each endpoint node will register
with a coordinator node. Periodically, the endpoint node is also required
to send a heartbeat message to the coordinator node to let the coordinator
know it is still alive. If contact with a coordinator node cannot be
established or is later lost, the endpoint node will reboot itself.

The endpoint nodes are required to periodically send heartbeat messages to
the coordinator node because if the coordinator node is power cycled for
any reason then it will lose the details of all registered nodes.

When an endpoint registers with the coordinator, metadata will be exchanged
which associated the node with a role. The role determines which events
(vocabulary) will be sent from the coordinator to the endpoint node. An
endpoint has a single role.

The endpoint runs a server application on core 0. This will listen for
messages from the coordinator and then execute them (typically on core 1 if
processing will take a while). The messages received are defined by the
role and will typically include actions.

Some endpoints also have input sensors (buttons, PIR, ultrasonic etc.).
The endpoint should take no action from these events but rather send them
to the coordinator who will then distribute the events to all required nodes.
Because input sensors do not typically take a lot of processing, these are
commonly done as part of the server application running on core 0; however
there is no requirement for this to be the case.

### Setup a new endpoint node

Copy the `config.py` file to the Pico and set the properties accordingly.
Copy the following files to the Pico:

* `pico.py` <- Pico W MicroPython compatible code only
* `directory.py` <- Common Python compatible code that handles lookup of names.
* `messages.py` <- Common Python compatible code that handles dealing with messages.
* `endpoint.py` <- Example Python compatible code, specific to endpoint nodes.

Create a new `main.py` file that contains:
TODO

# Coordinator node

The coordinator node is the brains of the operation but has no sensors or
outputs and thus plays no active part in the presentation or interaction.
Each endpoint node will register with the coordinator and is required to send
periodic heartbeat events to the coordinator. The coordinator maintains the
set of all nodes currently active and alive on the network. Any endpoint node
that fails to supply a heartbeat or respond to messages will be removed from
the set of nodes the coordinator manages.

Each node will have a name and role associated with it. The name should be
unique and only a single entry will be maintained for a given name. The role
is not unique and it is expected that multiple nodes will have the same role.
The coordinator will send messages either to a name (single node) or a role
(zero or more nodes).

The endpoint nodes will send messages to the coordinator that represent events
(such a button presses or sensor triggered). The coordinator will know which
nodes to distribute the incoming events to.

### Setup a new coordinator node

Copy the `config.py` file to the Pico and set the properties accordingly.
Copy the following files to the Pico:

* `pico.py` <- Pico W MicroPython compatible code only
* `directory.py` <- Common Python compatible code that handles lookup of names.
* `messages.py` <- Common Python compatible code that handles dealing with messages.
* `coordinator.py` <- Example Python compatible code, specific to coordinator nodes.

Create a new `main.py` file that contains the same code as in `template.py`

# Universal endpoint vocabulary

These messages must be responded to by all endpoints regardless of role.

* ALIVE - This message is sent by the coordinator to an endpoint which is overdue
  sending a HEARTBEAT message. An OK response is considered the same as receiving
  a HEARTBEAT message.
* ROLE - Respond with the endpoints role as plain text.
* NAME - Respond with the endpoints name as plain text.
* RESTART - The coordinator requests that the endpoint power cycles itself.

# Universal coordinator vocabulary

These messages must be responded to by coordinators.

* HEARTBEAT - Registers the endpoint with the coordinator. The coordinator may
  subsequently request name and role information from the endpoint.
* REGISTER
* UNREGISTER
