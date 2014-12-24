package java.awt.event;

public class ItemEvent extends AWTEvent {
  public static final int DESELECTED = 2;
  public static final int SELECTED = 1;

  public ItemEvent(ItemSelectable source, int id, Object item, int statechange);

  //public Object getItem();
  public ItemSelectable getItemSelectable();
  public int getStateChange();
}
