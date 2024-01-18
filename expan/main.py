import argparse
import os
import sys
from expan.preprocessor import PyPreprocessor
from expan.error import ExpansionError
import traceback as tb

path = os.path


def expand_src(src_path: str):
    with open(src_path, "r", encoding="utf8") as f:
        src = f.read()

    preproc = PyPreprocessor()
    return preproc.preprocess_src(path.abspath(src_path), src)


def main(argv: list[str] | None = None):
    if not argv:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser("expan.py")
    parser.add_argument(
        "src",
        help="The source file to perform macro expansion on. Must have the '.pyxp' extension.",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        help="Name of the output file containing the expanded source. If not provided, expansion result is printed to stdout.",
    )
    args = parser.parse_args(args=argv)

    if not path.exists(args.src):
        print(f"The path {args.src} does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        res = expand_src(args.src)
    except ExpansionError as e:
        print(
            e.explain(),
            file=sys.stderr,
        )
        sys.exit(1)

    # Write to outfile
    if args.outfile:
        with open(args.outfile, "w", encoding="utf8") as out:
            out.write(res)
    else:
        print(res)


if __name__ == "__main__":
    main()
