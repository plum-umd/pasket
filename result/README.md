* build.xml

Among others, the main purpose of this file is to test
whether the synthesized model is compilable:

    ...result $ ant [compile]

The next important feature is to copy the synthesized model
into symbolic executors,
such as JPF (with jpf-symbc and jpf-awt extensions)
and SymDroid (symbolic executor for Android).
You may need to set up your own paths to symbolic executors.

For Swing:

    ...result $ ant gui

For Android:

    ...result $ ./rename-android.sh
    ...result $ ant android

This build file will also be used to run sanity checkers,
which run the original tutorial on top of the synthesized model.
Refer to $pasket/test/test.py for more details.

* clean.sh

As its name implies, it will clean up all remnants.

* debug.sh

This script is designed to debug intermediate sketch files.
Pass the sk_* folder you want to debug:

    ...result $ ./debug.sh sk...demo

It will run Sketch while keeping temporary files; rerun it
with the last choices to generate executable c++ code.
This script automatically makes some changes over those generated files,
e.g., making a testing script executable;
adding correct -I path if you're running Sketch from the source; and
moving all of them to tmp/ folder.  Under tmp/ folder, just run the script:

    ...result $ cd tmp
    ...tmp $ ./script

You may need to revise sample.cpp and repeat the process
until you encounter either memory errors or assertion failure.  Good luck.

* rename-XXX.sh

The synthesize model uses the target framework's pacakge names,
which will conflict when running a symbolic executor with the model.
This script will visit every file in the java/ folder and rename the packages.

For Swing: refer to $pasket/test/test.py

For Android: refer to build.xml explanation

* stat.sh

This script will show you how big generated files are:

    ...result $ ./stat.sh sk...demo

* post.py

This script will post-analyze output files under output/ folder:

    ...result $ ./post.py

