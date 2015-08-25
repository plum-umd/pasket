package course.examples.UI.CheckBox;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.CheckBox;

import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.util.TypedValue;
import android.widget.TextView;

public class CheckBoxActivity extends Activity implements OnClickListener {

  public CheckBoxActivity() {
    super();
  }

  CheckBox checkbox;
  Button button;

  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.main);

    checkbox = (CheckBox) findViewById(R.id.checkbox);
    checkbox.setOnClickListener(this);

    button = (Button) findViewById(R.id.button);
    button.setOnClickListener(this);
  }

  @Override
  public void onClick(View v) {
    int vid = v.getId();
    if (vid == R.id.checkbox) {
	  if (checkbox.isChecked()) {
		checkbox.setText("I'm checked");
	  } else {
		checkbox.setText("I'm not checked");
      }
    } else if (vid == R.id.button) {
	  if (checkbox.isShown()) {
		checkbox.setVisibility(View.INVISIBLE);
		button.setText("Unhide CheckBox");
	  } else {
		checkbox.setVisibility(View.VISIBLE);
		button.setText("Hide CheckBox");
	  }
    }
  }


  @Override
  @SuppressWarnings("unused")
  public void setContentView(int id) {
    // Hard-codes the layout from R.layout.activity_visibility1

    // shortcuts for layout parameters
    int mp = ViewGroup.LayoutParams.MATCH_PARENT;
    int wc = ViewGroup.LayoutParams.WRAP_CONTENT;

    LinearLayout top_layout = new LinearLayout(this);
    top_layout.setOrientation(LinearLayout.VERTICAL);
    top_layout.setLayoutParams(new ViewGroup.LayoutParams(mp, mp));

    TextView tv = new TextView(this);
    tv.setText("This is a checkbox");
    //tv.setTextSize(TypedValue.COMPLEX_UNIT_SP, 24.0f);
    top_layout.addView(tv, 0,
      new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,
                                    LinearLayout.LayoutParams.WRAP_CONTENT));

    CheckBox cb = new CheckBox(this);
    cb.setText("I'm not checked");
    //cb.setTextSize(TypedValue.COMPLEX_UNIT_SP, 24.0f);
    cb.setId(R.id.checkbox);
    top_layout.addView(cb, 1,
      new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT,
                                    LinearLayout.LayoutParams.WRAP_CONTENT));

    Button b = new Button(this);
    b.setText("Hide CheckBox");
    //b.setTextSize(TypedValue.COMPLEX_UNIT_SP, 24.0f);
    b.setId(R.id.button);
    top_layout.addView(b, 2,
      new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT,
                                    LinearLayout.LayoutParams.WRAP_CONTENT));

    setContentView(top_layout);
  }

}
