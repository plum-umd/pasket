package java.awt;

public class BorderLayout implements LayoutManager {
  public static final String CENTER = "Center";
  public static final String LINE_START = "Before";
  public static final String PAGE_END = "Last";
  public static final String PAGE_START = "First";

  public BorderLayout();

  public void addLayoutComponent(String name, Component comp);
}
