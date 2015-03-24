package course.examples.UI.Button;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;

import android.view.ViewGroup;
import android.widget.RelativeLayout;

public class ButtonActivity extends Activity implements OnClickListener {
    int count = 0;
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

        Button button = (Button) findViewById(R.id.button);

        if (button.isEnabled()) {
            button.setOnClickListener(this);
        }
    }

    @Override
    public void onClick(View v) {
        //button.setText("Got Pressed:" + ++count);
        count = count + 1;
    }

    @Override
    public void setContentView(int id) {
        RelativeLayout top_layout = new RelativeLayout(this);
        top_layout.setLayoutParams(
            new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                                       ViewGroup.LayoutParams.MATCH_PARENT));
        Button btn = new Button(this);
        btn.setId(R.id.button);
        btn.setText("Press Me!");
        RelativeLayout.LayoutParams btnLP =
          new RelativeLayout.LayoutParams(RelativeLayout.LayoutParams.MATCH_PARENT,
                                          RelativeLayout.LayoutParams.WRAP_CONTENT);
        btnLP.addRule(RelativeLayout.ALIGN_PARENT_BOTTOM);
        btnLP.setMargins(10, 0, 0, 0);
        top_layout.addView(btn, 0, btnLP);

        setContentView(top_layout);
    }
}
