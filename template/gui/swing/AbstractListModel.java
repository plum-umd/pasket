package javax.swing;

public abstract class AbstractListModel implements ListModel {
  public AbstractListModel();

  public int getSize();
  public Object getElementAt(int index);
}
