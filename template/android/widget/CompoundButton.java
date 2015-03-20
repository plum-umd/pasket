package android.widget;

@ObserverPattern(MotionEvent)
public abstract class CompoundButton extends Button {
  public CompoundButton(Context context);

  @ObserverPattern(MotionEvent)
  public static interface OnCheckedChangeListener {
    public void onCheckedChanged(CompundButton buttonView, boolean isChecked);
  }

  public void setOnCheckedChangeListener(CompoundButton.OnCheckedChangeListener listener);

  // "internal purpose only" to propagate checked state change
  void setOnCheckedChangeWidgetListener(CompoundButton.OnCheckedChangeListener listener);

  public boolean isChecked();
  public void setChecked(boolean checked);

  public void toggle();

  public boolean performClick();
}
