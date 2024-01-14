import pytest
import expan.main as expmain


test_scaffold_expasion_err = """\
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
""".replace(
    "\n", ""
).replace(
    " ", ""
)

test_scaffold_expasion_import_err = """\
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
""".replace(
    "\n", ""
).replace(
    " ", ""
)


def test_scaffold_expasion_error_using_expan_cli(capsys):

    try:
        expmain.main(["tests/macros/badscaffold.pyxp"])
    except SystemExit:
        pass

    captured = capsys.readouterr()
    assert (
        captured.err.replace("\n", "").replace(" ", "")
        == test_scaffold_expasion_err
    )


def test_scaffold_expasion_error_using_import(capsys):
    try:
        import tests.macros.badscaffold
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert (
        captured.err.replace("\n", "").replace(" ", "")
        == test_scaffold_expasion_import_err
    )
