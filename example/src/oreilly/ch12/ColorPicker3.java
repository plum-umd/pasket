package oreilly.ch12;

// ColorPicker3.java
// A quick test of the JColorChooser dialog.  This example adds a custom
// preview pane.
//
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.colorchooser.*;

public class ColorPicker3 extends JFrame {

  Color c;

  public ColorPicker3() {
    super("JColorChooser Test Frame");
    setSize(200, 100);
    final JButton go = new JButton("Show_JColorChooser", null);
    final Container contentPane = getContentPane();
    go.addActionListener(new ActionListener() {
      final JColorChooser chooser = new JColorChooser();
      boolean first = true;
      public void actionPerformed(ActionEvent e) {
        if (first) {
          first = false;
          //GrayScalePanel gsp = new GrayScalePanel();
          //chooser.addChooserPanel(gsp);
          chooser.setPreviewPanel(new CustomPane());
        }
        JDialog dialog = JColorChooser.createDialog(ColorPicker3.this, 
            "Demo 3", true,
            chooser, new ActionListener() {
              public void actionPerformed(ActionEvent e) {
                c = chooser.getColor();
              }}, null);
        dialog.setVisible(true);
        contentPane.setBackground(c);
      }
    });
    //contentPane.add(go, BorderLayout.SOUTH);
    add(go);
    // addWindowListener(new BasicWindowMonitor());  // 1.1 & 1.2
    setDefaultCloseOperation(EXIT_ON_CLOSE);
  }

  public class CustomPane extends JPanel {
    JLabel j1 = new JLabel("This is a custom preview pane",
                           JLabel.CENTER);
    JLabel j2 = new JLabel("This label previews the background",
                           JLabel.CENTER);
    public CustomPane() {
      super(new GridLayout(0,1));
      j2.setOpaque(true);
      add(j1);
      add(j2);
    }

    public void setForeground(Color c) {
      super.setForeground(c);
      if (j1 != null) {
        j1.setForeground(c);
        j2.setBackground(c);
      }
    }
  }

  public static void main(String args[]) {
    ColorPicker3 cp3 = new ColorPicker3();
    cp3.setVisible(true);
  }
}
