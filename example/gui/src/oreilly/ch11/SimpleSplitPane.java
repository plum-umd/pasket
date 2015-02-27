package oreilly.ch11;

// SimpleSplitPane.java
// A quick test of the JSplitPane class.
//
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;

public class SimpleSplitPane extends JFrame {

  static String sometext = "This is a simple text string that is long enough " +
    "to wrap over a few lines in the simple demo we're about to build.  " +
    "We'll put two text areas side by side in a split pane.";

  public SimpleSplitPane() {
    super("Simple SplitPane Frame");
    setSize(450, 200);
    setDefaultCloseOperation(EXIT_ON_CLOSE);

    JTextArea jt1 = new JTextArea(); //new JTextArea(sometext);
    JTextArea jt2 = new JTextArea(); //new JTextArea(sometext);

    // Make sure our text boxes do line wrapping and have reasonable
    // minimum sizes.
/*
    jt1.setLineWrap(true);
    jt2.setLineWrap(true);
    jt1.setMinimumSize(new Dimension(150, 150));
    jt2.setMinimumSize(new Dimension(150, 150));
    jt1.setPreferredSize(new Dimension(250, 200));
*/
    //JSplitPane sp = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, jt1, jt2);
    JSplitPane sp = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
    sp.add(jt1);
    sp.add(jt2);
    //getContentPane().add(sp, BorderLayout.CENTER);
    add(sp);
  }

  public static void main(String args[]) {
    SimpleSplitPane ssb = new SimpleSplitPane();
    ssb.setVisible(true);
  }
}
