package javax.swing.event;

@ObserverPattern(DocumentEvent)
public interface DocumentListener {
  public void changedUpdate(DocumentEvent e);
  public void insertUpdate(DocumentEvent e);
  public void removeUpdate(DocumentEvent e);
}
