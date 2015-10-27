package javax.swing;

public class ActionMap {
  public ActionMap();

  public void clear();

  public Action get(Object key);
  public void put(Object key, Action action);
}
