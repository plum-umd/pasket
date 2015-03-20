package javax.swing.event;

@ObserverPattern(ListSelectionEvent)
public interface ListSelectionListener {
  public void valueChanged(ListSelectionEvent e);
}
