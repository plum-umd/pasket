/*
 * LunarPhases.java is a 1.4 example that requires
 * the following files:
 *    images/image0.jpg
 *    images/image1.jpg
 *    images/image2.jpg
 *    images/image3.jpg
 *    images/image4.jpg
 *    images/image5.jpg
 *    images/image6.jpg
 *    images/image7.jpg
 */
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.net.URL;

public class LunarPhases implements ActionListener {
    final static int NUM_IMAGES = 8;
    final static int START_INDEX = 3;

    ImageIcon[] images = new ImageIcon[NUM_IMAGES];
    JPanel mainPanel, selectPanel, displayPanel;

    JComboBox phaseChoices = null;
    JLabel phaseIconLabel = null;

    public LunarPhases() {
        //Create the phase selection and display panels.
        selectPanel = new JPanel();
        displayPanel = new JPanel();

        //Add various widgets to the sub panels.
        addWidgets();

        //Create the main panel to contain the two sub panels.
        mainPanel = new JPanel();
        mainPanel.setLayout(new BoxLayout(mainPanel, BoxLayout.PAGE_AXIS));
        mainPanel.setBorder(BorderFactory.createEmptyBorder(5,5,5,5));

        //Add the select and display panels to the main panel.
        mainPanel.add(selectPanel);
        mainPanel.add(displayPanel);
    }

    /*
     * Get the images and set up the widgets.
     */
    private void addWidgets() {
        //Get the images and put them into an array of ImageIcons.
        for (int i = 0; i < NUM_IMAGES; i++) {
            images[i] = createImageIcon("/images/image" + i + ".jpg");
        }

        /*
         * Create a label for displaying the moon phase images and
         * put a border around it.
         */
        phaseIconLabel = new JLabel();
        phaseIconLabel.setHorizontalAlignment(JLabel.CENTER);
        phaseIconLabel.setVerticalAlignment(JLabel.CENTER);
        phaseIconLabel.setVerticalTextPosition(JLabel.CENTER);
        phaseIconLabel.setHorizontalTextPosition(JLabel.CENTER);
        phaseIconLabel.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLoweredBevelBorder(),
            BorderFactory.createEmptyBorder(5,5,5,5)));

        phaseIconLabel.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createEmptyBorder(0,0,10,0),
            phaseIconLabel.getBorder()));

        //Create a combo box with lunar phase choices.
        String[] phases = { "New", "Waxing Crescent", "First Quarter", 
                            "Waxing Gibbous", "Full", "Waning Gibbous", 
                            "Third Quarter", "Waning Crescent" };
        phaseChoices = new JComboBox(phases);
        phaseChoices.setSelectedIndex(START_INDEX);

        //Display the first image.
        phaseIconLabel.setIcon(images[START_INDEX]);
        phaseIconLabel.setText("");

        //Add a border around the select panel.
        selectPanel.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createTitledBorder("Select Phase"), 
            BorderFactory.createEmptyBorder(5,5,5,5)));

        //Add a border around the display panel.
        displayPanel.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createTitledBorder("Display Phase"), 
            BorderFactory.createEmptyBorder(5,5,5,5)));

        //Add moon phases combo box to select panel and image label.
        displayPanel.add(phaseIconLabel);
        selectPanel.add(phaseChoices);

        //Listen to events from the combo box.
        phaseChoices.addActionListener(this);
    }

    public void actionPerformed(ActionEvent event) {
        if ("comboBoxChanged".equals(event.getActionCommand())) {
            //Update the icon to display the new phase.
            phaseIconLabel.setIcon(images[phaseChoices.getSelectedIndex()]);
        }
    }

    /** Returns an ImageIcon, or null if the path was invalid. */
    protected static ImageIcon createImageIcon(String path) {
        java.net.URL imageURL = LunarPhases.class.getResource(path);

        if (imageURL == null) {
            System.err.println("Resource not found: "
                               + path);
            return null;
        } else {
            return new ImageIcon(imageURL);
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

        //Create a new instance of LunarPhases.
        LunarPhases phases = new LunarPhases();

        //Create and set up the window.
        JFrame lunarPhasesFrame = new JFrame("Lunar Phases");
        lunarPhasesFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE); 
        lunarPhasesFrame.setContentPane(phases.mainPanel);

        //Display the window.
        lunarPhasesFrame.pack();
        lunarPhasesFrame.setVisible(true);
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
