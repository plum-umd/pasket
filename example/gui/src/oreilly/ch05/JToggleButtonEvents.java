package oreilly.ch05;

// JToggleButtonEvents.java
// The event demonstration program for JToggleButton.
//
import javax.swing.*;
import javax.swing.event.*;
import java.awt.*;
import java.awt.event.*;

public class JToggleButtonEvents {
  public static void main(String[] args) {
    JToggleButton jtb = new JToggleButton("Press_Me");

    jtb.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent ev) {
        System.out.println("ActionEvent!");
      }
    });
    jtb.addItemListener(new ItemListener() {
      public void itemStateChanged(ItemEvent ev) {
        System.out.println("ItemEvent!");
      }
    });
/*
    jtb.addChangeListener(new ChangeListener() {
      public void stateChanged(ChangeEvent ev) {
        System.out.println("ChangeEvent!");
      }
    });
*/
    JFrame f = new JFrame(JToggleButtonEvents.class.getName());
    f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
/*
    Container c = f.getContentPane();
    c.setLayout(new FlowLayout());
    c.add(jtb);
*/
    f.add(jtb);
    f.pack();
    f.setVisible(true);
  }
}
