# app.py
# ==========================================
# RENDER TERMINAL STYLE WEB APP
# SINGLE PYTHON FILE
# ==========================================

import os
import json
import html
import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

PORT = int(os.environ.get("PORT", "10000"))

HOSTNAME = "render-server"
USERNAME = "root"

# -------------------------------------------------
# DEMO FILE SYSTEM
# -------------------------------------------------

FILES = {
    "/": ["app", "bin", "etc", "home", "tmp", "usr", "var"],
    "/app": ["app.py", "README.md"],
    "/home": [],
    "/tmp": [],
    "/etc": ["hostname", "os-release"],
}


def normalize_path(path):
    if not path:
        return "/"

    if not path.startswith("/"):
        path = "/" + path

    parts = []

    for part in path.split("/"):
        if part in ("", "."):
            continue

        if part == "..":
            if parts:
                parts.pop()
        else:
            parts.append(part)

    return "/" + "/".join(parts)


def execute_demo_command(command, cwd="/"):
    command = command.strip()

    if not command:
        return ""

    parts = command.split()
    cmd = parts[0].lower()
    args = parts[1:]

    # -----------------------------------------
    # HELP
    # -----------------------------------------

    if cmd == "help":
        return """Available commands:

help       Show available commands
clear      Clear terminal
cls        Clear terminal
pwd        Show current directory
ls         List files
cd         Change directory
whoami     Show current user
hostname   Show hostname
date       Show current date/time
echo       Print text
uname      Show system information
env        Show demo environment
cat        Read demo files
history    Show command history
id         Show demo user information
neofetch   Show server information
version    Show application version
"""

    # -----------------------------------------
    # PWD
    # -----------------------------------------

    if cmd == "pwd":
        return cwd

    # -----------------------------------------
    # LS
    # -----------------------------------------

    if cmd == "ls":
        target = cwd

        if args:
            target = normalize_path(
                args[0] if args[0].startswith("/") else cwd + "/" + args[0]
            )

        if target not in FILES:
            return f"ls: cannot access '{target}': No such directory"

        return "  ".join(FILES[target])

    # -----------------------------------------
    # CD
    # -----------------------------------------

    if cmd == "cd":
        if not args:
            return "", "/"

        target = normalize_path(
            args[0] if args[0].startswith("/") else cwd + "/" + args[0]
        )

        if target not in FILES:
            return f"bash: cd: {args[0]}: No such directory"

        return "", target

    # -----------------------------------------
    # WHOAMI
    # -----------------------------------------

    if cmd == "whoami":
        return USERNAME

    # -----------------------------------------
    # HOSTNAME
    # -----------------------------------------

    if cmd == "hostname":
        return HOSTNAME

    # -----------------------------------------
    # DATE
    # -----------------------------------------

    if cmd == "date":
        return datetime.datetime.now().astimezone().strftime(
            "%a %b %d %H:%M:%S %Z %Y"
        )

    # -----------------------------------------
    # ECHO
    # -----------------------------------------

    if cmd == "echo":
        return " ".join(args)

    # -----------------------------------------
    # UNAME
    # -----------------------------------------

    if cmd == "uname":
        if "-a" in args:
            return (
                "Linux render-server 6.x-demo "
                "#1 SMP PREEMPT_DYNAMIC "
                "x86_64 GNU/Linux"
            )

        return "Linux"

    # -----------------------------------------
    # ENV
    # -----------------------------------------

    if cmd == "env":
        return """USER=root
HOME=/root
SHELL=/bin/bash
TERM=xterm-256color
LANG=C.UTF-8
PORT=10000
HOSTNAME=render-server"""

    # -----------------------------------------
    # ID
    # -----------------------------------------

    if cmd == "id":
        return "uid=0(root) gid=0(root) groups=0(root)"

    # -----------------------------------------
    # CAT
    # -----------------------------------------

    if cmd == "cat":

        if not args:
            return "cat: missing file operand"

        filename = args[0]

        demo_files = {
            "/etc/hostname": "render-server\n",

            "/etc/os-release": """NAME="Ubuntu"
VERSION="24.04 LTS"
ID=ubuntu
PRETTY_NAME="Ubuntu 24.04 LTS"
""",

            "/app/README.md": """# Render Terminal Demo

This is a browser-based terminal interface.

It does not execute arbitrary host shell commands.
""",

            "/app/app.py": "# Render Terminal Application\n",
        }

        target = normalize_path(
            filename if filename.startswith("/") else cwd + "/" + filename
        )

        if target not in demo_files:
            return f"cat: {filename}: No such file"

        return demo_files[target]

    # -----------------------------------------
    # HISTORY
    # -----------------------------------------

    if cmd == "history":
        return "History is maintained inside your browser session."

    # -----------------------------------------
    # NEOFETCH
    # -----------------------------------------

    if cmd == "neofetch":
        return r"""
        ██████╗ ███████╗███╗   ██╗██████╗ ███████╗██████╗
        ██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔════╝██╔══██╗
        ██████╔╝█████╗  ██╔██╗ ██║██║  ██║█████╗  ██████╔╝
        ██╔══██╗██╔══╝  ██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
        ██║  ██║███████╗██║ ╚████║██████╔╝███████╗██║  ██║
        ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝

        OS: Ubuntu 24.04 Demo
        Host: Render
        Shell: bash
        User: root
        Architecture: x86_64
        Terminal: Web
"""

    # -----------------------------------------
    # VERSION
    # -----------------------------------------

    if cmd == "version":
        return "Render Terminal Web v1.0.0"

    # -----------------------------------------
    # CLEAR
    # -----------------------------------------

    if cmd in ("clear", "cls"):
        return "__CLEAR__"

    # -----------------------------------------
    # UNKNOWN
    # -----------------------------------------

    return f"bash: {command}: command not found"


