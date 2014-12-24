package java.awt.event;

@ObserverPattern(ItemEvent)
public interface ItemListener {
  public void itemStateChanged(ItemEvent e);
}
