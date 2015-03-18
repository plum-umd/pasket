package com.microjobsinc.dloc;

import android.app.Activity;
import android.content.Context;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;

public class Main extends Activity {
  private LocationManager lm;
  private LocationListener locListenD;
  public TextView tvLatitude;
  public TextView tvLongitude;

  // jon added for debugging
  private static final String TAG = "DLoc";

  /** Called when the activity is first created. */
  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);

    // find the TextViews
    tvLatitude = (TextView)findViewById(R.id.tvLatitude);
    tvLongitude = (TextView)findViewById(R.id.tvLongitude);

    // get handle for LocationManager
    // note--the original tutorial declared this LocationManager locally (but
    // still had the instance variable declaration too). this caused null
    // pointer exceptions in onResume.
    lm = (LocationManager) getSystemService(Context.LOCATION_SERVICE);

    // connect to the GPS location service
    Location loc = lm.getLastKnownLocation("gps");

    // jon added for debugging
    if (loc == null)
      Log.w(TAG, "Null initial location!");

    // fill in the TextViews
    tvLatitude.setText(loc == null ? "null" : Double.toString(loc.getLatitude()));
    tvLongitude.setText(loc == null ? "null" : Double.toString(loc.getLongitude()));

    // ask the Location Manager to send us location updates
    locListenD = new DispLocListener();
    lm.requestLocationUpdates("gps", 30000L, 10.0f, locListenD);
  }

  private class DispLocListener implements LocationListener {

    @Override
    public void onLocationChanged(Location location) {
      // update TextViews
      tvLatitude.setText(Double.toString(location.getLatitude()));
      tvLongitude.setText(Double.toString(location.getLongitude()));
    }

    @Override
    public void onProviderDisabled(String provider) {
    }

    @Override
    public void onProviderEnabled(String provider) {
    }

    @Override
    public void onStatusChanged(String provider, int status, Bundle extras) {
    }
  }

  /**
   *  Turn off location updates if we're paused
   */
  @Override
  public void onPause() {
    super.onPause();
    lm.removeUpdates(locListenD);
  }

  /**
   * Resume location updates when we're resumed
   */
  @Override
  public void onResume() {
    super.onResume();
    lm.requestLocationUpdates("gps", 30000L, 10.0f, locListenD);
  }
}
