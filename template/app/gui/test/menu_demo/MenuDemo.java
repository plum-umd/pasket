package tutorial.menu_demo;

/*
 * Copyright (c) 1995, 2008, Oracle and/or its affiliates. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - Neither the name of Oracle or the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */ 

import java.awt.*;
import java.awt.event.*;
import javax.swing.JMenu;
import javax.swing.JMenuItem;
import javax.swing.JCheckBoxMenuItem;
import javax.swing.JRadioButtonMenuItem;
import javax.swing.ButtonGroup;
import javax.swing.JMenuBar;
import javax.swing.KeyStroke;
import javax.swing.ImageIcon;

import javax.swing.JPanel;
import javax.swing.JTextArea;
import javax.swing.JScrollPane;
import javax.swing.JFrame;
import javax.swing.text.Document;
import javax.accessibility.AccessibleContext;

/* MenuDemo.java requires images/middle.gif. */

/*
 * This class is just like MenuLookDemo, except the menu items
 * actually do something, thanks to event listeners.
 */
public class MenuDemo implements ActionListener, ItemListener {
    JTextArea output;
    JScrollPane scrollPane;
    String newline = "\n";
    
    public MenuDemo() {
        output = null;
        scrollPane = null;
    }

    public JMenuBar createMenuBar() {
        JMenuBar menuBar;
        JMenu menu;
        JMenu submenu;
        JMenuItem menuItem;
        JRadioButtonMenuItem rbMenuItem;
        JCheckBoxMenuItem cbMenuItem;

        //Create the menu bar.
        menuBar = new JMenuBar();

        //Build the first menu.
        menu = new JMenu("A_Menu");
        menu.setMnemonic(KeyEvent.VK_A);
        /*menu.getAccessibleContext().setAccessibleDescription(
                "The only menu in this program that has menu items");*/
        AccessibleContext tmpContext1 = menu.getAccessibleContext();
        tmpContext1.setAccessibleDescription("The only menu in this program that has menu items");
        menuBar.add(menu);

        //a group of JMenuItems
        menuItem = new JMenuItem("A_text-only_menu_item",
                                 KeyEvent.VK_T);
        //menuItem.setMnemonic(KeyEvent.VK_T); //used constructor instead
        /*menuItem.setAccelerator(KeyStroke.getKeyStroke(
                KeyEvent.VK_1, ActionEvent.ALT_MASK));*/
        KeyStroke tmpStroke = KeyStroke.getKeyStroke(KeyEvent.VK_1, ActionEvent.ALT_MASK);
        menuItem.setAccelerator(tmpStroke);
        /*menuItem.getAccessibleContext().setAccessibleDescription(
                "This doesn't really do anything");*/
        AccessibleContext tmpContext2 = menuItem.getAccessibleContext();
        tmpContext2.setAccessibleDescription("This doesn't really do anything");
        menuItem.addActionListener(this);
        menu.add(menuItem);

        ImageIcon icon = createImageIcon("images/middle.gif");
        menuItem = new JMenuItem("Both_text_and_icon", icon);
        menuItem.setMnemonic(KeyEvent.VK_B);
        menuItem.addActionListener(this);
        menu.add(menuItem);

        menuItem = new JMenuItem(icon);
        menuItem.setMnemonic(KeyEvent.VK_D);
        menuItem.addActionListener(this);
        menu.add(menuItem);

        //a group of radio button menu items
        menu.addSeparator();
        ButtonGroup group = new ButtonGroup();

        rbMenuItem = new JRadioButtonMenuItem("A_radio_button_menu_item");
        rbMenuItem.setSelected(true);
        rbMenuItem.setMnemonic(KeyEvent.VK_R);
        group.add(rbMenuItem);
        rbMenuItem.addActionListener(this);
        menu.add(rbMenuItem);

        rbMenuItem = new JRadioButtonMenuItem("Another_one");
        rbMenuItem.setMnemonic(KeyEvent.VK_O);
        group.add(rbMenuItem);
        rbMenuItem.addActionListener(this);
        menu.add(rbMenuItem);

        //a group of check box menu items
        menu.addSeparator();
        cbMenuItem = new JCheckBoxMenuItem("A_check_box_menu_item");
        cbMenuItem.setMnemonic(KeyEvent.VK_C);
        cbMenuItem.addItemListener(this);
        menu.add(cbMenuItem);

        cbMenuItem = new JCheckBoxMenuItem("Another_one");
        cbMenuItem.setMnemonic(KeyEvent.VK_H);
        cbMenuItem.addItemListener(this);
        menu.add(cbMenuItem);

        //a submenu
        menu.addSeparator();
        submenu = new JMenu("A_submenu");
        submenu.setMnemonic(KeyEvent.VK_S);

        menuItem = new JMenuItem("An_item_in_the_submenu");
        /*menuItem.setAccelerator(KeyStroke.getKeyStroke(
                KeyEvent.VK_2, ActionEvent.ALT_MASK));*/
        KeyStroke tmpStroke2 = KeyStroke.getKeyStroke(
                KeyEvent.VK_2, ActionEvent.ALT_MASK);
        menuItem.setAccelerator(tmpStroke2);
        menuItem.addActionListener(this);
        submenu.add(menuItem);

        menuItem = new JMenuItem("Another_item");
        menuItem.addActionListener(this);
        submenu.add(menuItem);
        menu.add(submenu);

        //Build second menu in the menu bar.
        menu = new JMenu("Another_Menu");
        menu.setMnemonic(KeyEvent.VK_N);
        /*menu.getAccessibleContext().setAccessibleDescription(
                "This menu does nothing");*/
        AccessibleContext tmpContext3 = menu.getAccessibleContext();
        tmpContext3.setAccessibleDescription("This menu does nothing");
        menuBar.add(menu);

        return menuBar;
    }

