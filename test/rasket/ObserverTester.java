package rasket.test;

import rasket.*;

class MockObserver implements ActionListener {
    private int aux;
    public MockObserver() {
	aux = 1;
    }
    public void actionPerformed(ActionEvent e) {}
}

public class ObserverTester {
    private static MockObserver mo;
    private static JButton jb;
    private static void init1() {
        mo = new MockObserver();
        jb = new JButton();
    }
    private static void init2() {
        mo = new MockObserver();
        jb = new JButton();
        jb.addActionListener(new MockObserver());
    }
    public static void addActionListenerTester() {
        init1();
        jb.addActionListener(mo);
    }
    public static void removeActionListenerTester() {
        init1();
        jb.removeActionListener(mo);
    }
    public static void fireActionPerformedTester() {
        init1();
        jb.removeActionListener(mo);
        init2();
        jb.removeActionListener(mo);
    }
    public static void main (String[] args) {
        addActionListenerTester();
        removeActionListenerTester();
        fireActionPerformedTester();
    }
}
