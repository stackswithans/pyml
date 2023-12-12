from pyml.elements import *


def Page(
    *,
    page_title: str = "",
    head_elements: HTMLRenderable | None = None,
    body: Element | None = None
) -> HTMLRenderable:
    return Siblings(
        [
            "<!DOCTYPE html>",
            html(
                child=[
                    head(
                        child=[
                            meta(charset="UTF-8"),
                            title(child=page_title),
                            head_elements,
                        ],
                    ),
                    body,
                ]
            ),
        ]
    )
