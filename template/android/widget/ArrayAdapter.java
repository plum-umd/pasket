package android.widget;

public class ArrayAdapter extends BaseAdapter {
  public ArrayAdapter(Context context, int resource, Object[] objects);

  public Object getItem(int position);

  public View getDropDownView(int position, View convertView, ViewGroup parent);
  public void setDropDownViewResource(int resource);
}
