package javax.swing;

public class JMenu extends JMenuItem implements Accessible {
  public JMenu();
  public JMenu(String s);

  public void addSeparator();

  public AccessibleContext getAccessibleContext();
}
