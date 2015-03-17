package javax.swing.event;

public class ListSelectionEvent extends EventObject {
  public ListSelectionEvent(Object source, int firstIndex, int lastIndex, boolean isAdjusting);

  public int getFirstIndex();
  public int getLastIndex();
  public boolean getValueIsAdjusting();
}
