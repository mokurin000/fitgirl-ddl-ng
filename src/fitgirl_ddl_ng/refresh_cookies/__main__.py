import asyncio

import typer
from fitgirl_ddl_ng.refresh_cookies import refresh_cookies

app = typer.Typer(add_completion=False)


@app.command()
def main(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Ignore valid cookies and force a refresh",
    ),
):
    asyncio.run(refresh_cookies(force))


if __name__ == "__main__":
    app()
