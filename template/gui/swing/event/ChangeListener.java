package javax.swing.event;

@ObserverPattern(ChangeEvent)
public interface ChangeListener {
  public void stateChanged(ChangeEvent e);
}