# -------------------------------------------------
# HTML
# -------------------------------------------------

HTML = r"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"
>

<title>Web Terminal</title>

<style>

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    background: #050505;
    color: #eeeeee;
    font-family:
        "Courier New",
        Courier,
        monospace;
    overflow: hidden;
}

body {
    display: flex;
    flex-direction: column;
}

/* TOP BAR */

.topbar {
    height: 52px;
    min-height: 52px;
    background: #111111;
    border-bottom: 1px solid #292929;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 14px;
}

.title {
    font-size: 14px;
    font-weight: bold;
    color: #eeeeee;
}

.status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: #8f8f8f;
}

.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #3ddc84;
}

/* TERMINAL */

.terminal {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 14px;
    background:
        radial-gradient(
            circle at top,
            #111111 0,
            #070707 45%,
            #030303 100%
        );
    -webkit-overflow-scrolling: touch;
}

.output {
    white-space: pre-wrap;
    word-break: break-word;
    font-size: 14px;
    line-height: 1.55;
}

.line {
    margin-bottom: 3px;
}

.command-line {
    color: #f1f1f1;
}

.prompt {
    color: #4ade80;
}

.output-text {
    color: #d2d2d2;
}

.error {
    color: #ff6868;
}

/* INPUT */

.input-area {
    background: #0e0e0e;
    border-top: 1px solid #292929;
    padding: 9px;
}

.input-row {
    display: flex;
    align-items: center;
    gap: 8px;
}

.prompt-small {
    color: #4ade80;
    font-size: 13px;
    white-space: nowrap;
}

#commandInput {
    flex: 1;
    min-width: 0;
    border: none;
    outline: none;
    background: transparent;
    color: white;
    font-family: inherit;
    font-size: 14px;
    caret-color: #4ade80;
}

#sendBtn {
    border: 0;
    background: #1f1f1f;
    color: #eeeeee;
    width: 42px;
    height: 38px;
    border-radius: 8px;
    font-size: 18px;
}

/* MOBILE KEYBOARD */

.keyboard {
    background: #0b0b0b;
    border-top: 1px solid #222222;
    padding: 7px;
}

.key-row {
    display: flex;
    gap: 5px;
    margin-bottom: 5px;
}

.key {
    flex: 1;
    min-width: 0;
    height: 36px;
    border: 1px solid #292929;
    border-radius: 6px;
    background: #171717;
    color: #dddddd;
    font-family: monospace;
    font-size: 12px;
    touch-action: manipulation;
}

.key:active {
    background: #292929;
    transform: scale(.97);
}

.key.wide {
    flex: 2;
}

@media (min-width: 700px) {

    .terminal {
        padding: 22px;
    }

    .output,
    #commandInput {
        font-size: 15px;
    }

    .keyboard {
        max-width: 900px;
        width: 100%;
        margin: auto;
    }
}

</style>

</head>

<body>

<div class="topbar">

    <div class="title">
        WEB TERMINAL
    </div>

    <div class="status">
        <span class="dot"></span>
        ONLINE
    </div>

</div>


<div
    id="terminal"
    class="terminal"
    onclick="focusInput()"
>

    <div id="output" class="output"></div>

</div>


<div class="input-area">

    <div class="input-row">

        <span
            id="prompt"
            class="prompt-small"
        >
            root@render:~#
        </span>

        <input
            id="commandInput"
            type="text"
            autocomplete="off"
            autocapitalize="none"
            spellcheck="false"
            enterkeyhint="send"
            placeholder="type command..."
        >

        <button
            id="sendBtn"
            onclick="runCommand()"
        >
            ➜
        </button>

    </div>

</div>


