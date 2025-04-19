from chainlit.types import CommandDict
from chainlit.input_widget import TextInput, Select, Slider, Switch, Tags


commands: list[CommandDict] = [
    {"id": "Picture", "icon": "image", "description": "Use DALL-E", "persistent": True, "button": False},
    {"id": "stream", "icon": "globe", "description": "Find on the web", "persistent": True, "button": True},
    {
        "id": "Canvas",
        "icon": "pen-line",
        "description": "Collaborate on writing and code", "persistent": True, "button": False,
    },
]

widgets = [
            TextInput(id="postgres", label="Postgres Sql",placeholder="postgresql://test:test@localhost:5432/my_db"),
            TextInput(id="pinecone", label="PineCone Api",placeholder="sk_..."),
            Select(
                id="Model",
                label="OpenAI - Model",
                values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"],
                initial_index=0,
            ),
            Slider(
                id="Temperature",
                label="OpenAI - Temperature",
                initial=0.4,
                min=0,
                max=2,
                step=0.1,
            ),
            Switch(id="Streaming", label="OpenAI - Stream Tokens", initial=True),
            Tags(id="StopSequence", label="OpenAI - StopSequence", initial=["Answer:"]),
        ]