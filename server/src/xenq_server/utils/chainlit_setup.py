from chainlit.types import CommandDict
from chainlit.input_widget import TextInput, Slider, Switch


commands: list[CommandDict] = [
    {"id": "CommandLink", "icon": "terminal", "description": "Use the clients cmd prompt", "persistent": True, "button": True},
    {"id": "Search Web", "icon": "globe", "description": "Find on the web", "persistent": True, "button": True},
]

widgets = [
            # Slider(
            #     id="Temperature",
            #     label="Temperature",
            #     initial=0.4,
            #     min=0,
            #     max=2,
            #     step=0.1,
            # ),
            Switch(id="hide_internal", label="Hide Internal Reasoning", initial=True),
            TextInput(id="psql_uri", label="Postgres Sql", placeholder="postgresql://test:test@localhost:5432/my_db"),
            TextInput(id="client_uri", label="Client Uri", placeholder="https://..."),
        ]