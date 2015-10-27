package oreilly.ch05;

// JButtonEvents.java
// A simple demonstration of button events including Action, Item and Change
// event types.
//

import javax.swing.*;
import javax.swing.event.*;
import java.awt.*;
import java.awt.event.*;

public class JButtonEvents {
  public static void main(String[] args) {
    JButton jb = new JButton("Press_Me", null);

    jb.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent ev) {
        System.out.println("ActionEvent!");
      }
    });
    jb.addItemListener(new ItemListener() {
      public void itemStateChanged(ItemEvent ev) {
        System.out.println("ItemEvent!");
      }
    });
/*
    jb.addChangeListener(new ChangeListener() {
      public void stateChanged(ChangeEvent ev) {
        System.out.println("ChangeEvent!");
      }
    });
*/
    JFrame f = new JFrame(JButtonEvents.class.getName());
    f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    f.add(jb); //f.getContentPane().add(jb);
    f.pack();
    f.setVisible(true);
  }
}
