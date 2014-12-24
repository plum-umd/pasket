package java.awt.event;

@ObserverPattern(ActionEvent)
public interface ActionListener {
  public void actionPerformed(ActionEvent e);
}
