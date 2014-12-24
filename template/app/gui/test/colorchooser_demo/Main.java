import pasket.java.awt.*;
import pasket.java.awt.event.*;
import pasket.javax.swing.*;
import java.io.InputStream;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.IOException;

class Main {

static public void main (String[] args) throws FileNotFoundException, IOException {
    int len = args.length;
    int i = 0;
    while (i < len) {
        simulate(args[i]);
        i = i + 1;
    }
}

static public void simulate (String fname) throws FileNotFoundException, IOException {
    AdaptedColorChooserDemo.main();
    AdaptedColorChooserDemo current = AdaptedColorChooserDemo.getColorChooserDemo();
    SwingEventHandler handler = SanityChecker.getEventHandler(current);
    InputStream is = new FileInputStream(fname);
    BufferedReader br = new BufferedReader(new InputStreamReader(is));
    String line = br.readLine();
    while (line != null) {
        handler.handleEvent(line);
        line = br.readLine();
    }
}


}