<div class="keyboard">

    <div class="key-row">

        <button class="key" onclick="insertKey('q')">q</button>
        <button class="key" onclick="insertKey('w')">w</button>
        <button class="key" onclick="insertKey('e')">e</button>
        <button class="key" onclick="insertKey('r')">r</button>
        <button class="key" onclick="insertKey('t')">t</button>
        <button class="key" onclick="insertKey('y')">y</button>
        <button class="key" onclick="insertKey('u')">u</button>
        <button class="key" onclick="insertKey('i')">i</button>
        <button class="key" onclick="insertKey('o')">o</button>
        <button class="key" onclick="insertKey('p')">p</button>

    </div>

    <div class="key-row">

        <button class="key" onclick="insertKey('a')">a</button>
        <button class="key" onclick="insertKey('s')">s</button>
        <button class="key" onclick="insertKey('d')">d</button>
        <button class="key" onclick="insertKey('f')">f</button>
        <button class="key" onclick="insertKey('g')">g</button>
        <button class="key" onclick="insertKey('h')">h</button>
        <button class="key" onclick="insertKey('j')">j</button>
        <button class="key" onclick="insertKey('k')">k</button>
        <button class="key" onclick="insertKey('l')">l</button>

    </div>

    <div class="key-row">

        <button class="key" onclick="insertKey('z')">z</button>
        <button class="key" onclick="insertKey('x')">x</button>
        <button class="key" onclick="insertKey('c')">c</button>
        <button class="key" onclick="insertKey('v')">v</button>
        <button class="key" onclick="insertKey('b')">b</button>
        <button class="key" onclick="insertKey('n')">n</button>
        <button class="key" onclick="insertKey('m')">m</button>
        <button class="key" onclick="insertKey('/')">/</button>
        <button class="key" onclick="backspace()">⌫</button>

    </div>

    <div class="key-row">

        <button
            class="key"
            onclick="insertKey(' ')"
        >
            SPACE
        </button>

        <button
            class="key"
            onclick="insertKey('-')"
        >
            -
        </button>

        <button
            class="key"
            onclick="insertKey('_')"
        >
            _
        </button>

        <button
            class="key"
            onclick="insertKey('.')"
        >
            .
        </button>

        <button
            class="key"
            onclick="runCommand()"
        >
            ENTER
        </button>

        <button
            class="key"
            onclick="clearTerminal()"
        >
            CLEAR
        </button>

    </div>

</div>


<script>

const input = document.getElementById("commandInput");
const output = document.getElementById("output");
const terminal = document.getElementById("terminal");
const promptElement = document.getElementById("prompt");

let cwd = "/";
let history = [];
let historyIndex = -1;


/* -----------------------------------------
   STARTUP
----------------------------------------- */

window.onload = function () {

    printOutput(
`Render Web Terminal
Type "help" to see available commands.

`
    );

    printPrompt();

    focusInput();
};


/* -----------------------------------------
   FOCUS
----------------------------------------- */

function focusInput() {
    input.focus();
}


/* -----------------------------------------
   INSERT KEY
----------------------------------------- */

function insertKey(key) {

    const start = input.selectionStart;
    const end = input.selectionEnd;

    input.value =
        input.value.substring(0, start) +
        key +
        input.value.substring(end);

    input.focus();

    input.selectionStart =
        input.selectionEnd =
        start + key.length;
}


/* -----------------------------------------
   BACKSPACE
----------------------------------------- */

function backspace() {

    const start = input.selectionStart;
    const end = input.selectionEnd;

    if (start !== end) {

        input.value =
            input.value.substring(0, start) +
            input.value.substring(end);

        input.selectionStart =
            input.selectionEnd =
            start;

        return;
    }

    if (start > 0) {

        input.value =
            input.value.substring(0, start - 1) +
            input.value.substring(start);

        input.selectionStart =
            input.selectionEnd =
            start - 1;
    }

    input.focus();
}


/* -----------------------------------------
   PRINT
----------------------------------------- */

function printOutput(text) {

    const div = document.createElement("div");

    div.className = "line output-text";

    div.textContent = text;

    output.appendChild(div);

    scrollBottom();
}


/* -----------------------------------------
   PROMPT
----------------------------------------- */

function printPrompt(command = null) {

    const div = document.createElement("div");

    div.className = "line command-line";

    const p = document.createElement("span");

    p.className = "prompt";

    const shownPath =
        cwd === "/" ? "~" : "~" + cwd;

    p.textContent =
        "root@render:" + shownPath + "# ";

    div.appendChild(p);

    if (command !== null) {

        const text = document.createTextNode(command);

        div.appendChild(text);
    }

    output.appendChild(div);

    scrollBottom();
}


/* -----------------------------------------
   RUN COMMAND
----------------------------------------- */

