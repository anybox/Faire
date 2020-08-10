import os
from rich.console import Console
from rich.table import Table


class PrettyDisplayMixin:
    def __repr__(self):
        table = Table(title=f"[bold red][[ {self.__class__.__name__} ]]")
        table.add_column("Field", justify="right", style="cyan", no_wrap=True)
        table.add_column("Type", style="bold red on #000000")
        table.add_column("Value", justify="right", style="green")

        for attr, attr_type in self.__annotations__.items():
            table.add_row(
                attr, f"({attr_type.__name__})", str(getattr(self, attr))
            )

        console = Console(record=True, file=open(os.devnull, "w"))
        console.print(table)

        return str(console.export_text(styles=True))


__all__ = ["PrettyDisplayMixin"]
