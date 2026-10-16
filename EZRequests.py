import sys
import os
from pathlib import Path

from src.compiler.Compiler import Compiler
from src.Editor import TextEditor
from src.Visualizer import TextViewer
from src.compiler.RequestBuilder import Builder

args = sys.argv[1:]
print(args)

def fileCompile(path):

    compiler = Compiler(str(path))
    compiler.compileCode()

    builder = Builder(compiler.headers, compiler.data, compiler.url, compiler.type)

    builder.createRequest()
    builder.getFile()
    print(builder.output)
    view = TextViewer(compiler, builder.output, builder)
    view.protocol("WM_DELETE_WINDOW", view.on_closing)

    view.mainloop()

def main():
    if len(args) < 1:
        TextEditor().mainloop()
    else:

        file_path = Path(args[0])
        fileCompile(file_path)
        if os.path.exists(file_path.name):
            if file_path.suffix.lower() == ".ezq":
                fileCompile(file_path)
            else:
                print("invalid file extension")
                print("file extension should be .ezq")
        else:
            print("cannot find " + file_path.name)

if __name__ == "__main__":
    main()