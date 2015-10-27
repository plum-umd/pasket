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

package symdroid.sample.spinner;

// Need the following import to get access to the app resources, since this
// class is in a sub-package.

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemSelectedListener;
import android.widget.ArrayAdapter;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;


public class Spinner1 extends Activity {

  void showToast(CharSequence msg) {
    Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
  }

  // hardcoded from R.array.colors
  String[] mColors = {"red", "orange", "yellow", "green", "blue", "purple"};
  // hardcoded from R.array.planets
  String[] mPlanets = {"Mercury", "Venus", "Earth", "Mars", "Ceres", "Jupiter",
                       "Saturn", "Uranus", "Neptune", "Pluto-Charon", "Haumea",
                       "Makemake", "Eris"};

  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_spinner1);

    Spinner s1 = (Spinner) findViewById(R.id.spinner1);
//    ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(
//        this, R.array.colors, R.layout.simple_spinner_item);
    ArrayAdapter<CharSequence> adapter;
    adapter = new ArrayAdapter<CharSequence>(this,
        R.layout.simple_spinner_item, mColors);
    adapter.setDropDownViewResource(R.layout.simple_spinner_dropdown_item);
    s1.setAdapter(adapter);
    s1.setOnItemSelectedListener(
        new OnItemSelectedListener() {
          public void onItemSelected(
              AdapterView<?> parent, View view, int position, long id) {
            showToast("Spinner1: position=" + position + " id=" + id);
          }

          public void onNothingSelected(AdapterView<?> parent) {
            showToast("Spinner1: unselected");
          }
        });

    Spinner s2 = (Spinner) findViewById(R.id.spinner2);
//    adapter = ArrayAdapter.createFromResource(this, R.array.planets,
//        R.layout.simple_spinner_item);
    adapter = new ArrayAdapter<CharSequence>(this,
        R.layout.simple_spinner_item, mPlanets);
    adapter.setDropDownViewResource(R.layout.simple_spinner_dropdown_item);
    s2.setAdapter(adapter);
    s2.setOnItemSelectedListener(
        new OnItemSelectedListener() {
          public void onItemSelected(
              AdapterView<?> parent, View view, int position, long id) {
            showToast("Spinner2: position=" + position + " id=" + id);
          }

          public void onNothingSelected(AdapterView<?> parent) {
            showToast("Spinner2: unselected");
          }
        });
  }
  @Override
  @SuppressWarnings("unused")
  public void setContentView(int id) {

    ViewGroup.LayoutParams mpwc = new ViewGroup.LayoutParams(
        ViewGroup.LayoutParams.MATCH_PARENT,
        ViewGroup.LayoutParams.WRAP_CONTENT
    );

    LinearLayout topLayout = new LinearLayout(this);
    topLayout.setOrientation(LinearLayout.VERTICAL);
    topLayout.setPadding(10, 10, 10, 10);
    topLayout.setLayoutParams(mpwc);


    TextView tv = new TextView(this);
    tv.setText("Color:");
    topLayout.addView(tv, 0, mpwc);

    Spinner s = new Spinner(this, Spinner.MODE_DROPDOWN);
    // the XML has an attribute drawSelectorOnTop="true"
    // this is apparently a mistake, as somebody on the internets said it has no effect:
    // https://groups.google.com/forum/?fromgroups=#!topic/android-developers/c0OcLBrxsaU
    s.setId(R.id.spinner1);
    s.setPrompt("Choose a color");
    topLayout.addView(s, 1, mpwc);

    tv = new TextView(this);
    tv.setText("Planet:");
    topLayout.addView(tv, 2, mpwc);

    s = new Spinner(this, Spinner.MODE_DROPDOWN);
    s.setId(R.id.spinner2);
    s.setPrompt("Choose a planet");
    topLayout.addView(s, 3, mpwc);

    setContentView(topLayout);
  }
}
