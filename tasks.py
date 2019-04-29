from invoke import task


@task
def gen_state_machine_diagrams(ctx):
    from config_composer.sources.machines import (
        BasicSourceMachine,
        ExpirableBasicSourceMachine,
    )
    from transitions.extensions import GraphMachine

    class BasicSourceGraphMachine(GraphMachine, BasicSourceMachine):
        pass

    class ExpirableBasicSourceMachine(GraphMachine, ExpirableBasicSourceMachine):
        pass

    class Foo:
        pass

    basic = BasicSourceGraphMachine(Foo())
    basic.get_graph().draw(
        "./docs/images/basic_source_machine_state_diagram.png", prog="dot"
    )

    expirable = ExpirableBasicSourceMachine(Foo())
    expirable.get_graph().draw(
        "./docs/images/expirable_basic_source_machine_state_diagram.png", prog="dot"
    )


@task(pre=[gen_state_machine_diagrams])
def build_docs(ctx):
    with ctx.cd("./docs"):
        ctx.run("make html")
