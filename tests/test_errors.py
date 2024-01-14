import pytest
import expan.main as expmain


def purge_ws(string: str) -> str:
    return string.replace("\n", "").replace(" ", "").replace("\t", "")


def test_scaffold_expansion_error_using_expan_cli(capsys):
    test_scaffold_expansion_err = purge_ws(
        """\
    Error while performing macro expansion:
    /home/stacks/files/personal/Projects/pyml/tests/macros/badscaffold.pyxp, macro call located at (line 7: col 12)
        pysx!("<!DOCTYPE html>",
            html {
                head {
                    meta {
                        charset: "utf-8"
                    },
                    meta {
                        name: "viewport",
                        content: "width=device-width",
                        initial-scale: 1
                    }
                },
                body{
                    children
                },
    -------------^


            }
        )

    ---------------------------------------------------

    , found ','  (at char 378), (line:15, col:14)
    """
    )
    try:
        expmain.main(["tests/macros/badscaffold.pyxp"])
    except SystemExit:
        pass

    captured = capsys.readouterr()
    assert (
        captured.err.replace("\n", "").replace(" ", "")
        == test_scaffold_expansion_err
    )


def test_scaffold_expansion_error_using_import(capsys):
    test_scaffold_expansion_import_err = purge_ws(
        """\
    Error while performing expansion of imported module:
    /home/stacks/files/personal/Projects/pyml/tests/macros/badscaffold.pyxp, macro call located at (line 7: col 12)
        pysx!("<!DOCTYPE html>",
            html {
                head {
                    meta {
                        charset: "utf-8"
                    },
                    meta {
                        name: "viewport",
                        content: "width=device-width",
                        initial-scale: 1
                    }
                },
                body{
                    children
                },
    -------------^


            }
        )

    ---------------------------------------------------

    , found ','  (at char 378), (line:15, col:14)
    """
    )
    try:
        import tests.macros.badscaffold
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert (
        captured.err.replace("\n", "").replace(" ", "")
        == test_scaffold_expansion_import_err
    )


def test_errors_on_void_element_child(capsys):
    error_str = purge_ws(
        """
    Error while performing macro expansion:
    /home/stacks/files/personal/Projects/pyml/tests/macros/badelement.pyxp, macro call located at (line 4: col 8)
        pysx!(input {
    ----------^


            "sou mau"
        }
    )

    -----------------

    Void element 'input' cannot have children
    """
    )
    try:
        expmain.main(["tests/macros/badelement.pyxp"])
    except SystemExit:
        pass

    captured = capsys.readouterr()
    assert purge_ws(captured.err) == error_str
