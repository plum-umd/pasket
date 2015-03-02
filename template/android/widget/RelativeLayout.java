package android.widget;

public class RelativeLayout extends ViewGroup {

  public static final int BELOW = 3;

  public static class LayoutParams extends ViewGroup.MarginLayoutParams {
    public void addRule(int verb);
    public void addRule(int verb, int anchor);
  }

}
