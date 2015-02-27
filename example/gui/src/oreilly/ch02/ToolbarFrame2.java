package oreilly.ch02;

// ToolbarFrame2.java
// The Swing-ified button example.  
//
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;

public class ToolbarFrame2 extends Frame {

  // This time, let's use JButtons!
  JButton cutButton, copyButton, pasteButton;
  JButton javaButton, macButton, motifButton, winButton;

  public ToolbarFrame2() {
    //super("Toolbar Example (Swing)");
    setSize(450, 250);

/*
    addWindowListener(new WindowAdapter() {
      public void windowClosing(WindowEvent e) {
        System.exit(0);
      }
    });
*/

    ActionListener printListener = new ActionListener() {
      public void actionPerformed(ActionEvent ae) {
        System.out.println(ae.getActionCommand());
      }
    };
  
    // JPanel works similarly to Panel, so we'll use it
    JPanel toolbar = new JPanel();
    //toolbar.setLayout(new FlowLayout(FlowLayout.LEFT));

    cutButton = new JButton("Cut", null);
    cutButton.addActionListener(printListener);
    toolbar.add(cutButton);

    copyButton = new JButton("Copy", null);
    copyButton.addActionListener(printListener);
    toolbar.add(copyButton);

    pasteButton = new JButton("Paste", null);
    pasteButton.addActionListener(printListener);
    toolbar.add(pasteButton);

    //add(toolbar, BorderLayout.NORTH);  // The new BorderLayout add
    add(toolbar);  // The new BorderLayout add

    // Add the look-and-feel controls
    JPanel lnfPanel = new JPanel();
    LnFListener lnfListener = new LnFListener(this);
    macButton = new JButton("Mac", null);
    macButton.addActionListener(lnfListener);
    lnfPanel.add(macButton);
    javaButton = new JButton("Metal", null);
    javaButton.addActionListener(lnfListener);
    lnfPanel.add(javaButton);
    motifButton = new JButton("Motif", null);
    motifButton.addActionListener(lnfListener);
    lnfPanel.add(motifButton);
    winButton = new JButton("Windows", null);
    winButton.addActionListener(lnfListener);
    lnfPanel.add(winButton);
    //add(lnfPanel, BorderLayout.SOUTH);
    add(lnfPanel);
  }

  public static void main(String args[]) {
    ToolbarFrame2 tf2 = new ToolbarFrame2();
    tf2.setVisible(true);
  }
}
