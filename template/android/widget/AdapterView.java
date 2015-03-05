package android.widget;

public abstract class AdapterView<T> extends ViewGroup {

  public static interface OnItemSelectedListener {
    public abstract void onItemSelected(AdapterView parent, View view, int position, long id);
    public abstract void onNothingSelected(AdapterView parent);
  }

  public void setOnItemSelectedListener(AdapterView.OnItemSelectedListener listener);
}
