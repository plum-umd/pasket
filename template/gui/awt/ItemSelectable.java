package java.awt;

@ObserverPattern(ItemEvent)
public interface ItemSelectable {
  void addItemListener(ItemListener l);
  void removeItemListener(ItemListener l);
}
