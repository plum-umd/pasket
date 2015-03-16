package android.view;

public class ViewGroup extends View {
  public ViewGroup(Context context);

  public static class LayoutParams {
    public static final int FILL_PARENT = -1; // deprecated since API Level 8
    public static final int MATCH_PARENT = -1;
    public static final int WRAP_CONTENT = -2;

    public LayoutParams(int width, int height);
  }

  public void addView(View child, int index, ViewGroup.LayoutParams params);
  public void addView(View child, ViewGroup.LayoutParams params);
  public void addView(View child);

  @Override
  protected View findViewTraversal(int id);

  public static class MarginLayoutParams extends ViewGroup.LayoutParams {
  }

}
