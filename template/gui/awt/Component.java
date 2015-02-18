package java.awt;

public class Component {
  protected Component();

  // public void dispatchEvent(AWTEvent event);

  public boolean isEnabled();
  public void setEnabled(boolean b);

  public boolean isVisible();
  public void setVisible(boolean b);

  public Color getBackground();
  public void setBackground(Color c);
}