    public Container createContentPane() {
        //Create the content-pane-to-be.
        /*JPanel contentPane = new JPanel(new BorderLayout());*/
        BorderLayout tmpLayout = new BorderLayout();
        JPanel contentPane = new JPanel(tmpLayout);
        contentPane.setOpaque(true);

        //Create a scrolled text area.
        output = new JTextArea(5, 30);
        output.setEditable(false);
        scrollPane = new JScrollPane(output);

        //Add the text area to the content pane.
        contentPane.add(scrollPane, BorderLayout.CENTER);

        return contentPane;
    }

    public void actionPerformed(ActionEvent e) {
        JMenuItem source = (JMenuItem)(e.getSource());
        String s = "Action event detected."
                   /*+ newline
                   + "    Event source: " + source.getText()
                   + " (an instance of " + getClassName(source) + ")"*/;
        output.append(s); // + newline);
        //output.setCaretPosition(output.getDocument().getLength());
        Document tmpDocument = output.getDocument();
        int tmpLength = 87; //tmpDocument.getLength();
        output.setCaretPosition(tmpLength);
    }

    public void itemStateChanged(ItemEvent e) {
        JMenuItem source = (JMenuItem)(e.getSource());
        String s = "Item event detected."
                   /*+ newline
                   + "    Event source: " + source.getText()
                   + " (an instance of " + getClassName(source) + ")"
                   + newline
                   + "    New state: "
                   + ((e.getStateChange() == ItemEvent.SELECTED) ?
                     "selected":"unselected")*/;
        output.append(s); // + newline);
        //output.setCaretPosition(output.getDocument().getLength());
        Document tmpDocument2 = output.getDocument();
        int tmpLength2 = 207; //tmpDocument2.getLength();
        output.setCaretPosition(tmpLength2);
    }

    // Returns just the class name -- no package info.
    /*protected String getClassName(Object o) {
        String classString = o.getClass().getName();
        int dotIndex = classString.lastIndexOf(".");
        return classString.substring(dotIndex+1);
    }*/

    /** Returns an ImageIcon, or null if the path was invalid. */
    protected static ImageIcon createImageIcon(String path) {
    /* TODO: .class returns the reference to java.lang.Class object
        java.net.URL imgURL = MenuDemo.class.getResource(path);
        if (imgURL != null) {
            return new ImageIcon(imgURL);
        } else {
            System.err.println("Couldn't find file: " + path);
            return null;
        }
    */
      return null;
    }

    /**
     * Create the GUI and show it.  For thread safety,
     * this method should be invoked from the
     * event-dispatching thread.
     */
    private static void createAndShowGUI() {
        //Create and set up the window.
        JFrame frame = new JFrame("MenuDemo");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        //Create and set up the content pane.
        MenuDemo demo = new MenuDemo();
        //frame.setJMenuBar(demo.createMenuBar());
        JMenuBar tmpBar = demo.createMenuBar();
        frame.setJMenuBar(tmpBar);
        //frame.setContentPane(demo.createContentPane());
        Container tmpPane = demo.createContentPane();
        frame.setContentPane(tmpPane);

        //Display the window.
        frame.setSize(450, 260);
        frame.setVisible(true);
    }

    public static void main() {
        //Schedule a job for the event-dispatching thread:
        //creating and showing this application's GUI.
        javax.swing.SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                createAndShowGUI();
            }
        });
    }
}
