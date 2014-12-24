import org.junit.Test;
import org.junit.Ignore;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;

import java.nio.file.*;
import java.io.*;
import java.util.*;
import java.lang.reflect.*;


@RunWith(JUnit4.class)
public class Button_html_demoTest extends SanityChecker {
    
    @Test
    public void thisAlwaysPasses() {
    }
    
    @Test
    public void check()
    throws ClassNotFoundException, NoSuchMethodException,
    IllegalAccessException, InvocationTargetException,
    IOException, InterruptedException {
        sanityCheck("button_html_demo", 1);
    }
    
    
}
