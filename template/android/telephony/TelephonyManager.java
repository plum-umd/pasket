package android.telephony;

//@Singleton
public class TelephonyManager {

  public static TelephonyManager getDefault();

  public String getDeviceId();
  public String getDeviceSoftwareVersion();
  public String getNetworkCountryIso();

  /** No phone radio. */
  public static final int PHONE_TYPE_NONE = 0;
  /** Phone radio is GSM. */
  public static final int PHONE_TYPE_GSM = 1;
  /** Phone radio is CDMA. */
  public static final int PHONE_TYPE_CDMA = 2;
  /** Phone is via SIP. */
  public static final int PHONE_TYPE_SIP = 3;

  public int getPhoneType();

  public String getSimCountryIso();
  public String getSimSerialNumber();
  public String getVoiceMailNumber();

  public boolean isNetworkRoaming();

}
