package javax.swing;

public class GroupLayout implements LayoutManager {
  public static final int DEFAULT_SIZE = -1;
  public static final int PREFERRED_SIZE = -2;

  public GroupLayout(Container host);

  public enum Alignment {
    LEADING,
    TRAILING,
    CENTER,
    BASELINE
  }

  public abstract class Group {
    public Group addComponent(Component component);
    public Group addComponent(Component component, int min, int pref, int max);
    public Group addGroup(Group group);
  }

  public class ParallelGroup extends Group {
    public ParallelGroup addComponent(Component component, Alignment alignment);
    public ParallelGroup addComponent(Component component, Alignment alignment, int min, int pref, int max);
    public ParallelGroup addGroup(Alignment alignment, Group group);
  }

  public class SequentialGroup extends Group {
    public SequentialGroup addContainerGap();
    public SequentialGroup addPreferredGap(LayoutStyle.ComponentPlacement type);
  }

  @Factory
  public ParallelGroup createParallelGroup(Alignment alignment);
  @Factory
  public SequentialGroup createSequentialGroup();

  public void setHorizontalGroup(Group group);
  public void setVerticalGroup(Group group);

}
