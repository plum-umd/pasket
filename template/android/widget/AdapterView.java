package android.widget;

@ObserverPattern(MotionEvent)
public abstract class AdapterView<T> extends ViewGroup {
  public AdapterView(Context context);

  public abstract void setSelection(int position);

  @ObserverPattern(MotionEvent)
  public static interface OnItemSelectedListener {
    public abstract void onItemSelected(AdapterView parent, View view, int position, long id);
    public abstract void onNothingSelected(AdapterView parent);
  }

  public int getSelectedItemPosition();
  public long getSelectedItemId();

  public void setOnItemSelectedListener(AdapterView.OnItemSelectedListener listener);

  public boolean performItemClick(View view, int position, long id);

  private void fireOnSelected();
}
