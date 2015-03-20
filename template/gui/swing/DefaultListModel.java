package javax.swing;

public class DefaultListModel extends AbstractListModel {
  public DefaultListModel();

  public void addElement(Object element);

  public boolean contains(Object elem);

  public void insertElementAt(Object element, int index);

  public Object remove(int index);
}
