from enum import auto
from typing import Iterable, List

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment

from textual import events
from textual.app import App
from textual.widgets import ScrollView


class PagerRenderable:
    def __init__(
        self, lines: Iterable[List[Segment]], new_lines: bool = False, width: int = 80
    ) -> None:
        """A simple renderable containing a number of lines of segments. May be used as an intermediate
        in rendering process.

        Args:
            lines (Iterable[List[Segment]]): Lists of segments forming lines.
            new_lines (bool, optional): Insert new lines after each line. Defaults to False.
        """
        self.lines = list(lines)
        self.new_lines = new_lines
        self.width = width

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        if self.new_lines:
            new_line = Segment.line()
            for line in self.lines:
                yield from line
                yield new_line
        else:
            for line in self.lines:
                yield from line

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return Measurement(self.width, self.width)


class PagerApp(App):
    """App to scroll renderable"""

    def __init__(
        self,
        *args,
        content=None,
        **kwargs,
    ) -> None:
        self.content = content
        super().__init__(*args, **kwargs)

    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_key(self, event: events.Key) -> None:
        if event.key == "j":
            self.body.scroll_up()
        elif event.key == "k":
            self.body.scroll_down()
        elif event.key == " ":
            self.body.page_down()
        elif event.key == "ctrl+u":
            self.body.target_y -= self.body.size.height // 2
            self.body.animate("y", self.body.target_y, easing="out_cubic")
        elif event.key == "ctrl+d":
            self.body.target_y += self.body.size.height // 2
            self.body.animate("y", self.body.target_y, easing="out_cubic")
        elif event.key == "f":
            # page down
            self.body.target_y += self.body.size.height
            self.body.y = self.body.target_y
        elif event.key == "b":
            # page up
            self.body.target_y -= self.body.size.height
            self.body.y = self.body.target_y
        elif event.key == "d":
            # half page-down
            self.body.target_y += self.body.size.height // 2
            self.body.y = self.body.target_y
        elif event.key == "u":
            # half page-up
            self.body.target_y -= self.body.size.height // 2
            self.body.y = self.body.target_y
        elif event.key == "g" or event.key == "1" :
            # jump to first line 
            # "g" is the "less" version; "1" is a shorthand for the "vi" command "1 -> Shift+G"
            self.body.target_x = self.body.target_y = 0
            self.body.x = self.body.y = 0
        elif event.key == "G":
            # jump to last line
            # Same shortcut in both "less" and "vi"
            self.body.target_x = 0
            self.body.target_y = self.body.window.virtual_size.height - self.body.size.height
            self.body.x, self.body.y = self.body.target_x, self.body.target_y

    async def on_mount(self, event: events.Mount) -> None:
        self.body = body = ScrollView(auto_width=True)

        await self.view.dock(body)
        await body.focus()
        await body.update(self.content)
