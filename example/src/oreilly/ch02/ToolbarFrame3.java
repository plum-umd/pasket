package oreilly.ch02;

// ToolbarFrame3.java
// The Swing-ified button example. The buttons in this toolbar all carry images
// but no text.
//
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;

public class ToolbarFrame3 extends Frame {

  JButton cutButton, copyButton, pasteButton;
  JButton javaButton, macButton, motifButton, winButton;

  public ToolbarFrame3() {
    //super("Toolbar Example (Swing no text)");
    setSize(450, 250);

/*
    addWindowListener(new WindowAdapter() {
      public void windowClosing(WindowEvent e) {
        System.exit(0);
      }
    });
*/

    // JPanel works much like Panel does, so we'll use it
    JPanel toolbar = new JPanel();
    //toolbar.setLayout(new FlowLayout(FlowLayout.LEFT));

    CCPHandler handler = new CCPHandler();

    cutButton = new JButton("Cut", new ImageIcon("cut.gif"));
    cutButton.setActionCommand(CCPHandler.CUT);
    cutButton.addActionListener(handler);
    toolbar.add(cutButton);

    copyButton = new JButton("Copy", new ImageIcon("copy.gif"));
    copyButton.setActionCommand(CCPHandler.COPY);
    copyButton.addActionListener(handler);
    toolbar.add(copyButton);

    pasteButton = new JButton("Paste", new ImageIcon("paste.gif"));
    pasteButton.setActionCommand(CCPHandler.PASTE);
    pasteButton.addActionListener(handler);
    toolbar.add(pasteButton);

    //add(toolbar, BorderLayout.NORTH);
    add(toolbar);

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
    ToolbarFrame3 tf3 = new ToolbarFrame3();
    tf3.setVisible(true);
  }
}
