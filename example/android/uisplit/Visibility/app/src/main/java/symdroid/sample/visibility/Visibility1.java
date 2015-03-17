package symdroid.sample.visibility;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;


public class Visibility1 extends Activity implements OnClickListener {

  private static String TAG = "Visibility1";
  private View mVictim;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_visibility1);

    // Find the view whose visibility will change
    mVictim = findViewById(R.id.victim);

    // Find our buttons
    Button visibleButton = (Button) findViewById(R.id.vis);
    Button invisibleButton = (Button) findViewById(R.id.invis);
    Button goneButton = (Button) findViewById(R.id.gone);

    // Wire each button to a click listener
/*
    visibleButton.setOnClickListener(mVisibleListener);
    invisibleButton.setOnClickListener(mInvisibleListener);
    goneButton.setOnClickListener(mGoneListener);
*/
    visibleButton.setOnClickListener(this);
    invisibleButton.setOnClickListener(this);
    goneButton.setOnClickListener(this);
  }

/*
  OnClickListener mVisibleListener = new OnClickListener() {
    public void onClick(View v) {
      mVictim.setVisibility(View.VISIBLE);
    }
  };

  OnClickListener mInvisibleListener = new OnClickListener() {
    public void onClick(View v) {
      mVictim.setVisibility(View.INVISIBLE);
    }
  };

  OnClickListener mGoneListener = new OnClickListener() {
    public void onClick(View v) {
      mVictim.setVisibility(View.GONE);
    }
  };
*/

  public void onClick(View v) {
    int id = v.getId();
    if (id == R.id.vis) {
        mVictim.setVisibility(View.VISIBLE);
    } else if (id == R.id.invis) {
        mVictim.setVisibility(View.INVISIBLE);
    } else if (id == R.id.gone) {
        mVictim.setVisibility(View.GONE);
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

    LinearLayout tv_layout = new LinearLayout(this);
    tv_layout.setOrientation(LinearLayout.VERTICAL);
    tv_layout.setLayoutParams(new ViewGroup.LayoutParams(mp, wc));
    // could set box drawable background

    TextView tv = new TextView(this);
    tv.setBackgroundColor(0xffff0000);
    tv.setText("View A");
    tv_layout.addView(tv, 0, new ViewGroup.LayoutParams(mp, wc));

    tv = new TextView(this);
    tv.setId(R.id.victim);
    tv.setBackgroundColor(0xff00ff00);
    tv.setText("View B");
    tv_layout.addView(tv, 1, new ViewGroup.LayoutParams(mp, wc));

    tv = new TextView(this);
    tv.setBackgroundColor(0xff0000ff);
    tv.setText("View C");
    tv_layout.addView(tv, 2, new ViewGroup.LayoutParams(mp, wc));

    LinearLayout btn_layout = new LinearLayout(this);
    btn_layout.setOrientation(LinearLayout.HORIZONTAL);
    btn_layout.setLayoutParams(new ViewGroup.LayoutParams(wc, wc));

    Button b = new Button(this);
    b.setId(R.id.vis);
    b.setText("Vis");
    btn_layout.addView(b, 0, new ViewGroup.LayoutParams(wc, wc));

    b = new Button(this);
    b.setId(R.id.invis);
    b.setText("Invis");
    btn_layout.addView(b, 1, new ViewGroup.LayoutParams(wc, wc));

    b = new Button(this);
    b.setId(R.id.gone);
    b.setText("Gone");
    btn_layout.addView(b, 2, new ViewGroup.LayoutParams(wc, wc));

    top_layout.addView(tv_layout);
    top_layout.addView(btn_layout);

    setContentView(top_layout);
  }

}
