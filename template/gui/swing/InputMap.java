package javax.swing;

public class InputMap {
  public InputMap();

  public void clear();

  public Object get(KeyStroke keyStroke);
  public void put(KeyStroke keyStroke, Object actionMapKey);
}
