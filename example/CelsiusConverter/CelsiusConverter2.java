/**
 * CelsiusConverter2.java is a 1.4 application that demonstrates
 * the use of JButton, JTextFormattedField, and JLabel and 
 * requires the following file:
 *     images/convert.gif
 */

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.text.NumberFormatter;
import java.text.ParseException;
import java.text.DecimalFormat;
import java.net.URL;

public class CelsiusConverter2 implements ActionListener {
    JFrame converterFrame;
    JPanel converterPanel;
    JFormattedTextField tempCelsius;
    JLabel celsiusLabel, fahrenheitLabel;
    JButton convertTemp;

    public CelsiusConverter2() {
        //Create and set up the window.
        converterFrame = new JFrame("Convert Celsius to Fahrenheit");
        converterFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        converterFrame.setSize(new Dimension(120, 40));

        //Create and set up the panel.
        converterPanel = new JPanel(new GridLayout(2, 2));

        //Add the widgets.
        addWidgets();

        //Set the default button.
        converterFrame.getRootPane().setDefaultButton(convertTemp);

        //Add the panel to the window.
        converterFrame.getContentPane().add(converterPanel, BorderLayout.CENTER);

        //Display the window.
        converterFrame.pack();
        converterFrame.setVisible(true);
    }

    /**
     * Create and add the widgets.
     */
    private void addWidgets() {
        //Create the widgets.
        ImageIcon convertIcon = createImageIcon("images/convert.gif",
            "Convert temperature");

        //Create the format for the Celsius text field.
        tempCelsius = new JFormattedTextField(new DecimalFormat("##0.0#"));
        tempCelsius.setFocusLostBehavior(JFormattedTextField.COMMIT_OR_REVERT);

        //Set and commit the default temperature.
        try {
            tempCelsius.setText("37.0");
            tempCelsius.commitEdit();
        } catch(ParseException e) {
            //Shouldn't get here unless the setText value doesn't agree
            //with the format set above.
            e.printStackTrace();
        }

        celsiusLabel = new JLabel("Celsius", SwingConstants.LEFT);
        convertTemp = new JButton(convertIcon);

        fahrenheitLabel = new JLabel("Fahrenheit", SwingConstants.LEFT);

        celsiusLabel.setBorder(BorderFactory.createEmptyBorder(5,5,5,5));
        fahrenheitLabel.setBorder(BorderFactory.createEmptyBorder(5,5,5,5));

        //Listen to events from the Convert button and
        //the tempCelsius text field.
        convertTemp.addActionListener(this);
        tempCelsius.addActionListener(this);

        //Add the widgets to the container.
        converterPanel.add(tempCelsius);
        converterPanel.add(celsiusLabel);
        converterPanel.add(convertTemp);
        converterPanel.add(fahrenheitLabel);
    }

    public void actionPerformed(ActionEvent event) {
        String eventName = event.getActionCommand();
        //Parse degrees Celsius as a double and convert to Fahrenheit.
        int tempFahr = (int)((Double.parseDouble(tempCelsius.getText()))
                             * 1.8 + 32);

        //Set fahrenheitLabel to the new value and set font color
        //based on the temperature.
        if (tempFahr <= 32) {
            fahrenheitLabel.setText("<html><font Color=blue>" +
                        tempFahr + "&#176 </font> Fahrenheit</html>");
        } else if (tempFahr <= 80) {
            fahrenheitLabel.setText("<html><font Color=green>" +
                        tempFahr + "&#176 </font> Fahrenheit</html>");
        } else {
            fahrenheitLabel.setText("<html><font Color=red>" +
                        tempFahr + "&#176 </font> Fahrenheit</html>");
        }
    }

    /** Returns an ImageIcon, or null if the path was invalid. */
    protected static ImageIcon createImageIcon(String path,
                                               String description) {
        java.net.URL imgURL = CelsiusConverter2.class.getResource(path);
        if (imgURL != null) {
            return new ImageIcon(imgURL, description);
        } else {
            System.err.println("Couldn't find file: " + path);
            return null;
        }
    }

    /**
     * Create the GUI and show it.  For thread safety,
     * this method should be invoked from the
     * event-dispatching thread.
     */
    private static void createAndShowGUI() {
        //Make sure we have nice window decorations.
        JFrame.setDefaultLookAndFeelDecorated(true);

        CelsiusConverter2 converter = new CelsiusConverter2();
    }

    public static void main(String[] args) {
        //Schedule a job for the event-dispatching thread:
        //creating and showing this application's GUI.
        javax.swing.SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                createAndShowGUI();
            }
        });
    }
}
