package android.widget;

public class RadioGroup extends LinearLayout {

  public static interface OnCheckedChangeListener {
    public abstract void onCheckedChanged(RadioGroup group, int checkedId);
  }

}
