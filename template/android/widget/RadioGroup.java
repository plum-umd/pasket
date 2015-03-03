package android.widget;

public class RadioGroup extends LinearLayout {

  public static interface OnCheckedChangeListener {
    public abstract void onCheckedChanged(RadioGroup group, int checkedId);
  }

  public void setOnCheckedChangeListener(RadioGroup.OnCheckedChangeListener listener);

  public void check(int id);
  public void clearCheck();
  public int getCheckedRadioButtonId();

}
