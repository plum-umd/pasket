package symdroid.sample.uitutorials;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.RelativeLayout;
import android.widget.Toast;


public class MainMenu extends Activity {

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main_menu);
  }

  public void startMiniApp(View button) {
    Intent intent;
    Class<? extends Activity> child;

    switch (button.getId()) {
      case R.id.startVisibility1:
        child = Visibility1.class;
        break;
      case R.id.startSpinner1:
        child = Spinner1.class;
        break;
      case R.id.startRadioGroup1:
        child = RadioGroup1.class;
        break;
      default:
        child = null;
        break;
    }

    if (child != null) {
      intent = new Intent(this, child);
      startActivity(intent);
    } else {
      Toast.makeText(this, "No handler for this button.", Toast.LENGTH_SHORT).show();
    }
  }

  @Override
  @SuppressWarnings("Unused")
  public void setContentView(int id) {
    ViewGroup.LayoutParams mpmp = new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
        ViewGroup.LayoutParams.MATCH_PARENT);

    RelativeLayout top_layout = new RelativeLayout(this);
    top_layout.setLayoutParams(mpmp);
    top_layout.setPadding(16, 16, 16, 16);

    // in automatically generated code we'd probably repeat this for each button
    View.OnClickListener ocl = new View.OnClickListener() {
      @Override
      public void onClick(View v) {
        startMiniApp(v);
      }
    };

    Button b = new Button(this);
    b.setId(R.id.startVisibility1);
    b.setOnClickListener(ocl);
    b.setText("Visibility");
    RelativeLayout.LayoutParams lp = new RelativeLayout.LayoutParams(
        RelativeLayout.LayoutParams.MATCH_PARENT,
        RelativeLayout.LayoutParams.WRAP_CONTENT);
    lp.addRule(RelativeLayout.CENTER_HORIZONTAL);
    top_layout.addView(b, lp);

    b = new Button(this);
    b.setId(R.id.startSpinner1);
    b.setOnClickListener(ocl);
    b.setText("Spinner");
    lp = new RelativeLayout.LayoutParams(
        RelativeLayout.LayoutParams.MATCH_PARENT,
        RelativeLayout.LayoutParams.WRAP_CONTENT);
    lp.addRule(RelativeLayout.CENTER_HORIZONTAL);
    lp.addRule(RelativeLayout.BELOW, R.id.startVisibility1);
    top_layout.addView(b, lp);

    b = new Button(this);
    b.setId(R.id.startRadioGroup1);
    b.setOnClickListener(ocl);
    b.setText("Radio Group");
    lp = new RelativeLayout.LayoutParams(
        RelativeLayout.LayoutParams.MATCH_PARENT,
        RelativeLayout.LayoutParams.WRAP_CONTENT);
    lp.addRule(RelativeLayout.CENTER_HORIZONTAL);
    lp.addRule(RelativeLayout.BELOW, R.id.startSpinner1);
    top_layout.addView(b, lp);

    setContentView(top_layout);
  }

}
