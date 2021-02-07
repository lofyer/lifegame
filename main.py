# -*- coding: UTF-8 -*-

import asyncio
from asyncio import Future, ensure_future
from sys import argv

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.document import Document
from prompt_toolkit.shortcuts import print_container
from prompt_toolkit.layout.containers import Float, HSplit, VSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.layout import Layout

from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.shortcuts import CompleteStyle, prompt, PromptSession

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
    SearchToolbar,
    TextArea,
)

help_text = """
OK
"""

commands = [
    "info",
    "about",
    "exit"
]


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

class ColorCompleter(Completer):
    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for command in commands:
            if command.startswith(word):
                yield Completion(
                    command,
                    start_position=-len(word),
                    #selected_style="fg:white bg:" + color,
                    #style="fg:" + color,
                )


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

async def print_counter():
    """
    Coroutine that prints counters.
    """
    try:
        i = 0
        while True:
            print("Counter: %i" % i)
            i += 1
            await asyncio.sleep(3)
    except asyncio.CancelledError:
        print("Background task cancelled.")

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

output_field = TextArea(style="class:output-field", text=help_text)

output_field_2 = TextArea(style="class:output-field", text=help_text)

search_field = SearchToolbar()

input_field = TextArea(
    height=2,
    prompt=">>> ",
    style="class:input-field",
    multiline=False,
    wrap_lines=False,
    search_field=search_field,
    completer=FuzzyCompleter(ColorCompleter(), enable_fuzzy=False)
)

def accept(buff):
    # Evaluate "calculator" expression.
    try:
        #output = "\n\nIn:  {}\nOut: {}".format(
        #    input_field.text, eval(input_field.text)
        #)  # Don't do 'eval' in real code!
        output = "You're typing " + input_field.text + "\n"
        if input_field.text == "info":
            do_about()
        if input_field.text == "exit":
            do_exit()
    except BaseException as e:
        output = "\n\n{}".format(e)
    new_text = output_field.text + output
    

    output_field.buffer.document = Document(
        text=new_text, cursor_position=len(new_text)
    )

    output_field_2.buffer.document = Document(
        text=new_text, cursor_position=len(new_text)
    )

input_field.accept_handler = accept

body_container = HSplit(
    [
        VSplit(
            [
                Frame(
                    output_field
                ),
                Frame(
                    output_field_2
                )
            ]
        ),
        search_field,
        Frame(
            input_field
        )
    ]
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
#bindings.add("tab")(focus_next)
#bindings.add("s-tab")(focus_previous)

@bindings.add("c-c")
def _(event):
    " Focus menu. "
    event.app.layout.focus(root_container.window)

@bindings.add("c-v")
def _(event):
    " Focus menu. "
    event.app.layout.focus(input_field.window)


application = Application(
    layout=Layout(root_container, focused_element=input_field.window), 
    key_bindings=bindings,
    #style=style,
    mouse_support=True,
    full_screen=True,
)

def run():
    result = application.run()

def commandline(argv):
    print(argv)

if __name__ == "__main__":
    if len(argv) >= 2:
        commandline(argv)
    else:
        run()
