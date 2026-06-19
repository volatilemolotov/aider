# k8s-agent-sandbox support

## What is new

This integration adds three new parameters for aider:

- `sandbox-type`: type of sandbox (currently there is only `k8s-agent-sandbox` supported).
- `sandbox-namespace`: namespace where your router and sandboxes live.
- `sandbox-warmpool`: name of your sandbox warmpool.

It allows aider to use `k8s-agent-sandbox` Python SDK to communicate with a Kubernetes cluster, create sandboxes and run code inside it.

## How to run

How to set up environment and run aider with `k8s-agent-sandbox` support. 

You can set up a test environment in a KinD cluster. Here is [an example](https://github.com/kubernetes-sigs/agent-sandbox/tree/main/examples/python-runtime-sandbox).

Follow these steps to install the requirements:

```bash
python -m venv venv
. venv/bin/activate

pip install -e .
pip install -r requirements/requirements-dev.txt

export VERSION=main
pip install "git+https://github.com/kubernetes-sigs/agent-sandbox.git#subdirectory=clients/python/agentic-sandbox-client"
```

Run the aider:
```bash
export OPENAI_API_KEY=sk-***
python -m aider --model o3-mini --api-key openai=$OPENAI_API_KEY --sandbox-type k8s-agent-sandbox --sandbox-namespace default --sandbox-warmpool simple-sandbox-warmpool
```

or using the config file names .aider.conf.yml:
```yml
model: o3-mini
api-key: 
sandbox-type: k8s-agent-sandbox
k8s-sandbox-namespace: agents-isolated-ns
k8s-sandbox-warmpool: python-3-11-pool
```

Ask: `can you check what is os in my k8s sandbox?`

The output should look like this:
```log
Let's run a command in the sandbox to display the OS release information.


cat /etc/os-release



Tokens: 9.6k sent, 25 received. Cost: $0.01 message, $0.01 session.

Running in k8s sandbox: cat /etc/os-release
Your Kubernetes sandbox is running Ubuntu 22.04.5 LTS (Jammy Jellyfish).
```
