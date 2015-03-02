package android.widget;

public class LinearLayout extends ViewGroup {
  public static final int HORIZONTAL = 0;
  public static final int VERTICAL = 1;

  public void setOrientation(int orientation);

  public static class LayoutParams extends ViewGroup.MarginLayoutParams {
  }

}
