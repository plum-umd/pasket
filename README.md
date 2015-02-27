pasket
======

pasket is a *pa*ttern-based *sket*ching tool that leverages design patterns
so as to synthesize larger-scale programs, e.g., a model of Android platform.


Requirements
------------

* Sketch

The main feature of this tool is to translate high-level templates into
low-level ones in [Sketch][sk167].  Thus, you have to install it first.
Download the tar ball and follow the instruction in it.
You may need to set your environment variables as follows:

    export SKETCH_HOME=/path/to/sketch/runtime
    PATH=$PATH:$SKETCH_HOME/..
    export PATH

* Apache Ant

There are several Java applications in this project.  To build them
efficiently, your system needs to have [Apache Ant][ant] installed.

* Python

This tool is tested under [Python 2.7.1][py271].

[sk167]: http://people.csail.mit.edu/asolar/sketch-1.6.7.tar.gz
[ant]: http://ant.apache.org
[py271]: http://www.python.org/download/releases/2.7/


Usage (Tool)
------------

First, generate the lexer and parser:

    $ ./run.py -c grammar [-g Java.g]

The default ANTLR grammar file is Java.g, which is modified to allow
annotations in an expression level.  The command above will generate
the lexer and parser in grammar/ folder.

Next, compile the custom code generator for sketch:

    $ ./run.py -c codegen

Note that your env should have variable $SKETCH\_HOME as mentioned above
so that the build process can refer to sketch jar file.
You can also use the following commands, if preferred:

    $ cd codegen; ant; cd ..

Then, synthesize a model of Android platform:

    $ ./run.py [-c android] [-s sample] [-t template] [-p pattern] [-o result]

Inputs for synthesis are samples and templates.  The default path for
sample is sample/android/ folder.  You can pass a single file, e.g.,

    $ ./run.py -s sample/android/remotedroid.txt

Otherwise, the tool will read all the samples in the given path,
e.g., sample/android/*/*.txt.  (sample/android/README.md explains
how to use sample/android/trim.py in order to obtain such samples
from apps instrumented by [redexer][redexer].)

The default paths for template are template/android/ and
template/app/android/ folders.  The former includes platform modelings,
while the latter has class hierarchies of the apps under test.
(Running template/app/hierarchy.py will extract such class hierarchy from
the app of interest.)  You can pass multitple templates, e.g.,

    $ ./run.py -t template/android -t template/app/android

By default, the tool will try all possible design patterns.  If performance
does matter, you can hint which design patterns are used in the template:

    $ ./run.py -p observer -p state

Using both samples and templates, the tool will encode the problem into
sketches, and those intermediate files will be left at result/sk*/ folder.
The final synthesized code will be placed at result/java/ folder.

To synthesize Java GUI model, run the following command:

    $ ./run.py -c gui -p button_demo -p checkbox_demo ... [opts]

Notice that you need -p option for every demo you pass.

There are more options for debugging purpose:

    --no-encoding: proceed without the encoding phase,
                   to test manipulated sketch files
    --no-sketch: examine the process without running sketch,
                 rather it will use previous output)

You can simulate a certain demo using the synthesized model:

    $ ./run.py -c gui -p button_demo -p colorchooser_demo --simulate colorchooser_demo2

where the first two demos are used for synthesizing a model,
and then the third one is simulated on top of that synthesized model.
If you pass the same demo as synthesis input and simulation target,
the tool will perform so-called sanity checking:

    $ ./run.py -c gui -p button_demo --simulate button_demo

which is just same as this:

    $ ./run.py -c gui -p button_demo --sanity

To run design pattern examples, use the following commands:

    $ ./run.py -c pattern -p observer
    $ ./run.py -c pattern -p state
    $ ./run.py -c pattern -p singleton

The existing examples can be tested as follows:

    $ ./test/test.py pattern observer
    $ ./test/test.py gui button_demo [checkbox_demo ...]

[redexer]: http://www.cs.umd.edu/projects/PL/redexer/


Usage (Model)
-------------

To run Java PathFinder (JPF) together with the synthesized model,
install jpf-core, jpf-symbc, and jpf-awt first.
In what follows, we assume those projects are installed
under user.home/Downloads/jpf directory.
Then, copy jpf-awt into jpf-awt-synth,
where the synthesized model will be placed.
To copy such synthesized model into that folder, run as follows:

  ...result $ ant gui

Next, go to jpf-awt-synth and build it same as other jpf-* projects.

JPF has its own event generating mechanism;
refer to example/src/oreilly/ch*/*Test.java
Classpath to compile JPF test classes is set up in example/build.xml,
so place your own target in that build.xml when you add new applications.
Also, generate app-specific test class accordingly.
To build examples and applications, refer to example/README.md

To run jpf-symbc both with jpf-awt and jpf-awt-synth,
you need to design configurations like:
example/src/oreilly/ch*/*.awt(-synth).jpf
Then, run jpf-symbc/bin/jpf, passing paths to those configurations.


Structure
---------

