package symdroid.sample.radiogroup;

/*
 * Copyright (C) 2007 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;


public class RadioGroup1 extends Activity implements RadioGroup.OnCheckedChangeListener,
    View.OnClickListener {

  private TextView mChoice;
  private RadioGroup mRadioGroup;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    setContentView(R.layout.activity_radio_group1);
    mRadioGroup = (RadioGroup) findViewById(R.id.menu);

    // test adding a radio button programmatically
    RadioButton newRadioButton = new RadioButton(this);
    newRadioButton.setText("Snack");
    newRadioButton.setId(R.id.snack);
    LinearLayout.LayoutParams layoutParams = new RadioGroup.LayoutParams(
        RadioGroup.LayoutParams.WRAP_CONTENT,
        RadioGroup.LayoutParams.WRAP_CONTENT);
    mRadioGroup.addView(newRadioButton, 0, layoutParams);

    // test listening to checked change events
    //String selection = "You have selected: ";
    mRadioGroup.setOnCheckedChangeListener(this);
    mChoice = (TextView) findViewById(R.id.choice);
    //mChoice.setText(selection + mRadioGroup.getCheckedRadioButtonId());
    String msg = Integer.toString(mRadioGroup.getCheckedRadioButtonId());
    mChoice.setText(msg);

    // test clearing the selection
    Button clearButton = (Button) findViewById(R.id.clear);
    clearButton.setOnClickListener(this);
  }

  public void onCheckedChanged(RadioGroup group, int checkedId) {
    /*
    String selection = "You have selected: ";
    String none = "(none)";
    String msg;
    if (checkedId == View.NO_ID) {
      msg = selection + none;
    } else {
      msg = selection + checkedId;
    }
    */
    String msg = Integer.toString(checkedId);
    mChoice.setText(msg);
  }

  public void onClick(View v) {
    mRadioGroup.clearCheck();
  }

  @Override
  @SuppressWarnings("unused")
  public void setContentView(int id) {
    ViewGroup.LayoutParams mpwc = new ViewGroup.LayoutParams(
        ViewGroup.LayoutParams.MATCH_PARENT,
        ViewGroup.LayoutParams.WRAP_CONTENT
    );

    ViewGroup.LayoutParams mpmp = new ViewGroup.LayoutParams(
        ViewGroup.LayoutParams.MATCH_PARENT,
        ViewGroup.LayoutParams.MATCH_PARENT
    );

    ViewGroup.LayoutParams wcwc = new ViewGroup.LayoutParams(
        ViewGroup.LayoutParams.WRAP_CONTENT,
        ViewGroup.LayoutParams.WRAP_CONTENT
    );

    LinearLayout topLayout = new LinearLayout(this);
    topLayout.setOrientation(LinearLayout.VERTICAL);
    topLayout.setLayoutParams(mpmp);

    RadioGroup rg = new RadioGroup(this);
    rg.setId(R.id.menu);
    rg.setOrientation(LinearLayout.VERTICAL);

    RadioButton rb = new RadioButton(this);
    rb.setId(R.id.breakfast);
    rb.setText("Breakfast");
    rg.addView(rb);

    rb = new RadioButton(this);
    rb.setId(R.id.lunch);
    rb.setText("Lunch");
    rg.addView(rb);

    rb = new RadioButton(this);
    rb.setId(R.id.dinner);
    rb.setText("Dinner");
    rg.addView(rb);

    rb = new RadioButton(this);
    rb.setId(R.id.all);
    rb.setText("All of them");
    rg.addView(rb);

    TextView tv = new TextView(this);
    tv.setId(R.id.choice);
    //tv.setText("You have selected: (none)");
    tv.setText("-1");
    rg.addView(tv);  // weird to add to the RG but that's what the layout file did

    rg.check(R.id.lunch);
    topLayout.addView(rg, 0, mpwc);

    Button b = new Button(this);
    b.setId(R.id.clear);
    b.setText("Clear");
    topLayout.addView(b, 1, wcwc);

    setContentView(topLayout);
  }

}
