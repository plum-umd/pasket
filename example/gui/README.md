Usage
-----

Build the LoggerAgent first:

    $ cd ../../logger; ant; cd ../example/gui

Compile tutorials:

    $ ant [compile]

Or, applications:

    $ ant apps

Run the trace collector (along with examples names of interest):

    $ ./run.py [-c agent] [observer state ...]
    $ ./run.py --app lunar --app guessing ...

Possible design patterns, swing tutorials, and applications are:

* patterns
    - builder
    - observer
    - proxy
    - singleton
    - state

* tutorials
    - button_demo
    - button_html_demo
    - checkbox_demo
    - colorchooser_demo
    - combobox_demo
    - custom_icon_demo
    - toolbar_demo
    - toolbar_demo2
    - ...

* applications
    - calc
    - celsius
    - guessing
    - lunar
    - drawing
    - words
    - vote
    - ...

Or, you can run either patterns or swing examples:

    $ ./run.py patterns
    $ ./run.py tutorials

If you want to look at raw outputs, run the script with the following option:

    $ ./run.py -d [...]
    $ ./run.py --debug [...]

You can run examples without LoggerAgent:

    $ ./run.py --no-agent [...]

