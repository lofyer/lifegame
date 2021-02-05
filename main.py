# -*- coding: UTF-8 -*-

from asyncio import Future, ensure_future

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.shortcuts import print_container
from prompt_toolkit.layout.containers import Float, HSplit, VSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.layout import Layout

from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    Float,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)

from prompt_toolkit.widgets import (
    Box,
    Button,
    Checkbox,
    Dialog,
    Frame,
    Label,
    MenuContainer,
    MenuItem,
    ProgressBar,
    RadioList,
    TextArea,
)

class MessageDialog:
    def __init__(self, title, text):
        self.future = Future()

        def set_done():
            self.future.set_result(None)

        ok_button = Button(text="OK", handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=text)]),
            buttons=[ok_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


def accept_yes():
    get_app().exit(result=True)


def accept_no():
    get_app().exit(result=False)


def do_exit():
    get_app().exit(result=False)

def do_about():
    show_message("About", "Multiple user terminal game for simulating people life.")

def show_message(title, text):
    async def coroutine():
        dialog = MessageDialog(title, text)
        await show_dialog_as_float(dialog)
    ensure_future(coroutine())


async def show_dialog_as_float(dialog):
    " Coroutine. "
    float_ = Float(content=dialog)
    root_container.floats.insert(0, float_)

    app = get_app()

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    result = await dialog.future
    app.layout.focus(focused_before)

    if float_ in root_container.floats:
        root_container.floats.remove(float_)

    return result


body_container = (
    Frame(
        TextArea(text="人生模拟器\nVersion 1.0"),
        title="人生模拟器",
    )
)

root_container = MenuContainer(
    body=body_container,
    menu_items=[
        MenuItem(
            text="Action",
            children=[
                MenuItem("Rest", children=[
                    MenuItem("Sleep"),
                    MenuItem("Snap"),
                ]),
                MenuItem("-", disabled=True),
                MenuItem(
                    "Learn",
                    children=[
                        MenuItem("Professional"),
                        MenuItem("Life"),
                        MenuItem(
                            "Something else..",
                            children=[
                                MenuItem("A"),
                                MenuItem("B"),
                                MenuItem("C"),
                                MenuItem("D"),
                                MenuItem("E"),
                            ],
                        ),
                    ],
                ),
                MenuItem("Save"),
                MenuItem("Save as..."),
                MenuItem("-", disabled=True),
                MenuItem("Exit", handler=do_exit),
            ],
        ),
        MenuItem("View", children=[MenuItem("Status Bar")]),
        MenuItem("Info", children=[MenuItem("About", handler=do_about)]),
    ]
)

# Global key bindings.
bindings = KeyBindings()
bindings.add("tab")(focus_next)
bindings.add("s-tab")(focus_previous)

@bindings.add("c-c")
def _(event):
    " Focus menu. "
    event.app.layout.focus(root_container.window)


application = Application(
    layout=Layout(root_container, focused_element=body_container), 
    key_bindings=bindings,
    #style=style,
    mouse_support=True,
    full_screen=True,
)

def run():
    result = application.run()
    #print("You said: %r" % result)


if __name__ == "__main__":
    run()