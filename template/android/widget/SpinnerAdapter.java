package android.widget;

public interface SpinnerAdapter extends Adapter {
  public abstract View getDropDownView(int position, View convertView, ViewGroup parent);
}