async function runCommand() {

    const command = input.value.trim();

    if (!command) {
        return;
    }

    history.push(command);

    historyIndex = history.length;

    printPrompt(command);

    input.value = "";

    try {

        const response = await fetch(
            "/api/command",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    command: command,
                    cwd: cwd
                })
            }
        );

        const data = await response.json();

        if (data.clear) {

            output.innerHTML = "";

            return;
        }

        if (data.cwd) {

            cwd = data.cwd;

            updatePrompt();
        }

        if (data.output) {

            const div = document.createElement("div");

            div.className =
                data.error
                ? "line error"
                : "line output-text";

            div.textContent = data.output;

            output.appendChild(div);

            scrollBottom();
        }

    } catch (error) {

        printOutput(
            "Connection error: " + error.message
        );
    }

    focusInput();
}


/* -----------------------------------------
   UPDATE PROMPT
----------------------------------------- */

function updatePrompt() {

    const shownPath =
        cwd === "/" ? "~" : "~" + cwd;

    promptElement.textContent =
        "root@render:" + shownPath + "#";
}


/* -----------------------------------------
   CLEAR
----------------------------------------- */

function clearTerminal() {

    output.innerHTML = "";

    printPrompt();

    input.value = "";

    focusInput();
}


/* -----------------------------------------
   SCROLL
----------------------------------------- */

function scrollBottom() {

    terminal.scrollTop =
        terminal.scrollHeight;
}


/* -----------------------------------------
   KEYBOARD
----------------------------------------- */

input.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            runCommand();

            return;
        }

        if (event.key === "ArrowUp") {

            event.preventDefault();

            if (!history.length) {
                return;
            }

            historyIndex =
                Math.max(
                    0,
                    historyIndex - 1
                );

            input.value =
                history[historyIndex];

            setTimeout(() => {

                input.selectionStart =
                    input.selectionEnd =
                    input.value.length;

            }, 0);

            return;
        }

        if (event.key === "ArrowDown") {

            event.preventDefault();

            if (!history.length) {
                return;
            }

            historyIndex =
                Math.min(
                    history.length,
                    historyIndex + 1
                );

            input.value =
                historyIndex === history.length
                ? ""
                : history[historyIndex];

            return;
        }

        if (
            event.ctrlKey &&
            event.key.toLowerCase() === "l"
        ) {

            event.preventDefault();

            clearTerminal();
        }
    }
);

</script>

</body>
</html>
"""


# -------------------------------------------------
# HTTP HANDLER
# -------------------------------------------------

class Handler(BaseHTTPRequestHandler):

    def send_response_data(
        self,
        data,
        status=200,
        content_type="application/json"
    ):

        if isinstance(data, str):
            body = data.encode("utf-8")
        else:
            body = json.dumps(data).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            content_type + "; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):

        path = urlparse(self.path).path

        if path == "/":

            self.send_response_data(
                HTML,
                200,
                "text/html"
            )

            return

        if path == "/health":

            self.send_response_data({
                "success": True,
                "status": "healthy"
            })

            return

        self.send_response_data({
            "success": False,
            "error": "Not found"
        }, 404)

    def do_POST(self):

        path = urlparse(self.path).path

        if path != "/api/command":

            self.send_response_data({
                "success": False,
                "error": "Not found"
            }, 404)

            return

        try:

            length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            # Basic request-size protection
            if length > 10000:

                self.send_response_data({
                    "success": False,
                    "error": "Request too large"
                }, 413)

                return

            raw = self.rfile.read(length)

            data = json.loads(
                raw.decode("utf-8")
            )

            command = str(
                data.get("command", "")
            )[:500]

            cwd = str(
                data.get("cwd", "/")
            )

            if cwd not in FILES:
                cwd = "/"

            result = execute_demo_command(
                command,
                cwd
            )

            new_cwd = cwd

            if isinstance(result, tuple):

                output, new_cwd = result

            else:

                output = result

            if output == "__CLEAR__":

                self.send_response_data({
                    "success": True,
                    "clear": True,
                    "cwd": new_cwd
                })

                return

            self.send_response_data({
                "success": True,
                "output": output,
                "cwd": new_cwd
            })

        except Exception as e:

            self.send_response_data({
                "success": False,
                "error": str(e)
            }, 400)

    def log_message(self, format, *args):

        print(
            "[HTTP]",
            format % args
        )


# -------------------------------------------------
# START SERVER
# -------------------------------------------------

def main():

    server = ThreadingHTTPServer(
        ("0.0.0.0", PORT),
        Handler
    )

    print("=" * 45)
    print(" RENDER WEB TERMINAL")
    print("=" * 45)
    print(f" Port: {PORT}")
    print(" Status: ONLINE")
    print("=" * 45)

    server.serve_forever()


if __name__ == "__main__":
    main()
