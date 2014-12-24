import org.junit.Test;
import org.junit.Ignore;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;

import java.nio.file.*;
import java.io.*;
import java.util.*;
import java.lang.reflect.*;


@RunWith(JUnit4.class)
public class Splitpane_divider_demoTest extends SanityChecker {
    
    @Test
    public void thisAlwaysPasses() {
    }
    
    @Test
    public void check()
    throws ClassNotFoundException, NoSuchMethodException,
    IllegalAccessException, InvocationTargetException,
    IOException, InterruptedException {
        sanityCheck("splitpane_divider_demo", 1);
    }

    
}
