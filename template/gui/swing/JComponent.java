package javax.swing;

public class JComponent extends Container {
  public static final int WHEN_FOCUSED = 0;
  public static final int WHEN_ANCESTOR_OF_FOCUSED_COMPONENT = 1;
  public static final int WHEN_IN_FOCUSED_WINDOW = 2;

  //public Border getBorder();
  //public void setBorder(Border border);

  public void setOpaque(boolean isOpaque);
  public void setToolTipText(String text);

  public final InputMap getInputMap(int condition);
  public final void setInputMap(int condition, InputMap map);

  public final ActionMap getActionMap();
  public final void setActionMap(ActionMap am);
}
