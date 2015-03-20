package javax.swing;

@ObserverPattern(ListSelectionEvent)
public class JList extends JComponent {
  public JList(ListModel dataModel);

  public void addListSelectionListener(ListSelectionListener listener);
  public void removeListSelectionListener(ListSelectionListener listener);

  //protected void fireSelectionValueChanged(int firstIndex, int lastIndex, boolean isAdjusting);
  protected void fireSelectionValueChanged(ListSelectionEvent e);

  public void ensureIndexIsVisible(int index);
  public void setSelectionMode(int selectionMode);

  public int getSelectedIndex();
  public void setSelectedIndex(int index);

  public int getVisibleRowCount();
  public void setVisibleRowCount(int visibleRowCount);
}
