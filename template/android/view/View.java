package android.view;

public class View {
  public View(Context context);

  public static interface OnClickListener {
    public abstract void onClick(View v);
  }

  public void setOnClickListener(View.OnClickListener l);
}