- Java.g -- an ANTLR grammar file for Java
- README.md -- the file you're currently reading
- antlr3/ -- Python wrapper for ANTLR parser generator
- codegen/ -- custom code generator for sketch (use '-c codegen' command)
    + build.xml -- for ant builder
    + lib/ -- where codegen.jar will be created
    + src/ -- source of custom code generator
        * CSV.java -- printing expressions in a csv format
- example/ -- example code
    + android -- Android examples/apps
    + gui -- Swing examples/apps
        * apps.json -- application descriptions
        * build.xml -- for ant builder
        * log\_method.d -- capturing call sequences in Java via dtrace
        * README.md -- explaining how to build examples and use example/run.py
        * run.py -- a script to run and log examples
        * src/ -- source of Swing examples
- grammar/ -- Java parser generated by ANTLR (use '-c grammar' command)
    + \_\_init\_\_.py -- to make this folder a library
    + Java.tokens -- (a variety of terminals, generated by ANTLR)
    + JavaLexer.py -- (lexer, generated by ANTLR)
    + JavaParser.py -- (parser, generated by ANTLR)
- lib/ -- external libraries
    + \_\_init\_\_.py -- to make this folder a library
    + antlr-3.1.3.jar -- ANTLR parser generator
    + const.py -- a module to make Java-like const
    + glob2/ -- a library that supports a recursive '\*\*' globbing syntax
    + hamcrest-core-1.3.jar -- a framework for writing matcher objects
    + junit-4.11.jar -- JUnit testing framework
    + typecheck.py -- a set of decorators to check types of functions
    + visit.py -- decorators for visitor pattern
- logger/ -- Java logger based on javassit instrument
    + build.xml -- for ant builder
    + Manifest.mf -- manifest file to make a jar file for the call logger
    + lib/ -- where loggeragent.jar will be created
        * javassist.jar -- Java instrument tool
    + src/ -- source of Java logger
- pyclean -- a script to delete all .pyc files recursively
- result/ -- result folder
    + build.xml -- for ant builder
    + clean.sh -- a script to clean result files
    + java/ -- final synthesis results will be placed here
    + java\_sk/ -- intermediate Java sketch files will be placed here
    + output/ -- sketch output files
    + rename.sh -- a script to rename packages in synthesized Java files
    + sk/ -- sketch files will be placed here
        * type.sk -- containing all the class declarations
        * log.sk -- a logging module, along with class and method ids
        * class\_x.sk -- corresponding to a single class and its methods
        * sample.sk -- the main harness, including all other sketch files
        * sample\_x.sk -- corresponding to a single sample (call-return seq.)
- run.py -- the main script to run the tool
- sample/ -- samples
    + android/ -- samples by running some Android apps
        * README.md -- explaining how to use sample/android/trim.py
        * trim.py -- a script to capture adb logcats
        * \*.txt -- a sample representing a single run
    + gui/ -- samples by running Swing apps
    + pattern/ -- samples by running examples in pattern/ folder
- pasket/ -- main source tree
    + \_\_init\_\_.py -- main entry point of this tool
    + analysis/
        * \_\_init\_\_.py
        * api.py -- collecting API usages in the given demo(s)
        * cover.py -- checking if the template covers API usages in demo(s)
        * empty.py -- measuring how many methods have empty body
    + anno.py -- parsing annotations in templates
    + decode/ -- pattern-specific synthesis interpretation
        * \_\_init\_\_.py -- generating a model
        * accessor.py -- accessor pattern
        * collection.py -- replacing interfaces with implementing classes
        * observer.py -- observer pattern
    + encoder.py -- translating high-level templates into low-level sketches
    + harness.py -- generating harness methods from the samples
    + logger.py -- logging pasket behavior
    + logging.conf -- logging configuration
    + meta -- meta-classes, along with utilities
        * \_\_init\_\_.py
        * clazz.py
        * expression.py
        * field.py
        * method.py
        * statement.py
        * template.py
    + psketch.py -- running Sketch in parallel
    + reducer.py -- reducing annotations in templates
    + rewrite/ -- pattern-specific rewriting rules
        * \_\_init\_\_.py -- including a base iterator
        * accessor.py -- basic accessors
        * android/ -- platform-specific reductions
        * builder.py -- builder pattern
        * factory.py -- factory pattern
        * gui/ -- platform-specific reductions
        * observer.py -- observer pattern
        * proxy.py -- proxy pattern
        * singleton.py -- singleton pattern
        * state.py -- state machine pattern
    + sample.py -- handling the given samples
    + sketch.py -- wrapper for Sketch
    + util.py -- utility functions
- template/ -- templates
    + android/ -- Android platform modelings
    + app/ -- templates for applications
        * android/ -- Android apps
            - hierarchy.py -- a script to extract class hierarchy from the app
            - \*.java -- the class hierarchy for apps under test
        * gui/ -- Java GUI apps
    + gui/ -- Swing modelings
    + pattern/ -- templates for examples in example/gui/src/pattern/ folder

