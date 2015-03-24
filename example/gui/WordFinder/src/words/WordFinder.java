package words;

/*import static layout.TableLayoutConstants.FILL;
import static layout.TableLayoutConstants.PREFERRED;
import layout.TableLayout;*/

import java.awt.Container;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;

import javax.swing.*;

import java.awt.BorderLayout;

/**
 * WordFinder is an interface for searching a word list.
 * When the user types any part of a word, the interface
 * displays all the words that match.
 */
public class WordFinder extends JFrame {

    private static final long serialVersionUID = 1L;
    
    private final WordList words = new WordList();
    
    private final JTextField find;
    
    private final JList list;
    
    private final JLabel counter;
    
    /**
     * Make a WordFinder window.
     */
    public WordFinder() {
        super("Word Finder");
        
        // call System.exit() when user closes the window
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        
        Container cp = this.getContentPane();
        /*
         * Task 2: set the layout manager of the content pane to a TableLayout.
         */
        cp.setLayout(new BorderLayout());
        
        cp.add(new JLabel("Find: "));
        
        find = new JTextField(20);
        cp.add(find);
        /*
         * Task 1: add an action listener to `find' that outputs matching words
         *         to the console
         */
        find.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                doFind();
            }
        });
        
        /*
         * Task 3: add a JList inside a JScrollPane that shows matching words
         */
        list = new JList(new DefaultListModel());
        JScrollPane scroller = new JScrollPane(list);
        cp.add(scroller);
        
        /*
         * Task 4: add a JLabel that shows the number of matching words
         */
        counter = new JLabel("");
        cp.add(counter);
        
        /*
         * Task 5: add a Search button
         */
        JButton search = new JButton("Search");
        search.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                doFind();
            } 
        });
        cp.add(search);
        
        JButton clear = new JButton("Clear");
        clear.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                doClear();
            } 
        });
        cp.add(clear);
        
        /*
         * Task 6: add a File menu with Open... and Exit options
         */
        JMenuBar menubar = new JMenuBar();
        JMenu fileMenu = new JMenu("File");
        
        JMenuItem openItem = new JMenuItem("Open...");
        fileMenu.add(openItem);
        openItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                doOpen();
            }
        });
        
        JMenuItem exitItem = new JMenuItem("Exit");
        exitItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                System.exit(0);
            }
        });
        fileMenu.add(exitItem);
        
        menubar.add(fileMenu);
        setJMenuBar(menubar);
        
        this.pack();
        
        try {
            InputStream in = new FileInputStream("words.txt");
            loadWords(in);
        } catch (IOException ioe) { }
        doFind();
    }
    
    private void doClear() {
        find.setText("");
        doFind();
        find.grabFocus();
    }
    
    private void doFind() {
        String query = find.getText();
        
        List<String> matches = words.find(query);
        DefaultListModel listModel = (DefaultListModel) list.getModel();
        listModel.removeAllElements();
        for (String match : matches) {
            listModel.addElement(match);
        }
        
        updateCounter(query);
        find.selectAll();
        find.grabFocus();
    }
    
    private void updateCounter(String query) {
        int n = list.getModel().getSize();
        String msg;
        if (query.equals("")) msg = n + " words total";
        else msg = n + " matches for '" + query + "'";
        counter.setText(msg);
    }
    
    private void loadWords(InputStream in) throws IOException {
        words.load(in);
        doClear();
    }
    
    private void doOpen() {
        JFileChooser chooser = new JFileChooser();
        int returnVal = chooser.showOpenDialog(this);
        if(returnVal == JFileChooser.APPROVE_OPTION) {
            try {
                loadFile(chooser.getSelectedFile());
            } catch (IOException e) {
                e.printStackTrace();
            }
        }        
    }
    
    private void loadFile(File file) throws IOException {
        FileInputStream in = new FileInputStream(file);
        loadWords(in);
        in.close();
    }
    
    /**
     * Main method.  Makes and displays a WordFinder window.
     * @param args Command-line arguments.  Ignored.
     */
    public static void main(String[] args) {
        // In general, Swing objects should only be accessed from
        // the event-handling thread -- not from the main thread
        // or other threads you create yourself.  SwingUtilities.invokeLater()
        // is a standard idiom for switching to the event-handling thread.
                // Make and display the WordFinder window.
                new WordFinder().setVisible(true);
    }    
}
