package javax.swing;

public class JToolBar extends JComponent {
  public JToolBar(String name);

  public void addSeparator() {
    Component separator = new JComponent(); // new Separator(); // TODO: inner class Separator
    // add(separator); // TODO: this will bother log conformity...
  }

  public void setFloatable(boolean b);
  public void setRollover(boolean rollover);
}
