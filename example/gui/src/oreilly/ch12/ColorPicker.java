package oreilly.ch12;

// ColorPicker.java
// A quick test of the JColorChooser dialog.
//
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;

public class ColorPicker extends JFrame {

  public ColorPicker() {
    super("JColorChooser Test Frame");
    setSize(200, 100);
    final Container contentPane = getContentPane();
    final JButton go = new JButton("Show_JColorChooser", null);
    go.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent e) {
        Color c;
        c = JColorChooser.showDialog(
                  ((Component)e.getSource()).getParent(),
                  "Demo", Color.blue);
        contentPane.setBackground(c); 
      }
    });
    //contentPane.add(go, BorderLayout.SOUTH);
    add(go);
    setDefaultCloseOperation(EXIT_ON_CLOSE);
  }

  public static void main(String args[]) {
    ColorPicker cp = new ColorPicker();
    cp.setVisible(true);
  }
}
