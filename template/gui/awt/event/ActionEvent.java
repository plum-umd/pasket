package java.awt.event;

public class ActionEvent extends AWTEvent {
  public static final int ALT_MASK = 8;
  public ActionEvent(Object source, int id, String actioncommand);
  public String getActionCommand();
}
