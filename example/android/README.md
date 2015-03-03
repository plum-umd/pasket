Usage
-----

trim.py can capture the call-return sequences of the instrumented app.
(You should first instrument the app under test using redexer.)

If those logs are short enough, i.e., the phone (or emulator) can hold
all information in the memory, you may use the offline mode of the script:

    $ ./trim.py -d

Note that all command-line parameters will be passed to adb logcat, and
by default, "org.umd.logging:I *:S" is passed to filter out irrelevant logs.

If logs overflow, you should use the online mode:

    $ ./trim.py

The script catches key interrupt, so you can finish logging via Ctrl+C.

In either mode, logs are saved in "log.txt" and shown to the screen at once.
Thus, after collecting logs, you may need to move that file, e.g.:

    $ mv log.txt app.scenario.txt

