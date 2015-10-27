package javax.swing;

public class JMenuItem extends AbstractButton implements Accessible {
  public JMenuItem();
  public JMenuItem(Icon icon);
  public JMenuItem(String text);
  public JMenuItem(String text, Icon icon);
  public JMenuItem(String text, int mnemonic);

  public KeyStroke getAccelerator();
  public void setAccelerator(KeyStroke keyStroke);

  public AccessibleContext getAccessibleContext();
}
