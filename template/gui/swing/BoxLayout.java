package javax.swing;

public class BoxLayout implements LayoutManager {
  public static final int X_AXIS = 0;
  public static final int Y_AXIS = 1;
  public static final int LINE_AXIS = 2;
  public static final int PAGE_AXIS = 3;

  public BoxLayout(Container target, int axis);

  void addLayoutComponent(String name, Component comp);
}
