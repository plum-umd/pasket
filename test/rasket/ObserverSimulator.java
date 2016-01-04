package rasket.test;

import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import javax.swing.JButton;

class RealObserver implements ActionListener {
    private int aux;
    public RealObserver() {
	aux = 1;
    }
    public void actionPerformed(ActionEvent e) {}
}

public class ObserverSimulator {
    private static RealObserver mo;
    private static JButton jb;
    private static void init1() {
        mo = new RealObserver();
        jb = new JButton();
    }
    private static void init2() {
        mo = new RealObserver();
        jb = new JButton();
        jb.addActionListener(new RealObserver());
    }
    public static void addActionListenerSimulator() {
        init1();
        jb.addActionListener(mo);
    }
    public static void removeActionListenerSimulator() {
        init1();
        jb.removeActionListener(mo);
    }
    public static void fireActionPerformedSimulator() {
        init1();
        jb.removeActionListener(mo);
        init2();
        jb.removeActionListener(mo);
    }
    public static void main (String[] args) {
        addActionListenerSimulator();
        removeActionListenerSimulator();
        fireActionPerformedSimulator();
    }
}
