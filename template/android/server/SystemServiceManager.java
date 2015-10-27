package com.android.server;

//@Singleton
public class SystemServiceManager {

  public static SystemServiceManager getInstance();

  public void registerService(String name, Object service);
  public Object getService(String name);

}
