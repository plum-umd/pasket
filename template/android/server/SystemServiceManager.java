package com.android.server;

//@Singleton
public class SystemServiceManager {

  static SystemServiceManager getInstance();

  void registerService(String name, Object service);
  Object getService(String name);

}
