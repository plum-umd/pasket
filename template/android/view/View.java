package android.view;

@ObserverPattern(MotionEvent)
public class View {
  public View(Context context);

  public void setBackgroundColor(int color);

  public void setPadding(int left, int top, int right, int bottom);
  public int getPaddingLeft();
  public int getPaddingTop();
  public int getPaddingRight();
  public int getPaddingBottom();

  public final static int VISIBLE = 0;
  public final static int INVISIBLE = 4;
  public final static int GONE = 8;

  public void setVisibility(int visibility);
  public int getVisibility();
  public boolean isShown();

  public static final int NO_ID = -1;

  public void setId(int id);
  public int getId();
  public final View findViewById(int id);
  protected View findViewTraversal(int id);

  public ViewGroup.LayoutParams getLayoutParams();
  public void setLayoutParams(ViewGroup.LayoutParams params);

  public Handler getHandler();

  @ObserverPattern(MotionEvent)
  public static interface OnClickListener {
    public abstract void onClick(View v);
  }

  public void setOnClickListener(View.OnClickListener l);

  public boolean dispatchTouchEvent(MotionEvent event);
  //public boolean onTouchEvent(MotionEvent event);

  public boolean performClick();
}
