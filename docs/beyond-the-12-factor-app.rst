.. _beyond-12-factor-app-config:

Beyond the 12 Factor App Config
===============================

.. contents:: Table of Contents
   :depth: 4
   :local:

A quick review
~~~~~~~~~~~~~~

It's a really good pattern (up to a point)
------------------------------------------

The *12 Factor App* section on `configuration <https://12factor.net/config>`_
advocates a

    ... strict separation of config from code ...

by storing

    ... config in environment variables ...

with the view that environment variables are:

    - ... easy to change between deploys without changing any code ...
    - ... [have] little chance of being checked into the code repo ...
    - ... are a language- and OS-agnostic standard ...

Using env vars as your sole source *is a great start*.

But config has to live somewhere and there will always be a process to load
the config into the environment for applications to use. Typically the
config will be stored in either:

    - files
    - databases
    - special config services

All these sources need appropriate processes for taking the values and
translating them into env vars before starting the application.


So is a Single Point of Truth (*SPoT*)
--------------------------------------

In addition a popular pattern is to put all configuration parameters into a
single canonical object/module/class to make it easy to reason about.

Having a SPoT greatly aides in auditing and documenting all the parameters
which can change the behvaiour of an application.


.. Keeping config DRY
.. ------------------
.. I your business develops and runs more than one
..
.. TODO


But Secrets make deployment more complicated
--------------------------------------------

As soon as an application requires secret configuration parameters (which
have to live somewhere secure) we have to make a decision on where to store
them. Possibly any of:

    1. bury our head in the sand and just store secrets next to normal config
       (unsecured)
    2. make the application aware of a secure secret store so it can retrieve
       secrets as needed
    3. use specialist launchers (envconsul, chamber, etc ...) that can
       retrieve the secrets and pass them to applications via env vars

Each come with their own issues:

    1. is just asking for trouble
    2. voilates the princle of having a SPoT for configuration parameters
    3. requires external tools to launch the application

If we want to maintain a SPoT and secure secrets then we should be choosing
option 3. at which point:

    - the launch tool becomes part of the application (as it cannot run in
      production without it).
    - changing our secret store involves updating our application as we have
      to update the supporting launch tools. Most tools are limited to one
      secret source which makes deployments inflexible.


And Dynamic parameters result in unstable processes
---------------------------------------------------

Using environment variables for configuration also has the down side that any
process which loads them into the runtime environment will have to restart the
application if it ever wants to update them.

Ideally our application should be able to source mutable configuration
parameters from appropriate sources.

The `boto` library running in an EC2 environment is a great example of this.
The compute instances metadata endpoint is regularly read to get up to date
id/secret pairs from which to access other AWS APIs.

A new config pattern
~~~~~~~~~~~~~~~~~~~~

Ideally an applications should:

    #. Maintain a strict separation of configuration from code.
    #. Have a *Single Point of Truth* for all configuration parameters *and*
       secrets.
    #. Get configuration parameters from a *varietry of sources* outside of
       the code base.
    #. Allow the source of configuration parameters & secrets to be set at
       deploytime.
    #. Support dynamic configuration parameters & secrets which can constantly
       change.

Environment Variables are just one source
-----------------------------------------

Environment variables are extremely useful, but we should be able to load
variables from the most appropriate sources for the environment the
application is running in.

For example a single application might want to load configuration parameters
and secrets from any of the following sources: env vars, files (ini, json,
yaml, toml), databases, HashiCorp Vault, AWS Parameter Store, etc ...


Configuring sources at deploytime makes deployment more flexible
----------------------------------------------------------------

We should always be able to customise deploys without changing any code.

Before deployment an application developer will mostly be concerned with the
set of parameter values needed for local and integration testing. We can
image that this is checked into the to the application project as:

    **testing_source_spec.ini**

    .. code:: ini

        [parameter_foo]
        source=Default
        value=bar

        [parameter_baz]
        source=Default
        value=qux

If sources can be easily overridden then the sources of parameters can easily
be defined at deploytime.

    **prod_ec2_source_spec.ini**

    .. code:: ini

        [parameter_foo]
        source=DotEnvFile
        dotenv_file=.env
        path=FOO

        [parameter_baz]
        source=Vault
        path=/secrets/prod/qux
        field=bar

And movement from one hosting platform to another should be fairly painless.

    **prod_k8s_source_spec.ini**

    .. code:: ini

        [parameter_foo]
        source=Env
        path=FOO

        [parameter_baz]
        source=Vault
        path=/secrets/prod/qux
        field=bar


Supporting multiple sources makes deployment simpler and more secure
--------------------------------------------------------------------

The more sources an application supports the more likely configuration
parameters and secrets will be stored in the most appropriate location.

Shared configuration will be sourced from a central location and avoid
copy/pasting changes in multiple locations.

Secrets will be stored in secure services with access control mechanisms
implemented.


Dynamic configuration parameters make an application more stable
-----------------------------------------------------------------

Once an application is aware that configuration can change during it's
runtime patterns can be followed which update configuration parameters from
their sources.

Runtime updates allow for the continuing operation of the application without
redploying or restarting.


.. Comparing old vs. new
.. ~~~~~~~~~~~~~~~~~~~~~
..
.. Comparing Env Var Config to ConfigSource
.. ----------------------------------------
..
.. Only using Env Vars
.. +++++++++++++++++++
..
.. **Local Testing**
..
.. A process laucnher (probably a bash script) will read a local file
.. which contains all the needed config parameters and secrets and inject
.. them into the environment before running the application:
..
..
.. .. blockdiag::
..
..    diagram {
..       orientation = portrait;
..
..       // Set labels to nodes.
..       TestConfig [label = "Test Config\nand Secrets", shape = note];
..       ProcessLaucher [label = "Process Launcher"];
..
..       Application <- Environment;
..       Environment <- ProcessLaucher;
..       ProcessLaucher <- TestConfig;
..    }
..
..
.. **GCP Cloud Compute**
..
.. - The Application is packaged into a contianer
.. - Secrets are stored on a HashiCorp Vault server
.. - Configuration env vars are set in the compute instance settings
..
..
.. .. blockdiag::
..
..    diagram {
..       orientation = portrait;
..
..       // Set labels to nodes.
..       ConfigStore [label = "Compute settings", shape = note];
..       SecretStore [label = "HashiCorp Vault", shape = "flowchart.database"];
..       ProcessLaucher [label = "Process Launcher"];
..
..       Application <- Environment;
..       Environment <- EnvConsul;
..       EnvConsul <- ProcessLaucher;
..       ProcessLaucher <- ConfigStore;
..       EnvConsul <- SecretStore;
..    }
..
..
.. Using ConfigSource
.. ++++++++++++++++++
..
.. **Local Testing**
..
.. .. blockdiag::
..
..    diagram {
..       orientation = portrait;
..
..       // Set labels to nodes.
..       Application [label = "Application + \nConfigSpec"];
..       TestConfig [label = "Test Config & Secrets", shape = note];
..       ProcessLaucher [label = "Process Launcher"];
..
..       Application <- Environment;
..       Application <- TestConfig;
..       Environment <- ProcessLaucher;
..    }
..
..
..
