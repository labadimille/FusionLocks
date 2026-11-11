# FusionLocks

![FusionLocks logo](logo.svg)

FusionLocks is a small, beginner-friendly programming language. Source files
use the `.fss` extension. This project is an early, working interpreter—not a
Python replacement or a security boundary.

## Download and portable setup (Windows)

1. Download this repository from GitHub with **Code > Download ZIP**, then
   extract it to a folder such as
   `C:\Users\YourName\Downloads\FusionLocks`.
2. The project does not need an installer or third-party packages. It can use
   Python 3 already installed on your computer.
3. For a self-contained folder, download the **Windows embeddable package**
   for Python 3.10 or newer from
   [python.org/downloads/windows](https://www.python.org/downloads/windows/).
   Extract the contents into this project's `runtime` folder so that this file
   exists: `FusionLocks\runtime\python.exe`. The launcher checks this runtime
   first. Keep the runtime and project together when moving the folder.
4. If you do not use the embeddable package, install Python 3 from the same
   official page and select **Add python.exe to PATH** in its installer.
5. Open Command Prompt in the project folder and run:

   ```bat
   run-fusionlocks.bat examples\hello.fss
   ```

   Or run it with Python directly:

   ```bat
   python fusionlocks.py examples\hello.fss
   ```

`runtime` is intentionally not included in the repository: Python's runtime is
distributed under its own license. Read the notices accompanying the Python
download before redistributing a bundled copy.

## Your first program

Create `hello.fss`:

```fss
let name = "Ada"
print "Hello, " + name + "!"

let n = 3
while n > 0 {
    print n
    set n = n - 1
}

if n == 0 {
    print "Done!"
}
```

Run it:

```bat
run-fusionlocks.bat hello.fss
```

Check syntax without running:

```bat
run-fusionlocks.bat --check hello.fss
```

## Language reference

- `let name = expression` declares a variable once.
- `set name = expression` changes a variable that was already declared.
- `print expression` writes a value to the console.
- `if condition { ... } else { ... }` selects a block.
- `while condition { ... }` repeats while its Boolean condition is `true`.
- Values: integers, decimal numbers, quoted strings, `true`, `false`.
- Operators: `+ - * / %`, comparisons `== != < <= > >=`, Boolean `and or not`,
  and parentheses.
- Use `#` for a comment. Separate statements with a new line or `;`.
- Conditions must evaluate to `true` or `false`. Numbers are not implicitly
  converted to strings; join strings with `+`.
- A safety limit stops programs after 100,000 executed statements.

## VS Code

The `vscode-extension` folder contains syntax highlighting for `.fss`. In VS
Code, open that folder, press **F5** to launch an Extension Development Host,
then open a `.fss` file in the new window.

## Project contents

- `fusionlocks.py` — interpreter and command-line tool.
- `run-fusionlocks.bat` — portable Windows launcher.
- `examples/` — working English and Italian examples.
- `tests/` — automated interpreter tests.
- `vscode-extension/` — VS Code language support.
- `logo.svg` — project logo; original vector artwork.

Run the tests with Python 3:

```bat
python -m unittest discover -s tests -v
```

## License and terms

FusionLocks is distributed under the [MIT License](LICENSE), which explains
the permissions and conditions for this project's code. There is no separate
FusionLocks Terms of Service: this repository is software, not a hosted
service. Python and VS Code are separate projects with their own licenses and
notices; consult their official sites for those terms.

## Publish on GitHub

Create an empty repository named `FusionLocks` at
[github.com/new](https://github.com/new) (do not pre-create a README or
license). From PowerShell in this folder, run the following, replacing the
placeholder with your GitHub username:

```powershell
git init
git add .
git commit -m "Initial FusionLocks language"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/FusionLocks.git
git push -u origin main
```

Do not add your private Python runtime to GitHub; `runtime/` is excluded by
`.gitignore`.

## Contributing

Issues and pull requests are welcome. Include a small `.fss` example and tests
when proposing a language feature. This is an early version; syntax and
behavior may evolve.
