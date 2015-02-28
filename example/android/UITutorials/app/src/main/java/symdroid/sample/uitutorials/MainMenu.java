package symdroid.sample.uitutorials;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
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
}
